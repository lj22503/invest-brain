# 券商交割单 CSV 导入 — 兼容方案说明

> 对应任务：D4「A股券商API接入方案」— 交割单 CSV 导入实现
> 状态：已实现（`src/mcp_server/broker/`），通过 `broker_*` MCP 工具对外提供服务

## 1. 背景

TradeZella / Edgewonk 均提供券商账户自动同步（broker sync），而 InvestBrain 此前只能手动记录交易。
本任务落地最小可行方案：**用户从券商 APP/网站导出交割单 CSV → 解析为标准交易记录 → 本地 SQLite 入库 → 通过 MCP 工具查询**。

不依赖任何券商开放 API（A 股券商个人接口大多不开放、需机构资质），因此以「CSV 导入」作为合规、零成本、覆盖全券商的第一步。

## 2. 主流券商交割单 CSV 格式差异调研

基于华泰（涨乐财富通）、中信（信e投）、招商（智远一户通）、国泰君安（君弘）等主流券商导出的交割单/对账单实测口径整理。

| 维度 | 华泰证券 | 中信证券 | 招商证券 | 国泰君安 | 处理策略 |
|---|---|---|---|---|---|
| 编码 | UTF-8（含 BOM） | UTF-8 | UTF-8/GBK | GBK | 自动探测 UTF-8→GB18030→GBK |
| 日期列名 | 成交日期 | 成交日期 | 交易日期 | 交易日期 | 别名归一化 |
| 日期格式 | 2026-07-15 | 2026-07-15 | 20260715（紧凑） | 2026-07-15 | 归一化 YYYY-MM-DD |
| 方向列名 | 买卖标志（证券买入/证券卖出） | 买卖标志（买入/卖出） | 买卖方向（买入/卖出） | 买卖标志（买入/卖出） | 统一 buy/sell/other |
| 数量单位 | 股 | 股 | 股 | 手（成交手数） | 表头含"手"×100 换算股 |
| 费用列 | 佣金/印花税/过户费/其他费 分列 | 佣金+过户费合并为「手续费」 | 佣金/印花税/过户费 分列 | 佣金/印花税/过户费 分列 | 手续费归一到 commission |
| 净额列 | 发生金额（买入为负） | 清算金额（绝对值正数） | 发生金额（买入为负） | 清算金额（绝对值正数） | 保留券商原始符号 |
| 余额列 | 本次余额 | 无 | 本次余额 | 无 | 可选字段 |
| 合同编号 | 有 | 有（隐藏） | 有 | 有 | 作为去重主键之一 |
| 表头前说明行 | 可能有 | 可能有 | 可能有 | 可能有 | 启发式定位表头行 |
| 合计行 | 有 | 有 | 有 | 有 | 自动跳过 |

### 关键差异总结

1. **费用列拆分不一致**：中信将佣金与过户费合并为一列「手续费」，华泰/招商/国君分列。标准化时统一将「手续费」归入 `commission`，`transfer_fee` 缺省为 0。
2. **日期格式不统一**：招商导出的紧凑格式 `20260715` 需归一化为 `2026-07-15`。
3. **数量单位不统一**：国泰君安导出「成交手数」，其余券商为「成交数量（股）」。按表头名称含"手"自动 ×100。
4. **净额列符号口径不一**：华泰/招商「发生金额」买入为负、卖出为正；中信/国君「清算金额」为绝对值正数。**保留券商原始值**，避免强行改号引入错误。
5. **编码不统一**：老版本券商客户端（如部分 GBK 环境）导出 GBK，需自动探测。

## 3. 兼容方案架构

```
券商交割单 CSV
   │  (编码自动探测 UTF-8/GBK)
   ▼
parsers.parse_statement_csv()
   │  ① 表头行定位（启发式 ≥2 已知列）
   │  ② 列名别名归一化（FIELD_ALIASES）
   │  ③ 券商自动识别（detect_broker 打分制，可显式指定覆盖）
   │  ④ 行级标准化：日期/时间/数量(手→股)/方向(buy/sell/other)/费用拆分
   │  ⑤ 净额兜底推算：买入=-(金额+费)，卖出=金额-费
   │  ⑥ 生成 trade_dedup_key（sha1 去重键）
   ▼
BrokerStore（SQLite: data/memory/broker.db，已被 .gitignore 保护）
   │  imports 批次表（file_hash 唯一 → 文件级幂等）
   │  trades  标准交易记录表（trade_key 唯一 → 行级去重）
   ▼
broker_* MCP 工具（server.py 注册 broker 前缀，共 5 个）
```

