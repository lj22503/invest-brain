"""券商交割单 CSV 解析器 — 支持主流 A 股券商及通用格式。

设计目标
--------
1. 编码自适应：A 股券商导出 CSV 常见 GBK/GB18030，也支持 UTF-8（含 BOM）。
2. 表头归一化：不同券商列名差异大（如"成交日期/交易日期/日期"），
   通过别名词典把原始表头映射到 InvestBrain 标准化字段。
3. 单位自适应：成交数量按"股"或"手"自动换算（1 手 = 100 股）。
4. 方向归一化：买入/卖出/融资买入/融券卖出等统一为 buy/sell。
5. 严格校验：无法识别表头时给出明确错误，避免静默错位入库。

标准化交易记录字段（与 broker.store.BrokerStore 对齐）：
    broker, account, trade_date, trade_time, side, symbol, symbol_name,
    price, quantity, amount, commission, stamp_tax, transfer_fee,
    other_fee, fee, net_amount, balance, contract_no, raw
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 券商元信息（用于识别与展示）
# ---------------------------------------------------------------------------

BROKERS = {
    "htsc": {
        "name": "华泰证券（涨乐财富通）",
        "sample_columns": "成交日期 成交时间 证券代码 证券名称 买卖标志 成交价格 成交数量 成交金额 佣金 印花税 过户费 发生金额 本次余额 合同编号",
    },
    "citic": {
        "name": "中信证券（信e投）",
        "sample_columns": "成交日期 证券代码 证券名称 买卖标志 成交价格 成交数量 成交金额 手续费 印花税 清算金额",
    },
    "cms": {
        "name": "招商证券（智远一户通）",
        "sample_columns": "成交日期 成交时间 证券代码 证券名称 买卖标志 成交价格 成交数量 成交金额 佣金 印花税 过户费 发生金额 本次余额",
    },
    "gtja": {
        "name": "国泰君安（君弘）",
        "sample_columns": "交易日期 证券代码 证券名称 买卖标志 成交价格 成交数量 成交金额 佣金 印花税 过户费 清算金额",
    },
    "generic": {
        "name": "通用/其他券商",
        "sample_columns": "成交日期 证券代码 证券名称 买卖方向 成交价格 成交数量 成交金额 手续费 印花税 净额",
    },
}

# 常用列名 → 标准字段（按别名出现频率排序；越靠前越优先匹配）
FIELD_ALIASES: Dict[str, List[str]] = {
    "trade_date": ["成交日期", "交易日期", "委托日期", "日期"],
    "trade_time": ["成交时间", "成交时刻", "时间"],
    "symbol": ["证券代码", "股票代码", "证券编码", "代码"],
    "symbol_name": ["证券名称", "股票名称", "证券简称", "名称"],
    "side": ["买卖标志", "买卖方向", "买卖类别", "操作", "方向", "业务名称", "委托类别"],
    "price": ["成交价格", "成交均价", "成交价", "价格"],
    "quantity": ["成交数量", "成交股数", "成交手数", "委托数量", "股数", "数量"],
    "amount": ["成交金额", "成交总额"],
    "commission": ["佣金", "手续费", "交易佣金"],
    "stamp_tax": ["印花税"],
    "transfer_fee": ["过户费", "结算费", "经手费", "过户费/经手费"],
    "other_fee": ["其他费", "其他费用", "其他费用合计"],
    "net_amount": ["发生金额", "清算金额", "净额", "资金发生额", "本次金额"],
    "balance": ["本次余额", "资金余额", "余额", "资金余额"],
    "contract_no": ["合同编号", "成交编号", "委托编号", "合同号"],
    "account": ["股东账号", "股东代码", "资金账号", "资金账户", "证券账户"],
}

# 必填字段：缺少任一字段的行无法构成标准交易记录
REQUIRED_FIELDS = ("trade_date", "symbol", "side", "price", "quantity")

_BUY_KEYWORDS = ("买入", "买", "buy", "b")
_SELL_KEYWORDS = ("卖出", "卖", "sell", "s")
# 常见非买卖操作（如红股入账、股息入账、资金转入转出）— 保留并标记 other
_OTHER_KEYWORDS = ("入账", "入金", "出金", "转出", "转入", "申购", "赎回", "红股", "股息", "利息", "其他")

# 表头名称里含"手"时按手换算为股
_LOT_PATTERNS = ("手数", "手)")


# ---------------------------------------------------------------------------
# 基础解析工具
# ---------------------------------------------------------------------------


def _decode_bytes(data: bytes) -> str:
    """按 UTF-8 -> GB18030 -> GBK 顺序尝试解码，兼容 BOM 与 GBK 中文编码。"""
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _parse_number(text) -> float:
    """清洗千分位/货币符号后转 float；空值返回 0.0。"""
    if text is None:
        return 0.0
    s = str(text).strip().replace(",", "").replace("，", "")
    s = s.replace("¥", "").replace("￥", "").replace(" ", "").replace("元", "")
    if s in ("", "-", "--", "None", "null", "—"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_date(text) -> str:
    """归一化日期为 YYYY-MM-DD；支持 20250121 / 2025-01-21 / 2025/1/2 / 2025.01.02。"""
    s = str(text).strip()
    if not s:
        return ""
    m = re.match(r"^(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?$", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # 日/月/年（少见，如 02/01/2025）
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return s  # 无法识别时原样返回，由调用方决定是否告警


def _parse_time(text) -> str:
    """归一化时间为 HH:MM:SS / HH:MM。"""
    s = str(text).strip()
    if not s:
        return ""
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", s)
    if m:
        hh, mm = int(m.group(1)), m.group(2)
        ss = m.group(3) if m.group(3) else "00"
        return f"{hh:02d}:{mm}:{ss}"
    m = re.match(r"^(\d{1,2})时(\d{1,2})分(\d{1,2})?秒?$", s)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}:{int(m.group(3) or 0):02d}"
    return s


def _parse_side(text) -> str:
    """方向归一化：buy / sell / other / unknown。"""
    s = str(text).strip().lower()
    if not s or s in ("-", "--", "none"):
        return "unknown"
    for kw in _BUY_KEYWORDS:
        if kw in s:
            return "buy"
    for kw in _SELL_KEYWORDS:
        if kw in s:
            return "sell"
    # 纯数字/英文码（0/1/2, B/S）
    if s in ("b", "buy", "0", "1"):
        return "buy"
    if s in ("s", "sell", "2"):
        return "sell"
    for kw in _OTHER_KEYWORDS:
        if kw in s:
            return "other"
    return "unknown"


def _parse_quantity(text, column_name: str = "") -> int:
    """数量归一化：表头含"手"时 ×100 换算为股。"""
    n = _parse_number(text)
    if any(k in str(column_name) for k in _LOT_PATTERNS):
        n = n * 100
    return int(round(n))


def _match_alias(column: str) -> Optional[str]:
    """将原始列名映射到标准字段；无匹配返回 None。"""
    key = re.sub(r"\s+", "", str(column)).strip()
    if not key:
        return None
    for std_field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in key:
                return std_field
    return None


def _is_header_row(row: List[str]) -> bool:
    """启发式：一行里命中 >=2 个已知标准列名即视为表头行。"""
    hits = 0
    for cell in row:
        if _match_alias(cell):
            hits += 1
    return hits >= 2


def _is_skippable_row(row: List[str]) -> bool:
    """跳过合计行、说明行等非交易行。"""
    joined = "".join(str(c) for c in row if c is not None)
    if not joined.strip():
        return True
    if "合计" in joined or "总计" in joined or "小计" in joined:
        return True
    return False


# ---------------------------------------------------------------------------
# 主解析入口
# ---------------------------------------------------------------------------


def detect_broker(headers: List[str]) -> str:
    """根据表头粗略识别券商（基于别名命中数量打分，命中最多者胜出）。

    识别不精确时返回 generic，由用户显式指定 broker 可覆盖。
    """
    alias_hit = {field: False for field in FIELD_ALIASES}
    for cell in headers:
        matched = _match_alias(cell)
        if matched:
            alias_hit[matched] = True

    # 综合表头特征打分
    header_text = "".join(str(c) for c in headers)
    scores = {"htsc": 0, "citic": 0, "cms": 0, "gtja": 0}
    if "合同编号" in header_text:
        scores["htsc"] += 3
    if "成交时间" in header_text:
        scores["htsc"] += 2
    if "手续费" in header_text and "佣金" not in header_text:
        scores["citic"] += 3
    if "清算金额" in header_text:
        scores["citic"] += 1
        scores["gtja"] += 1
    if "本次余额" in header_text:
        scores["htsc"] += 1
        scores["cms"] += 1
    if "发生金额" in header_text:
        scores["htsc"] += 1
        scores["cms"] += 1
    if "交易日期" in header_text and "成交日期" not in header_text:
        scores["cms"] += 1
        scores["gtja"] += 1
    if "买卖方向" in header_text:
        scores["cms"] += 2
    if "成交手数" in header_text:
        scores["gtja"] += 2
    if "过户费" in header_text and "手续费" not in header_text:
        scores["htsc"] += 1
        scores["cms"] += 1
        scores["gtja"] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "generic"


def parse_statement_csv(
    content: bytes,
    broker: str = "auto",
    file_name: str = "statement.csv",
) -> dict:
    """解析券商交割单 CSV 内容为标准化交易记录列表。

    Args:
        content: CSV 文件字节内容（自动识别 UTF-8/GBK）
        broker: 券商标识 htsc/citic/cms/gtja/generic，auto 时按表头启发式识别
        file_name: 源文件名（用于 trace）

    Returns:
        {
          "broker": 识别或指定的券商,
          "header": [原始表头],
          "column_map": {标准字段: 原始列名},
          "records": [{标准化交易记录}...],
          "total_rows": 数据行数（含被跳过行）,
          "skipped_rows": 被跳过行数,
          "warnings": [提示信息],
        }
    """
    text = _decode_bytes(content)

    # 分隔符探测：默认逗号；第一行 tab 明显更多时按 tab 处理
    first_line = text.splitlines()[0] if text.splitlines() else ""
    delimiter = "\t" if first_line.count("\t") > first_line.count(",") else ","

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = [r for r in reader]

    # 定位表头行（标题/说明行在前）
    header_idx: Optional[int] = None
    for i, row in enumerate(rows):
        if _is_header_row(row):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(
            "无法识别交割单表头：未找到包含成交日期/证券代码等标准列名的表头行。"
            "请确认文件为券商导出的交割单/对账单 CSV，或使用 broker_supported_formats 查看支持的格式。"
        )

    headers = [str(c).strip() for c in rows[header_idx]]
    column_map: Dict[str, str] = {}
    index_map: Dict[str, int] = {}
    for idx, raw in enumerate(headers):
        std = _match_alias(raw)
        if std and std not in column_map:
            column_map[std] = raw
            index_map[std] = idx

    # 必填字段缺失即无法标准化
    missing = [f for f in REQUIRED_FIELDS if f not in column_map]
    if missing:
        raise ValueError(
            f"表头缺少关键列：{', '.join(missing)}。当前识别列映射：{column_map}。"
            "该券商格式可能暂不支持，可将表头反馈给项目维护者以扩展兼容。"
        )

    if broker == "auto":
        broker = detect_broker(headers)
    if broker not in BROKERS:
        raise ValueError(f"不支持的券商标识 {broker}，可选：{'/'.join(BROKERS)}")

    # 逐行解析
    records: List[dict] = []
    warnings: List[str] = []
    skipped = 0
    for row in rows[header_idx + 1:]:
        if _is_skippable_row(row):
            skipped += 1
            continue
        if len(row) < 2 or not any(str(c).strip() for c in row):
            skipped += 1
            continue

        rec = _row_to_record(row, headers, index_map, broker, file_name)
        if rec is None:
            skipped += 1
            continue

        # 日期/数量校验：缺必要信息时跳过并告警
        if not rec["trade_date"]:
            warnings.append(f"第 {rows.index(row) + 1} 行无法解析成交日期，已跳过: {row}")
            skipped += 1
            continue
        if rec["quantity"] <= 0 and rec["side"] in ("buy", "sell"):
            # 数量为 0 的成交记录（如废单/撤单残留）跳过
            skipped += 1
            continue
        records.append(rec)

    return {
        "broker": broker,
        "header": headers,
        "column_map": column_map,
        "records": records,
        "total_rows": len(rows[header_idx + 1:]),
        "skipped_rows": skipped,
        "warnings": warnings,
    }


def _row_to_record(row: List[str], headers: List[str], index_map: Dict[str, int], broker: str, file_name: str) -> Optional[dict]:
    """把一行原始数据映射为标准交易记录；缺少必填字段时返回 None。"""

    def get(field: str) -> str:
        idx = index_map.get(field)
        if idx is None or idx >= len(row):
            return ""
        return str(row[idx] or "").strip()

    side = _parse_side(get("side"))
    symbol = get("symbol")
    # 证券代码清洗：去掉 .SH/.SZ 后缀与市场前缀
    symbol = re.sub(r"\.(SH|SZ|BJ)$", "", symbol.upper()).strip()
    if not symbol or symbol in ("--", "-"):
        return None

    qidx = index_map.get("quantity")
    quantity_col = headers[qidx] if (qidx is not None and qidx < len(headers)) else ""
    quantity = _parse_quantity(get("quantity"), quantity_col)
    price = _parse_number(get("price"))
    amount = _parse_number(get("amount"))

    # 若缺少成交金额，用 price * quantity 兜底推算
    if amount <= 0 and price > 0 and quantity > 0:
        amount = round(price * quantity, 4)

    commission = _parse_number(get("commission"))
    stamp_tax = _parse_number(get("stamp_tax"))
    transfer_fee = _parse_number(get("transfer_fee"))
    other_fee = _parse_number(get("other_fee"))
    fee = round(commission + stamp_tax + transfer_fee + other_fee, 4)

    net_amount = _parse_number(get("net_amount"))
    # 缺少净额列时用 amount ± fee 推算（买入净额=-(金额+费)，卖出净额=金额-费）
    if net_amount == 0 and amount > 0 and fee >= 0:
        if side == "buy":
            net_amount = round(-(amount + fee), 4)
        elif side == "sell":
            net_amount = round(amount - fee, 4)

    return {
        "broker": broker,
        "account": get("account"),
        "trade_date": _parse_date(get("trade_date")),
        "trade_time": _parse_time(get("trade_time")),
        "side": side,
        "symbol": symbol,
        "symbol_name": get("symbol_name"),
        "price": price,
        "quantity": quantity,
        "amount": amount,
        "commission": commission,
        "stamp_tax": stamp_tax,
        "transfer_fee": transfer_fee,
        "other_fee": other_fee,
        "fee": fee,
        "net_amount": net_amount,
        "balance": _parse_number(get("balance")),
        "contract_no": get("contract_no"),
        "source_file": file_name,
        "raw": ",".join(str(c) for c in row),
    }


def trade_dedup_key(rec: dict) -> str:
    """生成交易去重键：合同编号 + 日期 + 证券 + 方向 + 价格 + 数量。

    合同编号为空时退化为 日期+证券+方向+价格+数量（仍可跨文件去重同价同量成交）。
    """
    base = "|".join(
        [
            str(rec.get("broker", "")),
            str(rec.get("contract_no", "") or ""),
            str(rec.get("trade_date", "")),
            str(rec.get("symbol", "")),
            str(rec.get("side", "")),
            str(rec.get("price", "")),
            str(rec.get("quantity", "")),
        ]
    )
    return hashlib.sha1(base.encode("utf-8")).hexdigest()
