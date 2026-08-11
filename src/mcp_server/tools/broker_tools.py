"""券商交割单 CSV 导入 MCP 工具 — 解析券商导出的交割单/对账单为标准化交易记录。

遵循项目工具组模式（FastMCP 子实例 + server.py 统一注册，前缀 broker）：
- broker_supported_formats  查看支持的券商格式与字段映射
- broker_import_statement   导入券商交割单 CSV（自动识别编码/表头/券商）
- broker_list_trades        查询已导入的交易记录
- broker_get_trade_stats    汇总交易统计（买卖金额/费用/标的数）
- broker_get_imports        查看导入历史（支持幂等重复导入）

数据落库：data/memory/broker.db（SQLite，本地存储，已被 .gitignore 保护）。
"""

import hashlib
import os
from mcp.server.fastmcp import FastMCP

from ..broker import parsers
from ..broker.store import get_broker_store

broker_tools = FastMCP("broker-tools")


@broker_tools.tool()
def supported_formats() -> dict:
    """查看 InvestBrain 支持的券商交割单格式与标准字段映射。

    用于导入前确认券商格式兼容性；返回各券商典型列名与标准化字段对照。

    Returns:
        {brokers: [{id, name, sample_columns}], standard_fields: {...}, note}
    """
    return {
        "brokers": [
            {"id": bid, "name": info["name"], "sample_columns": info["sample_columns"]}
            for bid, info in parsers.BROKERS.items()
        ],
        "standard_fields": {
            field: aliases
            for field, aliases in parsers.FIELD_ALIASES.items()
        },
        "note": (
            "支持 CSV（UTF-8/GBK 自动识别）与标准表头归一化；"
            "识别不了的列会被忽略，缺少成交日期/证券代码/买卖标志/成交价格/成交数量会报错。"
            "详细兼容方案见 docs/broker-statement-csv-compat.md"
        ),
    }


@broker_tools.tool()
def import_statement(
    file_path: str,
    broker: str = "auto",
) -> dict:
    """导入券商交割单 CSV 文件，解析为标准化交易记录并入库（自动去重）。

    Args:
        file_path: 券商导出的交割单/对账单 CSV 文件绝对路径
        broker: 券商标识，可选 htsc / citic / cms / gtja / generic；
                默认 auto 自动按表头特征识别（无法确定时按 generic 处理）

    Returns:
        {
          import_id, broker, file_name,
          total_rows, imported_rows, duplicated_rows, skipped_rows,
          first_date, last_date, warnings, hint
        }
        重复导入同一文件时返回 imported_rows=0 并提示已存在。
    """
    path = os.path.abspath(file_path)
    if not os.path.exists(path):
        return {"imported_rows": 0, "error": f"文件不存在: {path}"}

    with open(path, "rb") as f:
        content = f.read()
    file_hash = hashlib.sha256(content).hexdigest()
    file_name = os.path.basename(path)

    store = get_broker_store()

    # 幂等：同一文件（内容哈希一致）重复导入直接返回
    existing = store.find_import_by_hash(file_hash)
    if existing:
        return {
            "import_id": existing["id"],
            "broker": existing["broker"],
            "file_name": existing["file_name"],
            "imported_rows": 0,
            "duplicated_rows": 0,
            "skipped_rows": 0,
            "error": None,
            "hint": (
                f"文件 {file_name} 已于 {existing['created_at']} 导入过（import_id={existing['id']}），"
                "未重复入库。如需重新导入请删除 data/memory/broker.db 中对应记录。"
            ),
        }

    # 解析 CSV
    try:
        parsed = parsers.parse_statement_csv(content, broker=broker, file_name=file_name)
    except ValueError as exc:
        return {"imported_rows": 0, "error": str(exc)}

    # 入库
    import_id = store.create_import(
        broker=parsed["broker"],
        file_name=file_name,
        file_hash=file_hash,
        source_path=path,
        total_rows=parsed["total_rows"],
        imported_rows=0,
        skipped_rows=parsed["skipped_rows"],
    )
    result = store.add_trades(import_id, parsed["records"])
    # 回填实际导入/去重数量与日期范围
    store.import_stats_update(
        import_id,
        imported_rows=result["inserted"],
        first_date=min((r["trade_date"] for r in parsed["records"]), default=""),
        last_date=max((r["trade_date"] for r in parsed["records"]), default=""),
    )

    return {
        "import_id": import_id,
        "broker": parsed["broker"],
        "file_name": file_name,
        "total_rows": parsed["total_rows"],
        "imported_rows": result["inserted"],
        "duplicated_rows": result["duplicated"],
        "skipped_rows": parsed["skipped_rows"],
        "first_date": min((r["trade_date"] for r in parsed["records"]), default=""),
        "last_date": max((r["trade_date"] for r in parsed["records"]), default=""),
        "warnings": parsed["warnings"][:20],
        "column_map": parsed["column_map"],
        "hint": (
            f"成功导入 {result['inserted']} 笔交易，去重 {result['duplicated']} 笔。"
            "可用 broker_list_trades 查询明细，broker_get_trade_stats 查看汇总。"
        ),
    }


