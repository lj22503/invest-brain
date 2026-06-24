#!/usr/bin/env python
"""行为模式挖掘 CLI

用法:
    python patterns_cli.py              # 检测+分析+报告
    python patterns_cli.py --detect     # 仅检测
    python patterns_cli.py --analyze   # 仅分析上次检测结果
    python patterns_cli.py --report      # 生成报告
"""

import argparse
import sys
from pathlib import Path

# 添加 src 目录到 path
sys.path.insert(0, str(Path(__file__).parent / "src" / "mcp_server"))

from mcp_server.patterns.detector import PatternDetector
from mcp_server.patterns.analyzer import PatternAnalyzer
from mcp_server.patterns.report import PatternReport


def main():
    parser = argparse.ArgumentParser(description='投资行为模式挖掘')
    parser.add_argument('--detect', action='store_true', help='仅检测模式')
    parser.add_argument('--analyze', action='store_true', help='仅分析检测结果')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--db', default='data/memory/memory.db', help='数据库路径')

    args = parser.parse_args()

    db_path = Path(__file__).parent / args.db

    print(f"📊 行为模式挖掘")
    print(f"数据库: {db_path}")
    print("")

    # 检测
    if args.detect or not (args.analyze or args.report):
        print("🔍 检测行为模式...")
        detector = PatternDetector(str(db_path))
        patterns = detector.detect_all()
        count = sum(len(v) for v in patterns.values())
        print(f"   检测到 {count} 个模式")
        for ptype, precords in patterns.items():
            if precords:
                print(f"   - {ptype}: {len(precords)} 次")
        return patterns

    # 分析
    if args.analyze or args.report:
        print("🤖 分析模式...")
        detector = PatternDetector(str(db_path))
        patterns = detector.detect_all()
        analyzer = PatternAnalyzer()
        results = analyzer.analyze_all(patterns)
        for ptype, result in results.items():
            print(f"   {ptype}: {result.get('insight', 'N/A')[:50]}...")
        if args.report:
            print("\n📝 生成报告...")
            report_gen = PatternReport()
            filepath = report_gen.save_report(results)
            print(f"   报告已保存: {filepath}")
        return results

    parser.print_help()


if __name__ == "__main__":
    main()
