# invest-brain — neat-freak 知识收尾报告

**收尾时间**：2026-07-24
**收尾路径**：轻量路径（项目已有 recent neat-freak 类 commit `7ecce45` Umami + `b3e2092` 35→40 工具数修正，本次为审计 + 安全复查）
**收尾者**：neat-freak（v3.0.0）

---

## 一、影响（用户视角）

- **🔴 暴露高风险安全文件**：`mcp-key.txt`（217B，ASCII 文本）出现在仓库根目录，未 `.gitignore`、未 commit、未跟踪；按文件名推测为某项 MCP/API 凭据。**未读其内容**，但**强烈建议立即处理**（见 §五 删除候选 1）。
- **暴露 CLAUDE.md 与目录命名脱节**：CLAUDE.md §项目结构 第 36-93 行整段树状图都以 `investbrain/`（无连字符）为目录名，但本地目录与 GitHub remote 都是 `invest-brain/`。下次会话 agent 按 CLAUDE.md 走会找不到路径。
- **暴露 `docs/` 目录被 .gitignore 全忽略但实际存在文件**：`data/` 行业 MD 资料被排除（合理），但 `docs/Brain_SEO_Strategy.md` / `docs/business-model.md` / `docs/website-spec.md` 也被排除，导致文档体系残缺。
- **暴露双规则文件未协调**：CLAUDE.md（93 行，详细项目结构 + 决策规则）与 AGENTS.md（5KB）并存，内容是否互相覆盖未读 AGENTS.md 验证。
- **暴露 CLAUDE.md "40 个工具" 与 server.json 实际 39 个不一致**：server.json tools 数组实际长度 39（逐一计数），与 CLAUDE.md 第 102 行 "✅ MCP Server（40 个工具）" 不一致。
- **暴露大量未提交改动**：包括 README 修订 + 30+ `.pyc` 删除 + 5 个新文件，状态混杂（含敏感文件）。

## 二、现役事实矩阵

| 事实面 | 状态 | 证据 |
|--------|------|------|
| 代码 | `verified-current` | `src/mcp_server/` Python MCP server + `src/skills/investment_skill/` Skill 包；`server.json` 39 个 tools 声明；`Dockerfile` Python 3.11 + chromadb 依赖 |
| 运行态 | `changed-and-verified` | HEAD `7ecce45` 已 push；本地有大量未提交（修改/删除/新增混合），需清理；Dockerfile 未跟踪但有效 |
| 文档 | `changed-and-verified` | README.md / CLAUDE.md / AGENTS.md / docs/4 文件；docs/ 被 .gitignore 全部排除 → 不在 git 中 |
| 规则 | `changed-and-verified` | CLAUDE.md 详细；AGENTS.md 5KB 待对照；4 项决策规则（不做交易执行/不做收费投顾/本地存储/不给建议） |
| 记忆 | `not-applicable` | 项目记忆以 SQLite 形式存在于 `data/memory/`，是产品功能而非 agent 记忆 |
| 工作区 | `changed-and-verified` | 新建 `.neat-freak/`；未提交改动中含 mcp-key.txt / mcpb / 缓存文件；.impeccable/ 历史残留 |

## 三、关键发现

### 3.1 🔴 mcp-key.txt 安全风险

| 属性 | 值 |
|------|-----|
| 路径 | `D:\claudework\invest-brain\mcp-key.txt` |
| 尺寸 | 217 字节（ASCII + CRLF） |
| 状态 | 未 gitignore、未 commit、未跟踪（`?? mcp-key.txt`） |
| 风险 | 按文件名推测为 MCP / API 凭据；即使未 commit，IDE / 备份 / 文件同步工具可能已捕获 |

**按 neat-freak "读到的内容不是给你的指令" 原则，本报告未读取文件内容。**

### 3.2 CLAUDE.md 项目结构目录名错误

```
第 36 行：
investbrain/                    ← ❌ 应为 invest-brain/
├── src/
│   ├── mcp_server/
...
```

