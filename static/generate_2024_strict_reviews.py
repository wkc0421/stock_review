import html
import json
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"
SKILL_DIR = Path(r"C:\Users\wkc\.codex\plugins\cache\personal\stock-cycle-review\0.1.0+codex.20260602143920\skills\stock-cycle-review")


DATES = [
    "2024-09-13",
    "2024-09-16",
    "2024-09-17",
    "2024-09-18",
    "2024-09-19",
    "2024-09-20",
    "2024-09-23",
    "2024-09-24",
    "2024-09-25",
    "2024-09-26",
    "2024-09-27",
    "2024-09-30",
    "2024-10-01",
    "2024-10-02",
    "2024-10-03",
    "2024-10-04",
    "2024-10-07",
    "2024-10-08",
    "2024-10-09",
    "2024-10-10",
    "2024-10-11",
    "2024-10-14",
    "2024-10-15",
    "2024-10-16",
    "2024-10-17",
    "2024-10-18",
    "2024-10-21",
    "2024-10-22",
    "2024-10-23",
    "2024-10-24",
    "2024-10-25",
    "2024-10-28",
    "2024-10-29",
    "2024-10-30",
    "2024-10-31",
    "2024-11-01",
    "2024-11-04",
    "2024-11-05",
    "2024-11-06",
    "2024-11-07",
    "2024-11-08",
    "2024-11-11",
    "2024-11-12",
    "2024-11-13",
    "2024-11-14",
    "2024-11-15",
    "2024-11-18",
    "2024-11-19",
    "2024-11-20",
    "2024-11-21",
    "2024-11-22",
    "2024-11-25",
    "2024-11-26",
    "2024-11-27",
    "2024-11-28",
    "2024-11-29",
    "2024-12-02",
    "2024-12-03",
    "2024-12-04",
    "2024-12-05",
    "2024-12-06",
    "2024-12-09",
    "2024-12-10",
    "2024-12-11",
    "2024-12-12",
    "2024-12-13",
    "2024-12-16",
    "2024-12-17",
    "2024-12-18",
    "2024-12-19",
    "2024-12-20",
    "2024-12-23",
    "2024-12-24",
    "2024-12-25",
    "2024-12-26",
    "2024-12-27",
    "2024-12-30",
    "2024-12-31",
    "2025-01-01",
]


HOLIDAYS = {
    "2024-09-16": "中秋节休市",
    "2024-10-01": "国庆节休市",
    "2024-10-02": "国庆节休市",
    "2024-10-03": "国庆节休市",
    "2024-10-04": "国庆节休市",
    "2024-10-07": "国庆节休市",
    "2025-01-01": "元旦休市",
}


EASTMONEY_URLS = {
    "海能达": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.002583&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20240925&end=20240925",
    "双成药业": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.002693&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20240918&end=20240918",
    "大千生态": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.603955&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241111&end=20241111",
    "日出东方": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.603366&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241115&end=20241115",
    "一鸣食品": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.605179&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241129&end=20241129",
    "粤桂股份": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.000833&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241119&end=20241119",
    "益民集团": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600824&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241217&end=20241217",
    "友阿股份": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.002277&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241217&end=20241217",
    "实益达": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.002137&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241225&end=20241225",
    "中百集团": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.000759&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241230&end=20241230",
    "东百集团": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600693&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20241230&end=20241230",
}


KLINE_NOTES = {
    "海能达": "2024-09-25：收盘涨停，换手28.10%，成交额20.61亿；5板分歧换手回封，满足换手>7%。",
    "双成药业": "2024-09-18：4板一字，换手0.62%，成交额0.19亿；买不到，排除。",
    "大千生态": "2024-11-08、11-11：4/5板均一字或准一字，换手0.47%/3.90%，排除。",
    "日出东方": "11月中旬多为N天M板与高位修复，不是连续4/5板标准买点；11-15虽涨停换手17.76%，但买点已不是模型定义的4/5板。",
    "一鸣食品": "2024-11-29：4板涨停，换手8.09%，但当日高位日出东方地天修复，旧高标未死，不能开新龙买点。",
    "粤桂股份": "2024-11-19：高换手40.85%且成交额25.66亿，但前后多日一字，高位链条不顺，不按标准4/5板新龙确认。",
    "益民集团": "2024-12-17：5板涨停，换手19.87%，成交额13.42亿；友阿股份同高一字被排除后，益民是可交易5板。",
    "友阿股份": "2024-12-17：5板一字，换手0.33%，成交额0.25亿；排除。",
    "实益达": "2024-12-25：5板涨停，换手29.02%，成交额12.86亿；满足换手>7%，题材主口径按微信小店 / 智能终端，AI眼镜与零售电商为背景助攻，不再简单归为大消费。",
    "中百集团": "2024-12-30：零售消费旧线补涨，4板涨停，换手33.01%，成交额25.34亿；益民集团后的零售消费链仍在反复，实益达已负反馈，不作新龙。",
    "东百集团": "2024-12-30：零售消费旧线补涨，4板涨停，换手17.61%，成交额9.29亿；与中百同属益民集团后的零售消费修复，不作新龙。",
}