@broker_tools.tool()
def list_trades(
    start_date: str = "",
    end_date: str = "",
    symbol: str = "",
    side: str = "",
    broker: str = "",
    limit: int = 200,
) -> dict:
    """查询已导入的标准化交易记录（默认时间倒序）。

    Args:
        start_date: 起始日期 YYYY-MM-DD（含）
        end_date: 结束日期 YYYY-MM-DD（含）
        symbol: 按证券代码模糊筛选（如 600519）
        side: 买卖方向筛选，可选 buy / sell / other / unknown
        broker: 券商标识筛选，可选 htsc / citic / cms / gtja / generic
        limit: 返回条数上限（默认 200，最大 2000）

    Returns:
        {total: n, trades: [{id, trade_date, trade_time, side, symbol,
                             symbol_name, price, quantity, amount, fee,
                             net_amount, broker, contract_no}...]}
    """
    store = get_broker_store()
    trades = store.list_trades(
        start_date=start_date,
        end_date=end_date,
        symbol=symbol,
        side=side,
        broker=broker,
        limit=limit,
    )
    if not trades:
        return {
            "total": 0,
            "trades": [],
            "hint": "暂无匹配交易记录。可先使用 broker_import_statement 导入券商交割单 CSV。",
        }

    slim = []
    for t in trades:
        slim.append(
            {
                "id": t["id"],
                "trade_date": t["trade_date"],
                "trade_time": t["trade_time"],
                "side": t["side"],
                "symbol": t["symbol"],
                "symbol_name": t["symbol_name"],
                "price": t["price"],
                "quantity": t["quantity"],
                "amount": t["amount"],
                "fee": t["fee"],
                "net_amount": t["net_amount"],
                "broker": t["broker"],
                "contract_no": t["contract_no"],
            }
        )
    return {"total": len(slim), "trades": slim}


@broker_tools.tool()
def get_trade_stats(
    start_date: str = "",
    end_date: str = "",
    broker: str = "",
) -> dict:
    """汇总已导入交易的统计指标（买卖笔数/股数/金额、费用、持仓标的数）。

    Args:
        start_date: 起始日期 YYYY-MM-DD（含）
        end_date: 结束日期 YYYY-MM-DD（含）
        broker: 券商标识筛选（默认全部）

    Returns:
        {buy: {...}, sell: {...}, total_trades, distinct_symbols, first_date, last_date}
    """
    store = get_broker_store()
    stats = store.get_trade_stats(
        start_date=start_date,
        end_date=end_date,
        broker=broker,
    )
    stats["hint"] = (
        "金额单位：人民币元；成交金额=价格×数量；净额已含费用（买入为负、卖出为正）。"
        "统计仅覆盖已导入的交割单数据。"
    )
    return stats


@broker_tools.tool()
def get_imports(limit: int = 20) -> dict:
    """查看交割单导入历史（文件、券商、导入时间、成功/跳过行数）。

    Args:
        limit: 返回最近 N 次导入记录（默认 20，最大 200）

    Returns:
        {imports: [{id, broker, file_name, imported_rows, skipped_rows,
                    total_rows, first_date, last_date, created_at}...]}
    """
    store = get_broker_store()
    imports = store.list_imports(limit=limit)
    if not imports:
        return {
            "imports": [],
            "hint": "暂无导入记录。可先使用 broker_import_statement 导入券商交割单 CSV。",
        }
    return {"imports": imports}
