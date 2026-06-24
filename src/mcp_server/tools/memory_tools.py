"""Memory system tools - get_user_profile, record_decision, get_behavior_patterns"""

import re
import time
from typing import Optional
from collections import Counter
from mcp.server.fastmcp import FastMCP

from ..memory.store import get_memory_store
from ..patterns.detector import PatternDetector

memory_tools = FastMCP("memory-tools")


def _mock_llm_extract_profile(thoughts: list) -> dict:
    """
    Mock LLM profile extraction - analyze thoughts to infer user profile.
    Replace with real LLM call when API key is configured.
    """
    if not thoughts:
        return {
            "risk_preference": "unknown",
            "circle_of_competence": [],
            "investment_principles": [],
            "experience_level": "unknown",
        }

    # Simple keyword-based inference
    all_text = " ".join([t.get("text", "") for t in thoughts]).lower()

    # Risk preference
    if any(w in all_text for w in ["保守", "安全", "低风险", "稳定"]):
        risk = "conservative"
    elif any(w in all_text for w in ["激进", "高风险", "成长", "弹性"]):
        risk = "aggressive"
    else:
        risk = "moderate"

    # Circle of competence - extract tickers
    tickers = [t.get("ticker") for t in thoughts if t.get("ticker")]
    top_tickers = [t for t, _ in Counter(tickers).most_common(5)]

    # Investment principles - extract recurring patterns
    principle_keywords = ["护城河", "安全边际", "周期", "价值", "成长", "本分", "能力圈"]
    found_principles = [kw for kw in principle_keywords if kw in all_text]

    return {
        "risk_preference": risk,
        "circle_of_competence": top_tickers,
        "investment_principles": found_principles,
        "experience_level": "unknown",
    }


def _analyze_behavior_patterns(decisions: list) -> list:
    """
    Analyze decisions to identify behavior patterns.
    """
    if len(decisions) < 3:
        return []

    patterns = []
    all_text = " ".join([d.get("reason", "") for d in decisions]).lower()
    actions = [d.get("action") for d in decisions]

    # Pattern: frequent buying vs selling
    buy_count = actions.count("buy")
    sell_count = actions.count("sell")
    if buy_count > sell_count * 2:
        patterns.append({
            "pattern": "倾向于买入",
            "description": f"历史决策中买入次数({buy_count})远多于卖出({sell_count})",
            "confidence": "medium"
        })

    # Pattern: price-based decisions
    if "价格" in all_text or "估值" in all_text:
        patterns.append({
            "pattern": "关注价格/估值",
            "description": "决策中经常提及价格或估值因素",
            "confidence": "high"
        })

    # Pattern: principle-based decisions
    if any(w in all_text for w in ["护城河", "安全边际", "能力圈"]):
        patterns.append({
            "pattern": "遵循投资原则",
            "description": "决策中引用价值投资原则（护城河、安全边际等）",
            "confidence": "high"
        })

    return patterns


@memory_tools.tool()
def get_user_profile() -> dict:
    """
    Get user investment profile.

    Returns:
        dict: User profile including risk preference, circle of competence, investment principles
    """
    store = get_memory_store()
    thoughts = store.get_thoughts(limit=100)

    profile = _mock_llm_extract_profile(thoughts)
    return profile


@memory_tools.tool()
def record_decision(data: dict) -> dict:
    """
    Record an investment decision made by the user.

    Args:
        data: Decision data including ticker, action (buy/sell/hold), price, reason, timestamp

    Returns:
        dict: Confirmation of recorded decision
    """
    ticker = data.get("ticker", "UNKNOWN")
    action = data.get("action", "hold")
    price = data.get("price")
    reason = data.get("reason", "")

    store = get_memory_store()
    decision_id = store.add_decision(
        ticker=ticker,
        action=action,
        price=price,
        reason=reason
    )

    # Auto-run pattern detection on new decision
    try:
        detector = PatternDetector()
        all_patterns = detector.detect_all()
        for pattern_type, records in all_patterns.items():
            if records:
                detector.save_patterns(records, pattern_type)
    except Exception:
        pass  # Detection failures should not block decision recording

    return {
        "decision_id": decision_id,
        "recorded": True,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


@memory_tools.tool()
def get_behavior_patterns() -> list:
    """
    Get identified behavior patterns from user's investment history.

    Returns:
        list: Behavior patterns like "tends to buy on price drops", "stops loss too early"
    """
    store = get_memory_store()

    # Get all decisions for pattern analysis
    conn = store._get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM decisions ORDER BY created_at DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    decisions = [
        {"id": r[0], "ticker": r[1], "action": r[2], "price": r[3],
         "reason": r[4], "created_at": r[5]}
        for r in rows
    ]

    patterns = _analyze_behavior_patterns(decisions)
    return patterns