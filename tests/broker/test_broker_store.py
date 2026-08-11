# tests/broker/test_broker_store.py
"""BrokerStore SQLite 存储测试 — 建表/入库/去重/查询/统计/导入批次。"""

import pytest

from src.mcp_server.broker.store import BrokerStore


@pytest.fixture()
def store(tmp_path) -> BrokerStore:
    return BrokerStore(db_path=str(tmp_path / "broker_test.db"))


def _rec(contract_no: str, date: str = "2026-07-15", side: str = "buy",
         symbol: str = "600519", price: float = 1500.0, quantity: int = 100,
         fee: float = 5.6, net: float = -150005.6, broker: str = "htsc",
         amount: float = 0.0, stamp_tax: float = 0.0, transfer_fee: float = 0.6) -> dict:
    return {
        "broker": broker, "account": "A1", "trade_date": date, "trade_time": "09:30:00",
        "side": side, "symbol": symbol, "symbol_name": "贵州茅台",
        "price": price, "quantity": quantity, "amount": amount or price * quantity,
        "commission": 5.0, "stamp_tax": stamp_tax, "transfer_fee": transfer_fee, "other_fee": 0.0,
        "fee": fee, "net_amount": net, "balance": 1000000.0,
        "contract_no": contract_no, "source_file": "ht.csv", "raw": "raw",
    }


def test_init_creates_tables(store: BrokerStore):
    import sqlite3
    conn = sqlite3.connect(str(store.db_path))
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"imports", "trades"} <= tables


def test_add_trades_dedup(store: BrokerStore):
    rec = _rec("C1")
    r1 = store.add_trades(import_id=1, records=[rec])
    r2 = store.add_trades(import_id=2, records=[rec])
    assert r1 == {"inserted": 1, "duplicated": 0}
    assert r2 == {"inserted": 0, "duplicated": 1}


def test_list_trades_filters(store: BrokerStore):
    store.add_trades(1, [_rec("C1", date="2026-07-15"),
                         _rec("C2", date="2026-07-20", side="sell", net=154916.9)])
    all_trades = store.list_trades()
    assert len(all_trades) == 2

    buy = store.list_trades(side="buy")
    assert len(buy) == 1 and buy[0]["contract_no"] == "C1"

    ranged = store.list_trades(start_date="2026-07-18", end_date="2026-07-31")
    assert len(ranged) == 1 and ranged[0]["contract_no"] == "C2"

    sym = store.list_trades(symbol="600519")
    assert len(sym) == 2


def test_get_trade_stats(store: BrokerStore):
    store.add_trades(1, [
        _rec("C1", date="2026-07-15", side="buy", quantity=100, amount=150000,
             fee=5.6, net=-150005.6),
        _rec("C2", date="2026-07-20", side="sell", quantity=100, amount=155000,
             stamp_tax=77.5, transfer_fee=0.6, fee=83.1, net=154916.9),
        _rec("C3", date="2026-07-21", side="buy", symbol="000001", price=11.5,
             quantity=1000, amount=11500, fee=5.0, net=-11505.0),
    ])
    stats = store.get_trade_stats()
    assert stats["total_trades"] == 3
    assert stats["buy"]["count"] == 2
    assert stats["sell"]["count"] == 1
    assert stats["buy"]["quantity"] == 1100
    assert stats["buy"]["amount"] == 161500.0
    assert stats["sell"]["stamp_tax"] == 77.5
    assert stats["distinct_symbols"] == 2
    assert stats["first_date"] == "2026-07-15"
    assert stats["last_date"] == "2026-07-21"

    filtered = store.get_trade_stats(start_date="2026-07-20")
    assert filtered["total_trades"] == 2


def test_import_flow_idempotent(store: BrokerStore):
    iid = store.create_import(
        broker="htsc", file_name="a.csv", file_hash="h1",
        source_path="/tmp/a.csv", total_rows=2, imported_rows=0, skipped_rows=0,
    )
    store.import_stats_update(iid, imported_rows=2, first_date="2026-07-15", last_date="2026-07-20")

    found = store.find_import_by_hash("h1")
    assert found is not None
    assert found["imported_rows"] == 2
    assert found["first_date"] == "2026-07-15"

    assert store.find_import_by_hash("h2") is None

    imports = store.list_imports()
    assert len(imports) == 1
    assert imports[0]["broker"] == "htsc"
