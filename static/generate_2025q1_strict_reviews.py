import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"
SKILL_DIR = Path(r"C:\Users\wkc\.codex\plugins\cache\personal\stock-cycle-review\0.1.0+codex.20260602143920\skills\stock-cycle-review")


DATES = [
    "2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07", "2025-01-08",
    "2025-01-09", "2025-01-10", "2025-01-13", "2025-01-14", "2025-01-15",
    "2025-01-16", "2025-01-17", "2025-01-20", "2025-01-21", "2025-01-22",
    "2025-01-23", "2025-01-24", "2025-01-27",
    "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31",
    "2025-02-03", "2025-02-04", "2025-02-05", "2025-02-06", "2025-02-07",
    "2025-02-10", "2025-02-11", "2025-02-12", "2025-02-13", "2025-02-14",
    "2025-02-17", "2025-02-18", "2025-02-19", "2025-02-20", "2025-02-21",
    "2025-02-24", "2025-02-25", "2025-02-26", "2025-02-27", "2025-02-28",
    "2025-03-03", "2025-03-04", "2025-03-05", "2025-03-06", "2025-03-07",
    "2025-03-10", "2025-03-11", "2025-03-12", "2025-03-13", "2025-03-14",
    "2025-03-17", "2025-03-18", "2025-03-19", "2025-03-20", "2025-03-21",
    "2025-03-24", "2025-03-25", "2025-03-26", "2025-03-27", "2025-03-28",
    "2025-03-31",
]

HOLIDAYS = {
    "2025-01-28": "春节休市",
    "2025-01-29": "春节休市",
    "2025-01-30": "春节休市",
    "2025-01-31": "春节休市",
    "2025-02-03": "春节休市",
    "2025-02-04": "春节休市",
}


def ths_url(d):
    return f"https://stock.10jqka.com.cn/fupan/{d.replace('-', '')}.shtml"


def eastmoney_url(secid, beg, end=None):
    end = end or beg
    return (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get?"
        f"secid={secid}&fields1=f1,f2,f3,f4,f5,f6"
        "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        f"&klt=101&fqt=1&beg={beg.replace('-', '')}&end={end.replace('-', '')}"
    )


STOCK_SECIDS = {
    "中百集团": "0.000759",
    "东百集团": "1.600693",
    "顺钠股份": "0.000533",
    "海得控制": "0.002184",
    "美邦股份": "1.605033",
    "兴业股份": "1.603928",
    "华联股份": "0.000882",
    "冀东装备": "0.000856",
    "冀凯股份": "0.002691",
    "新炬网络": "1.605398",
    "杭钢股份": "1.600126",
    "庄园牧场": "0.002910",
    "圣阳股份": "0.002580",
    "华丰股份": "1.605100",
    "大位科技": "1.600589",
    "信隆健康": "0.002105",
    "大连重工": "0.002204",
    "雪龙集团": "1.603949",
}


