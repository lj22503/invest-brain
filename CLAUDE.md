# CLAUDE.md — InvestBrain

## 项目概述

**定位**：投资第二大脑，有经验投资者的纪律自主工具

**核心问题**：解决投资者"知行合一"问题 — 被叙事带着走，操作没纪律，事后后悔

**目标用户**：有投资经验的老客户，需要纪律锚点和行为审计

**交付形式**：MCP Server + Skill 包，能被 Agent 调用

---

## 核心能力

1. **想法记录** — 用户说一句话，AI解析+关联历史+生成卡片
2. **投资知识RAG** — 大师思想检索问答（GraphRAG + 向量检索）
3. **记忆系统** — 用户画像、历史决策、行为模式挖掘
4. **提醒触发** — 价格/时间/条件监控，支持飞书/钉钉/Bark 多通道推送
5. **行为模式挖掘** — 自动发现投资者的偏差模式

---

## 技术栈

- **框架**：MCP Server（FastMCP）
- **知识库**：混合方案（知识图谱 + 向量检索）
- **数据源**：AKShare（免费）+ Tushare
- **LLM**：DeepSeek V4-Pro / Flash（按场景自动路由）
- **数据库**：SQLite（记忆库、行为模式库）

---

## 项目结构

```
investbrain/
├── src/
│   ├── mcp_server/        # MCP Server 主入口
│   │   ├── server.py      # 主入口
│   │   ├── scheduler.py   # APScheduler 定时任务
│   │   ├── price_checker.py  # 启动时价格检查
│   │   ├── notifier.py    # 通知分发（多通道）
│   │   ├── tools/         # MCP Tools
│   │   │   ├── thought_tools.py   # 想法记录
│   │   │   ├── rag_tools.py        # 投资 RAG
│   │   │   ├── memory_tools.py     # 记忆系统
│   │   │   ├── reminder_tools.py   # 提醒系统
│   │   │   └── pattern_tools.py    # 行为模式
│   │   ├── datasources/   # 数据源
│   │   │   ├── akshare_datasource.py
│   │   │   └── tushare_datasource.py
│   │   ├── knowledge/     # 知识库
│   │   │   ├── vector_store.py  # Chroma 向量存储
│   │   │   └── graph_client.py  # 图存储客户端
│   │   ├── memory/        # 记忆存储
│   │   │   └── store.py
│   │   ├── patterns/      # 行为模式挖掘
│   │   │   ├── detector.py
│   │   │   ├── analyzer.py
│   │   │   └── report.py
│   │   └── llm/           # LLM 客户端
│   │       └── deepseek_client.py
│   ├── skills/
│   │   └── investment_skill/  # Skill 包
│   │       ├── handlers/       # Skill Handlers
│   │       │   ├── idea_handler.py
│   │       │   ├── rag_handler.py
│   │       │   ├── memory_handler.py
│   │       │   ├── reminder_handler.py
│   │       │   ├── master_handler.py
│   │       │   └── orchestrator_handler.py
│   │       ├── skill.yaml
│   │       └── pyproject.toml
│   └── patterns_cli.py    # CLI 工具
├── data/
│   ├── knowledge/         # 知识库
│   │   └── vectors/      # 向量索引（Chroma）
│   ├── graph/            # 知识图谱
│   │   ├── masters/     # 16位大师 JSON
│   │   ├── concepts/    # 5个概念 JSON
│   │   └── relations/   # 关系 JSON
│   ├── memory/           # 用户记忆
│   │   ├── memory.db     # SQLite
│   │   ├── decisions/    # 决策历史
│   │   ├── patterns/     # 行为模式
│   │   └── user_profile/ # 用户画像
│   ├── cards/            # 想法卡片
│   ├── reminders/        # 提醒条件
│   └── config/           # 配置文件
│       └── webhook.json  # 通知 WebHook
```

---

## 当前状态

**阶段**：Phase 6 完成，核心功能可用

**已完成**：
- ✅ MCP Server（40个工具）
- ✅ DeepSeek LLM 集成
- ✅ Tushare/AKShare 数据源
- ✅ 行为模式挖掘 MVP
- ✅ 多通道通知

**待完成**：
- ⏳ ONNX 模型下载（向量检索）
- ⏳ 前端对话界面
- ⏳ 用户认证系统

---

## 启动方式

```bash
cd src/mcp_server
pip install -r requirements.txt
python server.py
```

---

## 决策规则

- 不做交易执行
- 不做收费投顾
- 用户数据本地存储，不上传云端
- 工具定位是"镜子"和"纪律锚点"，不给建议
