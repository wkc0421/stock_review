from __future__ import annotations

import json
import os
import re
import urllib.parse
from datetime import date, datetime, time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))

EASTMONEY_KLINE_URL = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://quote.eastmoney.com/",
    "User-Agent": USER_AGENT,
}

POPULAR_STOCKS = [
    {"symbol": "000001", "name": "平安银行"},
    {"symbol": "000333", "name": "美的集团"},
    {"symbol": "000858", "name": "五粮液"},
    {"symbol": "002594", "name": "比亚迪"},
    {"symbol": "300059", "name": "东方财富"},
    {"symbol": "300750", "name": "宁德时代"},
    {"symbol": "600036", "name": "招商银行"},
    {"symbol": "600519", "name": "贵州茅台"},
    {"symbol": "601318", "name": "中国平安"},
    {"symbol": "601899", "name": "紫金矿业"},
    {"symbol": "688981", "name": "中芯国际"},
]


class ApiError(Exception):
    def __init__(self, message: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


def normalize_symbol(raw_symbol: str) -> str:
    cleaned = raw_symbol.strip().upper()
    cleaned = cleaned.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    cleaned = re.sub(r"^(SH|SZ|BJ)", "", cleaned)
    match = re.fullmatch(r"\d{6}", cleaned)
    if not match:
        raise ApiError(f"股票代码无效：{raw_symbol}")
    return cleaned


def eastmoney_market(symbol: str) -> int:
    # 东方财富 secid: 1 表示沪市，0 表示深市/北交所。
    if symbol.startswith(("5", "6", "9")):
        return 1
    return 0


def parse_date(raw_date: str) -> date:
    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ApiError("日期格式应为 YYYY-MM-DD") from exc


def fetch_json(url: str, params: dict[str, str], timeout: int = 15) -> dict[str, Any]:
    session = requests.Session()
    session.trust_env = os.environ.get("USE_SYSTEM_PROXY") == "1"
    try:
        response = session.get(url, params=params, headers=REQUEST_HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "未知"
        raise ApiError(f"行情源返回 HTTP {status_code}", HTTPStatus.BAD_GATEWAY) from exc
    except requests.RequestException as exc:
        raise ApiError(f"无法连接行情源：{exc}", HTTPStatus.BAD_GATEWAY) from exc
    except json.JSONDecodeError as exc:
        raise ApiError("行情源返回了无法解析的数据", HTTPStatus.BAD_GATEWAY) from exc


def minute_rows_for_day(symbol: str, target_date: date) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    secid = f"{eastmoney_market(symbol)}.{symbol}"
    ymd = target_date.strftime("%Y%m%d")
    payload = fetch_json(
        EASTMONEY_KLINE_URL,
        {
            "secid": secid,
            "klt": "1",
            "fqt": "0",
            "lmt": "10000",
            "beg": f"{ymd}000000",
            "end": f"{ymd}235959",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
        },
    )
    data = payload.get("data")
    if not data:
        raise ApiError(f"{symbol} 未返回行情数据", HTTPStatus.BAD_GATEWAY)

    target_start = datetime.combine(target_date, time.min)
    target_end = datetime.combine(target_date, time.max)
    previous_close: float | None = None
    rows: list[dict[str, Any]] = []

    for raw_line in data.get("klines", []):
        fields = raw_line.split(",")
        if len(fields) < 7:
            continue

        row_datetime = datetime.strptime(fields[0], "%Y-%m-%d %H:%M")
        close_price = float(fields[2])

        if row_datetime < target_start:
            previous_close = close_price
            continue
        if row_datetime > target_end:
            break

        open_price = float(fields[1])
        high_price = float(fields[3])
        low_price = float(fields[4])
        volume = int(float(fields[5]))
        amount = float(fields[6])
        rows.append(
            {
                "time": row_datetime.strftime("%H:%M"),
                "datetime": row_datetime.strftime("%Y-%m-%d %H:%M"),
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": volume,
                "amount": amount,
            }
        )

    if rows:
        base_price = previous_close or rows[0]["open"]
        for row in rows:
            row["changePct"] = round((row["close"] - base_price) / base_price * 100, 4)
    else:
        base_price = None

    meta = {
        "symbol": symbol,
        "name": data.get("name") or symbol,
        "market": data.get("market"),
        "basePrice": base_price,
    }
    return meta, rows


def minutes_response(query: dict[str, list[str]]) -> dict[str, Any]:
    date_values = query.get("date", [])
    symbol_values = query.get("symbols", [])
    if not date_values:
        raise ApiError("缺少 date 参数")
    if not symbol_values:
        raise ApiError("请至少选择一只股票")

    target_date = parse_date(date_values[0])
    raw_symbols = ",".join(symbol_values)
    symbols = []
    for raw_symbol in raw_symbols.split(","):
        if raw_symbol.strip():
            symbol = normalize_symbol(raw_symbol)
            if symbol not in symbols:
                symbols.append(symbol)

    if not symbols:
        raise ApiError("请至少选择一只股票")
    if len(symbols) > 8:
        raise ApiError("一次最多对比 8 只股票")

    series = []
    errors = []
    for symbol in symbols:
        try:
            meta, rows = minute_rows_for_day(symbol, target_date)
            if rows:
                series.append({**meta, "points": rows})
            else:
                errors.append(f"{symbol} 在 {target_date.isoformat()} 没有 1 分钟数据")
        except ApiError as exc:
            errors.append(exc.message)

    if not series and errors:
        raise ApiError("；".join(errors), HTTPStatus.NOT_FOUND)

    return {
        "date": target_date.isoformat(),
        "series": series,
        "errors": errors,
        "source": "东方财富 1 分钟 K 线",
        "notice": "东方财富分钟数据通常只覆盖近期交易日；较早日期或停牌日可能没有结果。",
    }


class StockReviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/stocks":
            self.send_json({"stocks": POPULAR_STOCKS})
            return
        if parsed.path == "/api/minutes":
            try:
                payload = minutes_response(urllib.parse.parse_qs(parsed.query))
                self.send_json(payload)
            except ApiError as exc:
                self.send_json({"error": exc.message}, exc.status)
            except Exception as exc:
                self.send_json({"error": f"服务内部错误：{exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    if not STATIC_DIR.exists():
        raise SystemExit(f"静态目录不存在：{STATIC_DIR}")
    server = ThreadingHTTPServer((HOST, PORT), StockReviewHandler)
    print(f"复盘软件已启动：http://{HOST}:{PORT}")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
