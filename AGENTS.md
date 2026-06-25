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
| `SPEC.md` | Website spec + Agent-Friendly checklist |
| `src/mcp_server/server.py` | MCP Server entry point |
| `src/skills/investment_skill/skill.yaml` | Skill package definition |
| `data/knowledge/graph/masters/` | 16 investment master JSON files |
| `frontend/` | Next.js marketing site |

## Architecture

```
investbrain/
├── src/
│   ├── mcp_server/           # MCP Server — 35 tools
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
│   │   ├── llm/               # LLM client (DeepSeek + providers)
│   │   ├── api_server.py      # REST API for LLM config
│   │   └── server.py          # MCP server entry
│   ├── skills/
│   │   └── investment_skill/  # Hermes Agent Skill package
│   │       └── handlers/       # 6 handlers
│   └── patterns_cli.py        # CLI tool
├── frontend/                  # Next.js marketing site
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
| `data/knowledge/graph/masters/` | Investment master JSON knowledge |

## Agent-Friendly Files

This repo follows llms.txt standard and includes:

| File | Format | Purpose |
|------|--------|---------|
| `llms.txt` | Plain text | AI crawler summary |
| `CLAUDE.md` | Markdown | Agent entry point |
| `AGENTS.md` | Markdown | This file — deep agent context |
| `SPEC.md` | Markdown | Website spec |
| `frontend/public/robots.txt` | Text | Crawler permissions |

## Design Principles

- No trade execution
- No paid advisory
- User data stored locally, never uploaded
- Tool is a "mirror" and "discipline anchor"
- Multi-provider LLM support (not vendor-locked)
