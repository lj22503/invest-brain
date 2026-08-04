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

---

## 2026-07-30

### neat-freak 第二批：mcp-key.txt 本地副本处置

- **删除** `mcp-key.txt` 本地副本（217B，含 ed25519 私钥 `private_hex`、公钥 `public_b64`、DNS TXT 记录 `txt_record`）
- **验证**：全仓库 grep `mcp-key.txt` / `private_hex` / `txt_record` / `mcp_key` 四个关键字，**仅在 `.gitignore` 与本 PROGRESS/历史报告中出现**，无任何代码运行时引用。属安全删除。
- **`.gitignore` 规则保留**（`mcp-key.txt` 第 41 行）—— 防止未来类似文件再次进入工作目录
- `.gitignore` 此前已经在 07-28 commit `ffd76ac` 加好，本轮不重复

### 本轮发现的其他工作区残留（不在本轮处置）

| 文件 | 性质 |
|------|------|
| `M src/mcp_server/tools/coaching_tools.py` | 修改未提交 |
| `?? err.txt` / `err2.txt` / `err3.txt` / `err4.txt` / `err_final.txt` | 调试错误捕获（5 个） |
| `?? out4.txt` / `out_final.txt` | 调试输出捕获（2 个） |
| **合计** | 1 处修改 + 7 个 untracked debug 文件 |

→ 属 mcp server 开发调试残留，下次 neat-freak 或单独会话处置。

---

*neat-freak 第二轮收尾：mcp-key.txt 已删，工作区清理未在本轮范围。*

---

## 2026-08-03

### Plan 1 完成（Sidecar Bootstrap）

**状态**：✅ 通过

**范围**：Tauri 主进程 + Python sidecar 子进程 + IPC 通信

**7 个 Task 全部完成**：

| Task | commit | 内容 |
|---|---|---|
| 1 | `8a5e1b9` | Python sidecar 最小 health_check |
| 2 | `4f205db` | PyInstaller 打包脚本 |
| 3 | `a3819d5` | Tauri 主进程最小 Hello Window |
| 4 | `a98372f` | Tauri IPC `health_check` 命令 |
| 5 | `7325347` | Tauri auto-spawn sidecar |
| 6 | `39434ba` | Playwright e2e 占位 |
| 7 | (pending) | 整体验证 + ico blocker 修复 + 本条记录 |

**端到端验证**：
- Tauri 启动 → 自动 spawn Python sidecar → 8765 端口 listen → `/health` 返回 JSON
- 子进程 parent PID 匹配 Tauri PID
- Tauri 窗口显示 "InvestBrain - Sidecar Health" 验证页
- sidecar 4 个 pytest 全 PASS
- Playwright 1 placeholder skipped

**关键决策**：
- Tauri 桌面 App（不继续走 Web 端）
- Python sidecar 走 subprocess + HTTP IPC（不用 stdio MCP 协议）
- 首版不代码签名
- ico blocker：commit 91 字节 .ico 保证 fresh clone 可编译

**后续**：可进入 Plan 2 (in-app UI with Next.js) / Plan 3 (服务包更新) / Plan 4 (落地页改造) / Plan 5 (CI/CD + Windows 打包)