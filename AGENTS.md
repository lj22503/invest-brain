# AGENTS.md — InvestBrain Agent Context

> This file is for AI coding agents. It provides precise context about the InvestBrain repository structure, architecture, and conventions.

## Repository Purpose

InvestBrain is an **MCP Server + Skill package** for experienced investors. It acts as a "second brain" — a discipline anchor and behavioral mirror, *not* a robo-advisor. It does not execute trades.

**Key constraint**: Never give investment advice. The tool is a mirror + discipline anchor.

## Quick Navigation

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Agent entry point (Claude Code) |
| `README.md` | Human-readable overview |
| `src/mcp_server/server.py` | MCP Server entry point |
| `src/skills/investment_skill/skill.yaml` | Skill package definition |
| `data/graph/masters/` | 16 investment master JSON files |
| `app/` | Next.js marketing site |

## Architecture

```
invest-brain/
├── src/
│   ├── mcp_server/           # MCP Server — 40 tools
│   │   ├── server.py          # Main entry point
│   │   ├── tools/             # Tool implementations
│   │   │   ├── thought_tools.py   # Idea recording
│   │   │   ├── rag_tools.py       # Investment RAG
│   │   │   ├── memory_tools.py    # Memory system
│   │   │   ├── reminder_tools.py  # Alert system
│   │   │   └── pattern_tools.py   # Behavior patterns
│   │   ├── datasources/       # Data sources (AKShare, Tushare)
│   │   ├── knowledge/         # Knowledge base (GraphRAG + Vector)
│   │   ├── memory/            # User memory (SQLite)
│   │   ├── patterns/          # Behavior pattern detection
│   │   ├── llm/               # LLM client (multi-provider)
│   │   ├── deepseek_client.py
│   │   ├── llm_router.py
│   │   ├── providers.py
│   │   ├── local_model.py
│   │   └── routes.py
│   │   ├── api_server.py      # REST API for LLM config
│   │   └── server.py          # MCP server entry
│   ├── skills/
│   │   └── investment_skill/  # Hermes Agent Skill package
│   │       └── handlers/       # 6 handlers
│   └── patterns_cli.py        # CLI tool
├── app/                  # Next.js marketing site
├── data/                      # Knowledge, memory, config
└── docs/
    └── superpowers/plans/     # Development plans
```

## Tech Stack

- **Framework**: FastMCP (MCP Server)
- **Knowledge**: GraphRAG (JSON knowledge graph) + Vector search (Chroma)
- **Data Sources**: AKShare (free) + Tushare (pro)
- **LLM**: DeepSeek / Multi-provider (DeepSeek, OpenAI, Anthropic)
- **Database**: SQLite (memory, patterns)
- **Frontend**: Next.js 14 + Tailwind CSS (Vercel deploy)

## MCP Tool Categories

1. **Thought Recording** (`thought_*`) — Record ideas, search memories, get cards
2. **Investment RAG** (`rag_*`) — Ask investment questions, search master knowledge
3. **Memory System** (`memory_*`) — User profile, decisions, behavior patterns
4. **Reminders** (`reminder_*`) — Price/time/condition alerts
5. **Behavior Patterns** (`pattern_*`) — Bias detection and reports

## Development State

- **Phase**: 6 (core features operational)
- **Actively developing**: Frontend (Next.js site)
- **Pending**: ONNX model download, user auth system

## Key Files to Know

| Path | Description |
|------|-------------|
| `src/mcp_server/server.py` | Main server — tool registration + routes |
| `src/mcp_server/tools/thought_tools.py` | Uses DeepSeek to parse thoughts |
| `src/mcp_server/llm/llm_router.py` | LLM routing logic |
| `src/mcp_server/knowledge/graph_client.py` | GraphRAG client |
| `src/mcp_server/knowledge/vector_store.py` | Chroma vector store |
| `data/graph/masters/` | Investment master JSON knowledge |

## Agent-Friendly Files

This repo follows llms.txt standard and includes:

| File | Format | Purpose |
|------|--------|---------|
| `llms.txt` | Plain text | AI crawler summary |
| `CLAUDE.md` | Markdown | Agent entry point |
| `AGENTS.md` | Markdown | This file — deep agent context |
| `app/public/robots.txt` | Text | Crawler permissions |

## Design Principles

- No trade execution
- No paid advisory
- User data stored locally, never uploaded
- Tool is a "mirror" and "discipline anchor"
- Multi-provider LLM support (not vendor-locked)


---

## 提交前自查 4 问（2026-08-12 项目线规范，谁提交谁查）

> 任何 agent 在本仓库提交代码前，先过这 4 问（30 秒）：
1. **我改的是哪个项目？**（commit message 写明项目名）
2. **这个功能是不是已经存在？**（有没有重复实现——查一遍再写）
3. **我有没有绕过统一入口？**（有统一路由/工具就走统一入口，不另开独立通道）
4. **我改的是不是这个项目该改的？**（没串线——只动本项目文件）

**违反任一 → 停下修正后再提交。**


---

## 对话收尾流程（2026-08-12 项目线规范②，每次对话工作完成后必走）

> 完整规范：`D:\ObsidianVault\00-Meta\项目线-对话收尾流程.md`

1. **更新项目文档**：PROGRESS.md（今日进度：做了什么/下一步/卡点）+ docs/PITFALLS.md（今日坑点：现象→根因→修复→预防）
2. **neat-freak 六面审计**：代码/运行态/文档/规则/记忆/工作区一致性（五态：verified-current/changed-and-verified/pending/out-of-scope/not-applicable），消除多真相并存
3. **同步 GitHub**：commit（conventional commits + 提交前自查 4 问）+ push
4. **更新 Obsidian 02-Projects**：项目上下文.md / 项目经验.md（衔接③）
