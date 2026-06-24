# Investment Skill Package

可分发的投资助手Skill包，包含6个核心Skill。

## Skills

| Skill | 触发词 | 功能 |
|-------|--------|------|
| investment-orchestrator | 投资想法、投资问题、记忆、提醒、持仓检查、大师思想 | 主调度器，路由分析 |
| idea-recorder | 想法记录、投资想法、我觉得、想看看、关注、考虑买入、准备卖出 | 想法记录卡片生成 |
| knowledge-rag | 什么是、如何看待、如何分析、投资理论、护城河、安全边际、周期理论 | 投资知识问答RAG |
| memory-keeper | 我的持仓、我之前、关于XXX的想法、我的投资原则、行为模式 | 用户记忆管理 |
| reminder-scheduler | 提醒我、跌破、涨到、当PE分位、每周检查、每月总结、通知我 | 提醒调度管理 |
| master-analyst | 巴菲特怎么看、芒格说、段永平思想、大师观点、投资大师 | 大师思想分析 |

## 安装

```bash
pip install -e .
```

## 使用

通过Claude Code Skill工具调用。

## 结构

```
investment_skill/
├── skill.yaml          # Skill定义
├── handlers/           # 各功能handler实现
│   ├── idea_handler.py
│   ├── rag_handler.py
│   ├── memory_handler.py
│   ├── reminder_handler.py
│   └── master_handler.py
└── data/               # 内置知识库
```