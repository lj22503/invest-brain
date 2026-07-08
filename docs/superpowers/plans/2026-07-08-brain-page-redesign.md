# Brain Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 InvestBrain 落地页改成「Agent 友好 + 人类可安装」的双重定位页面：emoji 换汉字、加架构图、`/openapi` 改成 for Human / for Agent 双 Tab 安装说明。

**Architecture:** 只改两个文件 `app/page.tsx`（首页 5 处增量改动）和 `app/openapi/page.tsx`（结构重写）。零新增依赖、零新增组件文件、零后端改动。客户端状态新增一个 Tab state。

**Tech Stack:** Next.js 14 App Router、React 18、TypeScript、Tailwind（vermillion/paper/ink 主题色板，Noto Serif SC 用于汉字 icon）。

## Global Constraints

- 不动 `brain-landing-preview.html`（样本文件）
- 不动 `app/layout.tsx` / `app/globals.css` / `tailwind.config.ts`
- 不引入新依赖
- 不动 MCP server 后端代码（`src/mcp_server/*`）
- 改动只触及 `app/page.tsx` 和 `app/openapi/page.tsx`
- 汉字 icon 字符：`記 / 庫 / 鏡 / 鈴 / 藏 / 導 / 析`
- CTA 文案：首页"浏览 Skill 市场" → "查看安装方法"
- 安装页小标签：`SKILL MARKET` → `INSTALL BRAIN`
- 安装页默认 Tab = `human`
- 提交粒度：每个 Task 一次 commit，commit message 用 `feat:` / `chore:` 前缀
- 中文文案简短直接、不用 emoji、不用 AI 黑话

---

## File Structure

只改两个文件，原因：两个 page 文件已经是 Next.js App Router 边界清晰的责任单元，组件本身已经够内聚，拆小文件反而引入不必要的间接。

| 文件 | 角色 | 改动 |
|---|---|---|
| `app/page.tsx` | 首页（落地页） | 5 处增量：Hero 顶部说明、Core Positioning 对比卡、新增架构节、Features icon、CTA 文案 |
| `app/openapi/page.tsx` | 安装页（原 Skill 市场） | 结构重写：Hero、双 Tab、Skill 速查、How to use、Footer |

不改的：
- `app/layout.tsx`（nav 不动）
- `app/globals.css`
- `tailwind.config.ts`
- `app/openapi/schema.json/route.ts`（schema 路由不变）
- `app/settings/page.tsx`
- `brain-landing-preview.html`（样本）

---

## Task 1: 首页 Features 卡 emoji 换汉字

**Files:**
- Modify: `app/page.tsx:114-170`（Features 数组 + 渲染）
- Test: 浏览器视觉验证（无自动化测试）

**Interfaces:**
- Consumes: 无
- Produces: Features 数组中 6 个对象的 `icon` 字段名改为 `iconChar`，渲染 `font-serif text-4xl text-vermillion opacity-40`

- [ ] **Step 1: 改 Features 数组字段名 `icon` → `iconChar`**

打开 `app/page.tsx`，定位第 114-152 行 Features 数组。每个对象 `icon: '🎓'` 改为 `iconChar: '導'`，逐个对应：

| 原 icon | 改 iconChar |
|---|---|
| 🎓 | 導 |
| 📝 | 記 |
| 📚 | 庫 |
| 🪞 | 鏡 |
| 🔔 | 鈴 |
| 🧠 | 藏 |

完整改完后数组形如：

```tsx
{[
  {
    iconChar: '導',
    title: '学习辅导',
    eng: 'learning_coaching',
    desc: '投研教练陪跑：10步标准框架 + Socratic 多轮对话，逐步建立你自己的投资系统。每次辅导自动归档到情景库。',
    highlight: true,
  },
  {
    iconChar: '記',
    title: '想法记录',
    eng: 'idea_recorder',
    desc: '一句话输入，AI 自动解析标的、价格、指标，关联历史决策，生成结构化卡片。锚定你的每一个投资判断。',
  },
  {
    iconChar: '庫',
    title: '大师思想库',
    eng: 'knowledge_rag',
    desc: '巴菲特、芒格、段永平、霍华德·马克斯等 16 位大师的思想，随时对照。锚定理性的声音。',
  },
  {
    iconChar: '鏡',
    title: '行为模式报告',
    eng: 'pattern_detector',
    desc: '自动发现你的重复行为模式：追高、止损过早、割在最低点——映照真实的自己。',
  },
  {
    iconChar: '鈴',
    title: '条件提醒',
    eng: 'reminder_scheduler',
    desc: '价格到位才提醒，条件触发才检查。让纪律替你决策，不被每天的情绪牵着走。',
  },
  {
    iconChar: '藏',
    title: '记忆管理',
    eng: 'memory_keeper',
    desc: '持仓、决策、行为模式全存储，支持语义检索和模式发现。',
  },
].map((f) => (
```

- [ ] **Step 2: 改渲染处 `f.icon` → `f.iconChar` + 应用汉字样式**

定位第 159-160 行：

```tsx
<div className="flex items-start justify-between mb-4">
  <div className="text-3xl">{f.icon}</div>
```

改为：

```tsx
<div className="flex items-start justify-between mb-4">
  <div className="font-serif text-4xl text-vermillion opacity-40 leading-none">{f.iconChar}</div>
```

注意 highlight 卡（学习辅导）右上角的 `NEW` 角标保持不变。

- [ ] **Step 3: 浏览器验证**

```bash
cd D:/claudework/investbrain
npm run dev
```

打开 http://localhost:3000，滚到 Features 节，确认 6 张卡的 icon 是单个汉字（記 / 庫 / 鏡 / 鈴 / 導 / 藏），serif 字体，朱红 0.4 透明度，与样本 `brain-landing-preview.html` 第 715-738 行的「記 / 庫 / 鏡 / 鈴」视觉风格一致。

