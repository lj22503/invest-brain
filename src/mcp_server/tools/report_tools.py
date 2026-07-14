"""Periodic report tools — run_scheduled_report"""

from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

from ..patterns.detector import PatternDetector
from ..patterns.analyzer import PatternAnalyzer
from ..patterns.report import PatternReport

report_tools = FastMCP("report-tools")

_PERIOD_LABELS = {
    "week": "本周",
    "month": "本月",
}

_POSITIVE_HIGHLIGHTS = [
    "本周未违反投资原则，纪律保持良好",
    "所有操作均在能力圈内，知行合一",
    "决策模式稳定，无情绪化交易迹象",
]


def _period_range(range_type: str) -> str:
    """Build human-readable period string."""
    today = datetime.now()
    if range_type == "week":
        start = today - timedelta(days=today.weekday())
        return f"{start.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}"
    else:  # month
        return today.strftime("%Y年%m月")


@report_tools.tool()
def run_scheduled_report(range: str = "week") -> dict:
    """
    Generate a behavior pattern report for this week or month.
    Designed to be called on a schedule by the agent (e.g. every Sunday).

    Args:
        range: Report range — "week" (default) or "month"

    Returns:
        dict: Compact report with summary, insights, highlight, and report file path
    """
    period_label = _PERIOD_LABELS.get(range, "本周")
    date_range = _period_range(range)

    # Detect and save patterns
    detector = PatternDetector()
    all_patterns = detector.detect_all()
    for pattern_type, records in all_patterns.items():
        if records:
            detector.save_patterns(records, pattern_type)

    # Analyze
    analyzer = PatternAnalyzer()
    analysis = analyzer.analyze_all(all_patterns)

    # Save markdown report to disk
    report_gen = PatternReport()
    filepath = report_gen.save_report(analysis, period=range)

    # Build compact summary
    summary = {}
    insights = []
    severity_order = {"高": 0, "中": 1, "低": 2}

    for pattern_type, result in sorted(
        analysis.items(),
        key=lambda x: severity_order.get(x[1].get("severity", "中"), 1),
    ):
        cnt = result.get("count", 0)
        summary[pattern_type] = cnt
        insights.append({
            "type": pattern_type,
            "count": cnt,
            "severity": result.get("severity", "中"),
            "insight": result.get("insight", ""),
            "suggestion": result.get("suggestion", ""),
        })

    # Pick highlight
    high_severity = [i for i in insights if i["severity"] == "高"]
    if not high_severity:
        highlight = _POSITIVE_HIGHLIGHTS[len(analysis) % len(_POSITIVE_HIGHLIGHTS)]
    else:
        top = high_severity[0]
        highlight = f"重点关注：{top['type']}（{top['count']}次），建议{top['suggestion'][:40]}"

    return {
        "period": period_label,
        "date_range": date_range,
        "summary": summary,
        "insights": insights,
        "highlight": highlight,
        "report_file": filepath,
    }
