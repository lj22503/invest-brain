"""Thought recording tools - record_thought, search_memories, get_thought_cards"""

import re
import time
import json
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ..knowledge.graph_client import get_graph_client
from ..memory.store import get_memory_store
from ..llm import get_deepseek_client, is_llm_available

thought_tools = FastMCP("thought-tools")

# Master alignment keywords for simple matching (fallback when VectorStore unavailable)
MASTER_KEYWORDS = {
    "巴菲特": ["护城河", "安全边际", "能力圈", "贪婪", "恐惧", "价值"],
    "芒格": ["好生意", "多元思维", "逆向", "耐心"],
    "段永平": ["本分", "不懂不投", "stop doing"],
    "马克斯": ["周期", "第二层思维", "风险"],
    "李录": ["现代化", "中国"],
}

# ---- 去硬编码：运行时从数据源动态加载 ----

_STOCK_NAMES = None       # A股公司名列表，None 表示未加载
_STOCK_LOADED = False
_INDICATOR_KEYWORDS = None
_INDICATOR_LOADED = False


def _ensure_stock_names():
    """懒加载 A 股全量公司名（AKShare），失败则用申万代表公司兜底"""
    global _STOCK_NAMES, _STOCK_LOADED
    if _STOCK_LOADED:
        return
    _STOCK_LOADED = True
    try:
        import akshare as ak
        df = ak.stock_info_a_code_name()
        _STOCK_NAMES = df["name"].tolist()
        # 降序排列：优先匹配更长的公司名（如"贵州茅台"优先于"茅台"）
        _STOCK_NAMES.sort(key=len, reverse=True)
    except Exception:
        # 降级：从申万行业 JSON 提取代表公司
        try:
            industry_path = Path(__file__).resolve().parents[3] / "data" / "industry" / "申万28个行业分类.json"
            with open(industry_path, encoding="utf-8") as f:
                industry_data = json.load(f)
            companies = set()
            for cat in industry_data.get("categories", []):
                for c in cat.get("representative_companies", []):
                    companies.add(c)
            _STOCK_NAMES = sorted(companies, key=len, reverse=True)
        except Exception:
            _STOCK_NAMES = []


def _ensure_indicators():
    """懒加载投资指标关键词（申万28行业 key_indicators）"""
    global _INDICATOR_KEYWORDS, _INDICATOR_LOADED
    if _INDICATOR_LOADED:
        return
    _INDICATOR_LOADED = True
    try:
        industry_path = Path(__file__).resolve().parents[3] / "data" / "industry" / "申万28个行业分类.json"
        with open(industry_path, encoding="utf-8") as f:
            industry_data = json.load(f)
        indicators = set()
        # 通用财务指标（所有行业共享）
        indicators.update(["PE", "PB", "ROE", "ROA", "净利率", "市盈率", "市净率"])
        for cat in industry_data.get("categories", []):
            for ind in cat.get("key_indicators", []):
                indicators.add(ind)
        _INDICATOR_KEYWORDS = sorted(indicators, key=len, reverse=True)
    except Exception:
        _INDICATOR_KEYWORDS = ["PE", "PB", "ROE", "ROA", "毛利率", "净利率"]


def _match_ticker(text: str) -> Optional[str]:
    """从 A 股公司名列表中匹配文本中出现的公司"""
    _ensure_stock_names()
    # Pass 1: 公司名完整出现在文本中（如"宁德时代跌了"→"宁德时代"）
    for name in _STOCK_NAMES:
        if name in text:
            return name
    # Pass 2: 英文 ticker（如 AAPL），先做精确匹配避免中文歧义
    match = re.search(r'\b([A-Z]{3,5})\b', text, re.ASCII)
    if match:
        return match.group(1)
    # Pass 3: 中文简称模糊匹配（如"茅台"→"贵州茅台"），仅唯一匹配时返回避免误判
    candidates = set()
    for i in range(len(text)):
        for j in range(i + 3, min(i + 7, len(text) + 1)):
            chunk = text[i:j]
            if all('\u4e00' <= c <= '\u9fff' for c in chunk):
                candidates.add(chunk)
    candidates = sorted(candidates, key=len, reverse=True)
    for cand in candidates:
        matched = None
        for name in _STOCK_NAMES:
            if len(name) > len(cand) and cand in name:
                if matched is not None:
                    matched = None  # 多个公司匹配同一个简称，不可靠
                    break
                matched = name
        if matched:
            return matched
    return None