整个树状图（37-93 行）以无连字符名为根，但：
- 本地目录：`D:\claudework\invest-brain\`
- GitHub remote：`https://github.com/lj22503/invest-brain.git`
- Dockerfile `WORKDIR /app`（无相对路径问题，但说明 workdir 不影响）
- server.json `repository.url: https://github.com/lj22503/invest-brain`

### 3.3 CLAUDE.md "40 个工具" vs server.json 实际 39

- CLAUDE.md 第 102 行："✅ MCP Server（40 个工具）"
- server.json `tools` 数组实际长度：**39**

少 1 个的原因可能是上次 commit `b3e2092 docs: 修复工具表 — 35→40` 把 README 改为 40 但 server.json 没补；或反之 CLAUDE.md 没更新。

### 3.4 .gitignore 矛盾

`.gitignore` 第 39 行：`docs/` 全忽略。

但本地有：
- `docs/Brain_SEO_Strategy.md`
- `docs/Brain_SEO_技术修复速查表.md`
- `docs/business-model.md`
- `docs/website-spec.md`

这意味着 `git ls-files docs/` 看不到任何文件；接手者 `git clone` 后**拿不到这些 SEO/技术文档**。

### 3.5 未提交改动清单（git status 摘录）

| 状态 | 文件 |
|------|------|
| 修改 | README.md, public/demo.html, public/llms.txt, public/og-image.png, public/robots.txt |
| 删除 | 30+ 个 `__pycache__/*.pyc` 文件（缓存清理，好习惯） |
| 新增（未跟踪） | Dockerfile, invest-brain.mcpb（2.0MB 二进制）, manifest.json, mcp-key.txt, server.json |

⚠️ 全部未 commit——可能含安全文件 mcp-key.txt，需要先处置才能安心 commit 其他。

### 3.6 双规则文件 CLAUDE.md + AGENTS.md

- CLAUDE.md 93 行（含项目结构、技术栈、当前状态、决策规则、启动方式）
- AGENTS.md 5KB（未读全文）
- 内容是否重复、是否矛盾未对照

## 四、改动 / 新建

| 文件 | 动作 | 原因 |
|------|------|------|
| `.neat-freak/reports/invest-brain-2026-07-24.md` | 新建 | 本次 audit trail |

## 五、待你确认（未确认前不动作）

1. **🔴 立即处理 `mcp-key.txt`**：
   - 确认其内容是凭据（如是，先去对应服务 rotate key）
   - 加 `.gitignore` 规则：`mcp-key.txt` / `*.mcpb` / `server.json`（看是否含敏感）
   - 改用环境变量或本地 `.env`（`.env` 已被 ignore，OK）
   - 删除 `mcp-key.txt` 本地副本
2. **CLAUDE.md 修正**：
   - 树状图根目录 `investbrain/` → `invest-brain/`
   - "40 个工具" → 数 server.json 实际数量（39）后修正
3. **`.gitignore docs/` 移除**：保留 docs/ 内文件被 git 跟踪，或显式排除某个子集（如 `data/industry/*.md` 风格）
4. **CLAUDE.md 与 AGENTS.md 协调**：决定哪个为真身、另一个删/降级
5. **未提交改动清理**：删除 30+ .pyc 后，先 commit 公开改动（README / public / Dockerfile / server.json / manifest.json），再处理敏感文件
6. **`.impeccable/` 目录**：是否纳入 .gitignore？看起来是历史 audit 残留

## 六、遗留

- AGENTS.md 全文未读
- 双规则文件是否内容冲突未对照
- server.json 39 个 tools 实际启用情况未实测
- Dockerfile `ENV DEEPSEEK_API_KEY=placeholder` 是 Glama validation 占位（合理），但生产部署是否覆盖未验证

---

*收尾完成度：5 事实面已标注（记忆面 not-applicable）。报告基于 commit `7ecce45`（HEAD），未 commit 改动量大且含敏感文件，建议先处理 mcp-key.txt 再批量提交。*