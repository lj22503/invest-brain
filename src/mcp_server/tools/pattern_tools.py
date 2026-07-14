"""Behavior pattern detection tools - run_pattern_detection, get_pattern_summary, get_pattern_report"""

import time
from mcp.server.fastmcp import FastMCP

from ..patterns.detector import PatternDetector
from ..patterns.report import PatternReport

pattern_tools = FastMCP("pattern-tools")


@pattern_tools.tool()
def run_pattern_detection() -> dict:
    """
    Run behavior pattern detection on all recorded decisions and thoughts.

    Detects: 追高, 过早卖出, 情绪化交易, 原则违反.
    Results are saved to the behavior_patterns table.

    Returns:
        dict: Detection results with count and pattern list
    """
    detector = PatternDetector()
    all_patterns = detector.detect_all()

    saved_count = 0
    new_patterns = []

    for pattern_type, records in all_patterns.items():
        if not records:
            continue
        count = detector.save_patterns(records, pattern_type)
        saved_count += count

        # Build simplified view of new patterns
        for r in records:
            new_patterns.append({
                "type": r.get("type", pattern_type),
                "ticker": r.get("ticker"),
                "severity": r.get("severity", "中"),
                "trigger": str(r.get("trigger", r.get("reason", "")))[:100],
                "created_at": r.get("created_at"),
            })

    return {
        "new_patterns_found": saved_count,
        "patterns": new_patterns,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


@pattern_tools.tool()
def get_pattern_summary() -> dict:
    """
    Get cumulative summary of all detected behavior patterns.

    Returns:
        dict: Pattern type -> {count, last_seen}, plus prompt_hint for
              the agent to decide whether to proactively engage the user
    """
    detector = PatternDetector()
    summary = detector.get_pattern_summary()

    # Build prompt_hint for agent-side proactive engagement
    hint = _build_prompt_hint(summary)

    return {
        "patterns": summary,
        "prompt_hint": hint,
    }


def _build_prompt_hint(patterns: dict) -> str:
    """Build a natural-language hint for the agent to decide on proactive nudging."""
    if not patterns:
        return ""

    # High-severity: patterns with >=5 occurrences
    high = [(t, d["count"]) for t, d in patterns.items() if d["count"] >= 5]
    if high:
        top = max(high, key=lambda x: x[1])
        return (
            f"检测到累计{top[1]}次「{top[0]}」行为模式，"
            "建议在对话中主动提醒用户查看行为分析报告"
        )

    # Medium: patterns with >=3 occurrences
    mid = [(t, d["count"]) for t, d in patterns.items() if d["count"] >= 3]
    if mid:
        names = "、".join(f"「{t}」({c}次)" for t, c in mid[:2])
        return f"检测到{names}等行为模式，可在用户进行下次交易前提醒"

    return ""


@pattern_tools.tool()
def get_pattern_report(period: str = "weekly") -> dict:
    """
    Generate a behavior pattern report in Markdown format.

    Args:
        period: Report period — "weekly" (default) or "monthly"

    Returns:
        dict: Report path and full Markdown content
    """
    detector = PatternDetector()
    report_gen = PatternReport()

    # Run detection first to get fresh results
    all_patterns = detector.detect_all()

    if not any(all_patterns.values()):
        return {
            "report_path": None,
            "content": "# 行为模式报告\n\n暂未检测到任何行为模式。请先记录投资决策后调用 run_pattern_detection。",
            "period": period,
        }

    # Save fresh patterns
    for pattern_type, records in all_patterns.items():
        if records:
            detector.save_patterns(records, pattern_type)

    # Generate and save report
    filepath = report_gen.save_report(all_patterns, period=period)
    content = report_gen.generate_text(all_patterns, period=period)

    return {
        "report_path": filepath,
        "content": content,
        "period": period,
    }
