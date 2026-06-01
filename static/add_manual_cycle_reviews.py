import datetime as dt
import html
import json
import re
from pathlib import Path

from generate_cycle_reviews import CSS, esc, render_table


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"


MANUAL = [
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
        "prior": "大唐发电",
        "theme": "电力 / 算电协同",
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
    prior = item["prior"]
    theme = item["theme"]
    prev = previous_reports(item["date"])
    if (not prior or not theme) and prev:
        prior = prior or prev[-1].get("prior_confirmed_leader", "")
        theme = theme or prev[-1].get("prior_leader_theme", "")

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

    metadata = {
        "review_date": item["date"],
        "data_cutoff": item["date"],
        "next_trading_day": item["next"],
        "cycle_stage": item["cycle"],
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
        "intermediate_trial_chain": item["core"],
        "old_leader_chain": f"{prior} / {theme}",
        "current_core": item["core"],
        "tradable_high_board": item["tradable"],
        "next_opportunity": item["next_opportunity"],
        "hard_no_trade": "不顶一字，不买2/3板，不追6板首次开口，不用未来数据倒推",
        "model_verdicts": [
            {"stock": x[0], "role": "手工补源候选", "verdict": "reject" if x[5] == "放弃" else "observe only", "reason": f"{x[2]}；{x[4]}"}
            for x in item["candidates"]
        ],
        "sources": [{"name": item["source_name"], "url": item["source_url"]}],
    }

    source_link = f'<a href="{esc(item["source_url"])}">{esc(item["source_name"])}</a>' if item["source_url"] else esc(item["source_name"])
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A股短线周期复盘 - {esc(item["date"])}</title><style>{CSS}</style></head>
<body><main class="page">
<header><h1>A股短线周期复盘 - {esc(item["date"])}</h1><p class="note">次日计划对应：{esc(item["next"])}。复盘口径：历史实盘模拟，只使用 {esc(item["date"])} 当天及之前数据。{esc(item["source_note"])}</p><p class="risk">这是复盘框架，不构成投资建议或荐股。</p></header>
<section class="grid status-grid" aria-label="核心状态"><div class="metric"><div class="label">当前周期</div><div class="value">{esc(item["cycle"])}</div></div><div class="metric"><div class="label">上一轮龙头/板块</div><div class="value">{esc(prior)} / {esc(theme)}</div></div><div class="metric"><div class="label">中间试错高标</div><div class="value">{esc(item["core"])}</div></div><div class="metric"><div class="label">可交易最高板</div><div class="value">{esc(item["tradable"])}</div></div><div class="metric"><div class="label">下一次标准买点</div><div class="value">{esc(item["next_opportunity"])}</div></div><div class="metric"><div class="label">硬性禁买</div><div class="value">不使用未来数据倒推</div></div></section>
<section><h2>高位情绪快照</h2>{render_table(["最高板","可交易最高板","昨日高标表现","断板反馈","跌停高标","炸板高标","连板晋级率"], [[esc(item["core"]), esc(item["tradable"]), esc(f"{prior} / {theme}"), esc(item["sentiment"]), "见当日源", "见当日源", esc(item["sentiment"])]])}</section>
<section><h2>周期链路</h2><div class="timeline"><div class="step"><div class="title">上一龙头</div><p>{esc(prior)} / {esc(theme)}</p></div><div class="step"><div class="title">题材判断</div><p>{esc(item["themes"])}</p></div><div class="step"><div class="title">当前核心</div><p>{esc(item["core"])}</p></div><div class="step"><div class="title">下一触发</div><p>{esc(item["next_opportunity"])}</p></div></div></section>
<section><h2>最近归档对比</h2>{render_table(["日期","周期","核心","上次跟踪/机会","跟踪结论"], prev_rows)}</section>
<section><h2>板块强度</h2>{render_table(["板块","高标核心","一字/中位助攻","容量核心","与旧周期关系","强度"], theme_rows)}</section>
<section><h2>连板梯队</h2>{render_table(["板数","股票","题材","角色","交易性","模型结论"], ladder_rows)}</section>
<section><h2>4/5板候选检查</h2>{render_table(["股票","板数","买点状态","加分项","扣分项","模型结论"], candidate_rows)}</section>
<section><h2>次日盯盘预案</h2><div class="plan"><div class="plan-block"><strong>一、明日重点观察</strong><p>旧龙：{esc(prior)} / {esc(theme)}。观察其是否继续负反馈或修复。</p></div><div class="plan-block"><strong>二、候选买点</strong><p>{esc("候选买点：无" if not item["candidates"] else "候选买点按上表，只能打板确认，不半路低吸。")}</p></div><div class="plan-block"><strong>三、风险票</strong><p>风险：一字、尾盘、爆量、旧周期补涨、无助攻。处理：不买或只观察。</p></div></div></section>
<section><h2>最终四句话</h2><ol><li>当前周期：{esc(item["cycle"])}。</li><li>当前核心：{esc(item["core"])}。</li><li>下一次标准买点：{esc(item["next_opportunity"])}。</li><li>硬性禁买：不使用未来数据倒推，不追6板，不买2/3板。</li></ol></section>
<section><h2>数据源</h2><ul><li>{source_link}</li></ul></section>
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
        rows.append([f'<a href="{date}.html">{esc(date)}</a>', esc(data.get("cycle_stage")), esc(data.get("current_core")), esc(data.get("next_opportunity"))])
    index = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>A股短线周期复盘归档</title><style>{CSS}</style></head><body><main class="page"><header><h1>A股短线周期复盘归档</h1><p class="note">每个交易日页面只使用当日及之前数据；缺同日源日期会明确标记数据源不足。</p><p class="risk">这是复盘框架，不构成投资建议或荐股。</p></header><section><h2>归档列表</h2>{render_table(["日期","周期","核心","下一次标准买点"], rows)}</section></main></body></html>'
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")


def main():
    for item in MANUAL:
        (OUT_DIR / f'{item["date"]}.html').write_text(render(item), encoding="utf-8")
    rebuild_index()
    print(json.dumps({"manual_written": [item["date"] for item in MANUAL]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
