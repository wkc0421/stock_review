import datetime as dt
import html
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"
START = dt.date(2026, 3, 17)
END = dt.date(2026, 6, 1)
CATEGORY_URL = "https://wudaolu.com/c/aguhot/8.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}


CSS = """
:root{--bg:#f6f7f9;--panel:#fff;--text:#1f2937;--muted:#6b7280;--line:#d9dee7;--strong:#13795b;--warn:#b26a00;--danger:#b42318;--info:#1d4ed8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.55}.page{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 0 42px}header{display:grid;gap:10px;margin-bottom:16px}h1{margin:0;font-size:clamp(24px,4vw,36px);letter-spacing:0}h2{margin:0 0 12px;font-size:18px;letter-spacing:0}p{margin:0}.note{color:var(--muted);font-size:14px}.risk{border-left:4px solid var(--warn);background:#fff8ec;padding:10px 12px;color:#7a4b00}.grid{display:grid;gap:12px}.status-grid{grid-template-columns:repeat(6,minmax(0,1fr));margin:16px 0}.metric,section{background:var(--panel);border:1px solid var(--line);border-radius:8px}.metric{min-height:96px;padding:12px}.metric .label{color:var(--muted);font-size:12px;margin-bottom:6px}.metric .value{font-size:17px;font-weight:700}section{padding:16px;margin-bottom:14px}.timeline,.plan{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.plan{grid-template-columns:repeat(3,1fr)}.step,.plan-block{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fbfcfe}.title,.plan-block strong{display:block;font-weight:700;margin-bottom:6px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:10px 8px;text-align:left;vertical-align:top}th{color:var(--muted);font-weight:600;background:#f9fafb}.badge{display:inline-flex;align-items:center;min-height:24px;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}.buy{background:#e8f5ef;color:var(--strong)}.observe{background:#fff4db;color:var(--warn)}.reject{background:#fdebea;color:var(--danger)}.context{background:#eaf1ff;color:var(--info)}ul,ol{margin:0;padding-left:20px}a{color:var(--info)}@media(max-width:860px){.status-grid,.timeline,.plan{grid-template-columns:1fr}.table-wrap{overflow-x:auto}table{min-width:760px}}
""".strip()


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
        data = requests.get(url, headers=HEADERS, timeout=25).json()
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
    data = requests.get(f"{url}.json", headers=HEADERS, timeout=25).json()
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

    old_leader = state["prior_leader"]
    old_theme = state["prior_theme"]
    old_live = next((r for r in ladder if stock_label(r) == old_leader or r.get("代码") == state.get("prior_code")), None)
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

        verdict = "仅观察"
        if "一字或准一字交易性不足" in negatives or same_theme_blocked or row["board"] != tradable_high:
            verdict = "放弃"
        elif len(positives) >= 4 and len(negatives) <= 1 and not overlap_theme(row, old_theme):
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

    current_core = "、".join(stock_label(r) + f"{r['board']}板" for r in nominal[:3]) if nominal else "无连板高度"
    tradable_high_text = "、".join(stock_label(r) + f"{r['board']}板" for r in tradable_high_rows[:3]) if tradable_high_rows else "无标准可交易4/5板买点"

    # Update state only after the report is classified, so the current report never benefits from future data.
    confirm = next((r for r in sorted(main_ladder, key=lambda x: x["board"], reverse=True) if r["board"] >= 6 and not is_one_word(r)), None)
    next_state = dict(state)
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
        "next_opportunity": next_opportunity,
        "hard_no_trade": "不顶一字，不买2/3板，不追6板首次开口，不买同板块后排替代",
        "old_leader": old_leader,
        "old_theme": old_theme,
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