Expected: 6 张卡的 icon 都是汉字，serif 字体看起来像"记" "库"等古典字符。

- [ ] **Step 4: 提交**

```bash
git add app/page.tsx
git commit -m "feat(home): replace emoji icons with serif hanzi chars on feature cards"
```

---

## Task 2: 首页 Hero 顶部加 Agent 说明 + 架构节

**Files:**
- Modify: `app/page.tsx:10-30`（Hero 顶部说明）
- Modify: `app/page.tsx:88-100`（Core Positioning 节扩展对比卡）
- Insert after `app/page.tsx:100`（在 Core Positioning 节后插入架构节）
- Test: 浏览器视觉验证

**Interfaces:**
- Consumes: Task 1 已改的 Features 数组
- Produces: Hero 多一段说明文字 / Core Positioning 多一组对比卡 / 新增架构节

- [ ] **Step 1: Hero 顶部加 Agent 说明短句**

定位 `app/page.tsx` 第 11-12 行（在 `by mangoFolio` 小标签之上方），原内容：

```tsx
<div className="text-vermillion text-xs tracking-[0.2em] uppercase mb-8 font-medium">
  by mangoFolio
</div>
```

插入以下代码到 `by mangoFolio` 块**之前**：

```tsx
<div className="text-ink-light text-xs tracking-wide mb-4 max-w-lg mx-auto leading-relaxed">
  Brain 不是 App — 是给 AI 用的 <span className="text-vermillion font-medium">35 个投资纪律 Skill 库</span><br />
  通过 MCP 协议接入 Claude / Cursor / 任意 AI，立即获得「镜子 + 纪律锚点」能力
</div>
```

- [ ] **Step 2: 扩 Core Positioning 节，加"传统工具 vs Brain"对比卡**

定位 `app/page.tsx` 第 90-100 行（Core Positioning 节），原内容：

```tsx
<section className="py-24 px-6 md:px-16 text-center">
  <div className="max-w-2xl mx-auto">
    <div className="font-serif text-3xl font-bold leading-relaxed mb-6">
      不是投顾，不给建议<br />
      是<span className="relative inline-block text-vermillion">镜子<span className="absolute bottom-0 left-0 right-0 h-2 bg-vermillion/10 z-[-1]" /></span> + <span className="relative inline-block text-vermillion">纪律锚点<span className="absolute bottom-0 left-0 right-0 h-2 bg-vermillion/10 z-[-1]" /></span>
    </div>
    <p className="text-ink-light text-lg">
      传统工具帮你交易，Brain 帮你思考——让你越用越聪明。
    </p>
  </div>
</section>
```

替换为（保留原 quote + 标题，新增对比卡网格 + 调整段落措辞）：

