# InvestBrain — 投资第二大脑

> 有经验投资者的纪律自主工具，解决"知行合一"问题

---

## 定位

**核心问题**：投资者被叙事带着走，操作没纪律，事后后悔

**目标用户**：有投资经验的老客户，需要纪律锚点和行为审计

**产品口号**：不是投顾，不给建议，而是"镜子" + "纪律锚点"

---

## 核心能力

| 功能 | 说明 |
|------|------|
| 想法记录 | 用户说一句话，AI解析 + 关联历史 + 生成卡片 |
| 投资RAG | 大师思想检索问答（GraphRAG + 向量检索） |
| 记忆系统 | 用户画像、历史决策、行为模式挖掘 |
| 提醒触发 | 价格/时间/条件监控，支持飞书推送 |
| 行为模式挖掘 | 自动发现投资者的偏差模式 |

---

## 快速开始

```bash
# 1. 安装依赖
cd src/mcp_server
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 3. 启动 REST API Server (LLM配置用)
python api_server.py

# 4. 启动 MCP Server (另一个终端)
python server.py
```

## 前端

```bash
# 安装依赖
cd frontend
npm install

# 开发模式
npm run dev

# 访问 http://localhost:3000 查看落地页
# 访问 http://localhost:3000/settings 配置 LLM
```

---

## 架构

```
src/
├── mcp_server/           # MCP Server（35个工具）
│   ├── server.py          # 主入口
│   ├── tools/             # 工具集
│   │   ├── thought_tools.py   # 想法记录
│   │   ├── rag_tools.py       # 投资 RAG
│   │   ├── memory_tools.py    # 记忆系统
│   │   ├── reminder_tools.py  # 提醒系统
│   │   └── pattern_tools.py   # 行为模式
│   ├── datasources/       # 数据源
│   │   ├── akshare_datasource.py
│   │   └── tushare_datasource.py
│   ├── knowledge/          # 知识库
│   │   ├── vector_store.py    # Chroma 向量存储
│   │   └── graph_client.py    # 图存储
│   ├── memory/            # 记忆存储
│   ├── patterns/           # 行为模式挖掘
│   └── llm/               # LLM 客户端
│       ├── llm_router.py   # 通用 LLM 路由
│       ├── providers.py    # Provider 配置
│       └── deepseek_client.py
│   └── api_server.py      # REST API (LLM 配置)
├── skills/
│   └── investment_skill/   # Skill 包
│       └── handlers/       # 6个 Handler
└── patterns_cli.py        # CLI 工具

data/
├── knowledge/             # 知识库
│   ├── graph/            # 16位大师 + 概念
│   └── vectors/          # 向量索引
├── memory/               # 用户记忆
├── cards/                # 想法卡片
├── reminders/            # 提醒条件
└── config/              # 配置文件
```

---

## MCP Tools

```json
// 想法记录
"thought_record_thought(text)",
"thought_search_memories(query)",
"thought_get_thought_cards(ticker)",

// 投资RAG
"rag_ask_investment(question)",
"rag_get_master_view(master, topic)",
"rag_search_knowledge(query)",

// 记忆系统
"memory_get_user_profile()",
"memory_record_decision(data)",
"memory_get_behavior_patterns()",

// 提醒
"reminder_set_reminder(condition)",
"reminder_get_reminders()",
"reminder_delete_reminder(id)"
```

---

## 知识库

**16位投资大师**：
巴菲特、芒格、段永平、霍华德·马克斯、李录、格雷厄姆、达莫达兰、阿克曼、凯西·伍德、迈克尔·伯里、帕伯莱、塔勒布、林奇、费雪、朱恩贾wala、德鲁肯米勒

**5个核心概念**：
护城河、安全边际、能力圈、第二层思维、非对称风险

**行业知识**：
申万28行业分类、白酒、银行、新能源电池

---

## 数据源

| 数据源 | 用途 | 状态 |
|--------|------|------|
| AKShare | 实时行情 | ✅ |
| Tushare | 财务/历史数据 | ✅ |
| Chroma | 向量索引 | ✅ |
| SQLite | 本地记忆 | ✅ |

---

## 相关项目

| 项目 | 用途 |
|------|------|
| [invest-buddy-pet](https://github.com/lj22503/invest-buddy-pet) | 入门陪伴产品（人格测试） |
| [mangoview](https://github.com/lj22503/mangoview) | 超级系统站（专业分析） |

---

**版本**: v0.1.0
**创建时间**: 2026-06-24
