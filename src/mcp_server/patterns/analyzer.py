"""模式分析器

用 LLM 辅助分析行为模式，生成洞察和建议
scene: pattern_analysis (DeepSeek-V4-Pro + thinking)
"""

import os
import json
from typing import Optional
from datetime import datetime

from ..llm import get_deepseek_client


class PatternAnalyzer:
    """行为模式分析器"""

    def __init__(self):
        """初始化分析器，使用全局 DeepSeek 客户端"""
        self.client = get_deepseek_client()

    def _call_llm(self, prompt: str) -> str:
        """调用 DeepSeek（scene: pattern_analysis）"""
        if self.client is None:
            raise RuntimeError("DEEPSEEK_API_KEY not configured")

        return self.client.chat_simple(prompt, scene="pattern_analysis")

    def analyze_pattern(self, pattern_records: list, pattern_type: str) -> dict:
        """
        分析单一类型的模式

        Args:
            pattern_records: 该类型的多次模式记录
            pattern_type: 模式类型

        Returns:
            包含洞察和建议的字典
        """
        if not pattern_records:
            return {
                'type': pattern_type,
                'count': 0,
                'insight': '未发现该模式',
                'suggestion': ''
            }

        # 格式化记录
        formatted = self._format_records(pattern_records, pattern_type)

        prompt = f"""你是一位投资行为分析师。用户有以下 {len(pattern_records)} 次 '{pattern_type}' 行为：

{formatted}

请分析：
1. 共同点是什么？（时间/情绪/市场环境/触发因素）
2. 可能的根因是什么？
3. 具体、可操作的改进建议是什么？

请用简洁的中文回复，格式：
### 洞察
[1-2句话的核心发现]

### 建议
[1条具体可操作的建议]

### 严重程度
[高/中/低，基于频率和影响]"""

        try:
            response = self._call_llm(prompt)
            return self._parse_response(pattern_type, pattern_records, response)
        except Exception as e:
            return self._fallback_analysis(pattern_type, pattern_records, str(e))

    def _format_records(self, records: list, pattern_type: str) -> str:
        """格式化记录为文本"""
        lines = []
        for i, r in enumerate(records[:10], 1):  # 最多10条
            if pattern_type == '追高':
                lines.append(f"{i}. {r.get('created_at', 'N/A')} | ticker:{r.get('ticker', 'N/A')} | 触发词:{r.get('keyword', 'N/A')} | 理由:{r.get('trigger', 'N/A')[:50]}")
            elif pattern_type == '过早卖出':
                lines.append(f"{i}. ticker:{r.get('ticker', 'N/A')} | 持有:{r.get('hold_days', 'N')}天 | 盈亏:{r.get('pnl_pct', 'N')}% | 理由:{r.get('buy_reason', 'N/A')[:50]}")
            elif pattern_type == '情绪化交易':
                lines.append(f"{i}. {r.get('created_at', 'N/A')} | 情绪词:{r.get('emotion_keyword', 'N/A')} | 交易:{r.get('action', 'N/A')} | 情绪内容:{r.get('emotion_text', 'N/A')[:30]}")
            elif pattern_type == '原则违反':
                lines.append(f"{i}. {r.get('created_at', 'N/A')} | ticker:{r.get('ticker', 'N/A')} | 信号:{r.get('signal', 'N/A')} | 理由:{r.get('reason', 'N/A')[:50]}")
            else:
                lines.append(f"{i}. {r}")

        return '\n'.join(lines)

    def _parse_response(self, pattern_type: str, records: list, response: str) -> dict:
        """解析 LLM 响应"""
        insight = ''
        suggestion = ''
        severity = '中'

        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if '洞察' in line:
                current_section = 'insight'
            elif '建议' in line or '改进' in line:
                current_section = 'suggestion'
            elif '严重' in line or '程度' in line:
                current_section = 'severity'
            elif current_section and line and not line.startswith('#'):
                if current_section == 'insight':
                    insight += line + ' '
                elif current_section == 'suggestion':
                    suggestion += line + ' '
                elif current_section == 'severity':
                    if '高' in line:
                        severity = '高'
                    elif '低' in line:
                        severity = '低'

        return {
            'type': pattern_type,
            'count': len(records),
            'last_time': records[0].get('created_at', 'N/A') if records else None,
            'insight': insight.strip() or self._default_insight(pattern_type),
            'suggestion': suggestion.strip() or self._default_suggestion(pattern_type),
            'severity': severity,
            'raw_response': response
        }

    def _default_insight(self, pattern_type: str) -> str:
        """默认洞察（LLM 不可用时"""
        defaults = {
            '追高': '倾向于在市场上涨时追入，可能受 FOMO 情绪影响',
            '过早卖出': '持有时间较短，可能缺乏耐心或风险偏好较高',
            '情绪化交易': '交易决策受情绪影响，可能需要更多冷静期',
            '原则违反': '实际行为与声称原则不一致，需要重新审视原则或加强执行',
            '能力圈外': '交易了自评能力圈外的标的，风险较高'
        }
        return defaults.get(pattern_type, '发现行为模式')

    def _default_suggestion(self, pattern_type: str) -> str:
        """默认建议（LLM 不可用时）"""
        defaults = {
            '追高': '设置"冷静期"：连续上涨后等待24小时再决策',
            '过早卖出': '制定持有期规则：如无基本面变化，最少持有N天',
            '情绪化交易': '记录情绪触发词，下次看到时强制等待再决策',
            '原则违反': '重新审视原则的可行性，或加强执行自律',
            '能力圈外': '先学习行业知识，懂了再交易'
        }
        return defaults.get(pattern_type, '建议深入复盘')

    def _fallback_analysis(self, pattern_type: str, records: list, error: str) -> dict:
        """LLM 不可用时的降级分析"""
        return {
            'type': pattern_type,
            'count': len(records),
            'last_time': records[0].get('created_at', 'N/A') if records else None,
            'insight': self._default_insight(pattern_type),
            'suggestion': self._default_suggestion(pattern_type),
            'severity': '中',
            'error': error
        }

    def analyze_all(self, patterns: dict) -> dict:
        """
        分析所有模式

        Args:
            patterns: detect_all() 返回的模式字典

        Returns:
            每个模式的分析结果
        """
        results = {}
        for pattern_type, records in patterns.items():
            if records:  # 只分析有记录的模式
                results[pattern_type] = self.analyze_pattern(records, pattern_type)
        return results


def analyze_patterns(patterns: dict) -> dict:
    """便捷函数：分析所有模式"""
    analyzer = PatternAnalyzer()
    return analyzer.analyze_all(patterns)