SPECIAL_MARKET = {
    "2024-09-13": {
        "phase": "旧周期结束 / 无龙观察",
        "current_core": "深圳华强二次跌停作为前置锚点；同花顺复盘显示国企改革、黄金、房地产活跃，保变电气10天7板但已偏高。",
        "themes": [
            ["国企改革", "保变电气10天7板", "同花顺当日复盘提到国企改革持续活跃", "旧周期结束后的高标延续，非新龙买点", "观察"],
            ["黄金 / 房地产", "板块活跃", "同花顺当日复盘列为主流方向", "题材轮动", "观察"],
        ],
        "high": "保变电气10天7板；深圳华强二次跌停",
        "loss": "深圳华强二次跌停，上一轮华为海思/消费电子龙头周期确认结束。",
    },
    "2024-09-25": {
        "phase": "新龙确认日",
        "current_core": "海能达5板分歧换手涨停；双成药业高位一字买不到，保变电气跌停，大唐电信、中交地产天地板。",
        "themes": [
            ["华为 / 专网通信 / 卫星导航", "海能达5板，常山北明等华为线活跃", "同花顺复盘主线偏大金融/传媒，但华为高标仍有辨识度", "深圳华强旧周期死亡后的新高标试错胜出", "强"],
            ["大金融 / 传媒", "天风证券、国海证券、华闻集团等涨停", "同花顺复盘列为涨幅居前", "指数共振背景", "强"],
        ],
        "high": "双成药业名义高标一字；海能达为排除一字后的可交易5板。",
        "loss": "保变电气跌停，大唐电信、中交地产天地板，高位分化明显。",
    },
    "2024-11-01": {
        "phase": "海能达负反馈 / 清仓",
        "current_core": "海能达跌停，成交额118.37亿，换手32.35%。",
        "themes": [["高位抱团", "海能达跌停", "东方财富日K核验", "本轮确认龙头负反馈", "弱"]],
        "high": "海能达跌停",
        "loss": "确认龙头跌停，周期进入清仓与观察。",
    },
    "2024-11-04": {
        "phase": "海能达死亡 / 无龙",
        "current_core": "海能达连续跌停，成交额110.94亿，换手36.87%。",
        "themes": [["高位抱团", "海能达连续跌停", "东方财富日K核验", "本轮确认龙头死亡", "弱"]],
        "high": "海能达连续跌停",
        "loss": "连续跌停，旧周期死亡，重新进入无龙观察。",
    },
    "2024-11-29": {
        "phase": "高标修复 / 不开新龙",
        "current_core": "日出东方地天修复；机器人、金融科技活跃；一鸣食品4板但不能越过高位修复锚点。",
        "themes": [
            ["机器人", "三丰智能、肇民科技、江苏雷利等十余股涨停", "同花顺复盘", "盘面主线", "强"],
            ["食品饮料 / 大消费", "一鸣食品4板，桂发祥/新世界等多为一字高标", "东方财富日K + 同花顺复盘", "高位修复背景下的补涨跟踪", "观察"],
        ],
        "high": "日出东方地天修复；一鸣食品4板。",
        "loss": "IP经济局部调整，日出东方早盘跌停后修复，不能直接判定高位死亡。",
    },
    "2024-12-17": {
        "phase": "新龙确认日 / 但情绪差",
        "current_core": "高位股集体重挫；益民集团5板分歧换手回封，友阿股份5板一字被排除。",
        "themes": [
            ["首发经济 / 零售", "益民集团5板、友阿股份5板一字、零售/消费仍有局部活跃", "同花顺复盘 + 东方财富日K", "高位大消费退潮里的逆势可交易高标", "中强"],
            ["足球 / 权重", "双象股份、粤传媒、共创草坪涨停；中兴通讯一度涨停", "同花顺复盘", "当天背景方向，不是龙空龙买点", "观察"],
        ],
        "high": "友阿股份名义同高一字；益民集团为可交易5板。",
        "loss": "大消费、AI应用、机器人等前期热点领跌，一鸣食品、建设工业、巨轮智能等跌停。",
    },
    "2024-12-19": {
        "phase": "益民集团负反馈 / 清仓",
        "current_core": "益民集团冲高后跌停，换手28.82%，成交额20.29亿。",
        "themes": [["首发经济 / 零售", "益民集团跌停", "东方财富日K核验", "确认龙头负反馈", "弱"]],
        "high": "益民集团跌停",
        "loss": "确认龙头跌停，按清仓处理。",
    },
    "2024-12-20": {
        "phase": "益民集团死亡 / 无龙",
        "current_core": "益民集团继续一字跌停，旧龙死亡。",
        "themes": [["首发经济 / 零售", "益民集团连续跌停", "东方财富日K核验", "旧龙死亡", "弱"]],
        "high": "益民集团继续跌停",
        "loss": "连续跌停，进入无龙等待。",
    },
    "2024-12-25": {
        "phase": "新龙确认日 / 低质量",
        "current_core": "实益达5板分歧换手涨停；同花顺当日未直接列出实益达，盘面同时有零售午后活跃和AI眼镜局部活跃。",
        "themes": [
            ["微信小店 / 智能终端", "实益达5板", "东方财富日K + 同花顺复盘零售、AI眼镜活跃；主源未直接列实益达，题材需人工归因", "益民集团死亡后的新试错胜出；与首发经济/零售不是完全同一主线，仅有电商消费映射", "中"],
            ["零售", "中百集团地天，百大集团、东百集团、友好集团涨停", "同花顺复盘", "板块助攻", "中强"],
            ["AI眼镜", "国星光电、创维数字、雷柏科技涨停", "同花顺复盘", "分支助攻", "中"],
        ],
        "high": "实益达5板可交易；其他高标以跟踪为主。",
        "loss": "全市场4400只个股飘绿，微盘股与高位情绪仍弱，买点质量低于强共振周期。",
    },
    "2024-12-27": {
        "phase": "实益达负反馈 / 清仓",
        "current_core": "实益达跌停，换手57.18%，成交额26.24亿，爆量失控。",
        "themes": [["微信小店 / 智能终端", "实益达跌停", "东方财富日K核验", "确认龙头负反馈", "弱"]],
        "high": "实益达跌停",
        "loss": "5板买点后的第2个交易日负反馈，按清仓处理。",
    },
    "2024-12-30": {
        "phase": "无龙补涨 / 不开新龙",
        "current_core": "中百集团、东百集团等零售补涨强，但属于益民集团后的零售消费旧线反复；实益达刚负反馈，仍不按新龙处理。",
        "themes": [
            ["零售 / 大消费", "中百集团、东百集团涨停", "东方财富日K + 同花顺复盘", "益民集团后的零售消费旧线补涨，不作新龙", "观察"],
        ],
        "high": "中百集团、东百集团4板跟踪",
        "loss": "实益达负反馈叠加益民集团后的零售消费旧线反复，高位补涨容易坑人。",
    },
    "2024-12-31": {
        "phase": "无龙补涨 / 年末退潮",
        "current_core": "市场普跌，零售补涨继续但不按新龙处理。",
        "themes": [["零售 / 大消费", "中百集团、东百集团延续", "同花顺复盘 + 东方财富日K", "同周期后段补涨", "观察"]],
        "high": "零售补涨高标",
        "loss": "全市场超4600只下跌，年末风险偏好回落。",
    },
}


