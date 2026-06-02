import datetime as dt
import html
import json
import re
from pathlib import Path

from generate_cycle_reviews import (
    CSS,
    esc,
    leader_state_for_date,
    load_skill_contract,
    load_leader_ledger,
    operation_for_phase,
    render_table,
    risk_control_for_phase,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"


MANUAL = [
    {
        "date": "2026-03-11",
        "next": "2026-03-12",
        "cycle": "豫能控股退潮后的混沌试错期",
        "prior": "豫能控股",
        "theme": "电力 / 算电协同",
        "core": "宁波建工4板；中南文化3板和绿电二板只做盘面跟踪",
        "tradable": "宁波建工4板",
        "next_opportunity": "暂无标准买点；等4/5板分歧换手回封",
        "sentiment": "财联社口径18股炸板，连板高度4板，未核到批量高标跌停",
        "themes": "建筑装饰/数据中心、绿电/电力、化工/锂电/煤炭",
        "ladder": [["4板", "宁波建工", "试错高标"], ["3板", "中南文化", "盘面跟踪"], ["2板", "绿电低位", "助攻观察"]],
        "candidates": [["宁波建工", "4", "可交易最高板，但不是标准龙空龙买点", "4板高度，非连续一字", "旧龙负反馈未充分兑现，板块助攻不完整，孤高试错属性重", "放弃"]],
        "source_name": "财联社3月11日焦点复盘",
        "source_url": "https://finance.sina.com.cn/jjxw/2026-03-11/doc-inhqrfck5567644.shtml",
        "sources": [
            {"name": "财联社3月11日焦点复盘", "url": "https://finance.sina.com.cn/jjxw/2026-03-11/doc-inhqrfck5567644.shtml"},
            {"name": "3月11日涨停板连板", "url": "https://cj.sina.com.cn/articles/view/3240851740/c12b791c00101ie0w"},
            {"name": "3月11日涨停原因", "url": "https://k.sina.com.cn/article_3240851740_c12b791c00101ie1i.html"},
        ],
        "source_note": "数据源：财联社复盘、新浪连板与涨停原因、巨潮公告",
    },
    {
        "date": "2026-03-12",
        "next": "2026-03-13",
        "cycle": "绿电加强但未确认标准买点",
        "prior": "豫能控股",
        "theme": "电力 / 算电协同",
        "core": "中南文化4板名义高标且一字；绿发电力、华电能源3板只做同板块助攻观察",
        "tradable": "无标准可交易4/5板买点",
        "next_opportunity": "暂无标准买点；不预设同板块3进4为买点，先等一字高标断板负反馈",
        "sentiment": "中南文化一字高标，绿电加强但同板块低位只能算助攻",
        "themes": "绿电/电力、基础化工/煤化工",
        "ladder": [["4板", "中南文化", "名义高标"], ["3板", "绿发电力、华电能源", "同板块助攻观察"], ["2板", "绿电低位", "助攻观察"]],
        "candidates": [["中南文化", "4", "一字属性强，交易性不足", "高度领先", "连续一字，不能作为标准买点", "放弃"]],
        "source_name": "3月12日涨停板连板",
        "source_url": "https://cj.sina.com.cn/articles/view/3240851740/c12b791c00101iea6",
        "sources": [
            {"name": "3月12日涨停板连板", "url": "https://cj.sina.com.cn/articles/view/3240851740/c12b791c00101iea6"},
            {"name": "3月12日绿色电力涨停板梳理", "url": "https://cj.sina.com.cn/articles/view/3240851740/c12b791c00101iebw"},
        ],
        "source_note": "数据源：新浪连板、绿电涨停梳理、沪深涨停分析、前日归档",
    },
    {
        "date": "2026-03-13",
        "next": "2026-03-16",
        "cycle": "旧龙负反馈后的高位分歧试错期",
        "prior": "豫能控股",
        "theme": "电力 / 算电协同",
        "core": "华电能源4板为排除一字后的可交易最高板，但更像电力二阶段核心",
        "tradable": "华电能源4板",
        "next_opportunity": "无标准新买点；华电能源3月16日5板不当新开仓买点",
        "sentiment": "豫能控股尾盘跌停，财联社口径18股炸板，连板晋级率37.5%，3板及以上仅3只",
        "themes": "绿电/风电/电力、化工/煤化工/化肥",
        "ladder": [["5板", "中南文化", "名义最高板"], ["4板", "华电能源", "电力二阶段核心"], ["3板", "金牛化工", "试错分支"]],
        "candidates": [["中南文化", "5", "名义最高板但一字属性强", "高度领先", "一字属性强，无法作为标准买点", "放弃"], ["华电能源", "4", "有可交易回封，但不确认标准龙空龙买点", "旧龙豫能控股跌停，绿电/风电有助攻", "与豫能控股同属电力大链条，分歧不充分", "仅观察"]],
        "source_name": "财联社3月13日焦点复盘",
        "source_url": "https://finance.sina.com.cn/roll/2026-03-13/doc-inhqvtih4125148.shtml",
        "sources": [
            {"name": "财联社3月13日焦点复盘", "url": "https://finance.sina.com.cn/roll/2026-03-13/doc-inhqvtih4125148.shtml"},
            {"name": "东方财富3月13日涨停复盘", "url": "https://finance.eastmoney.com/a/202603133671671653.html"},
            {"name": "3月13日涨停原因", "url": "https://k.sina.com.cn/article_3240851740_c12b791c00101iekg.html"},
            {"name": "3月13日连板复盘", "url": "https://wudaolu.com/t/topic/17328"},
            {"name": "中财网华电能源10:15封板快讯", "url": "https://cfi.cn/p20260313000008.html"},
        ],
        "source_note": "数据源：财联社复盘、东方财富、涨停原因、连板复盘、中财网封板快讯",
    },
    {
        "date": "2026-03-16",
        "next": "2026-03-17",
        "cycle": "豫能控股退潮后的混沌试错期",
        "prior": "豫能控股",
        "theme": "电力 / 算电协同",
        "core": "三房巷3板；连板高度只有3板",
        "tradable": "无标准可交易4/5板买点",
        "next_opportunity": "暂无标准买点；最高板只有3板，低位只做盘面跟踪",
        "sentiment": "涨停44家，跌停5家，封板率65%，连板6家，晋级率25%，最高3板三房巷",
        "themes": "存储芯片、PCB、航运",
        "ladder": [["3板", "三房巷", "试错高标"], ["2板", "连板合计6家中的低位票", "盘面跟踪"]],
        "candidates": [],
        "source_name": "A股2026年3月16日复盘_新浪新闻",
        "source_url": "https://www.sina.cn/news/detail/5277162259089629.html",
        "source_note": "发布时间：2026-03-16 18:29",
    },
    {
        "date": "2026-04-24",
        "next": "2026-04-27",
        "cycle": "数据源不足，维持前序周期观察",
        "prior": "",
        "theme": "",
        "core": "未找到当日同日发布的可靠连板复盘源",
        "tradable": "不做判断",
        "next_opportunity": "无标准买点；数据源不足时不做回测式判断",
        "sentiment": "未使用4月24日之后发布的复盘资料",
        "themes": "不做板块强弱排序",
        "ladder": [["未知", "缺同日源", "不复盘"]],
        "candidates": [],
        "source_name": "未找到同日发布复盘源",
        "source_url": "",
        "source_note": "为避免使用未来数据，本日只建空白归档",
    },
    {
        "date": "2026-05-11",
        "next": "2026-05-12",
        "cycle": "电力容量核心试错期",
        "prior": "",
        "theme": "",
        "core": "大唐发电4连板；电子、机械设备、电力设备涨停较多",
        "tradable": "大唐发电4板",
        "next_opportunity": "只可盘中检查大唐发电是否给出充分换手回封；收盘复盘不倒推买点",
        "sentiment": "涨停135只，跌停30只，46股封板未遂，封板率74.59%",
        "themes": "电子、机械设备、电力设备；电力方向由大唐发电带队",
        "ladder": [["4板", "大唐发电", "电力容量核心"], ["低位", "电子、机械设备、电力设备涨停较多", "板块宽度"]],
        "candidates": [["大唐发电", "4", "当日4板容量核心，需盘中确认换手回封", "板块强、封单居前", "缺少完整分时换手数据", "仅观察"]],
        "source_name": "数据宝：揭秘涨停 | 热门股4连板，封单金额近7亿元",
        "source_url": "https://finance.sina.com.cn/wm/2026-05-11/doc-inhxppic1853400.shtml",
        "source_note": "发布时间：2026-05-11 18:23",
    },
    {
        "date": "2026-05-12",
        "next": "2026-05-13",
        "cycle": "电力容量核心确认前分歧期",
        "prior": "",
        "theme": "",
        "core": "大唐发电延续高度；全市场57家涨停，最高11板",
        "tradable": "大唐发电5板按观察处理",
        "next_opportunity": "4板买点已过，5板只做持仓确认或观察，不做新开仓标准买点",
        "sentiment": "全市场57家涨停，最高11板",
        "themes": "电网设备、数据中心、电力需求、光通信等",
        "ladder": [["高标", "最高11板个股", "名义高度"], ["5板", "大唐发电", "电力容量核心"]],
        "candidates": [["大唐发电", "5", "4板买点已过，5板不作为新开仓", "电力方向延续", "不是首次标准买点", "仅观察"]],
        "source_name": "2026年05月12日 A股复盘：全市场57家涨停，最高11板",
        "source_url": "https://solbt.com/article/20260512",
        "source_note": "页面日期：2026-05-12",
    },
    {
        "date": "2026-05-13",
        "next": "2026-05-14",
        "cycle": "大唐发电确认后的高位分歧前夜",
        "prior": "大唐发电",
        "theme": "电力 / 算电协同",
        "core": "大唐发电6板确认；全市场100家涨停，最高9板",
        "tradable": "无新开仓标准买点",
        "next_opportunity": "大唐发电6板只做确认，不做新买点；等待高位负反馈后的新题材4/5板",
        "sentiment": "全市场100家涨停，最高9板；大唐发电封单资金居前",
        "themes": "华为概念、算力、数据中心、算电协同",
        "ladder": [["6板", "大唐发电", "电力容量核心"], ["首板潮", "华为概念、算力、数据中心", "板块扩散"]],
        "candidates": [["大唐发电", "6", "确认点，不是新买点", "容量核心、封单强", "6板以后不追", "放弃"]],
        "source_name": "2026年05月13日 A股复盘：全市场100家涨停，最高9板",
        "source_url": "https://solbt.com/article/20260513",
        "source_note": "页面日期：2026-05-13",
    },
    {
        "date": "2026-05-14",
        "next": "2026-05-15",
        "cycle": "大唐发电断板后的高位负反馈期",
        "prior": "大唐发电",
        "theme": "电力 / 算电协同",
        "core": "蒙娜丽莎5连板；利仁科技4连板；大唐发电炸板长阴",
        "tradable": "利仁科技4板仅观察",
        "next_opportunity": "旧龙大唐发电放量炸板后，不急于切新周期，先看负反馈是否扩散",
        "sentiment": "55股涨停，31股炸板，封板率64%，连板晋级率29.41%",
        "themes": "猪肉、工业气体、玻璃基板、第三代半导体领涨；绿电承压",
        "ladder": [["5板", "蒙娜丽莎", "独立高标"], ["4板", "利仁科技", "试错高标"], ["3板", "合肥城建、可川科技、花王股份", "中位跟踪"]],
        "candidates": [["利仁科技", "4", "旧龙刚负反馈，试错环境不稳定", "4板高度", "市场高位负反馈扩散", "仅观察"]],
        "source_name": "财联社5月14日焦点复盘",
        "source_url": "https://finance.sina.com.cn/roll/2026-05-14/doc-inhxwenm3981225.shtml",
        "source_note": "发布时间：2026-05-14 17:33",
    },
    {
        "date": "2026-05-15",
        "next": "2026-05-18",
        "cycle": "旧龙负反馈后的机器人低位扩散期",
        "prior": "大唐发电",
        "theme": "电力 / 算电协同",
        "core": "蒙娜丽莎6连板；机器人板块涨停潮",
        "tradable": "无新开仓标准买点",
        "next_opportunity": "蒙娜丽莎6板不追；机器人多为低位扩散，等待未来4/5板换手回封",
        "sentiment": "连板晋级率约25%，高标生态偏极端",
        "themes": "人形机器人、地产链、氟化工",
        "ladder": [["6板", "蒙娜丽莎", "名义最高板"], ["2板", "北自科技", "机器人中位"], ["首板", "巨轮智能、方正电机、雷赛智能等", "机器人扩散"]],
        "candidates": [["蒙娜丽莎", "6", "6板不作为新买点", "高度打开", "6板以后不追", "放弃"]],
        "source_name": "2026年05月15日股市复盘：机器人海啸席卷全场",
        "source_url": "https://www.52daban.com/daily_review/2026-05-15",
        "source_note": "发布时间：2026-05-15",
    },
]


LEADER_LEDGER = load_leader_ledger()
SKILL_CONTRACT = load_skill_contract()


def manual_market_phase(cycle):
    if "主升" in cycle:
        return "主升期"
    if "退潮" in cycle or "负反馈" in cycle:
        return "退潮期"
    if "确认" in cycle and "买点" not in cycle:
        return "新周期初期"
    if "分歧" in cycle or "高位" in cycle:
        return "分歧期"
    return "试错期"


def manual_loss_effect(item):
    if "退潮" in item["cycle"] or "负反馈" in item["cycle"]:
        level = "偏高"
    elif "炸板" in item["sentiment"] or "跌停" in item["sentiment"]:
        level = "中等"
    else:
        level = "待核验"
    return {
        "level": level,
        "summary": f"亏钱效应：{level}。手工补源页以当日源描述为准。",
        "rows": [
            ["高标是否继续A杀", "需结合当日分时/跌停榜核验", "手工补源不使用未来走势倒推"],
            ["断板票是否继续跌停", item["sentiment"], "若跌停扩散，操作降级为空仓"],
            ["昨日炸板票是否修复", "手工源未完整披露", "盘中补核，不在复盘中强行推断"],
            ["连板高度是否下降", item["core"], "高度下降时优先保护仓位"],
            ["补涨是否开始坑人", "按候选表风险原因判断", "旧周期补涨和无助攻默认不买"],
        ],
    }


def read_json(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="stock-cycle-review-data">\s*(.*?)\s*</script>', text, re.S)
    if not match:
        return None
    return json.loads(html.unescape(match.group(1)))


def previous_reports(date):
    reports = []
    for path in sorted(OUT_DIR.glob("2026-*.html")):
        if path.stem >= date:
            continue
        data = read_json(path)
        if data:
            reports.append(data)
    return reports[-5:]


def render(item):
    anchor = leader_state_for_date(dt.date.fromisoformat(item["date"]), LEADER_LEDGER)
    prior = item["prior"] or anchor["prior_leader"]
    theme = item["theme"] or anchor["prior_theme"]
    prior_confirmed = bool(item["prior"]) or anchor["prior_leader_confirmed"]
    prior_source = "手工补源复盘项" if item["prior"] else anchor["prior_leader_source"]
    prior_note = anchor["prior_leader_note"]
    phase = manual_market_phase(item["cycle"])
    loss_effect = manual_loss_effect(item)
    operation = operation_for_phase(phase)
    risk_control = risk_control_for_phase(phase)
    prev = previous_reports(item["date"])

    prev_rows = [
        [esc(r.get("review_date")), esc(r.get("cycle_stage")), esc(r.get("current_core")), esc(r.get("next_opportunity")), "只用前序归档滚动比较"]
        for r in prev
    ] or [["无更早归档", "无", "无", "无", "从本日开始"]]
    ladder_rows = [[esc(a), esc(b), esc(item["themes"]), esc(c), "按收盘资料判断", '<span class="badge observe">观察</span>'] for a, b, c in item["ladder"]]
    theme_rows = [[esc(item["themes"]), esc(item["core"]), esc(item["sentiment"]), "未完整披露", esc("与旧周期相关" if any(x in item["themes"] for x in theme.split(" / ")) else "独立或背景分支"), '<span class="badge context">中等</span>']]
    if item["candidates"]:
        candidate_rows = [[esc(x[0]), esc(x[1]), esc(x[2]), esc(x[3]), esc(x[4]), f'<span class="badge {"reject" if x[5]=="放弃" else "observe"}">{esc(x[5])}</span>'] for x in item["candidates"]]
    else:
        candidate_rows = [["当日无符合4/5板候选，低位票只做盘面跟踪", "-", "无买点", "无", "未到4/5板", '<span class="badge observe">仅观察</span>']]
    loss_rows = [[esc(a), esc(b), esc(c)] for a, b, c in loss_effect["rows"]]
    operation_rows = [[esc(phase), esc(operation["position"]), esc(operation["action"]), esc(operation["candidate"])]]
    risk_control_rows = [[esc(name), esc(rule)] for name, rule in risk_control]
    new_direction_rows = [[esc("手工补源：按当日主题描述观察"), esc(item["themes"]), esc("与旧周期相关" if any(x in item["themes"] for x in theme.split(" / ")) else "独立或背景分支"), esc("未确认标准买点")]]

    metadata = {
        "review_date": item["date"],
        "data_cutoff": item["date"],
        "next_trading_day": item["next"],
        "generated_by_skill": SKILL_CONTRACT,
        "cycle_stage": item["cycle"],
        "market_phase": phase,
        "old_leader_state": "未确认" if not prior_confirmed else ("明显退潮" if phase == "退潮期" else "按手工源观察"),
        "loss_effect": loss_effect,
        "new_direction": {
            "summary": "手工补源：按当日主题描述观察",
            "strong_independent": item["themes"],
            "old_related": "与旧周期相关" if any(x in item["themes"] for x in theme.split(" / ")) else "无",
        },
        "operation_plan": operation,
        "risk_control": risk_control,
        "high_level_sentiment": {
            "nominal_highest_board": item["core"],
            "tradable_highest_board": item["tradable"],
            "previous_high_board_performance": f"{prior} / {theme}",
            "broken_board_feedback": item["sentiment"],
            "high_level_limit_down_count": "见当日源",
            "high_level_broken_board_count": "见当日源",
            "promotion_rate": item["sentiment"],
        },
        "prior_confirmed_leader": prior,
        "prior_leader_theme": theme,
        "prior_leader_confirmed": prior_confirmed,
        "prior_leader_source": prior_source,
        "prior_leader_note": prior_note,
        "leader_watch": "无",
        "intermediate_trial_chain": item["core"],
        "old_leader_chain": f"{prior} / {theme}",
        "current_core": item["core"],
        "tradable_high_board": item["tradable"],
        "next_opportunity": item["next_opportunity"],
        "hard_no_trade": "退潮期空仓；不顶一字；不买2/3板；不追6板首次开口；不用未来数据倒推",
        "model_verdicts": [
            {"stock": x[0], "role": "手工补源候选", "verdict": "reject" if x[5] == "放弃" else "observe only", "reason": f"{x[2]}；{x[4]}"}
            for x in item["candidates"]
        ],
        "sources": item.get("sources") or [{"name": item["source_name"], "url": item["source_url"]}],
    }

    source_items = item.get("sources") or [{"name": item["source_name"], "url": item["source_url"]}]
    source_link = "".join(
        f'<li><a href="{esc(source.get("url"))}">{esc(source.get("name"))}</a></li>' if source.get("url") else f'<li>{esc(source.get("name"))}</li>'
        for source in source_items
    )
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A股短线周期复盘 - {esc(item["date"])}</title><style>{CSS}</style></head>
<body><main class="page">
<header><h1>A股短线周期复盘 - {esc(item["date"])}</h1><p class="note">次日计划对应：{esc(item["next"])}。复盘口径：历史实盘模拟，只使用 {esc(item["date"])} 当天及之前数据。{esc(item["source_note"])}</p><p class="note">生成依据：{esc(SKILL_CONTRACT["name"])} skill；流程：{esc(SKILL_CONTRACT["workflow"])}。</p><p class="risk">这是复盘框架，不构成投资建议或荐股。输出顺序由 skill 固定为：阶段 -> 旧龙 -> 亏钱效应 -> 新方向 -> 梯队 -> 买点 -> 操作 -> 风控。</p></header>
<section class="grid status-grid" aria-label="核心状态"><div class="metric"><div class="label">市场阶段</div><div class="value">{esc(phase)}</div></div><div class="metric"><div class="label">上一轮龙头/板块</div><div class="value">{esc(prior)} / {esc(theme)}</div></div><div class="metric"><div class="label">旧龙状态</div><div class="value">{esc(metadata["old_leader_state"])}</div></div><div class="metric"><div class="label">亏钱效应</div><div class="value">{esc(loss_effect["level"])}</div></div><div class="metric"><div class="label">新方向</div><div class="value">手工补源观察</div></div><div class="metric"><div class="label">操作仓位</div><div class="value">{esc(operation["position"])}</div></div></section>
<section><h2>高位情绪快照</h2>{render_table(["最高板","可交易最高板","昨日高标表现","断板反馈","跌停高标","炸板高标","连板晋级率"], [[esc(item["core"]), esc(item["tradable"]), esc(f"{prior} / {theme}"), esc(item["sentiment"]), "见当日源", "见当日源", esc(item["sentiment"])]])}</section>
<section><h2>亏钱效应</h2>{render_table(["检查项","当前判断","处理要点"], loss_rows)}</section>
<section><h2>周期链路</h2><div class="timeline"><div class="step"><div class="title">上一龙头</div><p>{esc(prior)} / {esc(theme)}。来源：{esc(prior_source)}。</p></div><div class="step"><div class="title">题材判断</div><p>{esc(item["themes"])}</p></div><div class="step"><div class="title">当前核心</div><p>{esc(item["core"])}</p></div><div class="step"><div class="title">下一触发</div><p>{esc(item["next_opportunity"])}</p></div></div></section>
<section><h2>最近归档对比</h2>{render_table(["日期","周期","核心","上次跟踪/机会","跟踪结论"], prev_rows)}</section>
<section><h2>板块强度</h2>{render_table(["板块","高标核心","一字/中位助攻","容量核心","与旧周期关系","强度"], theme_rows)}</section>
<section><h2>新方向判断</h2>{render_table(["结论","主要方向","与旧周期关系","买点状态"], new_direction_rows)}</section>
<section><h2>连板梯队</h2>{render_table(["板数","股票","题材","角色","交易性","模型结论"], ladder_rows)}</section>
<section><h2>4/5板候选检查</h2>{render_table(["股票","板数","买点状态","加分项","扣分项","模型结论"], candidate_rows)}</section>
<section><h2>次日盯盘预案</h2><div class="plan"><div class="plan-block"><strong>一、明日重点观察</strong><p>旧龙：{esc(prior)} / {esc(theme)}。观察其是否继续负反馈或修复。</p></div><div class="plan-block"><strong>二、候选买点</strong><p>{esc("候选买点：无" if not item["candidates"] else "候选买点按上表，只能打板确认，不半路低吸。")}</p></div><div class="plan-block"><strong>三、风险票</strong><p>风险：一字、尾盘、爆量、旧周期补涨、无助攻。处理：不买或只观察。</p></div></div></section>
<section><h2>操作与仓位</h2>{render_table(["市场阶段","仓位级别","操作动作","候选处理"], operation_rows)}</section>
<section><h2>风控纪律</h2>{render_table(["项目","规则"], risk_control_rows)}</section>
<section><h2>最终执行结论</h2><ol><li>当前市场阶段：{esc(phase)}；周期描述：{esc(item["cycle"])}。</li><li>当前核心：{esc(item["core"])}。</li><li>亏钱效应：{esc(loss_effect["level"])}；操作仓位：{esc(operation["position"])}。</li><li>下一次标准买点：{esc(item["next_opportunity"])}。</li><li>硬性禁买：退潮期空仓，不追6板，不买2/3板。</li></ol></section>
<section><h2>数据源</h2><ul>{source_link}</ul></section>
<script type="application/json" id="stock-cycle-review-data">
{json.dumps(metadata, ensure_ascii=False, indent=2)}
</script></main></body></html>"""
    return page


def rebuild_index():
    rows = []
    for path in sorted(OUT_DIR.glob("2026-*.html")):
        data = read_json(path)
        if not data:
            continue
        date = data.get("review_date")
        rows.append([f'<a href="{date}.html">{esc(date)}</a>', esc(data.get("market_phase") or "未标注"), esc(data.get("cycle_stage")), esc(data.get("current_core")), esc(data.get("next_opportunity"))])
    index = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A股短线周期复盘归档</title><style>{CSS}</style></head><body><main class="page"><header><h1>A股短线周期复盘归档</h1><p class="note">每个交易日页面只使用当日及之前数据；缺同日源日期会明确标记数据源不足。</p><p class="risk">这是复盘框架，不构成投资建议或荐股。</p></header><section><h2>归档列表</h2>{render_table(["日期","市场阶段","周期","核心","下一次标准买点"], rows)}</section></main></body></html>'
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")


def main():
    for item in MANUAL:
        (OUT_DIR / f'{item["date"]}.html').write_text(render(item), encoding="utf-8")
    rebuild_index()
    print(json.dumps({"manual_written": [item["date"] for item in MANUAL]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
