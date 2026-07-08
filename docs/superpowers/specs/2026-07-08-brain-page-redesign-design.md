# Brain 页面校准 — 设计文档

**日期**: 2026-07-08
**作者**: Claude (brainstorming 流程)
**项目**: InvestBrain (D:\claudework\investbrain)
**状态**: 待用户复核 → writing-plans

---

## 1. 背景与问题

用户反馈 brain 落地页 3 个问题：

1. **首页功能区 icon 是 emoji，丑** — 6 张功能卡用了 🎓📝📚🪞🔔🧠，与样本 `brain-landing-preview.html` 中「記 / 庫 / 鏡 / 鈴」等汉字 serif 风格不一致，视觉很跳。
2. **不突出 Agent 定位** — 用户打开页面 5 秒不知道 Brain 是给 AI Agent 用的，定位模糊。
3. **`/openapi` 页核心是「复制 Prompt」按钮，没用** — 真正的诉求是「其他 AI / 其他人类怎么安装 Brain」，prompt 复制只是边缘功能。

样本文件 `brain-landing-preview.html` 是用户提供的设计参考，风格基调：朱红 + 米黄纸 + 衬线 + 极简汉字字符。本设计保持站点现有 Tailwind 主题（vermillion / paper / ink），不重做 CSS。

---

## 2. 目标

- 让访客（人类）3 秒知道 Brain 是 MCP Server，是给 AI Agent 用的工具
- 让 AI Agent 能直接从页面读到 schema / tool 列表 / MCP 端点
- 让人类用户能 5 步把 Brain 装到自己的 AI 客户端上（Claude Desktop / Cursor）
- 首页功能卡 icon 与样本视觉风格统一

---

## 3. 非目标

- 不重做整体视觉风格 / Tailwind 配置 / globals.css
- 不改 MCP Server 后端代码（`src/mcp_server/*`）
- 不动样本预览文件 `brain-landing-preview.html`
- 不增加新依赖
- 不引入图片或外部资源（架构图用纯文本块表达）

---

## 4. 改动范围

只改两个文件：

| 文件 | 改动 |
|---|---|
| `app/page.tsx` | 首页 Hero 加 Agent 说明 / 扩 Core Positioning / 新增架构节 / Features 卡 emoji 换汉字 / CTA 文案 |
| `app/openapi/page.tsx` | Hero 重写 / 新增 to Human + to Agent 双 Tab / 7 张 skill 卡 icon 换汉字 / How to use 节重写 |

文件量：2 个，约 400 + 500 = 900 行（每个文件小范围改）。

---

## 5. 设计细节

### 5.1 首页 `app/page.tsx`

**5.1.1 Hero 顶部 Agent 标签条**（在现有 `by mangoFolio` 之上）

```tsx
<div className="text-ink-light text-xs tracking-wide mb-4 max-w-lg mx-auto leading-relaxed">
  Brain 不是 App — 是给 AI 用的 <span className="text-vermillion font-medium">35 个投资纪律 Skill 库</span><br />
  通过 MCP 协议接入 Claude / Cursor / 任意 AI，立即获得「镜子 + 纪律锚点」能力
</div>
```

**5.1.2 Core Positioning 节扩展**（在 Hero 之后，Features 之前）

保留原"不是投顾，不给建议 / 是镜子 + 纪律锚点"两行，紧接下方加对比块：

```tsx
<div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto text-sm">
  <div className="border border-border rounded p-5 bg-white">
    <div className="text-ink-faint text-xs mb-2">传统工具</div>
    <div className="text-ink-light">帮你交易 · 让你多操作 · 给建议</div>
  </div>
  <div className="border border-vermillion-light rounded p-5 bg-vermillion/[0.02]">
    <div className="text-vermillion text-xs mb-2 font-medium">Brain</div>
    <div className="text-ink-light">帮你思考 · 让你少操作但操作对 · 给「拷问」</div>
  </div>
</div>
```

**5.1.3 新增"架构 · 4 层关系"节**（在 Core Positioning 之后，Features 之前）

```tsx
<section className="py-24 px-6 md:px-16">
  <div className="max-w-5xl mx-auto">
    <div className="text-center mb-10">
      <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">架构</div>
      <h2 className="font-serif text-4xl font-bold">4 层关系</h2>
    </div>
    <div className="space-y-3 max-w-3xl mx-auto text-sm">
      <Row n="01" label="你" desc="普通用户 / 投资者 · 跟你的 AI 说话" />
      <Row n="02" label="AI Agent" desc="Claude / Cursor / 任意支持 MCP 的 AI 客户端" />
      <Row n="03" label="MCP 协议" desc="Model Context Protocol · AI 调用 Brain 的标准通道" />
      <Row n="04" label="Brain" desc="本地 MCP Server · 35 个 Skill Tools · SQLite 本地存储 · 16 位大师知识库" />
    </div>
  </div>
</section>
```

