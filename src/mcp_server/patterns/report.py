"""模式报告生成器

生成格式化的行为模式报告
"""

from datetime import datetime
from pathlib import Path
from typing import Optional


class PatternReport:
    """行为模式报告生成器"""

    def __init__(self, output_dir: str = "data/memory/patterns/reports"):
        self.output_dir = Path(output_dir)
        if not self.output_dir.is_absolute():
            self.output_dir = Path(__file__).resolve().parents[3] / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_text(self, analysis_results: dict, period: str = "weekly") -> str:
        """
        生成文本格式报告

        Args:
            analysis_results: analyze_all() 返回的分析结果
            period: 报告周期（weekly/monthly）

        Returns:
            格式化的文本报告
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        period_label = "周报" if period == "weekly" else "月报"

        lines = [
            f"# 投资行为模式 {period_label} — {date_str}",
            "",
            "---",
            "",
        ]

        # 汇总
        total_count = sum(r.get('count', 0) for r in analysis_results.values())
        lines.append(f"## 汇总")
        lines.append(f"**检测到 {total_count} 次行为模式**")
        lines.append("")

        # 按严重程度排序
        severity_order = {'高': 0, '中': 1, '低': 2}
        sorted_results = sorted(
            analysis_results.items(),
            key=lambda x: severity_order.get(x[1].get('severity', '中'), 1)
        )

        # 高优先级模式
        high_severity = [r for r in analysis_results.values() if r.get('severity') == '高']
        if high_severity:
            lines.append("## 🚨 高优先级问题")
            for r in high_severity:
                lines.extend(self._format_single(r))
                lines.append("")
            lines.append("")

        # 所有模式详情
        lines.append("## 📊 所有模式")
        for pattern_type, result in sorted_results:
            lines.append(f"### {self._type_label(pattern_type)}")
            lines.extend(self._format_single(result))
            lines.append("")

        # 下一步建议
        lines.extend(self._next_steps(analysis_results))

        # 页脚
        lines.extend([
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        return '\n'.join(lines)

    def _type_label(self, pattern_type: str) -> str:
        """模式类型中文标签"""
        labels = {
            '追高': '追高买入',
            '过早卖出': '过早止损',
            '情绪化交易': '情绪化决策',
            '原则违反': '原则违反',
            '能力圈外': '能力圈外交易',
            'chase_patterns': '追高买入',
            'quick_sell_patterns': '过早止损',
            'emotion_trades': '情绪化决策',
            'principle_violations': '原则违反',
            'circle_of_competence_violations': '能力圈外交易'
        }
        return labels.get(pattern_type, pattern_type)

    def _format_single(self, result: dict) -> list:
        """格式化单条模式结果"""
        lines = []
        lines.append(f"**次数:** {result.get('count', 0)}")
        if result.get('last_time'):
            lines.append(f"**最近:** {result.get('last_time')[:10]}")
        lines.append(f"**严重程度:** {result.get('severity', '中')}")
        lines.append("")
        lines.append(f"**洞察:** {result.get('insight', 'N/A')}")
        lines.append("")
        lines.append(f"**建议:** {result.get('suggestion', 'N/A')}")
        return lines

    def _next_steps(self, results: dict) -> list:
        """生成下一步行动建议"""
        lines = ["## 🎯 下一步行动"]
        lines.append("")

        action_items = []

        # 按严重程度和次数排序
        for pattern_type, result in results.items():
            if result.get('severity') == '高' or result.get('count', 0) >= 3:
                action_items.append(f"- [{result.get('severity')}] {result.get('suggestion', '')[:50]}")

        if action_items:
            lines.extend(action_items[:3])  # 最多3条
        else:
            lines.append("- 继续保持当前良好的投资习惯")
            lines.append("- 记录投资决策理由，培养纪律")

        return lines

    def save_report(self, analysis_results: dict, period: str = "weekly",
                    format: str = "markdown") -> str:
        """
        保存报告到文件

        Args:
            analysis_results: 分析结果
            period: 报告周期
            format: 格式（目前只支持 markdown）

        Returns:
            保存的文件路径
        """
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"pattern_report_{period}_{date_str}.md"
        filepath = self.output_dir / filename

        if format == "markdown":
            content = self.generate_text(analysis_results, period)
        else:
            raise ValueError(f"不支持的格式: {format}")

        filepath.write_text(content, encoding='utf-8')
        return str(filepath)

    def get_latest_report(self) -> Optional[str]:
        """获取最新报告路径"""
        reports = sorted(self.output_dir.glob("pattern_report_*.md"), reverse=True)
        if reports:
            return str(reports[0])
        return None


def generate_report(analysis_results: dict, period: str = "weekly") -> str:
    """便捷函数：生成并保存报告"""
    report_gen = PatternReport()
    filepath = report_gen.save_report(analysis_results, period)
    return filepath