SPECIAL = {
    "2025-01-02": {
        "phase": "无龙试错",
        "core": "零售、食品逆市；中百集团、东百集团已到6板，属于需要重新评估的消费高标，但4/5板买点已在上一年末发生。顺钠股份5板可交易，但不是排除一字后的市场可交易最高板。",
        "loss": "指数大跌，封板效率较差；旧零售链仍占高位，不能因为实益达题材修正就把6板消费高标倒推为当天买点。",
        "themes": [
            ["零售 / 食品", "中百集团、东百集团6板", "同花顺主流看点：零售、食品；东方财富核验二者均非一字", "与实益达不是同一主线；更接近益民集团后的零售消费二阶段高标，买点窗口已过", "观察"],
            ["数据中心电源 / 算力", "顺钠股份5板，电光科技高位活跃", "财联社涨停分析 + 东方财富核验顺钠5板换手29.26%", "新方向试错，但被更高旧线压制", "观察"],
        ],
        "candidates": [
            ["中百集团", "6板", "放弃", "消费高标必须重新列入观察，但复盘日已是6板，4/5板标准买点已过，不能追6板。", "reject"],
            ["东百集团", "6板", "放弃", "同属零售消费高标，不能因实益达题材修正而把6板改造成1月2日新买点。", "reject"],
            ["顺钠股份", "5板", "仅观察", "换手29.26%、成交额12.98亿；但中百/东百6板可交易，顺钠不是市场可交易最高板。", "observe"],
        ],
    },
    "2025-01-03": {
        "phase": "无龙试错",
        "core": "消费零售大面积回调，中百集团跌停；顺钠股份已到6板，东百集团继续高位。",
        "loss": "全市场超4700股下跌，消费和AI应用均弱；顺钠5板买点已过，不追6板。",
        "themes": [["贵金属", "黄金股逆市", "同花顺主流看点：贵金属", "避险轮动，不是连板龙", "观察"]],
        "candidates": [["顺钠股份", "6板", "放弃", "2025-01-02的5板窗口已过；6板不是标准新开买点。", "reject"]],
    },
    "2025-01-06": {
        "phase": "无龙试错 / 高位负反馈",
        "core": "零售股批量跌停；数据中心电源活跃，但顺钠股份高位爆量失败，电光科技地天，情绪不稳定。",
        "loss": "东百、中百等旧消费线跌停；顺钠高位爆量转弱。",
        "themes": [
            ["流感 / 医药", "新华制药、以岭药业等十余股涨停", "同花顺主流看点", "新低位题材", "观察"],
            ["数据中心电源", "海得控制、华塑科技、中恒电气等", "同花顺复盘提及", "顺钠失败后的同线延伸", "观察"],
        ],
        "candidates": [["海得控制", "4/5板区间", "放弃", "同线顺钠当天高位失败，且海得换手超过40%高风险；按同题材试错处理。", "reject"]],
    },
    "2025-01-22": {
        "phase": "无龙试错",
        "core": "AI硬件端、数据中心概念活跃；电光科技6天5板，华脉科技4连板。",
        "loss": "小红书、地产等前期方向调整；高位仍未形成清晰新龙。",
        "themes": [
            ["AI硬件 / 数据中心", "电光科技6天5板、华脉科技4连板", "同花顺复盘", "新题材试错，但电光不是标准连续4/5板窗口", "观察"],
        ],
        "candidates": [["华脉科技", "4板", "仅观察", "AI硬件方向有板块支持，但次日高位股跳水风险未释放；个股可交易性与封板质量需东方财富进一步确认，未给标准买点。", "observe"]],
    },
    "2025-01-23": {
        "phase": "无龙试错 / 高位跳水",
        "core": "大金融、AI应用活跃；部分高位股午后跳水，金奥博、瀛通通讯跌停，华脉科技天地板。",
        "loss": "高位股午后跳水，断板负反馈明显，先处理风险。",
        "themes": [
            ["AI应用", "引力传媒、龙韵股份涨停", "同花顺复盘", "低位轮动，不是4/5板新龙确认", "观察"],
            ["机器人 / 高位链", "金奥博、瀛通通讯跌停", "同花顺复盘", "旧高标负反馈，不开新仓", "弱"],
        ],
        "candidates": [["冀东装备", "4板附近", "仅观察", "同日主源重点是高位跳水，机器人高标金奥博、瀛通通讯跌停；冀东只能作试错观察，不能确认龙空龙买点。", "observe"]],
    },
    "2025-01-24": {
        "phase": "无龙试错",
        "core": "AI智能体全线爆发，新炬网络等涨停；机器人持续活跃，五洲新春、中大力德、晋拓股份等涨停。",
        "loss": "上一日高位跳水后仍处修复试错，不能直接重仓。",
        "themes": [
            ["AI智能体", "新炬网络等涨停", "同花顺复盘", "新方向首日强，但新炬尚不是4/5板可交易买点", "中强"],
            ["机器人", "五洲新春、中大力德、晋拓股份、美格智能、祥鑫科技涨停", "同花顺复盘", "高位跳水后的修复，仍按试错", "中"],
        ],
        "candidates": [
            ["冀东装备", "5板附近", "仅观察", "有高标辨识度，但同日AI智能体才是主源最强方向，且前一日机器人高标负反馈刚释放；不确认标准新龙。", "observe"],
            ["华联股份", "5板附近", "放弃", "零售/消费高标重新列入，但当日同花顺主线不是零售消费，缺少板块主源支持。", "reject"],
        ],
    },
    "2025-01-08": {
        "phase": "无龙试错",
        "core": "美邦股份进入高位，但市场仍处顺钠/海得失败后的试错链。",
        "loss": "前高标分歧未完全修复。",
        "themes": [["农药 / 化工", "美邦股份5板", "东方财富核验5板换手5.11%，金额1.32亿", "流动性不达标", "观察"]],
        "candidates": [["美邦股份", "5板", "放弃", "换手5.11%、成交额1.32亿，未满足换手>7%或成交额>25亿。", "reject"]],
    },
    "2025-01-16": {
        "phase": "无龙 / 高标退潮",
        "core": "美邦股份跌停，金奥博一字链条延续。",
        "loss": "美邦股份跌停，试错失败。",
        "themes": [["民爆 / 机器人", "金奥博高位", "东方财富核验前期多日一字", "一字高标，不是可交易买点", "观察"]],
        "candidates": [["金奥博", "高位", "放弃", "4/5板阶段一字，6板以后开口不转换成标准买点。", "reject"]],
    },
    "2025-01-23": {
        "phase": "无龙试错",
        "core": "冀东装备放量涨停，机器人/装备方向活跃。",
        "loss": "前期金奥博、美邦链条仍有负反馈；新高标多为试错。",
        "themes": [["机器人 / 装备", "冀东装备", "东方财富核验换手34.81%、成交额7.91亿", "偏机器人补涨试错", "观察"]],
        "candidates": [["冀东装备", "4板附近", "仅观察", "具备交易性，但板块上更像机器人补涨，前期高标负反馈未充分沉淀，不确认龙空龙标准龙。", "observe"]],
    },
    "2025-01-27": {
        "phase": "无龙试错 / 春节前弱修复",
        "core": "冀东装备高位换手涨停，新炬网络4板一字。",
        "loss": "连板接力仍不稳定，春节前不追一字和高位。",
        "themes": [["AI运维 / MLOps", "新炬网络4板一字", "东方财富核验新炬4板成交0.38亿、换手0.83%", "一字候选，等待开口", "观察"]],
        "candidates": [["新炬网络", "4板", "放弃", "一字/准一字，不能买；等待后续若5板开口再按当天重新评估。", "reject"]],
    },
    "2025-02-05": {
        "phase": "新龙确认",
        "core": "DeepSeek概念+14.73%，MLOps+7.88%；新炬网络5板开口涨停。",
        "loss": "冀东装备节后跌停，前期试错链负反馈释放。",
        "themes": [
            ["DeepSeek / AI应用", "安凯微、每日互动、三六零、天娱数科等超10股涨停", "同花顺主流看点", "独立新方向胜出", "强"],
            ["MLOps / AI运维", "新炬网络5板", "同花顺概念列表 + 东方财富日K", "新龙候选确认", "强"],
        ],
        "candidates": [["新炬网络", "5板", "标准买点", "4板一字放弃后，5板开口涨停；换手10.78%、成交额5.38亿，DeepSeek/MLOps板块强。", "buy"]],
    },
    "2025-02-14": {
        "phase": "龙头负反馈",
        "core": "新炬网络跌停，杭钢股份首次高位放量开口但属于DeepSeek同周期后排/容量补涨。",
        "loss": "新炬网络跌停，确认龙头负反馈。",
        "themes": [["DeepSeek / 算力", "杭钢股份高位放量", "东方财富核验杭钢2月14日换手23.77%、成交额81.27亿", "同周期后排，不作新龙", "观察"]],
        "candidates": [["杭钢股份", "高位", "放弃", "连续一字后高位首次开口，且属于新炬同周期，不是标准4/5板新龙。", "reject"]],
    },
    "2025-02-24": {
        "phase": "新炬死亡后的无龙观察",
        "core": "农业板块全线大涨，低空经济、基建、算力产业链活跃；DeepSeek多数调整。",
        "loss": "DeepSeek旧线继续调整，旧龙新炬后的AI链条仍在释放负反馈。",
        "themes": [
            ["农业", "智慧农业、福成股份、星光农机、庄园牧场涨停", "同花顺复盘", "低位启动，尚未到4/5板买点", "观察"],
            ["算力产业链", "常山北明、科华数据、银轮股份等涨停", "同花顺复盘", "新炬旧AI链条后的分支修复，谨慎", "观察"],
        ],
        "candidates": [],
    },
    "2025-02-25": {
        "phase": "无龙观察",
        "core": "消费电子、华为手机、AI眼镜方向领涨；机器人反弹，低空经济持续活跃。",
        "loss": "算力租赁尾盘回落，拓维信息、浙数文化、航锦科技跌停。",
        "themes": [
            ["消费电子 / AI眼镜", "大富科技、华映科技、福日电子、科森科技等涨停", "同花顺复盘", "新方向活跃，但未出现4/5板可交易龙头", "观察"],
            ["机器人", "巨轮智能涨停，五洲新春、兆威机电炸板", "同花顺复盘", "反弹而非确认", "观察"],
        ],
        "candidates": [],
    },
    "2025-02-26": {
        "phase": "无龙试错 / 4板候选日",
        "core": "机器人概念掀涨停潮，固态电池概念涨幅居前，华丰股份、圣阳股份4连板。",
        "loss": "农业板块领跌；算力旧线仍未完全修复。",
        "themes": [
            ["机器人", "万达轴承、力星股份、宝通科技、上海机电等多股涨停", "同花顺复盘", "新方向强，但当日4板候选核心更偏固态电池", "中强"],
            ["固态电池", "华丰股份、圣阳股份4连板，科森科技、普利特涨停", "同花顺复盘", "独立于新炬AI旧线的新试错方向", "中强"],
            ["农业 / 消费", "庄园牧场4板但农业领跌", "同花顺复盘 + 个股公开行情", "消费高标重新列入，但板块主源不支持", "观察"],
        ],
        "candidates": [
            ["华丰股份", "4板", "放弃", "固态电池有板块助攻，但公开行情显示4板阶段换手和成交额不足模型流动性门槛，不能确认标准买点。", "reject"],
            ["圣阳股份", "4板", "放弃", "4板阶段缩量，未满足换手>7%或成交额>25亿的分歧流动性要求。", "reject"],
            ["庄园牧场", "4板", "仅观察", "个股有换手，但同花顺当日农业领跌，缺少板块主源助攻；消费高标不能因被补看就直接确认。", "observe"],
        ],
    },
    "2025-02-27": {
        "phase": "无龙试错 / 5板集中日",
        "core": "大消费方向领涨，庄园牧场5连板；固态电池强，华丰股份、圣阳股份5连板；大位科技5板。",
        "loss": "AI硬件、铜缆高速连接、液冷服务器领跌；杭钢股份尾盘地天，旧AI链条仍剧烈波动。",
        "themes": [
            ["大消费 / 零售食品", "庄园牧场5板，友好集团、中百集团、东百集团、一鸣食品涨停", "同花顺复盘", "实益达修正后必须独立评估；当日板块强，但候选流动性不达标", "中强"],
            ["固态电池", "华丰股份、圣阳股份5板，上海洗霸、光华科技涨停", "同花顺复盘", "独立试错方向，候选缩量不合格", "中强"],
            ["华为一体机", "恒为科技、云从科技涨停", "同花顺复盘", "分支助攻，不是4/5板核心", "观察"],
        ],
        "candidates": [
            ["庄园牧场", "5板", "放弃", "大消费板块强，但公开行情显示5板换手约4.9%、成交额约1.1亿，未达换手>7%或成交额>25亿。", "reject"],
            ["华丰股份", "5板", "放弃", "5板阶段换手约5.5%、成交额约2.1亿，低于模型流动性门槛。", "reject"],
            ["圣阳股份", "5板", "放弃", "5板早盘成交极低，缩量/一字化特征明显，不是分歧换手回封。", "reject"],
            ["大位科技", "5板", "放弃", "5板成交额约1.5亿、换手不足，且更像AI旧线扰动，不能确认新龙。", "reject"],
        ],
    },
    "2025-02-28": {
        "phase": "无龙观察 / 买点已过",
        "core": "固态电池持续活跃，华丰股份、上海洗霸等涨停；白酒、油气局部活跃，机器人和铜缆/CPO领跌。",
        "loss": "机器人方向大跌，AI硬件继续负反馈；前一日5板候选已进入6板或高位，不能追。",
        "themes": [
            ["固态电池", "华丰股份、上海洗霸等涨停", "同花顺复盘", "前一日4/5板候选未达流动性门槛，今日不追6板", "观察"],
            ["白酒 / 消费", "海南椰岛、岩石股份涨停", "同花顺复盘", "低位轮动，不是标准4/5板", "观察"],
        ],
        "candidates": [["华丰股份", "6板", "放弃", "若看固态电池，标准窗口在2月26/27；2月28已是6板，不转换成新开买点。", "reject"]],
    },
    "2025-03-03": {
        "phase": "无龙试错失败",
        "core": "华丰股份、固态电池高标转弱，前一轮缩量高标试错失败。",
        "loss": "华丰股份大面，继续无龙；这是对2月26/27缩量候选的负反馈跟踪，不倒推改变当日结论。",
        "themes": [["固态电池 / 高位试错", "华丰股份转弱", "东方财富日K + 当日公开行情", "试错失败", "弱"]],
        "candidates": [],
    },
    "2025-03-07": {
        "phase": "新龙确认",
        "core": "机器人板块持续活跃，云鼎科技5连板，震裕科技、铭科精技、浙江黎明涨停；信隆健康4板换手涨停。",
        "loss": "华丰股份、上海洗霸跌停，旧高标负反馈清晰；算力租赁多数调整。",
        "themes": [
            ["机器人", "信隆健康4板，云鼎科技5板，震裕科技等涨停", "同花顺复盘 + 东方财富日K", "新方向从高位退潮中胜出", "中强"],
            ["AI智能体", "立方控股、新开普、用友网络等涨停", "同花顺复盘", "背景助攻但冲高回落", "观察"],
        ],
        "candidates": [["信隆健康", "4板", "标准买点", "换手17.97%、成交额4.96亿；华丰股份跌停，机器人方向仍有云鼎科技、震裕科技等助攻。", "buy"]],
    },
    "2025-03-17": {
        "phase": "龙头明显分歧",
        "core": "信隆健康高位放量回落，未跌停但已明显分歧。",
        "loss": "信隆健康换手35.87%，收跌5.95%，进入减仓观察。",
        "themes": [["机器人", "信隆健康高位分歧", "东方财富日K", "主升后分歧", "观察"]],
        "candidates": [],
    },
    "2025-03-18": {
        "phase": "龙头高位震荡 / 观察修复",
        "core": "机器人概念午后震荡走高，云鼎科技、国茂股份、晋拓股份、亚威股份等十余股涨停。",
        "loss": "信隆健康上一交易日首阴后仍未确认死亡；泛消费调整。",
        "themes": [["机器人", "云鼎科技、国茂股份、晋拓股份等涨停", "同花顺复盘", "信隆健康周期内的板块修复", "中"]],
        "candidates": [],
    },
    "2025-03-19": {
        "phase": "龙头明显分歧 / 减仓",
        "core": "黄金、电力等方向轮动；英伟达、CPO调整。信隆健康仍作为前一轮龙头锚点处理。",
        "loss": "机器人主线助攻减弱，按信隆高位分歧后的减仓观察，不寻找新龙。",
        "themes": [["电力 / 黄金", "韶能股份、嘉泽新能、广安爱众；黄金股活跃", "同花顺复盘", "轮动方向，信隆未确认死亡前不做新龙", "观察"]],
        "candidates": [],
    },
    "2025-03-20": {
        "phase": "龙头明显分歧 / 不开新仓",
        "core": "海工装备、海洋资源集体走高，巨力索具6连板，大连重工2连板。",
        "loss": "信隆健康仍处高位分歧后的风险期，旧龙未确认死亡前不追海工新方向。",
        "themes": [["海工装备 / 海洋资源", "巨力索具6板，大连重工2板", "同花顺复盘", "新方向启动观察，但信隆未死，不开新龙买点", "中强"]],
        "candidates": [],
    },
    "2025-03-21": {
        "phase": "龙头死亡",
        "core": "信隆健康跌停，机器人周期结束。",
        "loss": "信隆健康跌停，清仓并等待新4/5板。",
        "themes": [["机器人", "信隆健康跌停", "东方财富日K", "旧龙死亡", "弱"]],
        "candidates": [],
    },
    "2025-03-24": {
        "phase": "无龙试错 / 海工补看",
        "core": "旅游酒店领涨；海工装备持续活跃，大连重工4连板，振华重工、南方路机、佛山照明、亚星锚链涨停。",
        "loss": "算力租赁大跌，机器人持续调整；信隆周期负反馈仍在释放。",
        "themes": [
            ["海工装备 / 深海科技", "大连重工4板，振华重工等助攻", "同花顺复盘 + 财联社/东方财富同日快讯", "信隆死亡后的新方向试错，但大连4板一字化", "中强"],
            ["旅游酒店", "张家界、峨眉山A、大连圣亚涨停", "同花顺复盘", "低位轮动，不是4/5板核心", "观察"],
        ],
        "candidates": [
            ["大连重工", "4板", "放弃", "海工装备有板块助攻，但同日公开复盘称其一字晋级4连板，不能作为可交易分歧回封买点。", "reject"],
            ["雪龙集团", "5板", "仅观察", "5板地天有辨识度，但同花顺主线并非机器人，且机器人仍在持续调整，按高风险试错处理。", "observe"],
        ],
    },
    "2025-03-25": {
        "phase": "无龙试错",
        "core": "可控核聚变逆市大涨；算力产业链重挫，海工装备调整。",
        "loss": "海工装备前日试错次日调整，算力旧线跌停扩散。",
        "themes": [["可控核聚变", "合锻智能、久盛电气、兰石重装、海陆重工、融发核电等涨停", "同花顺复盘", "低位新方向，尚未到4/5板标准窗口", "观察"]],
        "candidates": [],
    },
    "2025-03-26": {
        "phase": "无龙试错",
        "core": "养殖业领涨，海工装备反复活跃，化工、机器人反弹。",
        "loss": "各题材轮动快，未形成标准4/5板龙头买点。",
        "themes": [
            ["养殖业", "京基智农、湘佳股份、福成股份等涨停", "同花顺复盘", "低位轮动", "观察"],
            ["海工装备", "大连重工、中信重工、巨力索具涨停", "同花顺复盘", "一字/高位链条买点已过", "观察"],
        ],
        "candidates": [["大连重工", "高位", "放弃", "3月24日4板一字已排除，后续高位不转换成标准新买点。", "reject"]],
    },
    "2025-03-27": {
        "phase": "无龙试错",
        "core": "化工板块反复活跃，半导体、医药上涨；海工装备跌幅居前。",
        "loss": "海工装备高位负反馈，大连重工、神开股份跌停。",
        "themes": [["化工", "中毅达、尤夫股份、丹化科技、华融化学等涨停", "同花顺复盘", "轮动试错，未到标准4/5板确认", "观察"]],
        "candidates": [],
    },
    "2025-03-28": {
        "phase": "无龙试错",
        "core": "医药、黄金、文化传媒活跃；化工、海工装备领跌。",
        "loss": "中毅达、鲁北化工、神开股份、大连重工、中信重工跌停，高位试错负反馈加重。",
        "themes": [["医药", "润都股份、百花医药、河化股份涨停", "同花顺复盘", "低位轮动，等待4/5板", "观察"]],
        "candidates": [],
    },
    "2025-03-31": {
        "phase": "无龙试错",
        "core": "黄金活跃，算力午后回流，大位科技、宏景科技、杭钢股份、恒润股份涨停；化工领跌。",
        "loss": "化工高标中毅达、红宝丽跌停，上一轮试错仍有负反馈。",
        "themes": [["算力", "大位科技、宏景科技、杭钢股份、恒润股份涨停", "同花顺复盘", "旧AI/算力线回流，信隆后无新4/5板标准买点", "观察"]],
        "candidates": [],
    },
}


