"""行为模式挖掘模块

检测用户投资行为中的重复模式，生成洞察和建议
"""

from .detector import PatternDetector, detect_patterns, EMOTION_KEYWORDS
from .analyzer import PatternAnalyzer, analyze_patterns
from .report import PatternReport, generate_report

__all__ = [
    'PatternDetector',
    'detect_patterns',
    'EMOTION_KEYWORDS',
    'PatternAnalyzer',
    'analyze_patterns',
    'PatternReport',
    'generate_report',
]