`<Row>` 子组件：左侧 vermillion 序号 + 中间标签 + 右侧说明，水平排列。

**5.1.4 Features 卡 emoji → 汉字 serif**

6 张功能卡 `f.icon` 字段名改为 `f.iconChar`，值：

| 中文标题 | iconChar | eng |
|---|---|---|
| 学习辅导 | 導 | learning_coaching |
| 想法记录 | 記 | idea_recorder |
| 大师思想库 | 庫 | knowledge_rag |
| 行为模式报告 | 鏡 | pattern_detector |
| 条件提醒 | 鈴 | reminder_scheduler |
| 记忆管理 | 藏 | memory_keeper |

渲染：

```tsx
<div className="font-serif text-4xl text-vermillion opacity-40">{f.iconChar}</div>
```

学习辅导卡右上角 NEW 角标保留。

**5.1.5 CTA 按钮文案**

- "浏览 Skill 市场" → "查看安装方法"
- "GitHub 部署" → 保留（指向 https://github.com/lj22503/invest-brain）

### 5.2 安装页 `app/openapi/page.tsx`

**5.2.1 Hero 重写**

```tsx
<div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-3">INSTALL BRAIN</div>
<h1>安装 Brain · 让你的 AI 获得投资纪律</h1>
<p>Brain 是一个本地运行的 MCP Server，提供 35 个 Skill 工具。
   通过两种方式接入：[给人类] 完整部署 · [给 AI Agent] MCP 协议。
   所有数据本地存储，不上传云端。</p>
```

**5.2.2 双 Tab 切换**（核心新增）

Tab 状态：`const [tab, setTab] = useState<"human" | "agent">("human")`

两个 Tab 内容分两块渲染。

**Tab A: for Human**

```
## 5 步把 Brain 装到你的 AI 上

01  准备环境
    · Python 3.10+
    · DeepSeek API Key（其它 LLM 也可）

02  克隆仓库
    $ git clone https://github.com/lj22503/invest-brain
    $ cd invest-brain

03  安装依赖
    $ cd src/mcp_server
    $ pip install -r requirements.txt

04  配置
    $ cp .env.example .env
    # 编辑 .env，填入 DEEPSEEK_API_KEY

05  启动 + 连接 Claude Desktop
    $ python server.py
    # 编辑 ~/.config/claude_desktop_config.json（或 Mac: ~/Library/Application Support/Claude/claude_desktop_config.json）：
    {
      "mcpServers": {
        "investbrain": {
          "command": "python",
          "args": ["/你的绝对路径/invest-brain/src/mcp_server/server.py"]
        }
      }
    }
    # 重启 Claude Desktop，Brain 工具即出现在 AI 可用工具列表
```

代码块样式：黑底浅字 + 等宽字体 + 复制按钮。

**Tab B: for Agent**

```
## 让你的 AI Agent 接入 Brain

Brain 暴露 35 个 MCP Tools。Agent 通过 MCP 协议调用。

### 自动发现 Schema
GET https://brain.mangofolio.com/openapi/schema.json

### MCP 端点
· 协议: MCP (Model Context Protocol)
· 传输: stdio / HTTP (本地)
· 入口: server.py
· 协议版本: 2024-11-05

### 35 个 Tools 分类（按模块）

【想法记录】3 个
  record_thought(text) — 记录一句话投资想法，AI 自动解析+关联历史
  search_memories(query) — 搜索历史想法
  get_thought_cards(ticker) — 获取某标的的全部想法卡

【学习辅导】5 个
  start_coaching(user_input) — 启动辅导会话
  continue_coaching(session_id, user_input) — 继续 Socratic 对话
  abandon_coaching(session_id) — 放弃当前会话
  switch_to_simple(session_id) — 切换到 10 步框架
  list_scenarios(limit) — 列出归档情景

【投资问答】4 个
  ask_investment(question) — RAG 检索 16 位大师
  get_master_view(master, topic) — 取某大师对某话题的观点
  search_knowledge(query) — 知识库关键词检索
  ...

【条件提醒】3 个
  set_reminder(condition) — 设置提醒
  get_reminders(status) — 查询提醒
  delete_reminder(id) — 删除提醒

【行为模式】3 个
  run_pattern_detection() — 跑行为模式检测
  get_pattern_report(period) — 取周/月报告
  ...

【记忆管理】3 个
  get_user_profile() — 取用户画像
  record_decision(data) — 记录决策
  get_behavior_patterns() — 取行为模式

【大师视角】1 个
  get_master_view(master, topic)

【系统工具】8 个（启动 / 健康检查 / 配置等内部 tools）
```