CANDIDATES = {
    "2024-09-18": [
        {
            "stock": "双成药业",
            "board": "4板",
            "status": "一字排除",
            "reason": KLINE_NOTES["双成药业"],
            "verdict": "放弃",
            "class": "reject",
        }
    ],
    "2024-09-25": [
        {
            "stock": "海能达",
            "board": "5板",
            "status": "标准买点",
            "reason": KLINE_NOTES["海能达"] + " 双成药业一字高标排除后，海能达是可交易最高板。",
            "verdict": "标准买点",
            "class": "buy",
        }
    ],
    "2024-11-11": [
        {
            "stock": "大千生态",
            "board": "5板",
            "status": "一字排除",
            "reason": KLINE_NOTES["大千生态"],
            "verdict": "放弃",
            "class": "reject",
        }
    ],
    "2024-11-15": [
        {
            "stock": "粤桂股份",
            "board": "4/5板区间",
            "status": "一字链条过重",
            "reason": "11月14日一字，11月15日虽有换手但高位日出东方仍强修复；不按新龙确认。",
            "verdict": "仅观察",
            "class": "observe",
        }
    ],
    "2024-11-19": [
        {
            "stock": "粤桂股份",
            "board": "高位",
            "status": "非标准4/5板",
            "reason": KLINE_NOTES["粤桂股份"],
            "verdict": "放弃",
            "class": "reject",
        }
    ],
    "2024-11-29": [
        {
            "stock": "一鸣食品",
            "board": "4板",
            "status": "旧高标未死",
            "reason": KLINE_NOTES["一鸣食品"],
            "verdict": "仅观察",
            "class": "observe",
        }
    ],
    "2024-12-17": [
        {
            "stock": "益民集团",
            "board": "5板",
            "status": "标准买点",
            "reason": KLINE_NOTES["益民集团"] + " 前期大消费/AI应用/机器人高标批量跌停，旧高位负反馈明确。",
            "verdict": "标准买点",
            "class": "buy",
        },
        {
            "stock": "友阿股份",
            "board": "5板",
            "status": "一字排除",
            "reason": KLINE_NOTES["友阿股份"],
            "verdict": "放弃",
            "class": "reject",
        },
    ],
    "2024-12-25": [
        {
            "stock": "实益达",
            "board": "5板",
            "status": "标准买点",
            "reason": KLINE_NOTES["实益达"] + " 益民集团已连续负反馈，允许重新看4/5板；但同花顺主源未直接把实益达列为当日主线核心，题材强度和归因质量标注为中低。",
            "verdict": "标准买点",
            "class": "buy",
        }
    ],
    "2024-12-30": [
        {
            "stock": "中百集团",
            "board": "4板",
            "status": "后段补涨",
            "reason": KLINE_NOTES["中百集团"],
            "verdict": "仅观察",
            "class": "observe",
        },
        {
            "stock": "东百集团",
            "board": "4板",
            "status": "后段补涨",
            "reason": KLINE_NOTES["东百集团"],
            "verdict": "仅观察",
            "class": "observe",
        },
    ],
}


