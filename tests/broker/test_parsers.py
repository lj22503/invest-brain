# tests/broker/test_parsers.py
"""券商交割单 CSV 解析器测试 — 覆盖多券商格式/编码/单位/方向归一化。"""

import pytest

from src.mcp_server.broker import parsers

# 华泰证券样式（UTF-8 + BOM，字段最全）
HTSC_CSV = (
    "\ufeff成交日期,成交时间,证券代码,证券名称,买卖标志,成交价格,成交数量,成交金额,"
    "佣金,印花税,过户费,其他费,发生金额,本次余额,合同编号,股东账号\n"
    "2026-07-15,09:35:12,600519,贵州茅台,证券买入,1500.00,100,150000.00,"
    "5.00,0.00,0.60,0.00,-150005.60,1000000.00,HT20260715001,A123456789\n"
    "2026-07-20,14:22:03,600519,贵州茅台,证券卖出,1550.00,100,155000.00,"
    "5.00,77.50,0.60,0.00,154916.90,1154916.90,HT20260720002,A123456789\n"
    "合计,,,,,,,,,,,,,,\n"
)

# 中信证券样式（佣金+过户费合并为"手续费"，用"清算金额"）
CITIC_CSV = (
    "成交日期,证券代码,证券名称,买卖标志,成交价格,成交数量,成交金额,手续费,印花税,清算金额\n"
    "2026-07-18,000001,平安银行,买入,11.50,1000,11500.00,5.00,0.00,11505.00\n"
    "2026-07-21,000001,平安银行,卖出,12.00,1000,12000.00,5.00,6.00,11989.00\n"
    "合计,,,,\n"
)

# 招商证券样式（同华泰但无合同编号；日期用 20260715 紧凑格式）
CMS_CSV = (
    "交易日期,证券代码,证券名称,买卖方向,成交价格,成交数量,成交金额,佣金,印花税,过户费,发生金额,本次余额\n"
    "20260715,510300,沪深300ETF,买入,3.850,10000,38500.00,3.00,0.00,0.40,38503.40,500000.00\n"
    "20260722,510300,沪深300ETF,卖出,3.900,10000,39000.00,3.00,19.50,0.40,38977.10,538977.10\n"
)

# 国泰君安样式（含手数列、GBK 编码）
GTJA_CSV_GBK = (
    "交易日期,证券代码,证券名称,买卖标志,成交价格,成交手数,成交金额,佣金,印花税,过户费,清算金额\n"
    "2026-07-25,601318,中国平安,买入,48.00,2,9600.00,5.00,0.00,0.10,9605.10\n"
    "2026-07-28,601318,中国平安,卖出,50.00,2,10000.00,5.00,5.00,0.10,9989.90\n"
    "合计,,,,,\n"
)


def test_parse_htsc_utf8_bom():
    result = parsers.parse_statement_csv(HTSC_CSV.encode("utf-8-sig"), broker="auto")
    assert result["broker"] == "htsc"
    assert len(result["records"]) == 2
    rec = result["records"][0]
    assert rec["trade_date"] == "2026-07-15"
    assert rec["trade_time"] == "09:35:12"
    assert rec["symbol"] == "600519"
    assert rec["symbol_name"] == "贵州茅台"
    assert rec["side"] == "buy"
    assert rec["price"] == 1500.00
    assert rec["quantity"] == 100
    assert rec["amount"] == 150000.00
    assert rec["commission"] == 5.00
    assert rec["stamp_tax"] == 0.00
    assert rec["transfer_fee"] == 0.60
    assert rec["fee"] == 5.60
    assert rec["net_amount"] == -150005.60
    assert rec["contract_no"] == "HT20260715001"

    sell = result["records"][1]
    assert sell["side"] == "sell"
    assert sell["stamp_tax"] == 77.50
    assert sell["net_amount"] == 154916.90
    # 合计行被跳过
    assert result["skipped_rows"] >= 1


def test_parse_citic_commission_merged():
    result = parsers.parse_statement_csv(CITIC_CSV.encode("utf-8"), broker="auto")
    assert result["broker"] == "citic"
    rec = result["records"][0]
    # 手续费列归一到 commission
    assert rec["commission"] == 5.00
    assert rec["fee"] == 5.00
    # 中信清算金额为净额绝对值（正数），保留原值
    assert rec["net_amount"] == 11505.00
    assert rec["symbol"] == "000001"


def test_parse_cms_compact_date():
    result = parsers.parse_statement_csv(CMS_CSV.encode("utf-8"), broker="auto")
    assert result["broker"] == "cms"
    rec = result["records"][0]
    assert rec["trade_date"] == "2026-07-15"
    assert rec["side"] == "buy"
    assert rec["amount"] == 38500.00
    assert rec["net_amount"] == 38503.40  # 有发生金额列，不重算


def test_parse_gtja_gbk_and_lot():
    result = parsers.parse_statement_csv(GTJA_CSV_GBK.encode("gbk"), broker="auto")
    assert result["broker"] == "gtja"
    rec = result["records"][0]
    # 手数 → 股：2 手 = 200 股
    assert rec["quantity"] == 200
    assert rec["side"] == "buy"
    assert rec["net_amount"] == 9605.10


def test_parse_missing_header_raises():
    bad = "姓名,电话,备注\n张三,13800000000,test\n"
    with pytest.raises(ValueError, match="无法识别交割单表头"):
        parsers.parse_statement_csv(bad.encode("utf-8"))


def test_parse_unknown_broker_raises():
    with pytest.raises(ValueError, match="不支持的券商标识"):
        parsers.parse_statement_csv(HTSC_CSV.encode("utf-8"), broker="nonexistent")


def test_dedup_key_stable():
    r1 = {"broker": "htsc", "contract_no": "C1", "trade_date": "2026-07-15",
          "symbol": "600519", "side": "buy", "price": 1500.0, "quantity": 100}
    r2 = dict(r1)
    r2["symbol_name"] = "贵州茅台"  # 不影响 key
    assert parsers.trade_dedup_key(r1) == parsers.trade_dedup_key(r2)
    r3 = dict(r1)
    r3["quantity"] = 200
    assert parsers.trade_dedup_key(r1) != parsers.trade_dedup_key(r3)


def test_parse_side_variants():
    assert parsers._parse_side("证券买入") == "buy"
    assert parsers._parse_side("买入") == "buy"
    assert parsers._parse_side("证券卖出") == "sell"
    assert parsers._parse_side("融资买入") == "buy"
    assert parsers._parse_side("融券卖出") == "sell"
    assert parsers._parse_side("股息入账") == "other"
    assert parsers._parse_side("") == "unknown"


def test_parse_number_cleanup():
    assert parsers._parse_number("1,500.00") == 1500.0
    assert parsers._parse_number("￥1,500.00") == 1500.0
    assert parsers._parse_number("-") == 0.0
    assert parsers._parse_number("") == 0.0


def test_parse_date_formats():
    assert parsers._parse_date("2026-07-15") == "2026-07-15"
    assert parsers._parse_date("20260715") == "2026-07-15"
    assert parsers._parse_date("2026/7/5") == "2026-07-05"
    assert parsers._parse_date("2026.01.02") == "2026-01-02"
    assert parsers._parse_date("") == ""
