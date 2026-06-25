# Contributing to InvestBrain

## Getting Started

1. Clone the repo: `git clone git@github.com:lj22503/invest-brain.git`
2. Install MCP server dependencies: `cd src/mcp_server && pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your `DEEPSEEK_API_KEY`
4. Install frontend dependencies: `cd frontend && npm install`

## Development Workflow

### MCP Server

```bash
# Start the API server (LLM config)
cd src/mcp_server && python api_server.py

# Start the MCP server (in another terminal)
cd src/mcp_server && python server.py
```

### Frontend (Next.js)

```bash
cd frontend && npm run dev
```

Visit `http://localhost:3000` for landing page, `http://localhost:3000/settings` for LLM config.

## Project Structure

See `AGENTS.md` or `CLAUDE.md` for full architecture.

## Code Conventions

- Python: Follow PEP 8
- Frontend: Next.js App Router + Tailwind CSS
- Tools: Each tool in `src/mcp_server/tools/` exports a `register_tools(app)` function
- Knowledge: Master data in `data/knowledge/graph/masters/` as JSON
- Git: Use descriptive commit messages in Chinese or English

## Agent-Friendly Standards

This project maintains AI Agent compatibility:

- `CLAUDE.md` — Agent entry point (keep updated with structural changes)
- `AGENTS.md` — Deep agent context (keep architecture diagram current)
- `llms.txt` — AI crawler summary (update when adding pages/tools)

When adding new features, update the relevant section in these files.

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run tests if applicable
4. Submit a PR with clear description

## Reporting Issues

Use GitHub Issues at https://github.com/lj22503/invest-brain/issues