STANDARD_BUY_META = {
    "2024-09-25": {
        "leader": "海能达",
        "theme": "华为 / 专网通信 / 卫星导航",
        "state": "新龙确认",
        "action": "建仓",
        "trigger": "次日看6板确认；若不能弱转强或高位失控，减仓。",
    },
    "2024-12-17": {
        "leader": "益民集团",
        "theme": "首发经济 / 零售",
        "state": "新龙确认",
        "action": "建仓",
        "trigger": "次日看6板确认；若高位大消费继续A杀且益民不能封住，清仓。",
    },
    "2024-12-25": {
        "leader": "实益达",
        "theme": "微信小店 / 智能终端",
        "state": "新龙确认",
        "action": "建仓",
        "trigger": "次日看6板确认；质量偏低，不加码补涨，出现跌停即清仓。",
    },
}


def parse_date(s):
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)


def next_trading_day(current):
    idx = DATES.index(current)
    for nxt in DATES[idx + 1 :]:
        if nxt not in HOLIDAYS:
            return nxt
    return ""


def ths_url(d):
    return f"https://stock.10jqka.com.cn/fupan/{d.replace('-', '')}.shtml"


def source_rows_for(d, candidates):
    if d in HOLIDAYS:
        return [{"name": HOLIDAYS[d], "url": ""}]
    rows = [{"name": f"同花顺复盘：{d}", "url": ths_url(d)}]
    for c in candidates:
        url = EASTMONEY_URLS.get(c["stock"])
        if url:
            rows.append({"name": f"东方财富日K：{c['stock']} {d}", "url": url})
    return rows


def badge(text, cls):
    return f'<span class="badge {cls}">{html.escape(text)}</span>'


def td(value):
    return f"<td>{value}</td>"


def tr(values):
    return "<tr>" + "".join(td(v) for v in values) + "</tr>"


def table(headers, rows, empty=None):
    if not rows and empty:
        rows = [empty]
    head = "<thead><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in headers) + "</tr></thead>"
    body = "<tbody>" + "".join(tr(row) for row in rows) + "</tbody>"
    return f'<div class="table-wrap"><table>{head}{body}</table></div>'


def default_market(d):
    return {
        "phase": "无龙观察",
        "current_core": "未出现经过完整4/5板核验的标准新龙；只记录同花顺当日主线与高标风险。",
        "themes": [["当日活跃题材", "以同花顺复盘为准", "主源已核或待复核", "无确认龙头时只观察", "观察"]],
        "high": "待同花顺/开盘啦逐项复核",
        "loss": "无确认龙头时默认空仓，等待4/5板可交易回封。",
    }