def render_report(parsed, analysis, previous_reports, next_date):
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

    old_watch = f"旧龙：{analysis['old_leader']} / {analysis['old_theme']}。{analysis['old_status']}。若继续不在涨停池或出现高位负反馈，说明旧周期压制仍在；若重新涨停，说明旧周期仍有修复。"
    if analysis["standard"]:
        candidate_plan = "候选买点：" + "、".join(stock_label(r) for r in analysis["standard"]) + "。买点方式：只按计划内打板确认；不能半路、低吸或顶一字。"
    else:
        candidate_plan = "候选买点：无。处理：空仓或只登记候选池；低位2/3板和同板块后排不替代标准4/5板。"
    risk_names = "、".join(stock_label(r) for r in analysis["nominal"][:3]) or "当日高标"
    risk_plan = f"风险票：{risk_names}。风险原因：一字、尾盘回封、爆量、旧周期补涨或无板块助攻。处理：不买或只观察负反馈。"

    final_lines = [
        f"当前周期：{analysis['cycle']}。",
        f"当前核心：上一轮龙头是{analysis['old_leader']} / {analysis['old_theme']}；当日核心为{analysis['current_core']}。",
        f"下一次标准买点：{analysis['next_opportunity']}。",
        f"硬性禁买：{analysis['hard_no_trade']}。",
    ]

    metadata = {
        "review_date": date.isoformat(),
        "data_cutoff": date.isoformat(),
        "next_trading_day": next_date.isoformat() if next_date else "",
        "cycle_stage": analysis["cycle"],
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
      <p class="risk">这是复盘框架，不构成投资建议或荐股。输出顺序固定为：周期 -> 题材 -> 梯队 -> 买点。</p>
    </header>
    <section class="grid status-grid" aria-label="核心状态">
      <div class="metric"><div class="label">当前周期</div><div class="value">{esc(analysis["cycle"])}</div></div>
      <div class="metric"><div class="label">上一轮龙头/板块</div><div class="value">{esc(analysis["old_leader"])} / {esc(analysis["old_theme"])}</div></div>
      <div class="metric"><div class="label">中间试错高标</div><div class="value">{esc(metadata["intermediate_trial_chain"] or "无")}</div></div>
      <div class="metric"><div class="label">可交易最高板</div><div class="value">{esc(analysis["tradable_high"])}</div></div>
      <div class="metric"><div class="label">下一次标准买点</div><div class="value">{esc(analysis["next_opportunity"])}</div></div>
      <div class="metric"><div class="label">硬性禁买</div><div class="value">{esc(analysis["hard_no_trade"])}</div></div>
    </section>
    <section>
      <h2>高位情绪快照</h2>
      {render_table(["最高板","可交易最高板","昨日高标表现","断板反馈","跌停高标","炸板高标","连板晋级率"], [[esc(metadata["high_level_sentiment"]["nominal_highest_board"]), esc(metadata["high_level_sentiment"]["tradable_highest_board"]), esc(analysis["old_status"]), "按当日梯队和前序归档判断", "不使用未来跌停数据", "见个股炸板字段", "见连板梯队"]])}
    </section>
    <section>
      <h2>周期链路</h2>
      <div class="timeline">
        <div class="step"><div class="title">上一龙头</div><p>{esc(analysis["old_leader"])} / {esc(analysis["old_theme"])}。{esc(analysis["old_status"])}</p></div>
        <div class="step"><div class="title">题材判断</div><p>{esc("、".join(main_theme_names := [g["name"] for g in analysis["theme_groups"][:3]]) or "无明确主线")} 是当日主要涨停方向，先看是否独立于旧周期。</p></div>
        <div class="step"><div class="title">当前核心</div><p>{esc(analysis["current_core"])}。名义最高板不等于可交易龙头。</p></div>
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
      <h2>最终四句话</h2>
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
    topics = fetch_topics()
    parsed_days = [parse_topic(topic) for topic in topics]
    reports = load_previous_reports()
    reports_by_date = {r.get("review_date"): r for r in reports}
    state = {
        "prior_leader": "豫能控股",
        "prior_code": "001896",
        "prior_theme": "电力 / 算电协同",
    }
    if "2026-03-13" in reports_by_date:
        base = reports_by_date["2026-03-13"]
        state["prior_leader"] = base.get("prior_confirmed_leader") or state["prior_leader"]
        state["prior_theme"] = base.get("prior_leader_theme") or state["prior_theme"]

    written = []
    rolling_reports = [r for r in reports if r.get("review_date", "") < START.isoformat()]
    for idx, parsed in enumerate(parsed_days):
        next_date = parsed_days[idx + 1]["date"] if idx + 1 < len(parsed_days) else None
        analysis = classify_day(parsed, state, rolling_reports)
        page, metadata = render_report(parsed, analysis, rolling_reports, next_date)
        out = OUT_DIR / f"{parsed['date'].isoformat()}.html"
        out.write_text(page, encoding="utf-8")
        written.append(out)
        rolling_reports.append(metadata)
        state = analysis["next_state"]

    # Navigation page for the generated archive.
    rows = []
    for report in rolling_reports:
        date = report.get("review_date", "")
        if not date:
            continue
        href = f"{date}.html"
        rows.append([f'<a href="{href}">{esc(date)}</a>', esc(report.get("cycle_stage")), esc(report.get("current_core")), esc(report.get("next_opportunity"))])
    index = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A股短线周期复盘归档</title><style>{CSS}</style></head><body><main class="page"><header><h1>A股短线周期复盘归档</h1><p class="note">从本地归档逐日汇总。每个交易日页面只使用当日及之前数据。</p><p class="risk">这是复盘框架，不构成投资建议或荐股。</p></header><section><h2>归档列表</h2>{render_table(["日期","周期","核心","下一次标准买点"], rows)}</section></main></body></html>"""
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")
    print(json.dumps({"written": [str(p) for p in written], "count": len(written), "index": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
