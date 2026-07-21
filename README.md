# InvestBrain — 投资第二大脑

> 有经验投资者的纪律自主工具，解决"知行合一"问题
> **不是投顾，不给建议，而是"镜子" + "纪律锚点"**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

<p align="center">
  <a href="#快速开始"><img src="https://img.shields.io/badge/MCP_Server_+_RAG-d6a52e?style=for-the-badge" alt="MCP Server + RAG"/></a>
  <a href="README_EN.md"><img src="https://img.shields.io/badge/English-README-blue?style=for-the-badge" alt="English README"/></a>
  <a href="llms.txt"><img src="https://img.shields.io/badge/llms.txt-AI_Ready-green?style=for-the-badge" alt="llms.txt"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-yellow?style=for-the-badge" alt="AGPL-3.0"/></a>
  <a href="#核心能力"><img src="https://img.shields.io/badge/行为模式_挖掘-purple?style=for-the-badge" alt="行为模式挖掘"/></a>
</p>

<p align="center">
  <strong>想法记录 × 投资 RAG × 记忆系统 × 提醒触发 × 行为模式挖掘</strong>
</p>

<!-- TODO: 添加 ≤10 秒的演示 GIF，提升 50% 转化率（见 GitHub 增长策略报告） -->

---

## 5 分钟快速体验

一条命令 clone 仓库后，三步完成启动：

```bash
# 1. 安装 MCP Server 依赖
cd src/mcp_server && pip install -r requirements.txt

# 2. 配置 DeepSeek API Key（开箱即用的中文投资 RAG 方案）
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=sk-xxx

# 3. 启动 MCP Server
python server.py
```

> **首次启动提示**：向量库（Chroma + ONNX Embedding）首次会下载约 80MB 模型文件。若希望跳过向量库、纯工具调用体验，可保持 `server.py` 中相关注释不变；如需完整 RAG 体验，下载后取消 `server.py` 内的注释行。