def leader_state_for(d):
    if d in HOLIDAYS:
        return {
            "leader": "休市",
            "theme": "休市",
            "state": "休市",
            "action": "不交易",
            "search": "不适用",
            "prior": "上一交易日锚点延续",
            "prior_theme": "上一交易日锚点延续",
            "trigger": "下一交易日再按龙头状态复盘。",
        }

    if d < "2024-09-25":
        return {
            "leader": "无有效龙头",
            "theme": "无",
            "state": "无龙",
            "action": "空仓观察",
            "search": "允许",
            "prior": "深圳华强",
            "prior_theme": "华为海思 / 消费电子",
            "trigger": "只等排除一字后的4/5板分歧换手回封。",
        }

    if d == "2024-09-25":
        meta = STANDARD_BUY_META[d]
        return {
            "leader": meta["leader"],
            "theme": meta["theme"],
            "state": meta["state"],
            "action": meta["action"],
            "search": "收盘后不允许",
            "prior": "深圳华强",
            "prior_theme": "华为海思 / 消费电子",
            "trigger": meta["trigger"],
        }

    if "2024-09-26" <= d <= "2024-10-09":
        state = "龙头主升" if d not in {"2024-09-27"} else "龙头明显分歧"
        action = "持仓 / 加仓" if d not in {"2024-09-27"} else "减仓观察"
        return {
            "leader": "海能达",
            "theme": "华为 / 专网通信 / 卫星导航",
            "state": state,
            "action": action,
            "search": "不允许",
            "prior": "深圳华强",
            "prior_theme": "华为海思 / 消费电子",
            "trigger": "只看海能达是否继续修复或出现跌停负反馈。",
        }

    if d in {"2024-10-10", "2024-10-14", "2024-10-17"}:
        return {
            "leader": "海能达",
            "theme": "华为 / 专网通信 / 卫星导航",
            "state": "龙头明显分歧",
            "action": "减仓",
            "search": "不允许",
            "prior": "深圳华强",
            "prior_theme": "华为海思 / 消费电子",
            "trigger": "若次日修复，继续按龙头处理；若跌停或连续杀，清仓。",
        }

    if "2024-10-11" <= d <= "2024-10-31":
        return {
            "leader": "海能达",
            "theme": "华为 / 专网通信 / 卫星导航",
            "state": "龙头主升" if d != "2024-10-24" else "龙头高位震荡",
            "action": "持仓 / 减仓跟随",
            "search": "不允许",
            "prior": "深圳华强",
            "prior_theme": "华为海思 / 消费电子",
            "trigger": "海能达未死，不看普通新方向。",
        }

    if d in {"2024-11-01", "2024-11-04"}:
        return {
            "leader": "海能达",
            "theme": "华为 / 专网通信 / 卫星导航",
            "state": "龙头负反馈" if d == "2024-11-01" else "龙头死亡",
            "action": "清仓",
            "search": "次日才重新允许",
            "prior": "海能达",
            "prior_theme": "华为 / 专网通信 / 卫星导航",
            "trigger": "等待旧龙停止A杀后，再看新的4/5板。",
        }

    if "2024-11-05" <= d < "2024-12-17":
        return {
            "leader": "无有效龙头",
            "theme": "无",
            "state": "无龙",
            "action": "空仓观察",
            "search": "允许",
            "prior": "海能达",
            "prior_theme": "华为 / 专网通信 / 卫星导航",
            "trigger": "只看4/5板可交易最高板；高位N天M板、一字高标和旧高标修复不算标准买点。",
        }

    if d == "2024-12-17":
        meta = STANDARD_BUY_META[d]
        return {
            "leader": meta["leader"],
            "theme": meta["theme"],
            "state": meta["state"],
            "action": meta["action"],
            "search": "收盘后不允许",
            "prior": "海能达",
            "prior_theme": "华为 / 专网通信 / 卫星导航",
            "trigger": meta["trigger"],
        }

    if d == "2024-12-18":
        return {
            "leader": "益民集团",
            "theme": "首发经济 / 零售",
            "state": "龙头主升",
            "action": "持仓",
            "search": "不允许",
            "prior": "海能达",
            "prior_theme": "华为 / 专网通信 / 卫星导航",
            "trigger": "只看益民集团6板后的封单和高位大消费修复。",
        }

    if d == "2024-12-19":
        return {
            "leader": "益民集团",
            "theme": "首发经济 / 零售",
            "state": "龙头负反馈",
            "action": "清仓",
            "search": "次日才重新允许",
            "prior": "益民集团",
            "prior_theme": "首发经济 / 零售",
            "trigger": "等益民集团停止跌停负反馈，再看新4/5板。",
        }

    if "2024-12-20" <= d < "2024-12-25":
        return {
            "leader": "无有效龙头",
            "theme": "无",
            "state": "无龙",
            "action": "空仓观察",
            "search": "允许",
            "prior": "益民集团",
            "prior_theme": "首发经济 / 零售",
            "trigger": "只看新4/5板分歧换手回封；同消费后排谨慎。",
        }

    if d == "2024-12-25":
        meta = STANDARD_BUY_META[d]
        return {
            "leader": meta["leader"],
            "theme": meta["theme"],
            "state": meta["state"],
            "action": meta["action"],
            "search": "收盘后不允许",
            "prior": "益民集团",
            "prior_theme": "首发经济 / 零售",
            "trigger": meta["trigger"],
        }

    if d == "2024-12-26":
        return {
            "leader": "实益达",
            "theme": "微信小店 / 智能终端",
            "state": "龙头主升",
            "action": "持仓",
            "search": "不允许",
            "prior": "益民集团",
            "prior_theme": "首发经济 / 零售",
            "trigger": "只看实益达是否继续封住；不扩展到普通补涨。",
        }

    if d == "2024-12-27":
        return {
            "leader": "实益达",
            "theme": "微信小店 / 智能终端",
            "state": "龙头负反馈",
            "action": "清仓",
            "search": "次日才重新允许",
            "prior": "实益达",
            "prior_theme": "微信小店 / 智能终端",
            "trigger": "跌停负反馈后，不再接旧零售消费线后段补涨。",
        }

    return {
        "leader": "无有效龙头",
        "theme": "无",
        "state": "无龙",
        "action": "空仓观察",
        "search": "允许但严格",
        "prior": "实益达",
        "prior_theme": "微信小店 / 智能终端",
        "trigger": "等待旧线负反馈释放后，再看独立新题材4/5板；消费补涨不作新龙。",
    }


def candidate_rows(candidates):
    rows = []
    if not candidates:
        return [[
            "当日无符合4/5板候选",
            "-",
            "无标准买点",
            "2/3板只作盘面跟踪；没有核验过的4/5板不写机会。",
            badge("仅观察", "observe"),
        ]]
    for c in candidates:
        rows.append(
            [
                html.escape(c["stock"]),
                html.escape(c["board"]),
                html.escape(c["status"]),
                html.escape(c["reason"]),
                badge(c["verdict"], c["class"]),
            ]
        )
    return rows


def model_verdicts(candidates):
    out = []
    for c in candidates:
        verdict = "standard buy" if c["verdict"] == "标准买点" else ("reject" if c["verdict"] == "放弃" else "observe")
        out.append(
            {
                "stock": c["stock"],
                "board": c["board"],
                "verdict": verdict,
                "visible_verdict": c["verdict"],
                "reason": c["reason"],
            }
        )
    return out