def next_trading_day(d):
    idx = DATES.index(d)
    for item in DATES[idx + 1:]:
        if item not in HOLIDAYS:
            return item
    return ""


def badge(text, cls):
    return f'<span class="badge {cls}">{html.escape(text)}</span>'


def table(headers, rows):
    head = "<thead><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in headers) + "</tr></thead>"
    body = "<tbody>" + "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows) + "</tbody>"
    return f'<div class="table-wrap"><table>{head}{body}</table></div>'


def default_special(d, state):
    if state["search"] in {"不允许", "收盘后不允许"}:
        return {
            "phase": state["state"],
            "core": f"{state['leader']}仍为当前龙头锚点；当日不重新筛选新龙，只处理龙头持仓、分歧和负反馈。",
            "loss": f"{state['leader']}未确认死亡前，不把其他方向升级为新龙。",
            "themes": [[state["theme"], state["leader"], "同花顺复盘 + 东方财富龙头走势跟踪", "当前龙头周期内，只作锚点跟踪", "观察"]],
            "candidates": [],
        }
    return {
        "phase": "无龙观察",
        "core": "按前一日锚点延续，未出现经同花顺/东方财富同时核验的4/5板标准买点。",
        "loss": "无有效龙头时默认空仓观察；只登记盘面，不追2/3板。",
        "themes": [["当日活跃题材", "见同花顺当日复盘", "同花顺复盘", "无确认龙头时只观察", "观察"]],
        "candidates": [],
    }