**5.2.3 Skill 速查卡**

移到 Tab B 下方，7 张卡保留（idea-recorder / learning-coaching / knowledge-rag / master-analyst / reminder-scheduler / memory-keeper / pattern-detector）。改动：

- icon 字段改 `iconChar`：`記 / 導 / 庫 / 鏡 / 鈴 / 藏 / 析`
- 渲染：`<div className="font-serif text-4xl text-vermillion opacity-40">{skill.iconChar}</div>`
- 卡片标题改为 "在 MCP 里叫什么"，下方放 tool name + 简述
- "复制 Prompt" 按钮保留（移到右下角小字）
- "详情" 按钮保留，展开显示全部 tools + params + returns

**5.2.4 How to use 节**

原 01/02/03 三步卡 → 改成两列路径卡：

```
## 两条路径

[ 给人类 ]  5 步完整部署  →  for Human Tab
[ 给 AI Agent ]  MCP / JSON Schema → for Agent Tab
```

**5.2.5 Footer**

保留协议 / 传输 / 存储 / GitHub 链接。

---

## 6. 数据 / 状态

- 安装页 Tab 状态：`useState<"human" | "agent">("human")`
- skill 卡详情展开：`useState<string | null>(expandedId)` — 保留现有
- 复制 Prompt 反馈：`useState<string | null>(copiedId)` — 保留现有

无新增接口、无新增依赖、无新增数据文件。

---

## 7. 错误处理

- 代码块复制按钮：`navigator.clipboard.writeText()` 失败时 fallback 用 `document.execCommand('copy')`，catch 后给个 toast："复制失败，请手动复制"
- Tab 切换无网络请求，纯前端

---

## 8. 测试 / 验收

**视觉验收**（手动浏览器 `npm run dev`）：
1. 首页 Hero 顶部有 Agent 说明短句
2. 首页 Core Positioning 节有"传统工具 vs Brain"对比卡
3. 首页"架构 · 4 层关系"节存在且 4 行可读
4. 首页 Features 6 张卡 icon 是单个汉字 + serif + vermillion 0.4 透明度
5. 首页 CTA 第一个按钮文案为"查看安装方法"
6. `/openapi` Hero 标题/小标签更新
7. `/openapi` 默认 Tab = for Human
8. `/openapi` for Human Tab 显示 5 步含真实 shell + JSON 代码
9. `/openapi` 切到 for Agent Tab 显示 35 个 tools 分类列表
10. `/openapi` 7 张 skill 卡 icon 是汉字

**功能验收**：
- `npm run dev` 启动无 TypeScript / ESLint 报错
- 复制 Prompt 按钮仍可用（点击后有 ✓ 已复制 反馈）
- Tab 切换无闪烁 / 无控制台报错
- 详情展开仍可用

**约束验收**：
- 不动 `brain-landing-preview.html`
- 不动 `app/layout.tsx` / `app/globals.css` / `tailwind.config.ts`
- `git diff` 只触及 `app/page.tsx` 和 `app/openapi/page.tsx` 两个文件

---

## 9. 实现顺序建议

1. 先改 `app/page.tsx`：icon 换汉字（最小改动可立即看效果）
2. 再加 Hero 顶部 Agent 说明 + 架构节
3. 改 CTA 文案
4. 再改 `app/openapi/page.tsx`：先动 Hero + Tab 框架
5. 填 for Human 内容（代码块）
6. 填 for Agent 内容（tools 列表）
7. 改 skill 卡 icon + 标题
8. 最后改 How to use 节

每步本地 `npm run dev` 看效果。

---

## 10. 风险与开放问题

- **风险 1**：汉字字符 `記 / 庫 / 鏡 / 鈴 / 藏 / 導 / 析` 在 Noto Serif SC 字体下显示效果可能差异较大，需浏览器实测；如显示异常 fallback 到 `font-serif` 通用。
- **风险 2**：Tab 内容（特别是 for Agent 的 35 个 tools 列表）当前还没列出完整 35 个，需要从 `app/openapi/schema.json` 或 `src/mcp_server/tools/*.py` 读取实际 tool 名补齐——实现阶段先列已有 7 类，再补到完整 35。
- **开放问题**：是否需要在安装页也放样本 `brain-landing-preview.html` 的视觉？当前决定**不放**（避免和真实站点视觉混淆）。

---

**等待用户复核。**