def render_html(d, previous_reports):
    state = leader_state_for(d)
    market = SPECIAL_MARKET.get(d, default_market(d))
    candidates = CANDIDATES.get(d, [])
    sources = source_rows_for(d, candidates)
    is_holiday = d in HOLIDAYS
    next_day = next_trading_day(d)

    theme_rows = []
    for theme, core, evidence, relation, strength in market["themes"]:
        cls = "buy" if strength == "强" else ("observe" if strength in {"中强", "中", "观察"} else "reject")
        theme_rows.append(
            [
                html.escape(theme),
                html.escape(core),
                html.escape(evidence),
                html.escape(relation),
                badge(strength, cls),
            ]
        )

    ladder_rows = [
        [
            html.escape(market["high"]),
            html.escape(state["theme"]),
            "龙头锚点" if state["leader"] not in {"无有效龙头", "休市"} else "盘面跟踪",
            html.escape("只按4/5板候选表确认买点"),
            badge("观察" if not any(c["verdict"] == "标准买点" for c in candidates) else "已确认", "observe" if not any(c["verdict"] == "标准买点" for c in candidates) else "buy"),
        ]
    ]

    recent_rows = []
    for prev in previous_reports[-5:]:
        recent_rows.append(
            [
                html.escape(prev["review_date"]),
                html.escape(prev["current_leader"]),
                html.escape(prev["leader_state"]),
                html.escape(prev["position_action"]),
                html.escape(prev["next_trigger"]),
            ]
        )
    if not recent_rows:
        recent_rows = [["无", "无", "无", "无", "本轮归档起点"]]

    if is_holiday:
        plan_blocks = [
            ("休市处理", HOLIDAYS[d]),
            ("下一交易日", "沿用上一交易日龙头锚点重新复盘。"),
            ("纪律", "休市不生成交易计划。"),
        ]
    elif state["search"] == "不允许" or state["search"] == "收盘后不允许":
        plan_blocks = [
            ("继续/修复", f"{state['leader']}继续强势或修复，按{state['action']}处理。"),
            ("分歧", f"{state['leader']}爆量、长上影或弱封，减仓，不看普通后排。"),
            ("负反馈", f"{state['leader']}跌停/大阴/连续杀，清仓，下一交易日再看是否进入无龙。"),
        ]
    else:
        plan_blocks = [
            ("旧龙负反馈", f"上一轮锚点：{state['prior']} / {state['prior_theme']}。若负反馈延续，保持空仓。"),
            ("候选条件", "只看排除一字后的4/5板分歧换手回封，换手>7%或成交额>25亿，且有板块助攻。"),
            ("放弃条件", "2/3板、连续一字、6板首次开口、旧周期后排补涨、板块无助攻，全部不买。"),
        ]

    plan_html = "".join(
        f'<div class="plan-block"><strong>{html.escape(title)}</strong><p>{html.escape(text)}</p></div>'
        for title, text in plan_blocks
    )

    data = {
        "review_date": d,
        "data_cutoff": d,
        "next_trading_day": next_day,
        "current_leader": state["leader"],
        "current_leader_theme": state["theme"],
        "leader_state": state["state"],
        "position_action": state["action"],
        "new_leader_search_allowed": state["search"],
        "next_trigger": state["trigger"],
        "market_phase": market["phase"],
        "cycle_stage": market["phase"],
        "old_leader_state": f"{state['prior']} / {state['prior_theme']}",
        "loss_effect": {"summary": market["loss"]},
        "new_direction": {"summary": "只有在当前龙头死亡或无有效龙头时，才评估新方向。"},
        "operation_plan": {"phase": market["phase"], "position": state["action"], "action": state["trigger"]},
        "risk_control": {
            "single_trade_loss": "打板失败或次日不能弱转强优先退出",
            "daily_loss": "当日出现龙头跌停负反馈时停止开仓",
            "continuous_trials": "连续两次试错失败后暂停",
            "position_cap": "无龙空仓；标准买点小中仓；主升才考虑加仓",
            "sell_conditions": "跌停、大阴、断板后继续杀、板块助攻断层",
        },
        "high_level_sentiment": {
            "nominal_highest_board": market["high"],
            "tradable_highest_board": "以4/5板候选检查表为准",
            "previous_high_board_performance": market["loss"],
            "broken_board_feedback": market["loss"],
            "high_level_limit_down_count": "同花顺复盘与东方财富个股核验",
            "high_level_broken_board_count": "同花顺复盘与东方财富个股核验",
            "promotion_rate": "批量历史复盘不做精确百分比，按锚点状态执行",
        },
        "prior_confirmed_leader": state["prior"],
        "prior_leader_theme": state["prior_theme"],
        "intermediate_trial_chain": "无龙时只记录试错；不把一字高标和N天M板自动升格为龙头。",
        "old_leader_chain": f"{state['prior']} / {state['prior_theme']} -> {state['state']}",
        "current_core": market["current_core"],
        "tradable_high_board": "见4/5板候选检查",
        "next_opportunity": "有标准买点" if any(c["verdict"] == "标准买点" for c in candidates) else "无标准买点",
        "hard_no_trade": "不顶一字，不买2/3板，不追6板首次开口；旧龙未死不找新龙。",
        "model_verdicts": model_verdicts(candidates),
        "sources": sources,
        "source_verification": {
            "sector_theme": "同花顺复盘作为板块/情绪主源；候选题材由人工按同花顺/开盘啦优先级复核。",
            "individual_price_action": "4/5板候选使用东方财富日K核验开收高低、换手、成交额；脚本只负责归档渲染。",
            "no_future_data": f"本页仅使用{d}及之前可见数据。",
        },
        "generated_by_skill": {
            "name": "stock-cycle-review",
            "skill_dir": str(SKILL_DIR),
            "workflow": "先定龙头 -> 龙头状态 -> 仓位动作 -> 是否允许找新龙 -> 允许才看4/5板候选 -> 风控",
        },
    }

    source_items = []
    for src in sources:
        if src["url"]:
            source_items.append(f'<li><a href="{html.escape(src["url"])}">{html.escape(src["name"])}</a></li>')
        else:
            source_items.append(f"<li>{html.escape(src['name'])}</li>")

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>A股短线周期复盘 - {html.escape(d)}</title>
  <style>
    :root {{--bg:#f6f7f9;--panel:#fff;--text:#1f2937;--muted:#6b7280;--line:#d9dee7;--green:#13795b;--orange:#b26a00;--red:#b42318;--blue:#1d4ed8;}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.55}}
    .page{{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 0 42px}} header{{display:grid;gap:10px;margin-bottom:16px}}
    h1{{margin:0;font-size:clamp(24px,4vw,34px);letter-spacing:0}} h2{{margin:0 0 12px;font-size:18px;letter-spacing:0}} p{{margin:0}}
    .note{{color:var(--muted);font-size:14px}} .risk{{border-left:4px solid var(--orange);background:#fff8ec;padding:10px 12px;color:#7a4b00}}
    .grid{{display:grid;gap:12px}} .status-grid{{grid-template-columns:repeat(6,minmax(0,1fr));margin:16px 0}}
    .metric,section{{background:var(--panel);border:1px solid var(--line);border-radius:8px}} .metric{{min-height:96px;padding:12px}}
    .metric .label{{color:var(--muted);font-size:12px;margin-bottom:6px}} .metric .value{{font-size:17px;font-weight:700}}
    section{{padding:16px;margin-bottom:14px}} .timeline,.plan{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}} .plan{{grid-template-columns:repeat(3,1fr)}}
    .step,.plan-block{{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fbfcfe}} .title,.plan-block strong{{display:block;font-weight:700;margin-bottom:6px}}
    table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{border-bottom:1px solid var(--line);padding:10px 8px;text-align:left;vertical-align:top}} th{{color:var(--muted);font-weight:600;background:#f9fafb}}
    .badge{{display:inline-flex;align-items:center;min-height:24px;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}}
    .buy{{background:#e8f5ef;color:var(--green)}} .observe{{background:#fff4db;color:var(--orange)}} .reject{{background:#fdebea;color:var(--red)}} .context{{background:#eaf1ff;color:var(--blue)}}
    ul,ol{{margin:0;padding-left:20px}} a{{color:var(--blue)}} @media(max-width:860px){{.status-grid,.timeline,.plan{{grid-template-columns:1fr}}.table-wrap{{overflow-x:auto}}table{{min-width:760px}}}}
  </style>
</head>
<body>
<main class="page">
<header>
  <h1>A股短线周期复盘 - {html.escape(d)}</h1>
  <p class="note">历史实盘模拟：只使用 {html.escape(d)} 当天及之前可见资料。输出为 stock-cycle-review 技能框架，不构成投资建议。</p>
  <p class="note">流程：先定龙头，再定龙头状态和仓位动作；只有当前龙头死亡或无有效龙头，才允许筛4/5板新龙候选。</p>
  <p class="risk">硬纪律：旧龙未死不找新龙；不顶连续一字；2/3板只跟踪；6板以后首次开口不是标准买点。</p>
</header>

<section class="grid status-grid">
  <div class="metric"><div class="label">当前龙头</div><div class="value">{html.escape(state['leader'])}<br><span class="note">{html.escape(state['theme'])}</span></div></div>
  <div class="metric"><div class="label">龙头状态</div><div class="value">{html.escape(state['state'])}</div></div>
  <div class="metric"><div class="label">当前动作</div><div class="value">{html.escape(state['action'])}</div></div>
  <div class="metric"><div class="label">是否找新龙</div><div class="value">{html.escape(state['search'])}</div></div>
  <div class="metric"><div class="label">上一轮龙头 / 板块</div><div class="value">{html.escape(state['prior'])}<br><span class="note">{html.escape(state['prior_theme'])}</span></div></div>
  <div class="metric"><div class="label">下一触发</div><div class="value">{html.escape(state['trigger'])}</div></div>
</section>

<section><h2>龙头锚点</h2>{table(['当前龙头','所属题材','状态','动作','是否允许新龙筛选'], [[html.escape(state['leader']), html.escape(state['theme']), html.escape(state['state']), html.escape(state['action']), html.escape(state['search'])]])}</section>
<section><h2>高位情绪快照</h2>{table(['名义最高/核心','可交易最高板','旧龙/前高标表现','亏钱效应'], [[html.escape(market['high']), '见4/5板候选检查', html.escape(state['prior'] + ' / ' + state['prior_theme']), html.escape(market['loss'])]])}</section>
<section><h2>周期链路</h2><div class="timeline">
  <div class="step"><div class="title">上一轮龙头</div><p>{html.escape(state['prior'])} / {html.escape(state['prior_theme'])}</p></div>
  <div class="step"><div class="title">当前锚点</div><p>{html.escape(state['leader'])} / {html.escape(state['state'])}</p></div>
  <div class="step"><div class="title">是否寻找新龙</div><p>{html.escape(state['search'])}</p></div>
  <div class="step"><div class="title">下一触发</div><p>{html.escape(state['trigger'])}</p></div>
</div></section>
<section><h2>板块强度</h2>{table(['板块/方向','高标核心','证据','与旧周期关系','强度'], theme_rows)}</section>
<section><h2>连板/活跃梯队</h2>{table(['核心/高标','题材','角色','交易性','模型结论'], ladder_rows)}</section>
<section><h2>4/5板候选检查</h2>{table(['股票','板数','买点状态','原因','模型结论'], candidate_rows(candidates))}</section>
<section><h2>次日龙头预案</h2><div class="plan">{plan_html}</div></section>
<section><h2>最近归档对比</h2>{table(['日期','龙头','状态','动作','上一触发'], recent_rows)}</section>
<section><h2>风控纪律</h2>{table(['项目','规则'], [
  ['仓位上限', '无龙空仓；标准买点小中仓；龙头主升才考虑加仓或重仓。'],
  ['单笔最大亏损', '打板失败、次日不能弱转强或龙头跌停，优先退出。'],
  ['连续试错次数', '连续两次失败后暂停，等待下一次清晰4/5板。'],
  ['卖出条件', '跌停、大阴、断板后继续杀、板块助攻断层。'],
])}</section>
<section><h2>最终五句话</h2><ol>
  <li>当前龙头：{html.escape(state['leader'])}，{html.escape(state['theme'])}。</li>
  <li>龙头状态：{html.escape(state['state'])}。</li>
  <li>当前动作：{html.escape(state['action'])}。</li>
  <li>是否允许寻找新龙：{html.escape(state['search'])}。</li>
  <li>下一触发：{html.escape(state['trigger'])}</li>
</ol></section>
<section><h2>数据源核验</h2><ul>{''.join(source_items)}</ul><p class="note">同花顺/开盘啦优先用于板块与梯队；东方财富用于候选个股日K、换手、成交额和可交易性。脚本只负责归档渲染，不作为买点证据。</p></section>
<script type="application/json" id="stock-cycle-review-data">{html.escape(json.dumps(data, ensure_ascii=False, indent=2))}</script>
</main>
</body>
</html>
"""
    return page, data


def render_index(reports):
    rows = []
    for report in reports:
        verdicts = [v for v in report.get("model_verdicts", []) if v.get("verdict") == "standard buy"]
        buy_text = "、".join(v["stock"] for v in verdicts) if verdicts else "无"
        rows.append(
            [
                f'<a href="{html.escape(report["review_date"])}.html">{html.escape(report["review_date"])}</a>',
                html.escape(report["current_leader"]),
                html.escape(report["leader_state"]),
                html.escape(report["position_action"]),
                html.escape(buy_text),
                html.escape(report["next_trigger"]),
            ]
        )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>A股短线周期复盘归档</title>
  <style>
    body{{margin:0;background:#f6f7f9;color:#1f2937;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.55}}
    main{{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 0 42px}} h1{{margin:0 0 6px;font-size:32px}} p{{margin:0 0 16px;color:#6b7280}}
    section{{background:white;border:1px solid #d9dee7;border-radius:8px;padding:16px}} table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{border-bottom:1px solid #d9dee7;padding:10px 8px;text-align:left;vertical-align:top}} th{{background:#f9fafb;color:#6b7280}} a{{color:#1d4ed8}}
    @media(max-width:860px){{.table-wrap{{overflow-x:auto}}table{{min-width:820px}}}}
  </style>
</head>
<body><main>
  <h1>A股短线周期复盘归档</h1>
  <p>使用 stock-cycle-review 技能生成。历史页面禁止未来数据；标准买点只统计4/5板可交易回封。</p>
  <section>{table(['日期','当前龙头','状态','动作','标准买点','下一触发'], rows)}</section>
</main></body></html>"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    reports = []
    for d in DATES:
        page, data = render_html(d, reports)
        (OUT_DIR / f"{d}.html").write_text(page, encoding="utf-8")
        reports.append(data)
    render_index(reports)
    print(json.dumps({"generated": len(reports), "standard_buys": [
        {"date": r["review_date"], "stock": v["stock"], "reason": v["reason"]}
        for r in reports for v in r.get("model_verdicts", []) if v.get("verdict") == "standard buy"
    ]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