def _match_indicator(text: str) -> Optional[str]:
    """从动态加载的指标列表中匹配文本中的指标"""
    _ensure_indicators()
    for ind in _INDICATOR_KEYWORDS:
        if ind in text:
            return ind
    return None


def _match_master_semantic(text: str) -> Optional[str]:
    """用 VectorStore 语义搜索匹配最相近的大师"""
    try:
        from ..knowledge.vector_store import get_vector_store
        vs = get_vector_store()
        results = vs.search(text, top_k=5)
        for r in results:
            if r["metadata"].get("type") == "master":
                return r["metadata"].get("name")
        return None
    except Exception:
        # 降级：关键词匹配
        for master, keywords in MASTER_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return master
        return None


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

    # Also vectorize for semantic search
    try:
        from ..knowledge.vector_store import get_vector_store
        vs = get_vector_store()
        vs.add_memory(
            memory_id=str(card_id),
            text=text,
            metadata={
                "ticker": parsed.get("ticker") or "",
                "price": str(parsed.get("price")) if parsed.get("price") else "",
                "indicator": parsed.get("indicator") or "",
                "master_alignment": parsed.get("master_alignment") or "",
            },
        )
    except Exception:
        pass  # Vector store may not be available

    return {
        "card_id": f"thought_{card_id}",
        "original_text": text,
        "parsed_entities": parsed,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "master_alignment": parsed.get("master_alignment"),
        "created": True,
    }


def _fallback_parse(text: str) -> dict:
    """降级解析：动态数据源匹配（LLM 不可用时）"""
    # ticker: AKShare A股名单匹配（降级→申万代表公司）
    ticker = _match_ticker(text)

    # price: 保留原有正则逻辑
    price_match = re.search(r'跌?到?(\d+(?:\.\d+)?)', text)
    price = float(price_match.group(1)) if price_match else None

    # indicator: 申万28行业指标列表匹配（降级→硬编码6个）
    indicator = _match_indicator(text)

    # master_alignment: VectorStore语义搜索（降级→关键词匹配）
    master_alignment = _match_master_semantic(text)

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
    Search user's historical thoughts and memories using semantic search.

    Args:
        query: Search query (e.g., "茅台", "上次关于苹果的想法")

    Returns:
        list: Matching thought cards, sorted by relevance
    """
    store = get_memory_store()

    # Try semantic search via Chroma vector store first
    semantic_results = {}
    try:
        from ..knowledge.vector_store import get_vector_store
        vs = get_vector_store()
        hits = vs.search_memories(query, top_k=10)
        for h in hits:
            memory_id = h["id"]
            semantic_results[memory_id] = {
                "card_id": f"thought_{memory_id}",
                "original_text": h["text"],
                "ticker": h["metadata"].get("ticker"),
                "price": h["metadata"].get("price"),
                "indicator": h["metadata"].get("indicator"),
                "distance": h["distance"],
                "match_type": "semantic",
            }
    except Exception:
        pass  # Fall back to substring

    # Substring fallback / supplement
    all_thoughts = store.get_thoughts(limit=100)
    query_lower = query.lower()
    substring_results = {}
    for thought in all_thoughts:
        tid = str(thought["id"])
        if query_lower in thought.get("text", "").lower():
            substring_results[tid] = {
                "card_id": f"thought_{thought['id']}",
                "original_text": thought["text"],
                "ticker": thought.get("ticker"),
                "price": thought.get("price"),
                "indicator": thought.get("indicator"),
                "created_at": thought.get("created_at"),
                "match_type": "substring",
            }

    # Merge: semantic first, then substring (dedup by id)
    merged = []
    seen = set()
    # Sort semantic results by distance
    sorted_semantic = sorted(semantic_results.values(), key=lambda x: x.get("distance", 999))
    for r in sorted_semantic:
        if r["card_id"] not in seen:
            merged.append(r)
            seen.add(r["card_id"])
    for r in substring_results.values():
        if r["card_id"] not in seen:
            merged.append(r)
            seen.add(r["card_id"])

    return merged


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