def state_for(d):
    if d in HOLIDAYS:
        return {
            "leader": "休市", "theme": "休市", "state": "休市", "action": "不交易",
            "search": "不适用", "prior": "上一交易日锚点延续", "prior_theme": "上一交易日锚点延续",
            "trigger": "下一交易日再按龙头状态复盘。"
        }
    if d < "2025-02-05":
        return {
            "leader": "无有效龙头", "theme": "无", "state": "无龙", "action": "空仓观察",
            "search": "允许但严格", "prior": "实益达", "prior_theme": "微信小店 / 智能终端",
            "trigger": "只等独立新题材4/5板分歧换手回封；旧消费补涨和一字高标不做。"
        }
    if d == "2025-02-05":
        return {
            "leader": "新炬网络", "theme": "DeepSeek / MLOps / AI运维", "state": "新龙确认", "action": "建仓",
            "search": "收盘后不允许", "prior": "实益达", "prior_theme": "微信小店 / 智能终端",
            "trigger": "次日看6板确认；不能弱转强或高位大面则减仓。"
        }
    if "2025-02-06" <= d <= "2025-02-13":
        return {
            "leader": "新炬网络", "theme": "DeepSeek / MLOps / AI运维", "state": "龙头主升" if d <= "2025-02-12" else "龙头高位震荡",
            "action": "持仓 / 减仓跟随" if d == "2025-02-13" else "持仓 / 加仓", "search": "不允许",
            "prior": "新炬网络", "prior_theme": "DeepSeek / MLOps / AI运维",
            "trigger": "新炬未死，不看普通后排；只处理修复、分歧、负反馈。"
        }
    if "2025-02-14" <= d <= "2025-02-21":
        return {
            "leader": "新炬网络", "theme": "DeepSeek / MLOps / AI运维", "state": "龙头负反馈" if d <= "2025-02-17" else "龙头死亡",
            "action": "清仓", "search": "死亡后才重新允许", "prior": "新炬网络",
            "prior_theme": "DeepSeek / MLOps / AI运维",
            "trigger": "等待旧AI链条负反馈释放后，再看独立新题材4/5板。"
        }
    if d < "2025-03-07":
        return {
            "leader": "无有效龙头", "theme": "无", "state": "无龙", "action": "空仓观察",
            "search": "允许但严格", "prior": "新炬网络", "prior_theme": "DeepSeek / MLOps / AI运维",
            "trigger": "只看独立新题材4/5板，DeepSeek同周期补涨不作新龙。"
        }
    if d == "2025-03-07":
        return {
            "leader": "信隆健康", "theme": "机器人", "state": "新龙确认", "action": "建仓",
            "search": "收盘后不允许", "prior": "新炬网络", "prior_theme": "DeepSeek / MLOps / AI运维",
            "trigger": "次日看5板/6板延续；机器人助攻断层或信隆负反馈则减仓。"
        }
    if "2025-03-10" <= d <= "2025-03-14":
        return {
            "leader": "信隆健康", "theme": "机器人", "state": "龙头主升", "action": "持仓 / 加仓",
            "search": "不允许", "prior": "信隆健康", "prior_theme": "机器人",
            "trigger": "信隆未死，不看普通新方向；只跟踪机器人助攻和龙头负反馈。"
        }
    if "2025-03-17" <= d <= "2025-03-20":
        return {
            "leader": "信隆健康", "theme": "机器人", "state": "龙头明显分歧" if d < "2025-03-19" else "龙头负反馈",
            "action": "减仓 / 清仓", "search": "不允许", "prior": "信隆健康", "prior_theme": "机器人",
            "trigger": "等信隆是否修复；若跌停或连续杀，周期结束。"
        }
    return {
        "leader": "无有效龙头", "theme": "无", "state": "无龙", "action": "空仓观察",
        "search": "允许但严格", "prior": "信隆健康", "prior_theme": "机器人",
        "trigger": "等待信隆负反馈释放后的独立新4/5板；机器人后排补涨谨慎。"
    }


