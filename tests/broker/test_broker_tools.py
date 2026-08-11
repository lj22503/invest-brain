# tests/broker/test_broker_tools.py
"""broker MCP 工具层测试 — monkeypatch get_broker_store 指向 tmp db。"""

import pytest

import src.mcp_server.tools.broker_tools as bt
from src.mcp_server.broker.store import BrokerStore

HTSC_CSV = (
    "成交日期,成交时间,证券代码,证券名称,买卖标志,成交价格,成交数量,成交金额,"
    "佣金,印花税,过户费,其他费,发生金额,本次余额,合同编号,股东账号\n"
    "2026-07-15,09:35:12,600519,贵州茅台,证券买入,1500.00,100,150000.00,"
    "5.00,0.00,0.60,0.00,-150005.60,1000000.00,HT20260715001,A123456789\n"
    "2026-07-20,14:22:03,600519,贵州茅台,证券卖出,1550.00,100,155000.00,"
    "5.00,77.50,0.60,0.00,154916.90,1154916.90,HT20260720002,A123456789\n"
)


@pytest.fixture()
def store(tmp_path) -> BrokerStore:
    return BrokerStore(db_path=str(tmp_path / "broker_tools_test.db"))


@pytest.fixture()
def patch_store(monkeypatch, store: BrokerStore):
    monkeypatch.setattr(bt, "get_broker_store", lambda: store)
    return store


def test_supported_formats(patch_store: BrokerStore):
    result = bt.supported_formats()
    broker_ids = [b["id"] for b in result["brokers"]]
    assert "htsc" in broker_ids and "citic" in broker_ids and "cms" in broker_ids
    assert "trade_date" in result["standard_fields"]


def test_import_statement_and_flow(tmp_path, patch_store: BrokerStore):
    csv_path = tmp_path / "htsc.csv"
    csv_path.write_text(HTSC_CSV, encoding="utf-8-sig")

    result = bt.import_statement(file_path=str(csv_path))
    assert result["imported_rows"] == 2
    assert result["broker"] == "htsc"
    assert result["duplicated_rows"] == 0
    assert result["first_date"] == "2026-07-15"
    assert result["last_date"] == "2026-07-20"

    # 同一文件重复导入 → 幂等跳过
    again = bt.import_statement(file_path=str(csv_path))
    assert again["imported_rows"] == 0
    assert again["error"] is None

    # 查询工具
    trades = bt.list_trades()
    assert trades["total"] == 2

    buy = bt.list_trades(side="buy")
    assert buy["total"] == 1 and buy["trades"][0]["symbol"] == "600519"

    # 统计工具
    stats = bt.get_trade_stats()
    assert stats["total_trades"] == 2
    assert stats["buy"]["amount"] == 150000.0
    assert stats["sell"]["stamp_tax"] == 77.5

    # 导入历史
    imports = bt.get_imports()
    assert len(imports["imports"]) == 1
    assert imports["imports"][0]["imported_rows"] == 2


def test_import_statement_missing_file(patch_store: BrokerStore):
    result = bt.import_statement(file_path="C:/no/such/file.csv")
    assert result["imported_rows"] == 0
    assert "不存在" in result["error"]


def test_import_statement_bad_header(tmp_path, patch_store: BrokerStore):
    bad = tmp_path / "bad.csv"
    bad.write_text("姓名,电话\n张三,138\n", encoding="utf-8")
    result = bt.import_statement(file_path=str(bad))
    assert result["imported_rows"] == 0
    assert "无法识别" in result["error"]


def test_list_trades_empty(patch_store: BrokerStore):
    result = bt.list_trades()
    assert result["total"] == 0
    assert "导入" in result["hint"]


def test_get_imports_empty(patch_store: BrokerStore):
    result = bt.get_imports()
    assert result["imports"] == []