## 4. 标准交易记录 Schema（trades 表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER PK | 自增主键 |
| broker | TEXT | htsc / citic / cms / gtja / generic |
| account | TEXT | 股东账号/资金账号（可选） |
| trade_date | TEXT | 成交日期 YYYY-MM-DD |
| trade_time | TEXT | 成交时间 HH:MM:SS（可选） |
| side | TEXT | buy / sell / other / unknown |
| symbol | TEXT | 证券代码（去 .SH/.SZ 后缀） |
| symbol_name | TEXT | 证券名称 |
| price | REAL | 成交价格 |
| quantity | INTEGER | 成交数量（股） |
| amount | REAL | 成交金额 |
| commission / stamp_tax / transfer_fee / other_fee | REAL | 各项费用 |
| fee | REAL | 费用合计 |
| net_amount | REAL | 净额（保留券商口径符号） |
| balance | REAL | 成交后余额（可选） |
| contract_no | TEXT | 合同编号（去重主键之一） |
| trade_key | TEXT UNIQUE | 去重键（sha1） |
| source_file / imported_at | TEXT | 来源追踪 |

## 5. MCP 工具清单

| 工具 | 功能 |
|---|---|
| `broker_supported_formats` | 查看支持的券商列表、标准字段与示例列名 |
| `broker_import_statement(file_path, broker="auto")` | 解析并入库交割单 CSV（文件哈希幂等 + 行级去重） |
| `broker_list_trades(side, symbol, start_date, end_date, limit)` | 查询交易记录 |
| `broker_get_trade_stats(side, symbol, start_date, end_date)` | 汇总统计（买入/卖出笔数、数量、金额、费用、日期范围） |
| `broker_get_imports(limit)` | 查看导入历史批次 |

### 调用示例（Claude / 任意 MCP 客户端）

```
用户：导入华泰证券交割单
→ broker_import_statement(file_path="D:/Downloads/交割单2026-07.csv")
→ {"broker": "htsc", "imported_rows": 32, "duplicated_rows": 0,
   "first_date": "2026-07-01", "last_date": "2026-07-31", ...}

用户：我这三个月交易情况如何
→ broker_get_trade_stats(start_date="2026-05-01")
→ {"total_trades": 87, "buy": {...}, "sell": {...}, "distinct_symbols": 12, ...}
```

## 6. 使用流程（终端用户）

1. 券商 APP（涨乐财富通/信e投/智远一户通/君弘等）→ 交易 → 交割单/对账单 → 选择日期范围 → 导出 CSV/Excel（存为 CSV）。
2. 交给任意支持 MCP 的 AI 客户端（Claude Desktop / Cursor 等），调用 `broker_import_statement` 传入文件路径。
3. 通过 `broker_list_trades` / `broker_get_trade_stats` 查询、分析、复盘。

## 7. 扩展新券商指南

1. 在 `BROKERS` 增加券商标识与样例列名。
2. 在 `FIELD_ALIASES` 补充该券商独有列名（如"业务名称"已映射 side）。
3. 若表头特征明显，在 `detect_broker` 增加打分规则；不明显则用户显式传 `broker=`。
4. 在 `tests/broker/test_parsers.py` 增加该券商样例 CSV 与断言。

## 8. 局限与后续方向

- **净额符号口径**：中信/国君清算金额为绝对值，导入后统计以 `amount` 与 `fee` 为准，`net_amount` 保留原始值，文档已说明。
- **更多券商/历史对账**：可扩展华宝、同花顺、雪球组合等格式；后续可基于 `imports` 批次做对账（校验资金流水一致）。
- **API 直连**：个人用户普遍无法获得券商开放 API；若未来有渠道（如 QMT/miniQMT、同花顺 iFinD），可新增 datasource 与 `broker_*` 并列，不影响现有 CSV 通道。
- **与行为模式联动**：交易入库后可衔接 patterns 检测（如追涨杀跌频率、卖飞率），形成「记录→分析→反馈」闭环。