def render_candidate_rows(candidates, search_state):
    if not candidates:
        if search_state in {"不允许", "收盘后不允许"}:
            return [["龙头未死，不检查新龙", "-", "不检查", "当前龙头仍为锚点，当日只处理持仓、减仓或清仓，不做4/5板新龙筛选。", badge("仅观察", "observe")]]
        return [["当日无符合4/5板候选", "-", "无标准买点", "2/3板只做盘面跟踪；无核验4/5板不写机会。", badge("仅观察", "observe")]]
    rows = []
    for stock, board, status, reason, cls in candidates:
        verdict = "标准买点" if cls == "buy" else ("放弃" if cls == "reject" else "仅观察")
        rows.append([html.escape(stock), html.escape(board), html.escape(status), html.escape(reason), badge(verdict, cls)])
    return rows


def model_verdicts(candidates):
    out = []
    for stock, board, status, reason, cls in candidates:
        out.append({
            "stock": stock,
            "board": board,
            "role": "4/5板候选",
            "verdict": "standard buy" if cls == "buy" else ("reject" if cls == "reject" else "observe only"),
            "visible_verdict": "标准买点" if cls == "buy" else ("放弃" if cls == "reject" else "仅观察"),
            "reason": reason,
        })
    return out


def render(d, prior_reports):
    state = state_for(d)
    note = SPECIAL.get(d, default_special(d, state))
    if d in HOLIDAYS:
        note = {
            "phase": "休市", "core": HOLIDAYS[d], "loss": HOLIDAYS[d],
            "themes": [["休市", HOLIDAYS[d], "交易所日历", "不交易", "观察"]], "candidates": []
        }
    theme_rows = [
        [html.escape(t), html.escape(core), html.escape(src), html.escape(rel), badge(strength, "buy" if strength == "强" else "observe")]
        for t, core, src, rel, strength in note["themes"]
    ]
    recent_rows = [
        [html.escape(r["review_date"]), html.escape(r["current_leader"]), html.escape(r["leader_state"]), html.escape(r["position_action"]), html.escape(r["next_trigger"])]
        for r in prior_reports[-5:]
    ] or [["无", "无", "无", "无", "本段起点"]]
    sources = [{"name": f"同花顺复盘：{d}", "url": ths_url(d)}] if d not in HOLIDAYS else [{"name": HOLIDAYS[d], "url": ""}]
    for v in model_verdicts(note["candidates"]):
        secid = STOCK_SECIDS.get(v["stock"])
        if secid:
            sources.append({"name": f"东方财富日K：{v['stock']} {d}", "url": eastmoney_url(secid, d)})
    plan = (
        [("继续/修复", f"{state['leader']}继续强势或修复，按{state['action']}处理。"),
         ("分歧", f"{state['leader']}爆量、弱封或长上影，减仓，不看普通后排。"),
         ("负反馈", f"{state['leader']}跌停/大阴/连续杀，清仓。")]
        if state["search"] in {"不允许", "收盘后不允许"} else
        [("旧龙锚点", f"上一轮：{state['prior']} / {state['prior_theme']}。"),
         ("候选条件", "只看排除一字后的4/5板分歧换手回封，换手>7%或成交额>25亿。"),
         ("放弃条件", "2/3板、连续一字、6板首次开口、同周期后排补涨全部不买。")]
    )
    data = {
        "review_date": d,
        "data_cutoff": d,
        "next_trading_day": next_trading_day(d),
        "current_leader": state["leader"],
        "current_leader_theme": state["theme"],
        "leader_state": state["state"],
        "position_action": state["action"],
        "new_leader_search_allowed": state["search"],
        "next_trigger": state["trigger"],
        "market_phase": note["phase"],
        "cycle_stage": note["phase"],
        "old_leader_state": f"{state['prior']} / {state['prior_theme']}",
        "loss_effect": {"summary": note["loss"]},
        "new_direction": {"summary": "只有当前龙头死亡或无有效龙头时，才筛4/5板新方向。"},
        "operation_plan": {"phase": note["phase"], "position": state["action"], "action": state["trigger"]},
        "risk_control": {
            "single_trade_loss": "打板失败或次日不能弱转强优先退出",
            "daily_loss": "确认龙头跌停或高位批量A杀时停止开仓",
            "continuous_trials": "连续两次试错失败后暂停",
            "position_cap": "无龙空仓；标准买点小中仓；主升才考虑加仓",
            "sell_conditions": "跌停、大阴、断板后继续杀、板块助攻断层",
        },
        "high_level_sentiment": {
            "nominal_highest_board": note["core"],
            "tradable_highest_board": "见4/5板候选检查",
            "previous_high_board_performance": note["loss"],
            "broken_board_feedback": note["loss"],
            "high_level_limit_down_count": "见同花顺复盘与东方财富候选核验",
            "high_level_broken_board_count": "见同花顺复盘与东方财富候选核验",
            "promotion_rate": "逐日模拟不使用后验高度统计",
        },
        "prior_confirmed_leader": state["prior"],
        "prior_leader_theme": state["prior_theme"],
        "intermediate_trial_chain": "无龙阶段只记录试错，不把一字高标、6板开口、同周期补涨自动升格。",
        "old_leader_chain": f"{state['prior']} / {state['prior_theme']} -> {state['state']}",
        "current_core": note["core"],
        "tradable_high_board": "见4/5板候选检查",
        "next_opportunity": "有标准买点" if any(c[-1] == "buy" for c in note["candidates"]) else "无标准买点",
        "hard_no_trade": "旧龙未死不找新龙；不顶一字；不买2/3板；不追6板首次开口。",
        "model_verdicts": model_verdicts(note["candidates"]),
        "sources": sources,
        "source_verification": {
            "sector_theme": "同花顺复盘优先；候选题材按当天可见资料人工判断。",
            "individual_price_action": "4/5板候选使用东方财富日K核验开收高低、换手、成交额。",
            "no_future_data": f"本页仅使用{d}及之前可见资料。",
        },
        "generated_by_skill": {
            "name": "stock-cycle-review",
            "skill_dir": str(SKILL_DIR),
            "workflow": "先定龙头 -> 龙头状态 -> 仓位动作 -> 是否允许找新龙 -> 允许才看4/5板候选 -> 风控",
        },
    }
    source_items = "".join(
        f'<li><a href="{html.escape(s["url"])}">{html.escape(s["name"])}</a></li>' if s.get("url") else f'<li>{html.escape(s["name"])}</li>'
        for s in sources
    )
    plan_html = "".join(f'<div class="plan-block"><strong>{html.escape(a)}</strong><p>{html.escape(b)}</p></div>' for a, b in plan)
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>A股短线周期复盘 - {html.escape(d)}</title>
<style>
:root{{--bg:#f6f7f9;--panel:#fff;--text:#1f2937;--muted:#6b7280;--line:#d9dee7;--green:#13795b;--orange:#b26a00;--red:#b42318;--blue:#1d4ed8}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.55}}.page{{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 0 42px}}header{{display:grid;gap:10px;margin-bottom:16px}}h1{{margin:0;font-size:clamp(24px,4vw,34px)}}h2{{margin:0 0 12px;font-size:18px}}p{{margin:0}}.note{{color:var(--muted);font-size:14px}}.risk{{border-left:4px solid var(--orange);background:#fff8ec;padding:10px 12px;color:#7a4b00}}.grid{{display:grid;gap:12px}}.status-grid{{grid-template-columns:repeat(6,minmax(0,1fr));margin:16px 0}}.metric,section{{background:var(--panel);border:1px solid var(--line);border-radius:8px}}.metric{{min-height:96px;padding:12px}}.metric .label{{color:var(--muted);font-size:12px;margin-bottom:6px}}.metric .value{{font-size:17px;font-weight:700}}section{{padding:16px;margin-bottom:14px}}.timeline,.plan{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.plan{{grid-template-columns:repeat(3,1fr)}}.step,.plan-block{{border:1px solid var(--line);border-radius:8px;padding:12px;background:#fbfcfe}}.title,.plan-block strong{{display:block;font-weight:700;margin-bottom:6px}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{border-bottom:1px solid var(--line);padding:10px 8px;text-align:left;vertical-align:top}}th{{color:var(--muted);font-weight:600;background:#f9fafb}}.badge{{display:inline-flex;min-height:24px;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}}.buy{{background:#e8f5ef;color:var(--green)}}.observe{{background:#fff4db;color:var(--orange)}}.reject{{background:#fdebea;color:var(--red)}}a{{color:var(--blue)}}@media(max-width:860px){{.status-grid,.timeline,.plan{{grid-template-columns:1fr}}.table-wrap{{overflow-x:auto}}table{{min-width:760px}}}}
</style></head><body><main class="page">
<header><h1>A股短线周期复盘 - {html.escape(d)}</h1><p class="note">历史实盘模拟：只使用 {html.escape(d)} 当天及之前可见资料。输出为 stock-cycle-review 技能框架，不构成投资建议。</p><p class="risk">先定龙头，再定仓位；旧龙未死不找新龙，只有无龙或龙头死亡才看4/5板候选。</p></header>
<section class="grid status-grid">
<div class="metric"><div class="label">当前龙头</div><div class="value">{html.escape(state['leader'])}<br><span class="note">{html.escape(state['theme'])}</span></div></div>
<div class="metric"><div class="label">龙头状态</div><div class="value">{html.escape(state['state'])}</div></div>
<div class="metric"><div class="label">当前动作</div><div class="value">{html.escape(state['action'])}</div></div>
<div class="metric"><div class="label">是否找新龙</div><div class="value">{html.escape(state['search'])}</div></div>
<div class="metric"><div class="label">上一轮龙头 / 板块</div><div class="value">{html.escape(state['prior'])}<br><span class="note">{html.escape(state['prior_theme'])}</span></div></div>
<div class="metric"><div class="label">下一触发</div><div class="value">{html.escape(state['trigger'])}</div></div>
</section>
<section><h2>龙头锚点</h2>{table(['当前龙头','所属题材','状态','动作','是否允许新龙筛选'], [[html.escape(state['leader']), html.escape(state['theme']), html.escape(state['state']), html.escape(state['action']), html.escape(state['search'])]])}</section>
<section><h2>高位情绪快照</h2>{table(['名义最高/核心','可交易最高板','旧龙/前高标表现','亏钱效应'], [[html.escape(note['core']), '见4/5板候选检查', html.escape(state['prior'] + ' / ' + state['prior_theme']), html.escape(note['loss'])]])}</section>
<section><h2>周期链路</h2><div class="timeline"><div class="step"><div class="title">上一轮龙头</div><p>{html.escape(state['prior'])} / {html.escape(state['prior_theme'])}</p></div><div class="step"><div class="title">当前锚点</div><p>{html.escape(state['leader'])} / {html.escape(state['state'])}</p></div><div class="step"><div class="title">是否寻找新龙</div><p>{html.escape(state['search'])}</p></div><div class="step"><div class="title">下一触发</div><p>{html.escape(state['trigger'])}</p></div></div></section>
<section><h2>板块强度</h2>{table(['板块/方向','高标核心','证据','与旧周期关系','强度'], theme_rows)}</section>
<section><h2>4/5板候选检查</h2>{table(['股票','板数','买点状态','原因','模型结论'], render_candidate_rows(note['candidates'], state['search']))}</section>
<section><h2>次日龙头预案</h2><div class="plan">{plan_html}</div></section>
<section><h2>最近归档对比</h2>{table(['日期','龙头','状态','动作','上一触发'], recent_rows)}</section>
<section><h2>风控纪律</h2>{table(['项目','规则'], [['仓位上限','无龙空仓；标准买点小中仓；龙头主升才考虑加仓。'],['单笔最大亏损','打板失败、次日不能弱转强或龙头跌停，优先退出。'],['连续试错次数','连续两次失败后暂停。'],['卖出条件','跌停、大阴、断板后继续杀、板块助攻断层。']])}</section>
<section><h2>最终五句话</h2><ol><li>当前龙头：{html.escape(state['leader'])}，{html.escape(state['theme'])}。</li><li>龙头状态：{html.escape(state['state'])}。</li><li>当前动作：{html.escape(state['action'])}。</li><li>是否允许寻找新龙：{html.escape(state['search'])}。</li><li>下一触发：{html.escape(state['trigger'])}</li></ol></section>
<section><h2>数据源核验</h2><ul>{source_items}</ul><p class="note">同花顺/开盘啦优先用于板块与梯队；东方财富用于4/5板候选日K、换手、成交额和可交易性。脚本只负责归档渲染。</p></section>
<script type="application/json" id="stock-cycle-review-data">{html.escape(json.dumps(data, ensure_ascii=False, indent=2))}</script>
</main></body></html>"""
    return page, data


def render_index():
    reports = []
    for path in sorted(OUT_DIR.glob("20*.html")):
        if path.name == "index.html":
            continue
        text = path.read_text(encoding="utf-8")
        marker = '<script type="application/json" id="stock-cycle-review-data">'
        if marker not in text:
            continue
        raw = text.split(marker, 1)[1].split("</script>", 1)[0]
        reports.append(json.loads(html.unescape(raw)))
    rows = []
    for r in sorted(reports, key=lambda item: item["review_date"]):
        buys = [v["stock"] for v in r.get("model_verdicts", []) if v.get("verdict") == "standard buy"]
        rows.append([f'<a href="{html.escape(r["review_date"])}.html">{html.escape(r["review_date"])}</a>', html.escape(r["current_leader"]), html.escape(r["leader_state"]), html.escape(r["position_action"]), html.escape("、".join(buys) if buys else "无"), html.escape(r["next_trigger"])])
    page = "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>A股短线周期复盘归档</title><style>body{margin:0;background:#f6f7f9;color:#1f2937;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;line-height:1.55}main{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:28px 0 42px}h1{margin:0 0 6px;font-size:32px}p{margin:0 0 16px;color:#6b7280}section{background:white;border:1px solid #d9dee7;border-radius:8px;padding:16px}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px;min-width:820px}th,td{border-bottom:1px solid #d9dee7;padding:10px 8px;text-align:left;vertical-align:top}th{background:#f9fafb;color:#6b7280}a{color:#1d4ed8}</style></head><body><main><h1>A股短线周期复盘归档</h1><p>使用 stock-cycle-review 技能生成。历史页面禁止未来数据；标准买点只统计4/5板可交易回封。</p><section>" + table(["日期","当前龙头","状态","动作","标准买点","下一触发"], rows) + "</section></main></body></html>"
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    reports = []
    for d in DATES:
        page, data = render(d, reports)
        (OUT_DIR / f"{d}.html").write_text(page, encoding="utf-8")
        reports.append(data)
    render_index()
    print(json.dumps({
        "generated": len(reports),
        "standard_buys": [
            {"date": r["review_date"], "stock": v["stock"], "reason": v["reason"]}
            for r in reports for v in r.get("model_verdicts", []) if v.get("verdict") == "standard buy"
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
