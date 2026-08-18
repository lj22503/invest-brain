# InvestBrain (投资第二大脑)

> **Your personal investment second brain** — capture thoughts, detect behavior patterns, and chat with 16 investing masters via local RAG. No cloud, no lock-in.

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/MCP_Server%2BRAG-AGPLv3-orange?style=for-the-badge" alt="MCP Server + RAG"/></a>
  <a href="README.md"><img src="https://img.shields.io/badge/中文-README-blue?style=for-the-badge" alt="中文 README"/></a>
  <a href="llms.txt"><img src="https://img.shields.io/badge/llms.txt-AI_Ready-green?style=for-the-badge" alt="llms.txt"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPLv3-yellow?style=for-the-badge" alt="AGPLv3"/></a>
</p>

## What problem does this solve?

| Pain Point | How this project helps |
|---|---|
| I keep repeating the same investing mistakes (chasing highs, panic selling) | Detects behavior patterns from your own records and surfaces them back |
| I forget my own reasoning and past decisions | Local memory store keeps every thought, decision, and master quote in one place |
| Generic AI advice, not tailored to my style | Builds a personal investor profile (principles, patterns, decisions) from real behavior |
| I want to learn from the greats, but reading is slow | 16 investing masters (Buffett, Munger, Duan Yongping…) available via local RAG Q&A |

## Core Capabilities

| Capability | What it does |
|---|---|
| Thought / decision capture | Record investing thoughts; auto-extract behavior patterns and decisions |
| Master RAG Q&A | Ask Buffett / Munger / 13+ masters, grounded in their writings (local embeddings) |
| Behavior pattern mining | Detects patterns like "chasing highs" / "panic selling" from your records |
| Reminder system | Price-triggered and scheduled reminders, pushed to WeChat via PushPlus |
| Weekly / monthly reports | Auto-generated investment reviews (roadmap) |
| Desktop app (Windows) | Tauri shell + local sidecar; data stored at `%APPDATA%\InvestBrain\data` |

## Quick Start

### Option A: Desktop Client (Windows, recommended)

1. Download and install `InvestBrain_0.1.2_x64_en-US.msi` from [Releases](https://github.com/lj22503/invest-brain/releases)
2. Open the app — the "brain loaded" status bar and try-chat guide appear immediately
3. Fill in your own LLM key in Settings to enable real conversation

### Option B: MCP Server (any MCP client)

```bash
# 1. Install dependencies
cd src/mcp_server && pip install -r requirements.txt

# 2. Configure your own LLM API key
cp .env.example .env
# edit .env, set DEEPSEEK_API_KEY to your own key

# 3. Start the MCP server
python server.py
```

> First run downloads ~80MB of embedding model files (Chroma + ONNX). The server accepts stdio MCP calls after startup.

### Configure Claude Desktop

Add to `claude_desktop_config.json` (paths vary by OS):

```json
{
  "mcpServers": {
    "investbrain": {
      "command": "python",
      "args": ["D:/claudework/invest-brain/src/mcp_server/server.py"],
      "env": { "DEEPSEEK_API_KEY": "sk-your-key-here" }
    }
  }
}
```

Restart Claude Desktop — the "投资助手" toolset (39 tools) appears.

## Security

- Your API key stays local: `data/config/llm.json` / `.env` are gitignored, never committed.
- Desktop sidecar proxies LLM calls locally — the key never enters the WebView.

## Tech Stack

- Python MCP Server (stdio) + FastAPI sidecar (HTTP, port 8765)
- Chroma vector store + ONNX embeddings (local RAG)
- SQLite memory store (`data/memory/memory.db`)
- Next.js (export) frontend + Tauri 2 (Windows desktop)
- Data sources: AKShare (A-share market data), PushPlus (WeChat push)

## License

AGPLv3 — free to use, modify, and distribute. Network-serving derivatives must also be open-sourced under the same license. See [LICENSE](./LICENSE).

---

**Project Metadata**
- **Version**: v0.1.2
- **GitHub**: https://github.com/lj22503/invest-brain
- **Other languages**: [简体中文](README.md)
