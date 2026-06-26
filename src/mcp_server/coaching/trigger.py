"""触发判断：简单问题 vs 复杂主题"""

from typing import Literal

# 复杂触发词（满足任一即复杂）
COMPLEX_TRIGGERS = [
    # 问"为什么"或"为什么不一样"
    "为什么", "为何", "怎么会", "怎么不一样",
    # 多资产联动
    "和.*走势", "和.*不同", "联动", "背离",
    # 用户表达困惑/错误认知
    "我觉得", "我认为", "是不是", "是不是因为",
    "我以为", "感觉.*不对",
    # 政策+市场交叉
    "对.*什么影响", "会导致", "会带来",
    # 宏观分析类
    "怎么看.*趋势", "最近.*为什么", ".*为什么涨", ".*为什么跌",
]

# 简单触发词（符合且不含复杂特征）
SIMPLE_TRIGGERS = [
    "该买", "该卖", "要不要", "可以买",
    "怎么看", "现在.*情况", "当前.*如何",
    "是什么", "什么是",
]

import re

def detect_complexity(user_input: str) -> Literal["simple", "complex"]:
    """
    判断用户输入是简单问题还是复杂主题

    Returns:
        "simple": 直接 10 步输出
        "complex": Socratic 多轮引导
    """
    text = user_input.lower()

    # 检查是否复杂
    for pattern in COMPLEX_TRIGGERS:
        if re.search(pattern, text):
            return "complex"

    # 检查是否简单
    for pattern in SIMPLE_TRIGGERS:
        if re.search(pattern, text):
            return "simple"

    # 默认：含宏观/投资主题词但无明显特征的，走简单
    macro_keywords = ["黄金", "茅台", "股市", "利率", "汇率", "原油", "美联储", "央行", "A股", "美股", "宏观"]
    if any(kw in text for kw in macro_keywords):
        return "simple"

    return "simple"  # 默认简单，避免过度触发