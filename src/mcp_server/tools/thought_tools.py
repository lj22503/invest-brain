"""Thought recording tools - record_thought, search_memories, get_thought_cards"""

import re
import time
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..knowledge.graph_client import get_graph_client
from ..memory.store import get_memory_store
from ..llm import get_deepseek_client, is_llm_available

thought_tools = FastMCP("thought-tools")

# Master alignment keywords for simple matching
MASTER_KEYWORDS = {
    "巴菲特": ["护城河", "安全边际", "能力圈", "贪婪", "恐惧", "价值"],
    "芒格": ["好生意", "多元思维", "逆向", "耐心"],
    "段永平": ["本分", "不懂不投", "stop doing"],
    "马克斯": ["周期", "第二层思维", "风险"],
    "李录": ["现代化", "中国"],
}


def _parse_with_llm(text: str) -> dict:
    """
    用 DeepSeek 解析投资想法，提取结构化信息。
    scene: thought_parsing
    """
    prompt = f"""分析以下投资想法，提取结构化信息。

输入：{text}

必须严格返回以下JSON格式，不得包含任何其他内容：
{{
  "ticker": "标的名称或代码，如贵州茅台或600519，未提到则null",
  "price": 价格数字，如1400，未提到则null，
  "indicator": "提到的估值指标，如PE/PB/ROE/毛利率等，未提到则null",
  "action_hint": "操作意图，如买入/加仓/观望/减仓/卖出，未提到则null",
  "emotion": "情绪倾向，如冷静/乐观/焦虑/冲动/后悔/兴奋，未提到则null",
  "master_alignment": "符合哪位大师思想，如巴菲特/芒格/段永平/马克斯/李录，未提到则null"
}}

只输出JSON，不要任何解释或前缀文字："""

    try:
        client = get_deepseek_client()
        if client is None:
            raise RuntimeError("LLM not available")

        response = client.chat_simple(prompt, scene="thought_parsing")
        result = json.loads(response.strip())

        return {
            "ticker": result.get("ticker"),
            "price": result.get("price"),
            "indicator": result.get("indicator"),
            "action_hint": result.get("action_hint"),
            "emotion": result.get("emotion"),
            "master_alignment": result.get("master_alignment"),
        }
    except Exception:
        # 降级：使用关键词匹配
        return _fallback_parse(text)


@thought_tools.tool()
def record_thought(text: str) -> dict:
    """
    Record an investment thought/idea from the user.

    Args:
        text: The raw thought text from user (e.g., "茅台跌到1400可以考虑买入")

    Returns:
        dict: A thought card with parsed entities and card ID
    """
    # Parse with DeepSeek LLM (falls back to regex if unavailable)
    parsed = _parse_with_llm(text)

    # Store in SQLite
    store = get_memory_store()
    card_id = store.add_thought(
        text=text,
        ticker=parsed.get("ticker"),
        price=parsed.get("price"),
        indicator=parsed.get("indicator")
    )

    return {
        "card_id": f"thought_{card_id}",
        "original_text": text,
        "parsed_entities": parsed,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "master_alignment": parsed.get("master_alignment"),
        "created": True,
    }


def _fallback_parse(text: str) -> dict:
    """降级解析：关键词匹配（LLM 不可用时）"""
    # Try to extract ticker (Chinese company name or AAPL-style)
    ticker_match = re.search(r'(茅台|苹果|腾讯|阿里|谷歌|微软|亚马逊|贵州茅台)', text)
    ticker_match2 = re.search(r'\b([A-Z]{2,5})\b', text)
    ticker = ticker_match.group(1) if ticker_match else (ticker_match2.group(1) if ticker_match2 else None)

    # Try to extract price
    price_match = re.search(r'跌?到?(\d+(?:\.\d+)?)', text)
    price = float(price_match.group(1)) if price_match else None

    # Try to extract indicator keywords
    indicator = None
    for ind in ["PE", "PB", "ROE", "ROA", "毛利率", "净利率"]:
        if ind in text:
            indicator = ind
            break

    # Determine master alignment via simple keyword matching
    master_alignment = None
    for master, keywords in MASTER_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                master_alignment = master
                break
        if master_alignment:
            break

    return {
        "ticker": ticker,
        "price": price,
        "indicator": indicator,
        "action_hint": None,
        "emotion": None,
        "master_alignment": master_alignment,
    }


@thought_tools.tool()
def search_memories(query: str) -> list:
    """
    Search user's historical thoughts and memories.

    Args:
        query: Search query (e.g., "茅台", "上次关于苹果的想法")

    Returns:
        list: Matching thought cards
    """
    # Semantic search stub - for now do simple substring match
    store = get_memory_store()
    all_thoughts = store.get_thoughts(limit=100)

    query_lower = query.lower()
    matched = []
    for thought in all_thoughts:
        if query_lower in thought.get("text", "").lower():
            matched.append({
                "card_id": f"thought_{thought['id']}",
                "original_text": thought["text"],
                "ticker": thought.get("ticker"),
                "price": thought.get("price"),
                "indicator": thought.get("indicator"),
                "created_at": thought.get("created_at"),
            })
    return matched


@thought_tools.tool()
def get_thought_cards(ticker: str) -> list:
    """
    Get all thought cards for a specific ticker/symbol.

    Args:
        ticker: Stock ticker (e.g., "贵州茅台", "AAPL")

    Returns:
        list: All thought cards for this ticker
    """
    store = get_memory_store()
    thoughts = store.get_thoughts(ticker=ticker, limit=50)

    return [
        {
            "card_id": f"thought_{t['id']}",
            "original_text": t["text"],
            "ticker": t.get("ticker"),
            "price": t.get("price"),
            "indicator": t.get("indicator"),
            "created_at": t.get("created_at"),
        }
        for t in thoughts
    ]