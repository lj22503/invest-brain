"""券商交割单交易记录 SQLite 本地存储。

遵循项目既有 SQLite 模式（参考 memory/store.py、user/store.py）：
- 默认 db 为 data/memory/broker.db（已被 .gitignore 保护，数据不出本地）
- 相对路径基于仓库根解析
- 每次操作独立连接，避免多线程/多进程共享连接问题

表结构：
- imports: 每次导入的文件批次（含文件哈希，支持幂等重复导入）
- trades:  标准化交易记录（trade_key 唯一约束，跨文件去重）
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Optional

from .parsers import trade_dedup_key


class BrokerStore:
    """SQLite-based broker statement (交割单) storage client"""

    def __init__(self, db_path: str = "data/memory/broker.db"):
        """Initialize the broker store.

        Args:
            db_path: Path to SQLite database (relative paths resolve from repo root)
        """
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            self.db_path = Path(__file__).resolve().parents[3] / self.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA encoding = 'UTF-8'")
        return conn

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()

        # 导入批次表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broker TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                source_path TEXT DEFAULT '',
                total_rows INTEGER DEFAULT 0,
                imported_rows INTEGER DEFAULT 0,
                skipped_rows INTEGER DEFAULT 0,
                first_date TEXT DEFAULT '',
                last_date TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_imports_file_hash ON imports (file_hash)"
        )

        # 标准化交易记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_key TEXT UNIQUE NOT NULL,
                broker TEXT NOT NULL,
                account TEXT DEFAULT '',
                trade_date TEXT NOT NULL,
                trade_time TEXT DEFAULT '',
                side TEXT DEFAULT 'unknown',
                symbol TEXT NOT NULL,
                symbol_name TEXT DEFAULT '',
                price REAL DEFAULT 0,
                quantity INTEGER DEFAULT 0,
                amount REAL DEFAULT 0,
                commission REAL DEFAULT 0,
                stamp_tax REAL DEFAULT 0,
                transfer_fee REAL DEFAULT 0,
                other_fee REAL DEFAULT 0,
                fee REAL DEFAULT 0,
                net_amount REAL DEFAULT 0,
                balance REAL DEFAULT 0,
                contract_no TEXT DEFAULT '',
                source_file TEXT DEFAULT '',
                import_id INTEGER,
                raw TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_date ON trades (trade_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades (symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_broker ON trades (broker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_import ON trades (import_id)")

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # 导入批次
    # ------------------------------------------------------------------

    def find_import_by_hash(self, file_hash: str) -> Optional[dict]:
        """按文件哈希查找历史导入记录（用于重复导入幂等跳过）。"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM imports WHERE file_hash = ?", (file_hash,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))

    def create_import(
        self,
        broker: str,
        file_name: str,
        file_hash: str,
        source_path: str = "",
        total_rows: int = 0,
        imported_rows: int = 0,
        skipped_rows: int = 0,
        first_date: str = "",
        last_date: str = "",
    ) -> int:
        """记录一次导入批次，返回 import_id。"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO imports
               (broker, file_name, file_hash, source_path, total_rows,
                imported_rows, skipped_rows, first_date, last_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (broker, file_name, file_hash, source_path, total_rows,
             imported_rows, skipped_rows, first_date, last_date),
        )
        conn.commit()
        import_id = cursor.lastrowid
        conn.close()
        return import_id

    def list_imports(self, limit: int = 20) -> list:
        """返回最近导入批次列表。"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM imports ORDER BY id DESC LIMIT ?",
            (max(1, min(int(limit), 200)),),
        )
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        return [dict(zip(cols, r)) for r in rows]

    def import_stats_update(
        self,
        import_id: int,
        imported_rows: int,
        first_date: str = "",
        last_date: str = "",
    ) -> None:
        """写入交易入库后回填批次统计（成功行数 + 日期范围）。"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE imports SET imported_rows = ?, first_date = ?, last_date = ?
               WHERE id = ?""",
            (imported_rows, first_date, last_date, import_id),
        )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # 交易记录
    # ------------------------------------------------------------------

    def add_trades(self, import_id: int, records: list) -> dict:
        """批量写入标准化交易记录（trade_key 去重）。

        Returns:
            {"inserted": n, "duplicated": n}
        """
        inserted = 0
        duplicated = 0
        conn = self._get_conn()
        cursor = conn.cursor()
        for rec in records:
            key = trade_dedup_key(rec)
            try:
                cursor.execute(
                    """INSERT INTO trades
                       (trade_key, broker, account, trade_date, trade_time, side,
                        symbol, symbol_name, price, quantity, amount,
                        commission, stamp_tax, transfer_fee, other_fee, fee,
                        net_amount, balance, contract_no, source_file, import_id, raw)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        key,
                        rec.get("broker", ""),
                        rec.get("account", ""),
                        rec.get("trade_date", ""),
                        rec.get("trade_time", ""),
                        rec.get("side", "unknown"),
                        rec.get("symbol", ""),
                        rec.get("symbol_name", ""),
                        rec.get("price", 0) or 0,
                        rec.get("quantity", 0) or 0,
                        rec.get("amount", 0) or 0,
                        rec.get("commission", 0) or 0,
                        rec.get("stamp_tax", 0) or 0,
                        rec.get("transfer_fee", 0) or 0,
                        rec.get("other_fee", 0) or 0,
                        rec.get("fee", 0) or 0,
                        rec.get("net_amount", 0) or 0,
                        rec.get("balance", 0) or 0,
                        rec.get("contract_no", "") or "",
                        rec.get("source_file", "") or "",
                        import_id,
                        rec.get("raw", "") or "",
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                duplicated += 1
        conn.commit()
        conn.close()
        return {"inserted": inserted, "duplicated": duplicated}

    def list_trades(
        self,
        start_date: str = "",
        end_date: str = "",
        symbol: str = "",
        side: str = "",
        broker: str = "",
        limit: int = 200,
    ) -> list:
        """按条件查询交易记录（时间倒序）。"""
        clauses = []
        params = []
        if start_date:
            clauses.append("trade_date >= ?")
            params.append(start_date)
        if end_date:
            clauses.append("trade_date <= ?")
            params.append(end_date)
        if symbol:
            clauses.append("symbol LIKE ?")
            params.append(f"%{symbol.upper()}%")
        if side:
            clauses.append("side = ?")
            params.append(side)
        if broker:
            clauses.append("broker = ?")
            params.append(broker)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(max(1, min(int(limit), 2000)))

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM trades {where} ORDER BY trade_date DESC, trade_time DESC, id DESC LIMIT ?",
            params,
        )
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        return [dict(zip(cols, r)) for r in rows]

    def get_trade_stats(
        self,
        start_date: str = "",
        end_date: str = "",
        broker: str = "",
    ) -> dict:
        """汇总交易统计：买卖笔数/股数/金额、费用、净额、持仓标的数等。"""
        clauses = []
        params = []
        if start_date:
            clauses.append("trade_date >= ?")
            params.append(start_date)
        if end_date:
            clauses.append("trade_date <= ?")
            params.append(end_date)
        if broker:
            clauses.append("broker = ?")
            params.append(broker)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        conn = self._get_conn()
        cursor = conn.cursor()

        def agg(side_where: str = "") -> dict:
            extra = ""
            if side_where:
                extra = f"WHERE {side_where}" if not where else f"AND {side_where}"
            cursor.execute(
                f"""SELECT COUNT(*), COALESCE(SUM(quantity),0), COALESCE(SUM(amount),0),
                           COALESCE(SUM(commission),0), COALESCE(SUM(stamp_tax),0),
                           COALESCE(SUM(transfer_fee),0), COALESCE(SUM(other_fee),0),
                           COALESCE(SUM(fee),0)
                    FROM trades {where} {extra}""".replace("  ", " "),
                params,
            )
            r = cursor.fetchone()
            return {
                "count": r[0],
                "quantity": r[1],
                "amount": round(r[2], 2),
                "commission": round(r[3], 2),
                "stamp_tax": round(r[4], 2),
                "transfer_fee": round(r[5], 2),
                "other_fee": round(r[6], 2),
                "fee": round(r[7], 2),
            }

        buy = agg("side = 'buy'")
        sell = agg("side = 'sell'")

        cursor.execute(f"SELECT COUNT(DISTINCT symbol) FROM trades {where}", params)
        symbols = cursor.fetchone()[0]

        cursor.execute(
            f"""SELECT MIN(trade_date), MAX(trade_date) FROM trades {where}""", params
        )
        first_date, last_date = cursor.fetchone()
        conn.close()

        return {
            "buy": buy,
            "sell": sell,
            "total_trades": buy["count"] + sell["count"],
            "distinct_symbols": symbols,
            "first_date": first_date,
            "last_date": last_date,
        }


# Singleton instance
_broker_store: Optional[BrokerStore] = None


def get_broker_store() -> BrokerStore:
    """Get the singleton broker store instance"""
    global _broker_store
    if _broker_store is None:
        _broker_store = BrokerStore()
    return _broker_store
