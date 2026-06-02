import datetime as dt
import hashlib
import html
import json
import os
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"
LEADER_LEDGER_PATH = ROOT / "static" / "cycle_leaders.json"
DEFAULT_SKILL_DIR = Path.home() / "plugins" / "stock-cycle-review" / "skills" / "stock-cycle-review"
SKILL_DIR = Path(os.environ.get("STOCK_CYCLE_REVIEW_SKILL_DIR", DEFAULT_SKILL_DIR))
START = dt.date(2026, 3, 17)
END = dt.date(2026, 6, 1)
CATEGORY_URL = "https://wudaolu.com/c/aguhot/8.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}


CSS = """
:root{--bg:#f6f7f9;--panel:#fff;--text:#1f2937;--muted:#6b7280;--line:#d9dee7;--strong:#13795b;--warn:#b26a00;--danger:#b42318;--info:#1d4ed8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.55}.page{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 0 42px}header{display:grid;gap:10px;margin-bottom:16px}h1{margin:0;font-size:clamp(24px,4vw,36px);letter-spacing:0}h2{margin:0 0 12px;font-size:18px;letter-spacing:0}p{margin:0}.note{color:var(--muted);font-size:14px}.risk{border-left:4px solid var(--warn);background:#fff8ec;padding:10px 12px;color:#7a4b00}.grid{display:grid;gap:12px}.status-grid{grid-template-columns:repeat(6,minmax(0,1fr));margin:16px 0}.metric,section{background:var(--panel);border:1px solid var(--line);border-radius:8px}.metric{min-height:96px;padding:12px}.metric .label{color:var(--muted);font-size:12px;margin-bottom:6px}.metric .value{font-size:17px;font-weight:700}section{padding:16px;margin-bottom:14px}.timeline,.plan{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.plan{grid-template-columns:repeat(3,1fr)}.step,.plan-block{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fbfcfe}.title,.plan-block strong{display:block;font-weight:700;margin-bottom:6px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:10px 8px;text-align:left;vertical-align:top}th{color:var(--muted);font-weight:600;background:#f9fafb}.badge{display:inline-flex;align-items:center;min-height:24px;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}.buy{background:#e8f5ef;color:var(--strong)}.observe{background:#fff4db;color:var(--warn)}.reject{background:#fdebea;color:var(--danger)}.context{background:#eaf1ff;color:var(--info)}ul,ol{margin:0;padding-left:20px}a{color:var(--info)}@media(max-width:860px){.status-grid,.timeline,.plan{grid-template-columns:1fr}.table-wrap{overflow-x:auto}table{min-width:760px}}
""".strip()

AUTO_CONFIRM_STANDARD_BUY = False
AUTO_UPDATE_PRIOR_LEADER = False
FETCH_RETRIES = 4
HARD_VETO_TERMS = (
    "一字或准一字交易性不足",
    "不是排除一字后的可交易最高板",
    "尾盘回封",
    "换手超过40%",
    "换手偏低，分歧不足",
    "炸板次数过多",
    "同板块一字高标仍在，低位只能算助攻",
    "与上一轮龙头同板块",
)