启动后 Server 会以 stdio 方式接受 MCP 客户端调用。配置 Claude Desktop 见下方 [Claude Desktop 接入](#claude-desktop-接入)。

---

## 它解决什么问题

**核心问题**：投资者被叙事带着走，操作没纪律，事后后悔。

| 常见痛点 | InvestBrain 的应对 |
|----------|-------------------|
| 看到某只股票大涨就追高 | 强制记录买入理由 + 关联历史相似决策 |
| 跌了恐慌割肉 | 触发 RAG 检索大师对"恐慌"的看法 |
| 同一类错误反复犯 | 行为模式挖掘自动识别"追涨杀跌"模式 |
| 重要时间/价格点位忘记 | 价格/时间/条件监控 + 飞书推送 |
| 想不起自己过去的判断 | 记忆系统 + 决策卡片回溯 |

---

## 核心能力

| 功能 | 说明 |
|------|------|
| 想法记录 | 用户说一句话，AI 解析 + 关联历史 + 生成卡片 |
| 投资 RAG | 大师思想检索问答（16 位投资大师 × 5 个核心概念） |
| 记忆系统 | 用户画像、历史决策、行为模式挖掘 |
| 提醒触发 | 价格/时间/条件监控，支持飞书推送 |
| 行为模式挖掘 | 自动发现投资者的偏差模式 |

---

## 示例对话

下面是三个核心价值场景的真实对话流（任意 MCP 客户端均可使用）：

### 场景 1：RAG 问答 — 大师思想碰撞

> **用户**：段永平怎么看"快钱"和"慢钱"？
>
> **调用**：`rag_ask_investment(question="段永平怎么看快钱和慢钱")`
>
> **AI 返回**：
> 段永平的核心观点是"快钱"看似机会多但风险敞口大，"慢钱"依靠复利与确定性。
> 在「段永平」语料中相关论述 12 条，节选：
> > "投资赚钱的速度不应该快过学习的速度。"
> > "敢重仓的就是你能看懂的生意，剩下的不是机会。"
> 关联概念：能力圈、安全边际、复利。

### 场景 2：行为模式分析 — 找出反复犯的错

> **用户**：我最近的交易有什么问题？
>
> **调用**：`memory_get_behavior_patterns()`
>
> **AI 返回**：
> 检测到你的两个行为模式（过去 30 天，11 笔交易）：
>
> 1. **追涨模式**（置信度 0.83）
>    触发样本：买入 NVDA/TSLA 在单日涨幅 > 5% 后的 D+1/D+2，胜率 25%，平均收益 -3.2%
>    建议：买入前强制查看 `rag_ask_investment(question="追高的代价")`
>
> 2. **恐慌割肉模式**（置信度 0.71）
>    触发样本：持仓亏损 > 15% 后的 5 日内卖出，后续 30 日反弹 67%
>    建议：触发时自动推送飞书提醒 + 大师原话引用

### 场景 3：智能提醒 — 纪律锚点

> **用户**：NVDA 到 950 美元时提醒我重新评估。
>
> **调用**：`reminder_set_reminder(condition={ticker:"NVDA", operator:"<=", threshold:950, action:"review"})`
>
> **AI 返回**：
> 提醒已建立：NVDA <= 950 USD 时触发"复盘评估"。
> 触发后将自动拉取：当前价格、你对此票的历史决策卡片、相关大师语录。
> 提醒已同步飞书机器人（如已配置）。

---

## Claude Desktop 接入

将 InvestBrain 接入 Claude Desktop（macOS / Windows 通用）：

**配置文件位置**：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**配置内容**：

```json
{
  "mcpServers": {
    "investbrain": {
      "command": "python",
      "args": [
        "D:/claudework/investbrain/src/mcp_server/server.py"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-your-key-here"
      }
    }
  }
}
```

> 路径请按你 clone 的实际位置修改。配置完成后**重启 Claude Desktop**，会在工具栏出现"投资助手"图标（35 个工具）。

---

## 开源协议与路线图

本项目采用 **GNU Affero General Public License v3.0 (AGPLv3)** 授权。简言之：你可以自由使用、修改和分发，但通过网络提供服务的衍生作品也必须以相同协议开源。详见 [LICENSE](./LICENSE)。

| 层级 | 功能 | 状态 |
|------|------|------|
| **免费层** | 本地 MCP Server | ✅ 已上线 |
| | 16 位大师 RAG 问答 | ✅ 已上线 |
| | 行为模式检测 | ✅ 已上线 |
| | 提醒系统 | ✅ 已上线 |
| | 无限记忆存储 | ✅ 已上线 |
| **个人版** | 云端周报/月报（AI 生成） | 计划中（￥39/月） |
| | 跨设备数据同步 | 计划中 |
| **团队版** | 团队协作与共享知识库 | 计划中（￥199/月） |

---

## 架构

```
src/mcp_server/            # MCP Server（35 个工具）
├── server.py               # 主入口
├── tools/                  # 工具集
│   ├── thought_tools.py    # 想法记录
│   ├── rag_tools.py        # 投资 RAG
│   ├── memory_tools.py     # 记忆系统
│   ├── reminder_tools.py   # 提醒系统
│   ├── pattern_tools.py    # 行为模式
│   ├── report_tools.py     # 周报/月报
│   ├── roundtable_tools.py # 大师圆桌
│   └── notifier_tools.py   # 飞书推送
├── datasources/            # 数据源
│   ├── akshare_datasource.py
│   └── tushare_datasource.py
├── knowledge/              # 知识库
│   ├── vector_store.py     # Chroma 向量存储
│   └── graph_client.py     # 图存储
├── memory/                 # 记忆存储
├── patterns/               # 行为模式挖掘
├── llm/                    # LLM 客户端
│   ├── llm_router.py       # 通用 LLM 路由
│   ├── providers.py        # Provider 配置
│   └── deepseek_client.py
└── api_server.py           # REST API (LLM 配置)

data/
├── knowledge/              # 知识库
│   ├── graph/              # 16 位大师 + 概念
│   └── vectors/            # 向量索引
├── memory/                 # 用户记忆
├── cards/                  # 想法卡片
├── reminders/              # 提醒条件
└── config/                 # 配置文件
```

---

## MCP Tools（35 个）

```json
// 想法记录（3）
"thought_record_thought(text)",
"thought_search_memories(query)",
"thought_get_thought_cards(ticker)",

// 投资 RAG（3）
"rag_ask_investment(question)",
"rag_get_master_view(master, topic)",
"rag_search_knowledge(query)",

// 记忆系统（3）
"memory_get_user_profile()",
"memory_record_decision(data)",
"memory_get_behavior_patterns()",

// 提醒系统（3）
"reminder_set_reminder(condition)",
"reminder_get_reminders()",
"reminder_delete_reminder(id)",

// 行为模式（2）
"pattern_detect_patterns()",
"pattern_get_corrections()",

// 周报/月报（2）
"report_generate_weekly()",
"report_generate_monthly()",

// 大师圆桌（2）
"invest_roundtable(question)",
"invest_ask_master(master, question)",

// 飞书推送（2）
"notify_send_feishu(message)",
"notify_configure_feishu(webhook)",

// 行情数据（市场 + Tushare 共 10+）
"market_get_quote(ticker)",
"market_get_kline(ticker, period)",
"tushare_get_financial(ticker)",
...
```

完整工具列表见 [src/mcp_server/tools/](./src/mcp_server/tools/)。

---

## 知识库

**16 位投资大师**：
巴菲特、芒格、段永平、霍华德·马克斯、李录、格雷厄姆、达莫达兰、阿克曼、凯西·伍德、迈克尔·伯里、帕伯莱、塔勒布、林奇、费雪、德鲁肯米勒

**5 个核心概念**：
护城河、安全边际、能力圈、第二层思维、非对称风险

**行业知识**：
28 个申万行业深度研究框架（向量库内检索，不公开原文，保护核心方法论 IP）

---

## 数据源

| 数据源 | 用途 | 状态 |
|--------|------|------|
| AKShare | 实时行情 | ✅ |
| Tushare | 财务/历史数据 | ✅ |
| Chroma | 向量索引 | ✅ |
| SQLite | 本地记忆 | ✅ |

---

## 开发

```bash
# 启动 REST API Server（用于 LLM 配置）
python src/mcp_server/api_server.py
# 访问 http://localhost:8000/api/llm/config

# 启动前端（Next.js 落地页 + 设置面板）
npm install
npm run dev
# 访问 http://localhost:3000
```

测试：

```bash
pytest tests/
```

---

## 相关项目

| 项目 | 用途 |
|------|------|
| [invest-buddy-pet](https://github.com/lj22503/invest-buddy-pet) | 入门陪伴产品（人格测试） |
| [mangoview](https://github.com/lj22503/mangoview) | 超级系统站（专业分析） |

---

## 🛠️ 推荐工具链

> 以下工具推荐基于 [awesome-finai-tools-zn](https://github.com/lj22503/awesome-finai-tools-zn) 的 [SKILL.md](https://github.com/lj22503/awesome-finai-tools-zn/blob/main/SKILL.md) 场景→工具映射表生成，每类场景精选 1 个最佳工具。完整工具清单请访问仓库主页。

| 推荐工具 | 功能 | 安装方式 |
|---------|------|---------|
| **ashare-mcp** | 生产级 A 股 MCP Server，30 个 tool（实时行情/K线/涨停池/龙虎榜/财报/板块资金） | `git clone https://github.com/CharmYue/ashare-mcp && cd ashare-mcp && uv sync` |
| **opencli-eastmoney-quote** | 零配置 CLI，A 股/港股/美股实时行情秒出结果 | `npm install -g @jackwener/opencli` |
| **opencli-xueqiu-search** | 雪球股票搜索 + 热门帖子舆情分析，中文/代码均可 | `npm install -g @jackwener/opencli` |
| **Qlib** | 微软 AI 量化框架，自动因子挖掘 + 模型训练 + 回测评估 | `pip install pyqlib` |
| **盈米基金 MCP** | 69 个标准化 MCP 工具 + 16 项技能组件，含组合回测/蒙特卡洛模拟 | 联系盈米 AI 开放平台获取 API Key |

> 工具推荐逻辑基于 awesome-finai-tools-zn/data/institution-skills.json，每周自动更新。

---

## 🔗 工具链联动

本仓库是 FinAI 工具生态的一部分，与其他仓库协作：

| 仓库 | 定位 | 与本仓库的关系 |
|------|------|---------------|
| [awesome-finai-tools-zn](https://github.com/lj22503/awesome-finai-tools-zn) | 数据底座 | 提供工具清单+机构Skill数据 |
| [invest-brain](https://github.com/lj22503/invest-brain) | 工具推荐引擎 | 基于场景自动推荐工具 |
| [investment-buddy-pet](https://github.com/lj22503/investment-buddy-pet) | 人格化投顾 | 按投资人格匹配工具箱 |
| [SoloAdvisor-Toolkit](https://github.com/lj22503/SoloAdvisor-Toolkit) | 投顾流程工具包 | KYC→配置→组合→报告 |
| [knowledge-workflow](https://github.com/lj22503/knowledge-workflow) | 知识管理 | 收集→打标→存储→产出 |
>
---

**版本**: v0.1.0
**创建时间**: 2026-06-24
**许可**: AGPL v3