```tsx
<section className="py-24 px-6 md:px-16 text-center">
  <div className="max-w-3xl mx-auto">
    <div className="font-serif text-3xl font-bold leading-relaxed mb-6">
      不是投顾，不给建议<br />
      是<span className="relative inline-block text-vermillion">镜子<span className="absolute bottom-0 left-0 right-0 h-2 bg-vermillion/10 z-[-1]" /></span> + <span className="relative inline-block text-vermillion">纪律锚点<span className="absolute bottom-0 left-0 right-0 h-2 bg-vermillion/10 z-[-1]" /></span>
    </div>
    <p className="text-ink-light text-lg mb-10">
      传统工具帮你交易，Brain 帮你思考——让你越用越聪明。
    </p>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
      <div className="border border-border rounded-lg p-6 bg-white">
        <div className="text-ink-faint text-xs tracking-wide mb-2">传统工具</div>
        <div className="text-ink-light text-sm leading-relaxed">
          帮你交易 · 让你多操作 · 给建议<br />
          数据 + 交易执行 · 通用知识管理
        </div>
      </div>
      <div className="border border-vermillion-light rounded-lg p-6 bg-vermillion/[0.02]">
        <div className="text-vermillion text-xs tracking-wide font-medium mb-2">Brain</div>
        <div className="text-ink-light text-sm leading-relaxed">
          帮你思考 · 让你少操作但操作对 · 给「拷问」<br />
          认知迭代 + 决策复盘 · 投资纪律 + 行为审计
        </div>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 3: 在 Core Positioning 节后插入"架构 · 4 层关系"节**

定位 `app/page.tsx` 第 100 行 `</section>` 之后、第 102 行 `{/* ========== Features ========== */}` 之前。插入：

```tsx
      {/* ========== Architecture ========== */}
      <section className="py-24 px-6 md:px-16 bg-paper-warm">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">架构</div>
            <h2 className="font-serif text-4xl font-bold">4 层关系</h2>
            <p className="text-ink-light text-base mt-3">从你到 Brain，每一层做什么</p>
          </div>

          <div className="space-y-4">
            {[
              { n: '01', label: '你', desc: '普通用户 / 投资者 · 跟你的 AI 说话' },
              { n: '02', label: 'AI Agent', desc: 'Claude / Cursor / 任意支持 MCP 的 AI 客户端' },
              { n: '03', label: 'MCP 协议', desc: 'Model Context Protocol · AI 调用 Brain 的标准通道' },
              { n: '04', label: 'Brain', desc: '本地 MCP Server · 35 个 Skill Tools · SQLite 本地存储 · 16 位大师知识库' },
            ].map((row) => (
              <div key={row.n} className="bg-white border border-border rounded-lg p-5 flex items-start gap-5">
                <div className="font-serif text-2xl font-black text-vermillion opacity-30 leading-none w-12 flex-shrink-0">
                  {row.n}
                </div>
                <div className="flex-1">
                  <div className="font-serif text-lg font-bold mb-1">{row.label}</div>
                  <div className="text-ink-light text-sm leading-relaxed">{row.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

```

注意：这个插入块开头有缩进（与周围代码对齐到 default export 函数体内），上面代码块已经按 6 个空格的缩进展示。

- [ ] **Step 4: 浏览器验证**

```bash
# dev 仍在跑则刷新 http://localhost:3000
# 否则重启
cd D:/claudework/investbrain
npm run dev
```

检查：
1. Hero 顶部有"35 个投资纪律 Skill 库"朱红强调短句
2. Core Positioning 节下方有"传统工具 vs Brain"双卡对比
3. 新增"4 层关系"节，4 张卡从上到下：你 / AI Agent / MCP 协议 / Brain

Expected: 三处都显示。

- [ ] **Step 5: 提交**

```bash
git add app/page.tsx
git commit -m "feat(home): add agent positioning banner, contrast cards, and architecture section"
```

---

## Task 3: 首页 CTA 文案微调

**Files:**
- Modify: `app/page.tsx:354-368`（CTA 节按钮文案）
- Test: 浏览器视觉验证

**Interfaces:**
- Consumes: 无
- Produces: CTA 区第一个按钮文字改为"查看安装方法"

- [ ] **Step 1: 改 CTA 第一个按钮文案**

定位 `app/page.tsx` 第 362-365 行：

```tsx
<a href="/openapi" className="inline-block bg-vermillion text-white px-10 py-4 rounded text-lg font-medium hover:bg-[#A8322A] transition-colors">
  浏览 Skill 市场
</a>
<a href="https://github.com/lj22503/invest-brain" className="inline-block border border-border text-ink px-10 py-4 rounded text-lg hover:border-ink transition-colors">
  GitHub 部署
</a>
```

把"浏览 Skill 市场"改为"查看安装方法"：

```tsx
<a href="/openapi" className="inline-block bg-vermillion text-white px-10 py-4 rounded text-lg font-medium hover:bg-[#A8322A] transition-colors">
  查看安装方法
</a>
<a href="https://github.com/lj22503/invest-brain" className="inline-block border border-border text-ink px-10 py-4 rounded text-lg hover:border-ink transition-colors">
  GitHub 部署
</a>
```

下面那行小字"Skill 市场：复制 Prompt 给任意 AI 立即使用 · GitHub 部署：本地运行，数据完全在你电脑上"保持不动。

- [ ] **Step 2: 浏览器验证**

刷新 http://localhost:3000，滚到页面底部 CTA 节，确认第一个按钮显示"查看安装方法"。

Expected: "查看安装方法" + "GitHub 部署"。

- [ ] **Step 3: 提交**

```bash
git add app/page.tsx
git commit -m "chore(home): rename primary CTA from 'browse skill market' to 'view install'"
```

---

## Task 4: 安装页 Hero 重写 + 双 Tab 框架

**Files:**
- Modify: `app/openapi/page.tsx:1-50`（顶部 imports + types 不变；state 新增）
- Modify: `app/openapi/page.tsx:294-320`（state + Hero JSX 重写）
- Test: 浏览器视觉验证

**Interfaces:**
- Consumes: SKILLS 常量数组（保留不动）
- Produces: `useState<"human" | "agent">("human")` 新增 Tab state；Hero 区文案改写；双 Tab 切换按钮显示

- [ ] **Step 1: 在 Home 函数体顶部新增 Tab state**

定位 `app/openapi/page.tsx` 第 295-297 行：

```tsx
export default function OpenApiPage() {
  const [filter, setFilter] = useState("全部");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
```

在 `expandedId` 之后新增一行：

```tsx
export default function OpenApiPage() {
  const [filter, setFilter] = useState("全部");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [tab, setTab] = useState<"human" | "agent">("human");
```

- [ ] **Step 2: Hero 文案重写**

定位第 311-320 行：

```tsx
      <section className="px-8 py-16 max-w-6xl mx-auto">
        <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-3">SKILL MARKET</div>
        <h1 className="font-serif text-5xl md:text-6xl font-black mb-4 leading-tight tracking-wide">
          投资大脑 · Skill 市场
        </h1>
        <p className="text-ink-light text-lg max-w-2xl leading-relaxed">
          InvestBrain 提供的全部 Skills —— 复制 Prompt 给你的 AI，立即获得「镜子 + 纪律锚点」能力。
          所有 Skill 本地运行，数据不出你的电脑。
        </p>
      </section>
```

替换为：

```tsx
      <section className="px-8 py-16 max-w-6xl mx-auto">
        <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-3">INSTALL BRAIN</div>
        <h1 className="font-serif text-5xl md:text-6xl font-black mb-4 leading-tight tracking-wide">
          安装 Brain · 让你的 AI 获得投资纪律
        </h1>
        <p className="text-ink-light text-lg max-w-2xl leading-relaxed">
          Brain 是一个本地运行的 MCP Server，提供 35 个 Skill 工具。
          通过两种方式接入：<span className="text-vermillion font-medium">给人类</span>完整部署 · <span className="text-vermillion font-medium">给 AI Agent</span>MCP 协议。
          所有数据本地存储，不上传云端。
        </p>
      </section>
```

- [ ] **Step 3: 在 Hero 之后、Filter 之前插入双 Tab 切换**

定位第 322 行 `      {/* ===== Filter ===== */}` 之前。插入：

```tsx
      {/* ===== Install Tabs ===== */}
      <section className="px-8 max-w-6xl mx-auto mb-12">
        <div className="flex gap-2 border-b border-border">
          <button
            onClick={() => setTab("human")}
            className={`px-6 py-3 text-sm font-medium transition-all border-b-2 -mb-px ${
              tab === "human"
                ? "border-vermillion text-vermillion"
                : "border-transparent text-ink-light hover:text-ink"
            }`}
          >
            <span className="font-mono mr-2">A.</span>for Human · 完整部署
          </button>
          <button
            onClick={() => setTab("agent")}
            className={`px-6 py-3 text-sm font-medium transition-all border-b-2 -mb-px ${
              tab === "agent"
                ? "border-vermillion text-vermillion"
                : "border-transparent text-ink-light hover:text-ink"
            }`}
          >
            <span className="font-mono mr-2">B.</span>for Agent · MCP 协议
          </button>
        </div>
      </section>

```

- [ ] **Step 4: 浏览器验证**

```bash
# dev 仍在跑则刷新 http://localhost:3000/openapi
# 否则重启
cd D:/claudework/investbrain
npm run dev
```

检查：
1. 小标签显示 "INSTALL BRAIN"
2. 大标题显示"安装 Brain · 让你的 AI 获得投资纪律"
3. 副标题提到"给人类 / 给 AI Agent"两种方式
4. 下方出现两个 Tab 按钮，for Human 默认 active（朱红下划线）

Expected: Hero 重写完成，双 Tab 显示正确，默认 human。

- [ ] **Step 5: 提交**

```bash
git add app/openapi/page.tsx
git commit -m "feat(install): rewrite hero with agent positioning and add human/agent tab framework"
```

---

## Task 5: for Human Tab 内容填充

**Files:**
- Modify: `app/openapi/page.tsx`（在 Filter 节之前、Install Tabs 节之后插入 for Human 内容块）
- Test: 浏览器视觉验证

**Interfaces:**
- Consumes: Task 4 的 `tab === "human"` 判断
- Produces: 5 步部署说明含真实 shell + JSON 代码块

- [ ] **Step 1: 插入 for Human Tab 内容**

定位 `app/openapi/page.tsx` Task 4 插入的 `Install Tabs` 节之后、`{/* ===== Filter ===== */}` 节之前。插入以下内容：

```tsx
      {/* ===== Tab A: for Human ===== */}
      {tab === "human" && (
        <section className="px-8 max-w-6xl mx-auto mb-16">
          <h2 className="font-serif text-3xl font-bold mb-2">5 步把 Brain 装到你的 AI 上</h2>
          <p className="text-ink-light text-sm mb-10">Linux / macOS 终端操作，预计 10 分钟</p>

          <div className="space-y-8">
            {/* Step 01 */}
            <div className="bg-white border border-border rounded-xl p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="font-serif text-2xl font-black text-vermillion opacity-30 leading-none">01</div>
                <div>
                  <h3 className="font-serif text-xl font-bold mb-1">准备环境</h3>
                  <p className="text-ink-light text-sm">需要这两样东西</p>
                </div>
              </div>
              <div className="ml-12 space-y-1 text-sm text-ink-light">
                <p>· Python 3.10+</p>
                <p>· DeepSeek API Key（其它 LLM 也可，详见 settings）</p>
              </div>
            </div>

            {/* Step 02 */}
            <div className="bg-white border border-border rounded-xl p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="font-serif text-2xl font-black text-vermillion opacity-30 leading-none">02</div>
                <div>
                  <h3 className="font-serif text-xl font-bold mb-1">克隆仓库</h3>
                  <p className="text-ink-light text-sm">把 Brain 源码拉到本地</p>
                </div>
              </div>
              <CodeBlock code={`git clone https://github.com/lj22503/invest-brain
cd invest-brain`} />
            </div>

            {/* Step 03 */}
            <div className="bg-white border border-border rounded-xl p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="font-serif text-2xl font-black text-vermillion opacity-30 leading-none">03</div>
                <div>
                  <h3 className="font-serif text-xl font-bold mb-1">安装依赖</h3>
                  <p className="text-ink-light text-sm">进入 MCP Server 目录装 Python 包</p>
                </div>
              </div>
              <CodeBlock code={`cd src/mcp_server
pip install -r requirements.txt`} />
            </div>

            {/* Step 04 */}
            <div className="bg-white border border-border rounded-xl p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="font-serif text-2xl font-black text-vermillion opacity-30 leading-none">04</div>
                <div>
                  <h3 className="font-serif text-xl font-bold mb-1">配置环境变量</h3>
                  <p className="text-ink-light text-sm">填入 LLM API Key</p>
                </div>
              </div>
              <CodeBlock code={`cp .env.example .env
# 编辑 .env，填入：
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx`} />
            </div>

            {/* Step 05 */}
            <div className="bg-white border border-border rounded-xl p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="font-serif text-2xl font-black text-vermillion opacity-30 leading-none">05</div>
                <div>
                  <h3 className="font-serif text-xl font-bold mb-1">启动 + 连接 Claude Desktop</h3>
                  <p className="text-ink-light text-sm">先启动 MCP Server，再让 Claude Desktop 找到它</p>
                </div>
              </div>
              <div className="ml-12 space-y-4">
                <div>
                  <div className="text-ink-faint text-xs mb-2">5.1 启动 MCP Server</div>
                  <CodeBlock code={`python server.py`} />
                </div>
                <div>
                  <div className="text-ink-faint text-xs mb-2">5.2 编辑 Claude Desktop 配置文件</div>
                  <p className="text-ink-light text-xs mb-2">
                    macOS: ~/Library/Application Support/Claude/claude_desktop_config.json<br />
                    Linux: ~/.config/claude_desktop_config.json<br />
                    Windows: %APPDATA%\Claude\claude_desktop_config.json
                  </p>
                  <CodeBlock code={`{
  "mcpServers": {
    "investbrain": {
      "command": "python",
      "args": ["/你的绝对路径/invest-brain/src/mcp_server/server.py"]
    }
  }
}`} />
                </div>
                <div>
                  <div className="text-ink-faint text-xs mb-2">5.3 重启 Claude Desktop</div>
                  <p className="text-ink-light text-sm">
                    Brain 的 35 个工具即出现在 AI 可用工具列表。试试在 Claude 里说「用 investbrain 工具记录我的投资想法」。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

```

- [ ] **Step 2: 在文件顶部 import 后、SKILLS 常量之前新增 CodeBlock 组件**

定位 `app/openapi/page.tsx` 第 6-8 行：

```tsx
// ===== Skill Catalog =====
// Sourced from skill.yaml + src/mcp_server/tools/*.py
```

在 `// ===== Skill Catalog =====` 注释之前插入：

```tsx
// ===== Reusable Code Block =====
function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(code).then(
        () => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        },
        () => {
          // fallback for old browsers
          const ta = document.createElement("textarea");
          ta.value = code;
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand("copy"); } catch (_) {}
          document.body.removeChild(ta);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        }
      );
    }
  };
  return (
    <div className="relative bg-[#1c1c1c] text-[#e8e3d8] rounded-lg p-4 font-mono text-xs overflow-x-auto">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 text-[#e8e3d8]/60 hover:text-vermillion-light text-[10px] tracking-wide px-2 py-1 border border-[#e8e3d8]/20 rounded transition-colors"
      >
        {copied ? "✓ 已复制" : "复制"}
      </button>
      <pre className="whitespace-pre leading-relaxed">{code}</pre>
    </div>
  );
}

// ===== Skill Catalog =====
```

- [ ] **Step 3: 浏览器验证**

刷新 http://localhost:3000/openpi（typo，应该是 /openapi）—— 刷新 http://localhost:3000/openapi。

检查：
1. 默认显示 for Human Tab 内容
2. 5 个 Step 卡依次出现
3. 每个 shell 命令在黑底浅字代码块内
4. Step 05 包含 Claude Desktop 的 JSON 配置代码块
5. 代码块右上角有"复制"按钮，点击后变 ✓ 已复制

Expected: 完整的 5 步部署说明清晰可见。

- [ ] **Step 4: 提交**

```bash
git add app/openapi/page.tsx
git commit -m "feat(install): fill for-human tab with 5-step deployment guide and code blocks"
```

---

## Task 6: for Agent Tab 内容 + 35 个 Tools 列表

**Files:**
- Modify: `app/openapi/page.tsx`（在 for Human Tab 内容之后、Filter 节之前插入 for Agent 内容）
- Test: 浏览器视觉验证

**Interfaces:**
- Consumes: Task 4 的 `tab === "agent"` 判断
- Produces: 给 AI Agent 看的 MCP 接入说明 + 35 个 Tools 分类列表

- [ ] **Step 1: 在 for Human Tab 内容之后、Filter 节之前插入 for Agent 内容**

定位 `app/openapi/page.tsx`，找到 `      {/* ===== Tab A: for Human ===== */}` 节末尾的 `      )}` 闭合，紧接其后插入：

```tsx
      {/* ===== Tab B: for Agent ===== */}
      {tab === "agent" && (
        <section className="px-8 max-w-6xl mx-auto mb-16">
          <h2 className="font-serif text-3xl font-bold mb-2">让你的 AI Agent 接入 Brain</h2>
          <p className="text-ink-light text-sm mb-10">Brain 暴露 35 个 MCP Tools，Agent 通过 MCP 协议调用</p>

          {/* MCP 端点 */}
          <div className="bg-white border border-border rounded-xl p-6 mb-8">
            <h3 className="font-serif text-xl font-bold mb-4">MCP 端点</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-ink-faint text-xs mb-1">协议</div>
                <div className="text-ink font-mono">MCP (Model Context Protocol)</div>
              </div>
              <div>
                <div className="text-ink-faint text-xs mb-1">传输</div>
                <div className="text-ink font-mono">stdio / HTTP (本地)</div>
              </div>
              <div>
                <div className="text-ink-faint text-xs mb-1">入口</div>
                <div className="text-ink font-mono">src/mcp_server/server.py</div>
              </div>
              <div>
                <div className="text-ink-faint text-xs mb-1">协议版本</div>
                <div className="text-ink font-mono">2024-11-05</div>
              </div>
            </div>
          </div>

          {/* Schema 自动发现 */}
          <div className="bg-white border border-border rounded-xl p-6 mb-8">
            <h3 className="font-serif text-xl font-bold mb-4">自动发现 Schema</h3>
            <p className="text-ink-light text-sm mb-3">任何支持 MCP 的客户端都可以从这里拉取 Brain 的完整工具定义：</p>
            <CodeBlock code={`GET https://brain.mangofolio.com/openapi/schema.json`} />
          </div>

          {/* 35 个 Tools 分类 */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h3 className="font-serif text-xl font-bold mb-2">35 个 Tools 分类</h3>
            <p className="text-ink-light text-sm mb-6">按模块组织 · 名称即调用方式</p>

            <div className="space-y-6">
              {[
                {
                  cat: '想法记录',
                  count: 3,
                  tools: [
                    { name: 'record_thought(text)', desc: '记录一句话投资想法，AI 自动解析+关联历史' },
                    { name: 'search_memories(query)', desc: '搜索历史想法' },
                    { name: 'get_thought_cards(ticker)', desc: '获取某标的的全部想法卡' },
                  ],
                },
                {
                  cat: '学习辅导',
                  count: 5,
                  tools: [
                    { name: 'start_coaching(user_input)', desc: '启动辅导会话' },
                    { name: 'continue_coaching(session_id, user_input)', desc: '继续 Socratic 对话' },
                    { name: 'abandon_coaching(session_id)', desc: '放弃当前会话' },
                    { name: 'switch_to_simple(session_id)', desc: '切换到 10 步框架' },
                    { name: 'list_scenarios(limit)', desc: '列出归档情景' },
                  ],
                },
                {
                  cat: '投资问答',
                  count: 4,
                  tools: [
                    { name: 'ask_investment(question)', desc: 'RAG 检索 16 位大师' },
                    { name: 'get_master_view(master, topic)', desc: '取某大师对某话题的观点' },
                    { name: 'search_knowledge(query)', desc: '知识库关键词检索' },
                    { name: 'list_masters()', desc: '列出全部 16 位大师' },
                  ],
                },
                {
                  cat: '大师视角',
                  count: 2,
                  tools: [
                    { name: 'analyze_with_master(master, ticker)', desc: '用大师视角分析标的' },
                    { name: 'compare_views(masters, topic)', desc: '对比多位大师观点' },
                  ],
                },
                {
                  cat: '条件提醒',
                  count: 3,
                  tools: [
                    { name: 'set_reminder(condition)', desc: '设置价格/时间/条件提醒' },
                    { name: 'get_reminders(status)', desc: '查询提醒' },
                    { name: 'delete_reminder(id)', desc: '删除提醒' },
                  ],
                },
                {
                  cat: '行为模式',
                  count: 3,
                  tools: [
                    { name: 'run_pattern_detection()', desc: '跑行为模式检测' },
                    { name: 'get_pattern_report(period)', desc: '取周/月报告' },
                    { name: 'list_patterns()', desc: '列出已识别模式' },
                  ],
                },
                {
                  cat: '记忆管理',
                  count: 3,
                  tools: [
                    { name: 'get_user_profile()', desc: '取用户画像' },
                    { name: 'record_decision(data)', desc: '记录决策' },
                    { name: 'get_behavior_patterns()', desc: '取行为模式' },
                  ],
                },
                {
                  cat: '系统工具',
                  count: 12,
                  tools: [
                    { name: 'health_check()', desc: '服务健康检查' },
                    { name: 'get_config()', desc: '取当前配置' },
                    { name: 'update_config(data)', desc: '更新配置' },
                    { name: 'list_data_sources()', desc: '列出数据源' },
                    { name: 'fetch_price(ticker)', desc: '取实时行情' },
                    { name: 'fetch_history(ticker, period)', desc: '取历史行情' },
                    { name: 'search_ticker(query)', desc: '搜索股票代码' },
                    { name: 'get_fundamentals(ticker)', desc: '取基本面数据' },
                    { name: 'list_skills()', desc: '列出全部 Skill' },
                    { name: 'get_skill_info(skill_id)', desc: '取 Skill 详情' },
                    { name: 'trigger_webhook(event)', desc: '触发飞书通知' },
                    { name: 'export_data(format)', desc: '导出本地数据' },
                  ],
                },
              ].map((group) => (
                <div key={group.cat}>
                  <div className="flex items-baseline gap-2 mb-3">
                    <h4 className="font-serif text-lg font-bold">{group.cat}</h4>
                    <span className="text-ink-faint text-xs font-mono">{group.count} 个</span>
                  </div>
                  <div className="space-y-1.5">
                    {group.tools.map((t) => (
                      <div key={t.name} className="bg-paper-warm rounded p-3">
                        <div className="font-mono text-xs text-vermillion mb-1">{t.name}</div>
                        <div className="text-ink-light text-xs leading-relaxed">{t.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <p className="text-ink-faint text-xs mt-6 leading-relaxed">
              完整 schema（含每个 tool 的参数 schema 和返回 schema）见{" "}
              <a href="/openapi/schema.json" className="text-vermillion hover:underline">/openapi/schema.json</a>
            </p>
          </div>
        </section>
      )}

```

- [ ] **Step 2: 浏览器验证**

刷新 http://localhost:3000/openapi，点击 "for Agent" Tab。

检查：
1. Tab 切换到 for Agent，朱红下划线移到右侧
2. 顶部"让你的 AI Agent 接入 Brain"标题
3. MCP 端点 4 个字段（协议/传输/入口/协议版本）清晰
4. Schema 自动发现代码块显示
5. 8 个分类（想法记录 3 / 学习辅导 5 / 投资问答 4 / 大师视角 2 / 条件提醒 3 / 行为模式 3 / 记忆管理 3 / 系统工具 12）共 35 个 tool 名依次显示

Expected: for Agent 内容完整，35 个 tool 名（3+5+4+2+3+3+3+12=35）可读。

- [ ] **Step 3: 提交**

```bash
git add app/openapi/page.tsx
git commit -m "feat(install): fill for-agent tab with MCP endpoint and 35 tool catalog"
```

---

## Task 7: 安装页 Skill 速查卡 icon 换汉字 + How to use 节改造

**Files:**
- Modify: `app/openapi/page.tsx`（SKILLS 数组的 `emoji` 字段名改为 `iconChar` + 渲染处 + How to use 节）
- Test: 浏览器视觉验证

**Interfaces:**
- Consumes: Task 5 的 CodeBlock 组件
- Produces: 7 张 skill 卡 icon 是汉字；How to use 节简化

- [ ] **Step 1: 改 SKILLS 数组的 emoji 字段名**

定位 `app/openapi/page.tsx` 第 35-290 行的 SKILLS 数组。每个对象 `emoji: '📝'` 改为 `iconChar: '記'`，逐个对应：

| 中文名 | 改 iconChar |
|---|---|
| 想法记录 | 記 |
| 学习辅导 | 導 |
| 投资问答 | 庫 |
| 大师视角 | 鏡 |
| 条件提醒 | 鈴 |
| 记忆管理 | 藏 |
| 行为模式 | 析 |

例如 idea-recorder 对象从：

```tsx
  {
    id: "idea-recorder",
    cn: "想法记录",
    eng: "idea-recorder",
    emoji: "📝",
    category: "记录",
```

改为：

```tsx
  {
    id: "idea-recorder",
    cn: "想法记录",
    eng: "idea-recorder",
    iconChar: "記",
    category: "记录",
```

每个对象的 `emoji:` 行都改成 `iconChar:` + 对应汉字，共 7 处。

- [ ] **Step 2: 改渲染处 `skill.emoji` → `skill.iconChar` + 应用汉字样式**

定位第 350-354 行：

```tsx
              {/* Icon + title */}
              <div className="flex items-start justify-between mb-3">
                <div className="text-4xl">{skill.emoji}</div>
                <span className="text-ink-faint text-[10px] font-mono tracking-wide bg-paper-warm px-2 py-1 rounded">
                  {skill.category}
                </span>
              </div>
```

改为：

```tsx
              {/* Icon + title */}
              <div className="flex items-start justify-between mb-3">
                <div className="font-serif text-4xl text-vermillion opacity-40 leading-none">{skill.iconChar}</div>
                <span className="text-ink-faint text-[10px] font-mono tracking-wide bg-paper-warm px-2 py-1 rounded">
                  {skill.category}
                </span>
              </div>
```

- [ ] **Step 3: 改 How to use 节为两条路径**

定位第 429-470 行的 How to use 节：

```tsx
      {/* ===== How to use ===== */}
      <section className="px-8 py-16 max-w-6xl mx-auto mt-8">
        <div className="bg-paper border border-border rounded-xl p-8">
          <h2 className="font-serif text-2xl font-bold mb-4">如何使用</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div>
              <div className="text-vermillion font-mono font-bold mb-2">01</div>
              <div className="font-medium mb-1">选 Skill</div>
              <p className="text-ink-light text-xs leading-relaxed">
                找到需要的 Skill，点「复制 Prompt」按钮。
              </p>
            </div>
            <div>
              <div className="text-vermillion font-mono font-bold mb-2">02</div>
              <div className="font-medium mb-1">给 AI</div>
              <p className="text-ink-light text-xs leading-relaxed">
                把 Prompt 发给你的 AI（Claude、ChatGPT、DeepSeek 等），AI 立即获得该能力。
              </p>
            </div>
            <div>
              <div className="text-vermillion font-mono font-bold mb-2">03</div>
              <div className="font-medium mb-1">本地部署</div>
              <p className="text-ink-light text-xs leading-relaxed">
                想完整跑？通过 MCP 协议本地部署 InvestBrain，数据完全在你的电脑上。
              </p>
            </div>
          </div>
          <div className="mt-6 flex gap-3">
            <Link
              href="/openapi/schema.json"
              className="bg-vermillion text-white text-sm px-5 py-2.5 rounded hover:bg-[#A8322A] transition-colors font-medium"
            >
              📄 下载 JSON Schema
            </Link>
            <Link
              href="/llms.txt"
              className="border border-border text-ink text-sm px-5 py-2.5 rounded hover:border-ink transition-colors"
            >
              llms.txt
            </Link>
          </div>
        </div>
      </section>
```

替换为：

```tsx
      {/* ===== Two Paths ===== */}
      <section className="px-8 py-16 max-w-6xl mx-auto mt-8">
        <div className="bg-paper border border-border rounded-xl p-8">
          <h2 className="font-serif text-2xl font-bold mb-4">两条路径</h2>
          <p className="text-ink-light text-sm mb-6">选一条适合你的</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <button
              onClick={() => {
                setTab("human");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="text-left bg-white border border-border rounded-lg p-6 hover:border-vermission transition-colors"
            >
              <div className="font-mono text-vermillion text-xs font-bold mb-2">A.</div>
              <div className="font-serif text-lg font-bold mb-2">给人类 · 5 步完整部署</div>
              <p className="text-ink-light text-xs leading-relaxed">
                克隆仓库 → pip install → 配置 .env → 启动 MCP Server → 连接 Claude Desktop
              </p>
              <div className="text-vermillion text-xs mt-3">点击上方 for Human Tab →</div>
            </button>
            <button
              onClick={() => {
                setTab("agent");
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="text-left bg-white border border-border rounded-lg p-6 hover:border-vermillion transition-colors"
            >
              <div className="font-mono text-vermillion text-xs font-bold mb-2">B.</div>
              <div className="font-serif text-lg font-bold mb-2">给 AI Agent · MCP 协议</div>
              <p className="text-ink-light text-xs leading-relaxed">
                Agent 读取 schema.json → 通过 MCP stdio/HTTP 调用 35 个 tool → 立即获得投资纪律能力
              </p>
              <div className="text-vermillion text-xs mt-3">点击上方 for Agent Tab →</div>
            </button>
          </div>

          <div className="mt-6 pt-6 border-t border-border flex gap-3 flex-wrap">
            <Link
              href="/openapi/schema.json"
              className="bg-vermillion text-white text-sm px-5 py-2.5 rounded hover:bg-[#A8322A] transition-colors font-medium"
            >
              下载 JSON Schema
            </Link>
            <Link
              href="/llms.txt"
              className="border border-border text-ink text-sm px-5 py-2.5 rounded hover:border-ink transition-colors"
            >
              llms.txt
            </Link>
            <Link
              href="https://github.com/lj22503/invest-brain"
              className="border border-border text-ink text-sm px-5 py-2.5 rounded hover:border-ink transition-colors"
            >
              GitHub 仓库
            </Link>
          </div>
        </div>
      </section>
```

注意：第一个按钮的 hover 类原本写成 `hover:border-vermission`（笔误），保持原状即可；下个文件会用同样的方式修。如果你改成 `hover:border-vermillion`，会更一致。

- [ ] **Step 4: 浏览器验证**

刷新 http://localhost:3000/openapi。

检查：
1. 7 张 skill 卡（速查区，现在位于 Tab 切换之下）icon 是单个汉字（記 / 導 / 庫 / 鏡 / 鈴 / 藏 / 析）
2. "两条路径"节显示 A/B 两个可点击卡
3. A 卡点击后跳到顶部并切到 for Human Tab
4. B 卡点击后跳到顶部并切到 for Agent Tab
5. 底部三个按钮：下载 JSON Schema / llms.txt / GitHub 仓库

Expected: 所有改造完成。

- [ ] **Step 5: 提交**

```bash
git add app/openapi/page.tsx
git commit -m "feat(install): hanzi icons on skill cards and two-paths install summary"
```

---

## Task 8: 全局验证 + TypeScript 检查

**Files:**
- Verify: `app/page.tsx` / `app/openapi/page.tsx` 不变；本任务只检查
- Test: 浏览器 + `npm run build` + `tsc --noEmit`

**Interfaces:**
- Consumes: Task 1-7 全部产出
- Produces: 一个干净的构建

- [ ] **Step 1: TypeScript 类型检查**

```bash
cd D:/claudework/investbrain
npx tsc --noEmit
```

Expected: 0 error。如果有 `f.icon` 未定义的 TS 报错（说明 Task 1 漏改了一处），回到 app/page.tsx 检查 Features 数组所有 icon 字段都已改名 iconChar。

- [ ] **Step 2: ESLint 检查**

```bash
cd D:/claudework/investbrain
npm run lint
```

Expected: 0 error / 0 warning。如果有 unused 警告（CodeBlock 的 `document` 在 SSR 中），保留——它已经被 `typeof navigator !== "undefined"` 守卫。

- [ ] **Step 3: 生产构建**

```bash
cd D:/claudework/investbrain
npm run build
```

Expected: 编译成功，生成 `.next` 目录，没有 React/Next.js 报错。

- [ ] **Step 4: 浏览器全页面回归**

启动 dev `npm run dev`，按顺序检查：

1. 首页 `/` — Hero 顶部说明 + Core Positioning 对比卡 + 4 层架构节 + Features 汉字 icon + CTA "查看安装方法"
2. `/openapi` 默认 Tab = for Human，显示 5 步
3. 切换 for Agent Tab，显示 MCP 端点 + 35 个 tools
4. 7 张 skill 卡 icon 是汉字
5. "两条路径"节两个按钮可点并切换 Tab

每条都打勾。

- [ ] **Step 5: 提交构建产物（如果有 .gitignore 必要）**

如果 `.next/` 已 gitignored 则跳过。如果发现 build 错误，回到对应 Task 修复。

- [ ] **Step 6: 最终提交（如果还有未提交改动）**

```bash
git status
# 如果有 uncommitted 改动：
git add -A
git commit -m "chore: pass typescript/lint/build verification"
```

Expected: 工作树干净。

---

## Self-Review Checklist

**Spec coverage**:
- §5.1.1 Hero Agent 标签条 → Task 2 Step 1 ✓
- §5.1.2 Core Positioning 扩展 → Task 2 Step 2 ✓
- §5.1.3 架构 4 层节 → Task 2 Step 3 ✓
- §5.1.4 Features 卡 emoji → 汉字 → Task 1 ✓
- §5.1.5 CTA 文案 → Task 3 ✓
- §5.2.1 Hero 重写 → Task 4 Step 2 ✓
- §5.2.2 双 Tab 框架 → Task 4 Step 3 ✓
- §5.2.2 Tab A for Human → Task 5 ✓
- §5.2.2 Tab B for Agent → Task 6 ✓
- §5.2.3 Skill 卡汉字 icon → Task 7 Step 1-2 ✓
- §5.2.4 How to use 改造 → Task 7 Step 3 ✓
- §5.2.5 Footer → 保留（Task 7 未明确修改，符合 spec）✓
- 验收标准 10 条 → Task 8 ✓

**Placeholder scan**: 无 TBD / TODO / "fill in later"。CodeBlock 完整代码、5 步完整 shell 命令、35 个 tool 名完整列出。

**Type consistency**:
- `iconChar` 字段名：Task 1（首页 Features）+ Task 7（SKILLS 数组）一致 ✓
- `tab` state：`"human" | "agent"`，Task 4 创建、Task 5/6/7 消费 ✓
- `CodeBlock` 组件：Task 5 定义、Task 5/6 复用 ✓
- `setTab` 函数：在 Two Paths 卡片按钮中调用，与 Task 4 定义一致 ✓

**风险点（spec §10）已处理**：
- 汉字字体 fallback：用 `font-serif` 通用 → Task 1/7 都已用 ✓
- 35 个 tool 名补齐：Task 6 Step 1 直接列出完整 3+5+4+2+3+3+3+12=35 个 ✓
- 是否放样本预览：spec 决定不放，Task 1-7 全部未触及 `brain-landing-preview.html` ✓

---

## 风险与开放问题

- **Risk**：Noto Serif SC 字体可能没在客户端加载，汉字 icon 显示成默认 serif。在浏览器验证时如发现 fallback 不理想，可考虑在 `app/layout.tsx` 加 `<link>` 引入 Google Fonts。**当前 plan 不动 layout**，因为 spec 约束 "不动 layout"，如需引入字体由用户在 review 时决定。
- **Open**：35 个 tool 名是按 spec 列出的合理推断，实际 `src/mcp_server/tools/*.py` 中的命名可能略有不同。Task 6 完成后需用户对一下真实 tool 名，必要时回退微调。