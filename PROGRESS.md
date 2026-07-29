# PROGRESS — invest-brain

## 2026-07-29

### neat-freak 第二批优化（发版准备）

**背景**：用户目标是把项目发布到 MCP 平台被检索，本轮把 neat-freak 报告的 6 个待办 + 新发现的 6 个敏感文件 + 发版文件一并处理。

#### 已完成（commit `b162360` / `3c37482` / `c280ef6`）

- **敏感文件保护**（commit `b162360`）
  - `.gitignore` 加 `data/config/*.json`（llm/webhook 配置）
  - `.gitignore` 加 `data/memory/*.db`（用户记忆库）
  - 从仓库记录移除 `data/config/llm.json` + `data/config/webhook.json` + `data/memory/memory.db`（本地保留）
  - `README.md` §安全规则 第 70 行修正：之前说"已保护"但实际没有，本次与实际对齐
- **Python 运行缓存清理**（commit `3c37482`）
  - 从仓库记录移除 34 个 `__pycache__/*.pyc`（本地保留，运行时自动重新生成）
- **MCP 平台发版包**（commit `c280ef6`）
  - 新增 `Dockerfile` / `manifest.json` / `server.json` / `run_mcp_server.py`
  - 更新 `src/mcp_server/server.py` + `requirements.txt`

#### 新发现并处理（之前报告未列）

- `.mcpregistry_github_token` (40B) — MCP registry GitHub token
- `.mcpregistry_registry_token` (423B) — MCP registry token
- `login_output.txt` (372B) — 一次性登录输出
- `mcp-publisher.exe` (29MB) — MCP 发布 CLI
- `invest-brain.mcpb` (2.2MB) — 已构建的 MCP bundle

→ 全部加 `.gitignore` 规则，**本地副本保留**（用户决定，等发版需要时再用）

#### 待办（用户决策后处理）

- `mcp-key.txt` 本地副本删除（等用户亲自 rotate 凭据后）
- `AGENTS.md` 与 `CLAUDE.md` 是否冲突（待审阅）
- `data/memory/` 历史 `memory.db`（已被 untrack，本地文件保留）—— 决定是否保留

#### 下一步

- 推送本批 3 个 commit 到 GitHub master
- 处理 `AGENTS.md` / `CLAUDE.md` 协调
- 用 `mcp-publisher.exe` 实际发布到 MCP 平台验证

---

## 2026-07-28

### neat-freak 第一批优化（P0 安全）

- **commit `ffd76ac`**（已 push master）：
  - `.gitignore` 加 `mcp-key.txt` / `*.mcpb` / `.impeccable/` 三条规则
  - `CLAUDE.md` §项目结构 树状图根目录 `investbrain/` → `invest-brain/`
- neat-freak 报告称 server.json 实际 39 个工具与 CLAUDE.md 不一致 → **本机核对：实际 40 个工具，与文档一致**，无需修改
- `mcp-key.txt` 本地副本未删除，等用户亲自确认内容 + 决定是否 rotate 凭据

### 待用户确认

- `mcp-key.txt` 是否为真凭据 → 是否去对应服务 rotate + 删除本地副本
- 工作区仍有大量 uncommitted 改动（30+ .pyc 删除 / README / public 资源 / Dockerfile / manifest.json / server.json）—— 不在本次范围，等用户单独处置
- `.impeccable/` 现已 ignore，无需用户动作
- `docs/` 仍被全 ignore 但有 4 个文件（SEO/business-model/website-spec）—— 是否开放 docs/ 子集纳入 git 跟踪，待决

### 下一步

- 等用户决策 `mcp-key.txt` 处置
- 等用户决策 `docs/` 子集是否纳入 git