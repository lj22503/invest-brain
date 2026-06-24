# 行为模式挖掘 MVP — SPEC

## 目标

在用户记录投资想法/决策时，**自动检测行为模式**，并生成可读的 Markdown 报告。

---

## 1. 数据结构

### `behavior_patterns` 表（已有）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PRIMARY KEY | `{pattern_type}_{decision_id}` |
| pattern_type | TEXT | 模式类型：追高/过早卖出/情绪化交易/原则违反/能力圈外 |
| trigger_content | TEXT | 触发内容（原文片段，最多500字） |
| context | TEXT | 上下文（原因/背景，最多500字） |
| happened_at | TIMESTAMP | 发生时间 |
| severity | TEXT | 高/中/低 |
| times_count | INTEGER | 累计次数 |
| created_at | TIMESTAMP | 记录时间 |

### 模式输出结构（检测器返回值）

每种模式返回的字段不同，统一包装为：

```python
{
  "type": "追高",
  "decision_id": "xxx",
  "ticker": "茅台",
  "trigger": "追了涨停板",
  "keyword": "追",
  "created_at": "2026-06-20 10:00:00",
  "severity": "高"
}
```

---

## 2. 检测规则

### 2.1 追高（chase）

**触发条件：** 买入理由中含关键词：`追`、`涨`、`热门`、`忍不住`、`冲动`、`大家都`、`朋友圈`

**输出字段：**
- `type`: "追高"
- `decision_id`: 决策ID
- `ticker`: 标的
- `trigger`: 理由原文（前100字）
- `keyword`: 命中的关键词
- `severity`: `冲动/忍不住` → 高，其他 → 中

### 2.2 过早卖出（quick_sell）

**触发条件：** 同一标的买入后 **5个交易日** 内卖出

**输出字段：**
- `type`: "过早卖出"
- `buy_decision_id` / `sell_decision_id`: 买卖决策ID
- `ticker`: 标的
- `hold_days`: 持有天数
- `buy_price` / `sell_price`: 买卖价格
- `pnl_pct`: 盈亏百分比
- `severity`: 亏损卖出 → 高，盈利卖出 → 中

### 2.3 情绪化交易（emotion_trade）

**触发条件：** 情绪词出现后 **24小时** 内有交易

**情绪关键词：** `焦虑`、`睡不着`、`担心`、`害怕`、`恐慌`、`兴奋`、`忍不住`、`冲动`、`后悔`、`懊恼`

**输出字段：**
- `type`: "情绪化交易"
- `thought_id`: 情绪 thought ID
- `emotion_text`: 情绪 thought 原文（前100字）
- `emotion_keyword`: 情绪关键词
- `emotion_time`: 情绪出现时间
- `decision_id`: 后续交易决策ID
- `action`: 交易动作（buy/sell）
- `hours_after_emotion`: 情绪后几小时交易
- `severity`: 高

### 2.4 原则违反（principle_violation）

**触发条件：** 决策理由中含信号词：`违背原则`、`没遵守`、`违反`、`说了不`、`知道但还是`

**输出字段：**
- `type`: "原则违反"
- `decision_id`: 决策ID
- `ticker`: 标的
- `action`: 动作
- `reason`: 理由原文（前200字）
- `signal`: 信号词
- `severity`: 违反/违背原则 → 高，知道但还是 → 高，其他 → 中

### 2.5 能力圈外（coc_violation）

**当前版本：** 返回空列表（需要用户主动标注能力圈数据后实现）

---

## 3. 触发机制

### 3.1 手动触发（V1）

提供 MCP 工具 `run_pattern_detection()`，用户/Agent 主动调用。

**调用时机示例：**
- 每次复盘时
- 定期（用户自己决定频率）

### 3.2 被动触发（V1）

在 `record_decision()` 执行后，自动调用 `PatternDetector.detect_all()`，把检测到的新模式存入数据库。

**不重复写入：** 用 `INSERT OR REPLACE`，同一 `id` 的模式不重复计数（`times_count` 暂不实现递增）。

### 3.3 定时触发（V2）

由外部 scheduler 控制，不在这阶段做。

---

## 4. 产出形式

### 4.1 MCP 返回

#### `run_pattern_detection()`

返回本次检测到的新模式列表：

```json
{
  "new_patterns_found": 3,
  "patterns": [
    {
      "type": "追高",
      "ticker": "茅台",
      "severity": "中",
      "trigger": "看到朋友圈都在说...",
      "created_at": "2026-06-20 10:00:00"
    }
  ]
}
```

#### `get_pattern_summary()`

返回累计汇总：

```json
{
  "追高": {"count": 5, "last_seen": "2026-06-20"},
  "过早卖出": {"count": 2, "last_seen": "2026-06-18"},
  "情绪化交易": {"count": 1, "last_seen": "2026-06-15"}
}
```

#### `get_pattern_report()`

返回 Markdown 格式报告路径和全文：

```json
{
  "report_path": "data/memory/patterns/reports/pattern_report_weekly_20260624.md",
  "content": "# 投资行为模式 周报 — 2026-06-24\n\n## 汇总\n**检测到 3 次行为模式**\n\n..."
}
```

### 4.2 报告格式

见 `patterns/report.py`，已实现。周期参数支持 `weekly` / `monthly`。

---

## 5. 实现清单

| 任务 | 文件 | 状态 |
|------|------|------|
| 整理 detector 输出格式 | `patterns/detector.py` | 参考本 spec 调整字段名 |
| 新增 MCP 工具 `run_pattern_detection` | `tools/pattern_tools.py`（新建） | — |
| 新增 MCP 工具 `get_pattern_summary` | `tools/pattern_tools.py` | — |
| 新增 MCP 工具 `get_pattern_report` | `tools/pattern_tools.py` | — |
| `record_decision` 自动触发检测 | `tools/memory_tools.py` | 修改 |
| 注册 pattern_tools 到 server | `server.py` | 修改 |
| 验证端到端 | — | — |

---

## 6. 不在这阶段做

- LLM 驱动的深度分析（`PatternAnalyzer`，需要 LLM API）
- `PatternDetector.detect_coc_violations()` 实现（需要用户能力圈数据）
- 定时自动检测（scheduler 集成）
- `times_count` 递增逻辑
- 飞书推送报告