SKILL_REQUIRED_MARKERS = (
    "当前市场阶段",
    "亏钱效应",
    "新方向",
    "操作仓位",
    "风控",
    "4/5板",
)


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def load_skill_contract():
    files = {
        "SKILL.md": SKILL_DIR / "SKILL.md",
        "daily-review-template.md": SKILL_DIR / "references" / "daily-review-template.md",
        "html-report-template.md": SKILL_DIR / "references" / "html-report-template.md",
    }
    missing = [str(path) for path in files.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("缺少 stock-cycle-review skill 文件：" + "；".join(missing))

    combined = "\n".join(path.read_text(encoding="utf-8") for path in files.values())
    missing_markers = [marker for marker in SKILL_REQUIRED_MARKERS if marker not in combined]
    if missing_markers:
        raise ValueError("stock-cycle-review skill 缺少必要流程标记：" + "、".join(missing_markers))

    return {
        "name": "stock-cycle-review",
        "skill_dir": str(SKILL_DIR),
        "workflow": "阶段 -> 旧龙 -> 亏钱效应 -> 新方向 -> 梯队 -> 买点 -> 操作 -> 风控",
        "files": {name: {"path": str(path), "sha256": file_sha256(path)} for name, path in files.items()},
    }


def fetch_json(url):
    errors = []
    use_system_proxy = os.environ.get("USE_SYSTEM_PROXY") == "1"
    proxy_modes = (use_system_proxy, False) if use_system_proxy else (False, True)
    for trust_env in proxy_modes:
        session = requests.Session()
        session.trust_env = trust_env
        for attempt in range(FETCH_RETRIES):
            try:
                response = session.get(url, headers=HEADERS, timeout=25)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                errors.append(f"trust_env={trust_env} attempt={attempt + 1}: {exc}")
                time.sleep(1 + attempt)
    raise RuntimeError(f"无法获取数据：{url}\n" + "\n".join(errors[-6:]))


def esc(value):
    return html.escape(str(value or ""), quote=True)


def stock_parts(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    match = re.match(r"(\d{6})\s+(.+)", text)
    if match:
        return match.group(1), match.group(2).strip()
    return "", text


def is_main_board(code):
    return bool(re.match(r"^(00|001|002|003|60)\d{4}$", code or ""))


def to_float(text):
    if text is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(text).replace(",", ""))
    return float(match.group(0)) if match else None


def parse_date(value):
    if not value:
        return None
    return dt.date.fromisoformat(str(value))


def load_leader_ledger():
    if not LEADER_LEDGER_PATH.exists():
        return []
    rows = json.loads(LEADER_LEDGER_PATH.read_text(encoding="utf-8"))
    ledger = []
    for row in rows:
        item = dict(row)
        item["effective_date_value"] = parse_date(item.get("effective_date"))
        item["valid_until_value"] = parse_date(item.get("valid_until"))
        if item["effective_date_value"]:
            ledger.append(item)
    return sorted(ledger, key=lambda x: x["effective_date_value"])


def leader_state_for_date(review_date, ledger):
    candidates = []
    for item in ledger:
        effective = item["effective_date_value"]
        valid_until = item.get("valid_until_value")
        if effective <= review_date and (valid_until is None or review_date <= valid_until):
            candidates.append(item)
    if not candidates:
        return {
            "prior_leader": "未确认",
            "prior_code": "",
            "prior_theme": "未确认",
            "prior_leader_confirmed": False,
            "prior_leader_source": "人工龙头台账未覆盖本日",
            "prior_leader_note": "不能据此确认新旧周期，候选只能观察。",
        }
    item = candidates[-1]
    return {
        "prior_leader": item.get("leader") or "未确认",
        "prior_code": item.get("code") or "",
        "prior_theme": item.get("theme") or "未确认",
        "prior_leader_confirmed": item.get("confidence") == "confirmed",
        "prior_leader_source": item.get("source") or "人工龙头台账",
        "prior_leader_note": item.get("note") or "",
    }


def time_minutes(text):
    match = re.match(r"(\d{2}):(\d{2})", str(text or ""))
    if not match:
        return None
    return int(match.group(1)) * 60 + int(match.group(2))


def table_rows(table):
    rows = []
    trs = table.find_all("tr")
    if not trs:
        return rows
    headers = [c.get_text(" ", strip=True) for c in trs[0].find_all(["th", "td"])]
    for tr in trs[1:]:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if not cells:
            continue
        row = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
        if "股票" in row:
            row["代码"], row["名称"] = stock_parts(row["股票"])
        rows.append(row)
    return rows


def fetch_topics():
    items = {}
    for page in range(0, 80):
        url = CATEGORY_URL if page == 0 else f"{CATEGORY_URL}?page={page}"
        data = fetch_json(url)
        for topic in data.get("topic_list", {}).get("topics", []):
            title = topic.get("title", "")
            if "昨日" in title:
                continue
            match = re.search(r"2026/(\d{1,2})/(\d{1,2})", title)
            if not match:
                continue
            date = dt.date(2026, int(match.group(1)), int(match.group(2)))
            if START <= date <= END:
                items[date] = {"id": topic["id"], "title": title, "created_at": topic.get("created_at", "")}
        if not data.get("topic_list", {}).get("more_topics_url"):
            break
    return [items[d] | {"date": d} for d in sorted(items)]


def parse_topic(topic):
    url = f"https://wudaolu.com/t/topic/{topic['id']}"
    data = fetch_json(f"{url}.json")
    soup = BeautifulSoup(data["post_stream"]["posts"][0]["cooked"], "html.parser")
    text = soup.get_text("\n", strip=True)
    update_match = re.search(r"数据更新时间:\s*([0-9/:\s]+)", text)
    update_time = update_match.group(1).strip() if update_match else f"{topic['date']} 15:05"

    details = {}
    all_rows = []
    theme_groups = []

    for table in soup.find_all("table"):
        previous = table.find_previous(["h4", "h3"])
        section = previous.get_text(" ", strip=True) if previous else ""
        rows = table_rows(table)
        if rows:
            all_rows.extend(rows)
        if section and "只)" in section:
            theme = re.sub(r"\s*\(\d+只\).*", "", section).strip()
            group = {"name": theme, "raw": section, "rows": rows}
            theme_groups.append(group)
            for row in rows:
                key = row.get("代码") or row.get("名称")
                if key:
                    details.setdefault(key, {}).setdefault("themes", [])
                    if theme not in details[key]["themes"]:
                        details[key]["themes"].append(theme)

        for row in rows:
            key = row.get("代码") or row.get("名称")
            if not key:
                continue
            merged = details.setdefault(key, {})
            merged.update({k: v for k, v in row.items() if v not in ("", None)})
            merged.setdefault("themes", [])

    ladder = []
    ladder_heading = next((h for h in soup.find_all("h3") if h.get_text(strip=True) == "连板梯队"), None)
    if ladder_heading:
        for sib in ladder_heading.next_siblings:
            if getattr(sib, "name", None) == "h3":
                break
            if getattr(sib, "name", None) != "ul":
                continue
            for li in sib.find_all("li", recursive=False):
                item_text = li.get_text(" ", strip=True)
                match = re.match(r"(\d+)连板\s*\((\d+)只\)\s*:\s*(.+)", item_text)
                if not match:
                    continue
                board = int(match.group(1))
                for chunk in re.split(r"[，,]", match.group(3)):
                    code, name = stock_parts(chunk.strip())
                    if not code and not name:
                        continue
                    detail = details.get(code, {}).copy()
                    detail.setdefault("代码", code)
                    detail.setdefault("名称", name)
                    detail.setdefault("股票", f"{code} {name}".strip())
                    detail["board"] = board
                    detail["main_board"] = is_main_board(code)
                    ladder.append(detail)

    for row in all_rows:
        if "连板" in row:
            row["board"] = int(to_float(row.get("连板")) or 0)
        elif "连板数" in row:
            row["board"] = int(to_float(row.get("连板数")) or 0)

    return {
        "date": topic["date"],
        "topic_id": topic["id"],
        "title": data.get("title", topic["title"]),
        "url": url,
        "created_at": data.get("created_at", topic.get("created_at", "")),
        "update_time": update_time,
        "ladder": ladder,
        "theme_groups": theme_groups,
        "details": details,
    }


def first_time(row):
    return row.get("首次封板") or ""


def last_time(row):
    return row.get("最后封板") or row.get("首次封板") or ""


def broken_count(row):
    value = to_float(row.get("炸板"))
    return int(value) if value is not None else 0


def turnover(row):
    return to_float(row.get("换手率"))


def is_one_word(row):
    first = time_minutes(first_time(row))
    last = time_minutes(last_time(row))
    broken = broken_count(row)
    turn = turnover(row)
    if first is None:
        return False
    if first <= 565 and (last is None or last <= 566) and broken == 0:
        return True
    if first <= 570 and (last is None or last <= 570) and broken == 0 and (turn is None or turn <= 5):
        return True
    return False


def is_near_one_word(row):
    first = time_minutes(first_time(row))
    last = time_minutes(last_time(row))
    if first is None:
        return False
    return first <= 570 and (last is None or last <= 585) and broken_count(row) <= 1 and (turnover(row) or 0) <= 8


def stock_label(row):
    return f"{row.get('名称', '')}".strip() or row.get("股票", "")


def stock_full(row):
    code = row.get("代码", "")
    name = stock_label(row)
    return f"{code} {name}".strip()


def board_rows(ladder, board):
    return [row for row in ladder if row.get("board") == board]


def theme_label(row):
    themes = row.get("themes") or []
    if themes:
        return "、".join(themes[:2])
    return row.get("所属行业") or "未归类"


def overlap_theme(row, prior_theme):
    text = f"{theme_label(row)} {row.get('所属行业','')}"
    for token in re.split(r"[ /、,，]+", prior_theme or ""):
        if token and len(token) >= 2 and token in text:
            return True
    return False


def extract_board_number(text):
    numbers = [int(x) for x in re.findall(r"(\d+)板", str(text or ""))]
    return max(numbers) if numbers else None


def latest_previous_report(previous_reports):
    return previous_reports[-1] if previous_reports else {}


def previous_max_board(previous_reports):
    prev = latest_previous_report(previous_reports)
    sentiment = prev.get("high_level_sentiment") or {}
    return extract_board_number(sentiment.get("nominal_highest_board")) or extract_board_number(prev.get("current_core"))


def classify_market_phase(cycle, old_confirmed, old_live, standard, tradable_high_rows, max_board, previous_high):
    if not old_confirmed:
        return "试错期"
    if standard:
        return "新周期初期"
    if old_live and old_live.get("board", 0) >= 5:
        if broken_count(old_live) >= 3 or (turnover(old_live) or 0) >= 30:
            return "分歧期"
        return "主升期"
    if previous_high and previous_high - max_board >= 2:
        return "退潮期"
    if tradable_high_rows:
        return "分歧期"
    return "试错期"


def operation_for_phase(phase):
    mapping = {
        "主升期": {
            "position": "正常仓",
            "action": "只看龙头和核心补涨，普通后排不做。",
            "candidate": "持仓以强弱和板块助攻为准，新开仓只接受计划内核心。",
        },
        "分歧期": {
            "position": "降低仓位",
            "action": "高位震荡期减少出手，不做普通后排，优先观察分歧后的修复质量。",
            "candidate": "只有计划内4/5板分歧回封才可继续核验。",
        },
        "退潮期": {
            "position": "空仓",
            "action": "高标负反馈扩散时不试错，先等亏钱效应收敛。",
            "candidate": "不做新开仓，最多记录下一批题材强度。",
        },
        "试错期": {
            "position": "极小仓或空仓",
            "action": "只观察最强辨识度，低位和后排不替代龙头买点。",
            "candidate": "候选只能进观察池，不能因为高度或题材热度直接买。",
        },
        "新周期初期": {
            "position": "小中仓",
            "action": "只做新方向胜出后的核心确认，买点必须是计划内打板。",
            "candidate": "标准4/5板分歧回封可执行，次日看弱转强和板块助攻。",
        },
    }
    return mapping.get(phase, mapping["试错期"])


def risk_control_for_phase(phase):
    common = [
        ["单笔最大亏损", "计划内打板失败或次日不及预期，优先执行退出；单笔亏损不扩大。"],
        ["当日最大亏损", "当日触发账户回撤上限后停止开仓，只复盘不加戏。"],
        ["连续试错次数", "连续两次试错失败后暂停，等新方向重新给出4/5板确认。"],
        ["卖出条件", "不能弱转强、板块助攻断层、高位爆量失控、跌停负反馈，按卖点处理。"],
    ]
    phase_limit = {
        "主升期": "仓位上限：正常仓，但高潮后段不盲目加仓。",
        "分歧期": "仓位上限：降低到半仓以下，普通后排不做。",
        "退潮期": "仓位上限：空仓，禁止用低位杂毛试错。",
        "试错期": "仓位上限：极小仓或空仓，只允许最高辨识度试错。",
        "新周期初期": "仓位上限：小中仓，确认后再考虑加到正常仓。",
    }
    return [["仓位上限", phase_limit.get(phase, phase_limit["试错期"])]] + common


def stock_names(rows):
    return "、".join(stock_label(row) for row in rows if stock_label(row))


def loss_effect_analysis(ladder, previous_reports, candidates, max_board):
    prev = latest_previous_report(previous_reports)
    previous_high = previous_max_board(previous_reports)
    current_names = {stock_label(row) for row in ladder}
    prev_core = prev.get("current_core", "")
    prev_core_names = [name for name in re.findall(r"([\u4e00-\u9fa5A-Za-zＡ-Ｚａ-ｚ]+)\d+板", prev_core) if name]
    missing_prev = [name for name in prev_core_names if name not in current_names]
    resealed_high = [row for row in ladder if row.get("board", 0) >= 4 and broken_count(row) > 0]
    rejected_complements = [item["row"] for item in candidates if item["role"] == "旧周期二阶段/补涨" and item["verdict"] == "放弃"]

    if previous_high is None:
        height_text = "缺少前一日高度锚点，不能判断高度升降。"
    elif max_board > previous_high:
        height_text = f"连板高度从{previous_high}板升至{max_board}板，情绪有修复或延伸。"
    elif max_board < previous_high:
        height_text = f"连板高度从{previous_high}板降至{max_board}板，注意退潮或分歧扩散。"
    else:
        height_text = f"连板高度维持{max_board}板，高位仍在博弈。"

    rows = [
        ["高标是否继续A杀", "需结合分时/跌停榜核验" if missing_prev else "昨日核心仍可在当前梯队或缺少前序核心", "、".join(missing_prev) if missing_prev else "无明确失踪高标"],
        ["断板票是否继续跌停", "当前源未完整披露断板跌停明细", "若昨日核心断板后跌停，按退潮加重处理"],
        ["昨日炸板票是否修复", "当前源未完整披露昨日炸板修复", "只能用当日回封和板块修复做辅助判断"],
        ["连板高度是否下降", height_text, "高度下降两档以上时，仓位直接降级"],
        ["补涨是否开始坑人", "旧周期补涨风险偏高" if rejected_complements else "未发现被模型硬否决的旧周期补涨候选", stock_names(rejected_complements) or "无"],
    ]

    if missing_prev or (previous_high and previous_high - max_board >= 2):
        level = "偏高"
    elif resealed_high or rejected_complements:
        level = "中等"
    else:
        level = "可控"
    summary = f"亏钱效应：{level}。{height_text}"
    return {"level": level, "summary": summary, "rows": rows}


def new_direction_analysis(theme_groups, old_theme, candidates):
    independent = []
    old_related = []
    for group in theme_groups:
        related = any(group["name"] in old_theme or token in group["name"] for token in re.split(r"[ /、]+", old_theme) if len(token) >= 2)
        if related:
            old_related.append(group)
        else:
            independent.append(group)
    strong_independent = [group for group in independent if len(group["rows"]) >= 7]
    standard_candidates = [item for item in candidates if item["verdict"] == "标准买点"]
    if standard_candidates:
        summary = "新方向已进入买点核验区"
    elif strong_independent:
        summary = "有独立强分支，但仍需4/5板买点确认"
    elif old_related and not independent:
        summary = "资金仍偏旧方向延续或补涨"
    else:
        summary = "新方向不清晰，继续试错观察"
    return {
        "summary": summary,
        "strong_independent": "、".join(group["name"] for group in strong_independent) or "无",
        "old_related": "、".join(group["name"] for group in old_related) or "无",
    }


def classify_day(parsed, state, previous_reports):
    ladder = parsed["ladder"]
    max_board = max([r["board"] for r in ladder], default=0)
    nominal = board_rows(ladder, max_board)
    main_ladder = [r for r in ladder if r.get("main_board")]
    eligible_45 = [r for r in main_ladder if r["board"] in (4, 5)]
    tradable_45 = [r for r in eligible_45 if not is_one_word(r) and not is_near_one_word(r)]
    tradable_high = max([r["board"] for r in tradable_45], default=0)
    tradable_high_rows = [r for r in tradable_45 if r["board"] == tradable_high]

    theme_groups = sorted(parsed["theme_groups"], key=lambda g: len(g["rows"]), reverse=True)[:5]
    main_theme_names = [g["name"] for g in theme_groups[:3]]

    old_leader = state.get("prior_leader") or "未确认"
    old_theme = state.get("prior_theme") or "未确认"
    old_confirmed = bool(state.get("prior_leader_confirmed"))
    old_source = state.get("prior_leader_source") or "未登记"
    old_note = state.get("prior_leader_note") or ""
    old_live = None
    if old_confirmed:
        old_live = next((r for r in ladder if stock_label(r) == old_leader or r.get("代码") == state.get("prior_code")), None)
    old_status = "上一轮龙头未人工确认，周期判断降级为观察"
    if old_confirmed:
        old_status = f"{old_leader}未在涨停池，按旧龙未继续连板处理"
    if old_live:
        old_status = f"{old_leader}{old_live['board']}板仍在涨停池，旧周期未完全结束"

    one_word_high = [r for r in eligible_45 if is_one_word(r) or is_near_one_word(r)]
    live_one_word_theme = one_word_high[0] if one_word_high else None

    candidates = []
    standard = []
    for row in eligible_45:
        positives = []
        negatives = []
        role = "试错高标"
        if overlap_theme(row, old_theme):
            role = "旧周期二阶段/补涨"
            negatives.append("与上一轮龙头同板块")
        if is_one_word(row) or is_near_one_word(row):
            negatives.append("一字或准一字交易性不足")
        else:
            positives.append("非一字，具备盘中交易性")
        if row["board"] == tradable_high and row in tradable_high_rows:
            positives.append("排除一字后的可交易最高板")
        else:
            negatives.append("不是排除一字后的可交易最高板")
        first = time_minutes(first_time(row))
        last = time_minutes(last_time(row))
        if first is not None and first <= 630:
            positives.append("10:30前首次封板")
        if last is not None and last > 870:
            negatives.append("尾盘回封")
        turn = turnover(row)
        if turn is not None:
            if 15 <= turn <= 30:
                positives.append("换手在15%-30%区间")
            elif turn > 40:
                negatives.append("换手超过40%")
            elif turn < 8:
                negatives.append("换手偏低，分歧不足")
        if broken_count(row) >= 8:
            negatives.append("炸板次数过多")
        if theme_label(row) in main_theme_names or row.get("所属行业") in main_theme_names:
            positives.append("属于当日强板块")

        same_theme_blocked = bool(live_one_word_theme and row is not live_one_word_theme and theme_label(row) == theme_label(live_one_word_theme))
        if same_theme_blocked:
            negatives.append("同板块一字高标仍在，低位只能算助攻")

        if not old_confirmed:
            negatives.append("上一轮龙头未确认，不能判定新周期窗口")
        if old_live and old_live.get("board", 0) >= 5:
            negatives.append("旧周期高标仍在，不能认定新周期")
        if not AUTO_CONFIRM_STANDARD_BUY:
            negatives.append("自动批量复盘不确认标准买点，需人工核验旧龙负反馈和板块独立性")

        verdict = "仅观察"
        hard_veto = any(term in negatives for term in HARD_VETO_TERMS)
        if hard_veto or same_theme_blocked or row["board"] != tradable_high:
            verdict = "放弃"
        elif (
            AUTO_CONFIRM_STANDARD_BUY
            and len(positives) >= 4
            and not negatives
            and not overlap_theme(row, old_theme)
            and not (old_live and old_live.get("board", 0) >= 5)
        ):
            verdict = "标准买点"
            standard.append(row)
        candidates.append({"row": row, "role": role, "positives": positives, "negatives": negatives, "verdict": verdict})

    if not candidates:
        candidate_empty = "当日无符合4/5板候选，低位票只做盘面跟踪"
    else:
        candidate_empty = ""

    if standard:
        cycle = "旧龙负反馈后的新题材4/5板买点窗口"
        next_opportunity = "已有标准候选；次日只按弱转强和板块助攻执行"
    elif tradable_high_rows:
        cycle = "高位分歧试错期"
        next_opportunity = "暂无标准买点；可交易4/5板仍需继续观察"
    else:
        cycle = "混沌试错期"
        next_opportunity = "暂无标准买点；空仓或只观察"

    if old_live and old_live.get("board", 0) >= 5:
        cycle = "旧周期延续或高位分歧期"
    if not old_confirmed:
        cycle = "旧龙锚点未确认的混沌试错期"
        next_opportunity = "无标准买点；先补齐上一轮龙头和负反馈确认"

    current_core = "、".join(stock_label(r) + f"{r['board']}板" for r in nominal[:3]) if nominal else "无连板高度"
    tradable_high_text = "、".join(stock_label(r) + f"{r['board']}板" for r in tradable_high_rows[:3]) if tradable_high_rows else "无标准可交易4/5板买点"
    leader_watch_rows = [
        r for r in sorted(main_ladder, key=lambda x: x["board"], reverse=True)
        if r["board"] >= 6 and not is_one_word(r) and not is_near_one_word(r)
    ]
    leader_watch = "、".join(stock_label(r) + f"{r['board']}板" for r in leader_watch_rows[:3]) if leader_watch_rows else "无"
    previous_high = previous_max_board(previous_reports)
    market_phase = classify_market_phase(cycle, old_confirmed, old_live, standard, tradable_high_rows, max_board, previous_high)
    if not old_confirmed:
        old_leader_state = "未确认"
    elif old_live and old_live.get("board", 0) >= 5 and market_phase == "主升期":
        old_leader_state = "强势主升"
    elif old_live:
        old_leader_state = "高位震荡"
    elif market_phase == "退潮期":
        old_leader_state = "明显退潮"
    else:
        old_leader_state = "已经死亡或离开涨停主线，等待新方向"
    loss_effect = loss_effect_analysis(ladder, previous_reports, candidates, max_board)
    new_direction = new_direction_analysis(theme_groups, old_theme, candidates)
    operation = operation_for_phase(market_phase)
    risk_control = risk_control_for_phase(market_phase)

    # Update state only after the report is classified, so the current report never benefits from future data.
    next_state = dict(state)
    confirm = None
    if AUTO_UPDATE_PRIOR_LEADER:
        confirm = next((r for r in sorted(main_ladder, key=lambda x: x["board"], reverse=True) if r["board"] >= 6 and not is_one_word(r)), None)
    if confirm:
        next_state["prior_leader"] = stock_label(confirm)
        next_state["prior_code"] = confirm.get("代码")
        next_state["prior_theme"] = theme_label(confirm)

    return {
        "cycle": cycle,
        "old_status": old_status,
        "nominal": nominal,
        "max_board": max_board,
        "current_core": current_core,
        "tradable_high": tradable_high_text,
        "eligible_45": eligible_45,
        "candidates": candidates,
        "candidate_empty": candidate_empty,
        "standard": standard,
        "theme_groups": theme_groups,
        "market_phase": market_phase,
        "old_leader_state": old_leader_state,
        "loss_effect": loss_effect,
        "new_direction": new_direction,
        "operation": operation,
        "risk_control": risk_control,
        "next_opportunity": next_opportunity,
        "hard_no_trade": "退潮期空仓；不顶一字；不买2/3板；不追6板首次开口；不买同板块后排替代",
        "old_leader": old_leader,
        "old_theme": old_theme,
        "old_confirmed": old_confirmed,
        "old_source": old_source,
        "old_note": old_note,
        "leader_watch": leader_watch,
        "next_state": next_state,
        "previous_reports": previous_reports,
    }


def badge(text, cls):
    return f'<span class="badge {cls}">{esc(text)}</span>'


def render_table(headers, rows):
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return '<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in headers) + "</tr></thead><tbody>" + "".join(body) + "</tbody></table></div>"


def render_report(parsed, analysis, previous_reports, next_date, skill_contract):
    date = parsed["date"]
    title = f"A股短线周期复盘 - {date.isoformat()}"
    top_boards = []
    for board in sorted({r["board"] for r in parsed["ladder"]}, reverse=True)[:5]:
        names = "、".join(stock_label(r) for r in board_rows(parsed["ladder"], board)[:8])
        top_boards.append([f"{board}板", esc(names), esc("、".join(sorted({theme_label(r) for r in board_rows(parsed["ladder"], board)})[:3])), "盘面跟踪", "按模型筛选", badge("观察", "observe")])

    theme_rows = []
    for group in analysis["theme_groups"]:
        rows = group["rows"]
        high = sorted(rows, key=lambda r: int(to_float(r.get("连板数") or r.get("连板") or 0) or 0), reverse=True)[:3]
        high_text = "、".join((r.get("名称") or r.get("股票", "")) + (f"{int(to_float(r.get('连板数') or r.get('连板') or 0) or 0)}板" if int(to_float(r.get("连板数") or r.get("连板") or 0) or 0) > 1 else "") for r in high)
        relation = "与旧周期相关" if any(group["name"] in analysis["old_theme"] or token in group["name"] for token in re.split(r"[ /、]+", analysis["old_theme"]) if len(token) >= 2) else "独立或背景分支"
        cls = "buy" if len(rows) >= 7 else "context" if len(rows) >= 4 else "observe"
        theme_rows.append([esc(group["name"]), esc(high_text or "无明确高标"), esc(f"{len(rows)}只涨停/封板"), esc("看容量表与成交额排序"), esc(relation), badge("强" if len(rows) >= 7 else "中等", cls)])

    candidate_rows = []
    if analysis["candidate_empty"]:
        candidate_rows.append([esc(analysis["candidate_empty"]), "-", "无买点", "无", "未到4/5板或交易性不足", badge("仅观察", "observe")])
    else:
        for item in analysis["candidates"]:
            row = item["row"]
            cls = "buy" if item["verdict"] == "标准买点" else "reject" if item["verdict"] == "放弃" else "observe"
            candidate_rows.append([
                esc(stock_full(row)),
                esc(row["board"]),
                esc(f"{first_time(row)}首次封板，{last_time(row)}最后封板，换手{row.get('换手率','未知')}"),
                esc("；".join(item["positives"]) or "无"),
                esc("；".join(item["negatives"]) or "无"),
                badge(item["verdict"], cls),
            ])

    prev_rows = []
    for prev in previous_reports[-5:]:
        prev_rows.append([
            esc(prev.get("review_date")),
            esc(prev.get("cycle_stage")),
            esc(prev.get("current_core")),
            esc(prev.get("next_opportunity")),
            esc("按今日数据滚动跟踪，不使用后续日期结论"),
        ])
    if not prev_rows:
        prev_rows.append(["无更早归档", "无", "无", "无", "从本日开始滚动"])

    if analysis["old_confirmed"]:
        old_watch = f"旧龙：{analysis['old_leader']} / {analysis['old_theme']}。{analysis['old_status']}。若继续不在涨停池或出现高位负反馈，说明旧周期压制仍在；若重新涨停，说明旧周期仍有修复。"
    else:
        old_watch = f"旧龙：未确认。原因：{analysis['old_source']}。先补齐上一轮龙头、所属题材和负反馈证据；未补齐前不确认新周期买点。"
    if analysis["standard"]:
        candidate_plan = "候选买点：" + "、".join(stock_label(r) for r in analysis["standard"]) + "。买点方式：只按计划内打板确认；不能半路、低吸或顶一字。"
    else:
        candidate_plan = f"候选买点：无。处理：{analysis['operation']['position']}，只登记候选池；低位2/3板和同板块后排不替代标准4/5板。"
    risk_names = "、".join(stock_label(r) for r in analysis["nominal"][:3]) or "当日高标"
    risk_plan = f"风险票：{risk_names}。风险原因：一字、尾盘回封、爆量、旧周期补涨或无板块助攻。处理：不买或只观察负反馈。"
    operation_rows = [[
        esc(analysis["market_phase"]),
        esc(analysis["operation"]["position"]),
        esc(analysis["operation"]["action"]),
        esc(analysis["operation"]["candidate"]),
    ]]
    risk_control_rows = [[esc(name), esc(rule)] for name, rule in analysis["risk_control"]]
    loss_rows = [[esc(a), esc(b), esc(c)] for a, b, c in analysis["loss_effect"]["rows"]]
    new_direction_rows = [[
        esc(analysis["new_direction"]["summary"]),
        esc(analysis["new_direction"]["strong_independent"]),
        esc(analysis["new_direction"]["old_related"]),
        esc("有标准候选" if analysis["standard"] else "未确认标准买点"),
    ]]

    final_lines = [
        f"当前市场阶段：{analysis['market_phase']}；周期描述：{analysis['cycle']}。",
        f"当前核心：上一轮龙头是{analysis['old_leader']} / {analysis['old_theme']}；待确认高标为{analysis['leader_watch']}；当日核心为{analysis['current_core']}。",
        f"亏钱效应：{analysis['loss_effect']['level']}；操作仓位：{analysis['operation']['position']}。",
        f"下一次标准买点：{analysis['next_opportunity']}。",
        f"硬性禁买：{analysis['hard_no_trade']}。",
    ]

    metadata = {
        "review_date": date.isoformat(),
        "data_cutoff": date.isoformat(),
        "next_trading_day": next_date.isoformat() if next_date else "",
        "generated_by_skill": skill_contract,
        "cycle_stage": analysis["cycle"],
        "market_phase": analysis["market_phase"],
        "old_leader_state": analysis["old_leader_state"],
        "loss_effect": analysis["loss_effect"],
        "new_direction": analysis["new_direction"],
        "operation_plan": analysis["operation"],
        "risk_control": analysis["risk_control"],
        "high_level_sentiment": {
            "nominal_highest_board": f"{analysis['max_board']}板：" + "、".join(stock_label(r) for r in analysis["nominal"][:5]),
            "tradable_highest_board": analysis["tradable_high"],
            "previous_high_board_performance": analysis["old_status"],
            "broken_board_feedback": "以当日涨停复盘和前序归档滚动判断",
            "high_level_limit_down_count": "未使用未来跌停数据",
            "high_level_broken_board_count": "见当日炸板字段",
            "promotion_rate": "见当日连板梯队",
        },
        "prior_confirmed_leader": analysis["old_leader"],
        "prior_leader_theme": analysis["old_theme"],
        "prior_leader_confirmed": analysis["old_confirmed"],
        "prior_leader_source": analysis["old_source"],
        "prior_leader_note": analysis["old_note"],
        "leader_watch": analysis["leader_watch"],
        "intermediate_trial_chain": "、".join(stock_label(r) + f"{r['board']}板" for r in parsed["ladder"] if 3 <= r["board"] <= 5)[:200],
        "old_leader_chain": f"{analysis['old_leader']} / {analysis['old_theme']}",
        "current_core": analysis["current_core"],
        "tradable_high_board": analysis["tradable_high"],
        "next_opportunity": analysis["next_opportunity"],
        "hard_no_trade": analysis["hard_no_trade"],
        "model_verdicts": [
            {
                "stock": stock_label(item["row"]),
                "role": item["role"],
                "verdict": "standard buy" if item["verdict"] == "标准买点" else "reject" if item["verdict"] == "放弃" else "observe only",
                "reason": "；".join(item["negatives"] or item["positives"]),
            }
            for item in analysis["candidates"]
        ],
        "sources": [{"name": parsed["title"], "url": parsed["url"]}],
    }

    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <main class="page">
    <header>
      <h1>{esc(title)}</h1>
      <p class="note">次日计划对应：{esc(metadata["next_trading_day"] or "下一交易日待确认")}。复盘口径：历史实盘模拟，只使用 {esc(date.isoformat())} 当天及之前数据。主数据源发布时间：{esc(parsed["created_at"])}；数据更新时间：{esc(parsed["update_time"])}。</p>
      <p class="note">生成依据：{esc(skill_contract["name"])} skill；流程：{esc(skill_contract["workflow"])}。</p>
      <p class="risk">这是复盘框架，不构成投资建议或荐股。输出顺序由 skill 固定为：阶段 -> 旧龙 -> 亏钱效应 -> 新方向 -> 梯队 -> 买点 -> 操作 -> 风控。</p>
    </header>
    <section class="grid status-grid" aria-label="核心状态">
      <div class="metric"><div class="label">市场阶段</div><div class="value">{esc(analysis["market_phase"])}</div></div>
      <div class="metric"><div class="label">上一轮龙头/板块</div><div class="value">{esc(analysis["old_leader"])} / {esc(analysis["old_theme"])}</div></div>
      <div class="metric"><div class="label">旧龙状态</div><div class="value">{esc(analysis["old_leader_state"])}</div></div>
      <div class="metric"><div class="label">亏钱效应</div><div class="value">{esc(analysis["loss_effect"]["level"])}</div></div>
      <div class="metric"><div class="label">新方向</div><div class="value">{esc(analysis["new_direction"]["summary"])}</div></div>
      <div class="metric"><div class="label">操作仓位</div><div class="value">{esc(analysis["operation"]["position"])}</div></div>
    </section>
    <section>
      <h2>高位情绪快照</h2>
      {render_table(["最高板","可交易最高板","昨日高标表现","断板反馈","跌停高标","炸板高标","连板晋级率"], [[esc(metadata["high_level_sentiment"]["nominal_highest_board"]), esc(metadata["high_level_sentiment"]["tradable_highest_board"]), esc(analysis["old_status"]), "按当日梯队和前序归档判断", "不使用未来跌停数据", "见个股炸板字段", "见连板梯队"]])}
    </section>
    <section>
      <h2>亏钱效应</h2>
      {render_table(["检查项","当前判断","处理要点"], loss_rows)}
    </section>
    <section>
      <h2>周期链路</h2>
      <div class="timeline">
        <div class="step"><div class="title">上一龙头</div><p>{esc(analysis["old_leader"])} / {esc(analysis["old_theme"])}。{esc(analysis["old_status"])}。来源：{esc(analysis["old_source"])}。</p></div>
        <div class="step"><div class="title">题材判断</div><p>{esc("、".join(main_theme_names := [g["name"] for g in analysis["theme_groups"][:3]]) or "无明确主线")} 是当日主要涨停方向，先看是否独立于旧周期。</p></div>
        <div class="step"><div class="title">当前核心</div><p>{esc(analysis["current_core"])}。待确认高标：{esc(analysis["leader_watch"])}。名义最高板不等于可交易龙头。</p></div>
        <div class="step"><div class="title">下一触发</div><p>{esc(analysis["next_opportunity"])}</p></div>
      </div>
    </section>
    <section>
      <h2>最近归档对比</h2>
      {render_table(["日期","周期","核心","上次跟踪/机会","跟踪结论"], prev_rows)}
    </section>
    <section>
      <h2>板块强度</h2>
      {render_table(["板块","高标核心","一字/中位助攻","容量核心","与旧周期关系","强度"], theme_rows)}
    </section>
    <section>
      <h2>新方向判断</h2>
      {render_table(["结论","独立强分支","旧方向相关","买点状态"], new_direction_rows)}
    </section>
    <section>
      <h2>连板梯队</h2>
      {render_table(["板数","股票","题材","角色","交易性","模型结论"], top_boards)}
    </section>
    <section>
      <h2>4/5板候选检查</h2>
      {render_table(["股票","板数","买点状态","加分项","扣分项","模型结论"], candidate_rows)}
    </section>
    <section>
      <h2>次日盯盘预案</h2>
      <div class="plan">
        <div class="plan-block"><strong>一、明日重点观察</strong><p>{esc(old_watch)}</p></div>
        <div class="plan-block"><strong>二、候选买点</strong><p>{esc(candidate_plan)}</p></div>
        <div class="plan-block"><strong>三、风险票</strong><p>{esc(risk_plan)}</p></div>
      </div>
    </section>
    <section>
      <h2>操作与仓位</h2>
      {render_table(["市场阶段","仓位级别","操作动作","候选处理"], operation_rows)}
    </section>
    <section>
      <h2>风控纪律</h2>
      {render_table(["项目","规则"], risk_control_rows)}
    </section>
    <section>
      <h2>最终执行结论</h2>
      <ol>{"".join(f"<li>{esc(line)}</li>" for line in final_lines)}</ol>
    </section>
    <section>
      <h2>数据源</h2>
      <ul><li><a href="{esc(parsed["url"])}">{esc(parsed["title"])}</a></li></ul>
    </section>
    <script type="application/json" id="stock-cycle-review-data">
{json.dumps(metadata, ensure_ascii=False, indent=2)}
    </script>
  </main>
</body>
</html>
"""
    return html_doc, metadata


def load_previous_reports():
    reports = []
    for path in sorted(OUT_DIR.glob("*.html")):
        match = re.search(r'<script type="application/json" id="stock-cycle-review-data">\s*(.*?)\s*</script>', path.read_text(encoding="utf-8"), re.S)
        if not match:
            continue
        try:
            reports.append(json.loads(html.unescape(match.group(1))))
        except Exception:
            continue
    return reports


def main():
    OUT_DIR.mkdir(exist_ok=True)
    skill_contract = load_skill_contract()
    topics = fetch_topics()
    parsed_days = [parse_topic(topic) for topic in topics]
    parsed_date_keys = {p["date"].isoformat() for p in parsed_days}
    reports = load_previous_reports()
    ledger = load_leader_ledger()
    gap_reports = sorted(
        [
            r for r in reports
            if START.isoformat() <= str(r.get("review_date", "")) <= END.isoformat()
            and r.get("review_date") not in parsed_date_keys
        ],
        key=lambda r: r.get("review_date", ""),
    )

    written = []
    rolling_reports = [r for r in reports if r.get("review_date", "") < START.isoformat()]
    for idx, parsed in enumerate(parsed_days):
        while gap_reports and gap_reports[0].get("review_date", "") < parsed["date"].isoformat():
            gap = gap_reports.pop(0)
            if all(r.get("review_date") != gap.get("review_date") for r in rolling_reports):
                rolling_reports.append(gap)
        next_date = parsed_days[idx + 1]["date"] if idx + 1 < len(parsed_days) else None
        state = leader_state_for_date(parsed["date"], ledger)
        analysis = classify_day(parsed, state, rolling_reports)
        page, metadata = render_report(parsed, analysis, rolling_reports, next_date, skill_contract)
        out = OUT_DIR / f"{parsed['date'].isoformat()}.html"
        out.write_text(page, encoding="utf-8")
        written.append(out)
        rolling_reports.append(metadata)

    # Navigation page for the generated archive.
    rows = []
    for report in rolling_reports:
        date = report.get("review_date", "")
        if not date:
            continue
        href = f"{date}.html"
        rows.append([f'<a href="{href}">{esc(date)}</a>', esc(report.get("market_phase") or "未标注"), esc(report.get("cycle_stage")), esc(report.get("current_core")), esc(report.get("next_opportunity"))])
    index = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A股短线周期复盘归档</title><style>{CSS}</style></head><body><main class="page"><header><h1>A股短线周期复盘归档</h1><p class="note">从本地归档逐日汇总。每个交易日页面只使用当日及之前数据。</p><p class="risk">这是复盘框架，不构成投资建议或荐股。</p></header><section><h2>归档列表</h2>{render_table(["日期","市场阶段","周期","核心","下一次标准买点"], rows)}</section></main></body></html>"""
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")
    print(json.dumps({"written": [str(p) for p in written], "count": len(written), "index": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
