"""行为模式检测器

检测用户投资行为中的重复模式：
- 追高
- 过早卖出
- 情绪化交易
- 原则违反
- 能力圈外交易
"""

import re
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path


# 情绪关键词列表
EMOTION_KEYWORDS = [
    '焦虑', '睡不着', '担心', '害怕', '恐慌',
    '兴奋', '忍不住', '冲动', '后悔', '懊恼'
]

# 追高阈值：前N日涨幅超过X%
CHASE_THRESHOLD_DAYS = 20
CHASE_THRESHOLD_RETURN = 0.20  # 20%

# 过早卖出阈值：持有天数少于N天
QUICK_SELL_DAYS = 5

# 情绪窗口：情绪词后N小时内交易
EMOTION_WINDOW_HOURS = 24


class PatternDetector:
    """行为模式检测器"""

    def __init__(self, db_path: str = "data/memory/memory.db"):
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            self.db_path = Path(__file__).resolve().parents[2] / db_path

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA encoding = 'UTF-8'")
        return conn

    def detect_all(self) -> dict:
        """检测所有模式"""
        return {
            '追高': self.detect_chase(),
            '过早卖出': self.detect_quick_sell(),
            '情绪化交易': self.detect_emotion_trades(),
            '原则违反': self.detect_principle_violations(),
            '能力圈外': self.detect_coc_violations(),
        }

    def detect_chase(self, threshold_days: int = CHASE_THRESHOLD_DAYS,
                     threshold_return: float = CHASE_THRESHOLD_RETURN) -> list:
        """
        检测追高模式

        逻辑：买入前N日涨幅超过阈值
        注意：需要配合行情数据，暂时返回基于思想的模式
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # 获取所有买入决策
        cursor.execute("""
            SELECT id, ticker, action, price, reason, created_at
            FROM decisions
            WHERE action IN ('buy', '买入')
            ORDER BY created_at DESC
            LIMIT 50
        """)
        buys = cursor.fetchall()
        conn.close()

        patterns = []

        # 简单启发式检测：
        # 1. 如果reason中包含"追"、"涨"、"热门"等词
        # 2. 如果reason中包含"忍不住"、"冲动"等词
        chase_keywords = ['追', '涨', '热门', '忍不住', '冲动', '大家都', '朋友圈']

        for buy in buys:
            buy_id, ticker, action, price, reason, created_at = buy
            if reason:
                for keyword in chase_keywords:
                    if keyword in reason:
                        patterns.append({
                            'type': '追高',
                            'decision_id': buy_id,
                            'ticker': ticker,
                            'trigger': reason[:100],
                            'keyword': keyword,
                            'created_at': created_at,
                            'severity': '高' if keyword in ['忍不住', '冲动'] else '中'
                        })
                        break

        return patterns

    def detect_quick_sell(self, min_hold_days: int = QUICK_SELL_DAYS) -> list:
        """
        检测过早卖出模式

        逻辑：买入后N天内就卖出
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # 获取所有 buy 和 sell 记录，按 ticker 分组
        cursor.execute("""
            SELECT id, ticker, action, price, reason, created_at
            FROM decisions
            WHERE action IN ('buy', 'sell', '买入', '卖出')
            ORDER BY ticker, created_at
        """)
        all_decisions = cursor.fetchall()
        conn.close()

        patterns = []
        buy_records = {}  # ticker -> buy record

        for decision in all_decisions:
            dec_id, ticker, action, price, reason, created_at = decision

            if action in ('buy', '买入'):
                buy_records[ticker] = {
                    'id': dec_id,
                    'price': price,
                    'reason': reason,
                    'created_at': created_at
                }
            elif action in ('sell', '卖出') and ticker in buy_records:
                buy_record = buy_records[ticker]
                buy_date = datetime.strptime(buy_record['created_at'], '%Y-%m-%d %H:%M:%S')
                sell_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                hold_days = (sell_date - buy_date).days

                if hold_days < min_hold_days:
                    # 判断亏损还是盈利
                    if buy_record['price'] and price:
                        pnl = (price - buy_record['price']) / buy_record['price'] * 100
                        severity = '高' if pnl < 0 else '中'
                    else:
                        pnl = None
                        severity = '中'

                    patterns.append({
                        'type': '过早卖出',
                        'buy_decision_id': buy_record['id'],
                        'sell_decision_id': dec_id,
                        'ticker': ticker,
                        'hold_days': hold_days,
                        'buy_price': buy_record['price'],
                        'sell_price': price,
                        'pnl_pct': pnl,
                        'buy_reason': buy_record['reason'],
                        'created_at': created_at,
                        'severity': severity
                    })

                # 清除该ticker的buy记录
                del buy_records[ticker]

        return patterns

    def detect_emotion_trades(self, window_hours: int = EMOTION_WINDOW_HOURS) -> list:
        """
        检测情绪化交易

        逻辑：情绪词出现后N小时内有交易
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # 获取所有 thoughts
        cursor.execute("""
            SELECT id, text, ticker, created_at
            FROM thoughts
            ORDER BY created_at DESC
            LIMIT 100
        """)
        thoughts = cursor.fetchall()

        # 获取所有 decisions
        cursor.execute("""
            SELECT id, ticker, action, created_at
            FROM decisions
            ORDER BY created_at
        """)
        decisions = cursor.fetchall()
        conn.close()

        patterns = []
        emotion_records = []

        # 找所有情绪词匹配的 thoughts
        for thought in thoughts:
            thought_id, text, ticker, created_at = thought
            if text:
                for keyword in EMOTION_KEYWORDS:
                    if keyword in text:
                        emotion_records.append({
                            'id': thought_id,
                            'text': text[:100],
                            'ticker': ticker,
                            'keyword': keyword,
                            'created_at': created_at
                        })
                        break

        # 检查情绪词后window小时内是否有交易
        for emotion in emotion_records:
            emotion_time = datetime.strptime(emotion['created_at'], '%Y-%m-%d %H:%M:%S')
            emotion_hour = emotion_time.timestamp()

            for decision in decisions:
                dec_id, dec_ticker, action, dec_created_at = decision
                dec_time = datetime.strptime(dec_created_at, '%Y-%m-%d %H:%M:%S')
                dec_timestamp = dec_time.timestamp()

                # 在情绪词之后window小时内
                if dec_timestamp > emotion_hour:
                    hours_diff = (dec_time - emotion_time).total_seconds() / 3600
                    if hours_diff <= window_hours:
                        patterns.append({
                            'type': '情绪化交易',
                            'thought_id': emotion['id'],
                            'emotion_text': emotion['text'],
                            'emotion_keyword': emotion['keyword'],
                            'emotion_time': emotion['created_at'],
                            'decision_id': dec_id,
                            'ticker': dec_ticker,
                            'action': action,
                            'hours_after_emotion': round(hours_diff, 1),
                            'created_at': dec_created_at,
                            'severity': '高'
                        })
                        break  # 一个情绪词只匹配一次

        return patterns

    def detect_principle_violations(self) -> list:
        """
        检测原则违反

        逻辑：需要用户有原则记录 + 原则解析 + 交易比对
        当前版本：基于决策理由中的明显违反信号词
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # 获取所有决策
        cursor.execute("""
            SELECT id, ticker, action, price, reason, created_at
            FROM decisions
            WHERE reason IS NOT NULL AND reason != ''
            ORDER BY created_at DESC
            LIMIT 50
        """)
        decisions = cursor.fetchall()
        conn.close()

        patterns = []

        # 违反信号词
        violation_signals = [
            ('违背原则', '高'),
            ('没遵守', '中'),
            ('违反', '高'),
            ('说了不', '中'),
            ('知道但还是', '高'),
        ]

        for decision in decisions:
            dec_id, ticker, action, price, reason, created_at = decision
            for signal, severity in violation_signals:
                if signal in reason:
                    patterns.append({
                        'type': '原则违反',
                        'decision_id': dec_id,
                        'ticker': ticker,
                        'action': action,
                        'reason': reason[:200],
                        'signal': signal,
                        'created_at': created_at,
                        'severity': severity
                    })
                    break

        return patterns

    def detect_coc_violations(self) -> list:
        """
        检测能力圈外交易

        逻辑：用户标记为不懂的行业，却买了该行业
        需要用户自评能力圈数据（当前版本返回空）
        """
        # TODO: 实现需要用户自评能力圈
        return []

    def save_patterns(self, patterns: list, pattern_type: str) -> int:
        """保存检测到的模式到数据库"""
        conn = self._get_conn()
        cursor = conn.cursor()
        count = 0

        for p in patterns:
            pattern_id = f"{pattern_type}_{p.get('decision_id', p.get('created_at') or datetime.now().strftime('%Y%m%d%H%M%S'))}"

            cursor.execute("""
                INSERT OR REPLACE INTO behavior_patterns
                (id, pattern_type, trigger_content, context, happened_at, severity, times_count)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                pattern_id,
                p.get('type', pattern_type),
                str(p.get('trigger', '')[:500]),
                str(p.get('reason', '')[:500] if p.get('reason') else None),
                p.get('created_at'),
                p.get('severity', '中'),
            ))
            count += 1

        conn.commit()
        conn.close()
        return count

    def get_pattern_summary(self) -> dict:
        """获取模式汇总"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT pattern_type, COUNT(*) as count, MAX(happened_at)
            FROM behavior_patterns
            GROUP BY pattern_type
        """)
        rows = cursor.fetchall()
        conn.close()

        return {
            row[0]: {'count': row[1], 'last_seen': row[2]}
            for row in rows
        }


def detect_patterns(db_path: str = "data/memory/memory.db") -> dict:
    """便捷函数：检测所有模式"""
    detector = PatternDetector(db_path)
    return detector.detect_all()
