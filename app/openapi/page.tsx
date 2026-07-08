"use client";

import { useState } from "react";
import Link from "next/link";

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
// Sourced from skill.yaml + src/mcp_server/tools/*.py

type Tool = {
  name: string;
  params: Record<string, unknown>;
  returns: string;
  example: string;
  note?: string;
};

type Skill = {
  id: string;
  cn: string;
  eng: string;
  emoji: string;
  category: string;
  shortDesc: string;
  description: string;
  triggers: string[];
  tools: Tool[];
  prompt?: string;
  highlights?: {
    framework: string;
    safeguards: string;
    archive: string;
  };
};

const SKILLS: Skill[] = [
  {
    id: "idea-recorder",
    cn: "想法记录",
    eng: "idea-recorder",
    emoji: "📝",
    category: "记录",
    shortDesc: "一句话记录，自动解析标的、价格、指标",
    description:
      "用户输入一句投资想法，AI 自动解析出股票名称、价格、估值指标（如 PE/PB），关联历史决策和大师思想，生成结构化想法卡片，永久保存到本地。",
    triggers: ["我觉得", "想看看", "考虑买入", "准备卖出", "关注"],
    tools: [
      {
        name: "record_thought",
        params: { text: "用户原始想法文本" },
        returns: "{ card_id, parsed_entities: {ticker, price, indicator, master_alignment}, created_at }",
        example: 'record_thought(text="茅台跌到1400可以考虑买入")',
      },
      {
        name: "search_memories",
        params: { query: "搜索关键词" },
        returns: "list of matching thought cards",
        example: 'search_memories(query="茅台")',
      },
      {
        name: "get_thought_cards",
        params: { ticker: "股票名称或代码" },
        returns: "all thought cards for this ticker",
        example: 'get_thought_cards(ticker="贵州茅台")',
      },
    ],
    prompt: `请用 InvestBrain 的想法记录 skill 帮我记录投资想法：
1. 解析我说的股票名称、价格、指标
2. 关联历史上我对同一标的的想法
3. 检查是否符合某位大师的思想（如巴菲特护城河、段永平本分）
4. 生成结构化卡片保存`,
  },
  {
    id: "learning-coaching",
    cn: "学习辅导",
    eng: "learning-coaching",
    emoji: "🎓",
    category: "辅导",
    shortDesc: "投研教练陪跑，10步框架 + Socratic 多轮对话",
    description:
      "内置的投研教练。简单问题（如「茅台怎么看」）直接给 10 步框架输出；复杂主题（如「黄金为什么一直涨」）进入 Socratic 多轮对话，逐步引导用户暴露认知 gap。每次辅导自动写入情景库，下次类似事件可对比历史。强引导 + 零错误传播（A 来源引用 + B 用户把关 + D 不确定时降级）。",
    triggers: [
      "为什么涨/跌", "为什么.*不一样", "对.*什么影响",
      "怎么看.*趋势", "宏观", "利率", "汇率", "黄金", "原油", "美联储",
    ],
    tools: [
      {
        name: "start_coaching",
        params: { user_input: "投资主题或问题" },
        returns: "{ session_id, mode, current_step, total_steps:10, question, options, answer }",
        example: 'start_coaching(user_input="黄金为什么一直涨")',
        note: "简单问题直接 10 步输出，复杂主题进入 Socratic 多轮对话",
      },
      {
        name: "continue_coaching",
        params: { session_id: "string", user_input: "用户选择（A/B/C/D 或自由文本）" },
        returns: "{ session_id, current_step, question, options, acknowledgement, feedback }",
        example: 'continue_coaching(session_id="session_xxx", user_input="A")',
      },
      {
        name: "abandon_coaching",
        params: { session_id: "string" },
        returns: "{ status: abandoned, scenario_id }",
        example: 'abandon_coaching(session_id="session_xxx")',
      },
      {
        name: "switch_to_simple",
        params: { session_id: "string" },
        returns: "{ mode: simple, answer: full 10-step, scenario_id }",
        example: 'switch_to_simple(session_id="session_xxx")',
      },
      {
        name: "list_scenarios",
        params: { limit: "int (default 20)" },
        returns: "list of archived scenarios",
        example: "list_scenarios(limit=10)",
      },
    ],
    highlights: {
      framework:
        "10 步：变量拆解 → 因果链 → 资产影响 → 历史情景 → 情景推演 → 市场逻辑 → 交易方案 → 反向校验 → 失效条件 → 3句归档",
      safeguards: "A 自动校验（来源引用）+ B 用户把关（不构成投资建议）+ D 不确定时降级为普通 RAG",
      archive: "每次辅导自动写入 scenarios 表（触发事件/因果链/教训），可关联想法卡片",
    },
    prompt: `请用 InvestBrain 的学习辅导 skill 帮我分析投资主题：
- 简单问题：直接走 10 步标准框架（变量拆解→因果链→交易方案→失效条件）
- 复杂主题：进入 Socratic 多轮对话，每次只问一个问题 + 2-4 个选项（A/B/C/D）
- 每次结束后自动归档到我的情景库
- 必须附来源、必须提示「不构成投资建议」`,
  },
  {
    id: "knowledge-rag",
    cn: "投资问答",
    eng: "knowledge-rag",
    emoji: "📚",
    category: "检索",
    shortDesc: "16 位大师思想库，RAG 即时检索",
    description:
      "基于 16 位投资大师（巴菲特、芒格、段永平、霍华德·马克斯、彼得·林奇等）的思想库和投资理论，回答投资问题，附带来源引用。",
    triggers: ["什么是", "如何看待", "如何分析", "护城河", "安全边际", "周期理论"],
    tools: [
      {
        name: "ask_investment",
        params: { question: "投资问题" },
        returns: "{ answer, sources: [{id, name, type}], master_views }",
        example: 'ask_investment(question="什么是护城河？")',
      },
      {
        name: "get_master_view",
        params: { master: "大师名", topic: "话题" },
        returns: "{ master, view, source, related_topics }",
        example: 'get_master_view(master="巴菲特", topic="护城河")',
      },
      {
        name: "search_knowledge",
        params: { query: "关键词" },
        returns: "list of matching concepts/masters/relationships",
        example: 'search_knowledge(query="价值投资")',
      },
    ],
    prompt: `请用 InvestBrain 的大师思想库 skill 回答我的投资问题：
- 检索 16 位大师的相关思想（巴菲特/芒格/段永平/霍华德·马克斯等）
- 综合多个观点给洞察
- 必须标注来源
- 如有需要可附加 1-2 个追问问题引导我深入`,
  },
  {
    id: "master-analyst",
    cn: "大师视角",
    eng: "master-analyst",
    emoji: "🧙",
    category: "检索",
    shortDesc: "用某位大师的视角分析标的",
    description:
      "把用户的投资问题交给特定大师（如「巴菲特怎么看茅台」），从该大师的思想体系出发给出观点。",
    triggers: ["巴菲特怎么看", "芒格说", "段永平思想", "大师观点"],
    tools: [
      {
        name: "get_master_view",
        params: { master: "string", topic: "string" },
        returns: "{ master, view, source, related_topics }",
        example: 'get_master_view(master="芒格", topic="好生意")',
      },
    ],
    prompt: `请用 InvestBrain 的大师视角 skill 帮我分析：
- 选择某位大师（巴菲特/芒格/段永平/霍华德·马克斯等）
- 从该大师的思想体系出发分析我说的标的或话题
- 必须引用该大师的原始语录或著作`,
  },
  {
    id: "reminder-scheduler",
    cn: "条件提醒",
    eng: "reminder-scheduler",
    emoji: "🔔",
    category: "提醒",
    shortDesc: "价格到位才提醒，条件触发才检查",
    description:
      "管理价格提醒（跌破/涨到某价位）、时间提醒（每周/每月）、条件提醒（PE 分位等）。条件触发时通知用户，避免每天被情绪牵着走。",
    triggers: ["提醒我", "跌破", "涨到", "当PE分位", "每周检查", "每月总结"],
    tools: [
      {
        name: "set_reminder",
        params: { condition: "{ type, ticker, target?, rule?, expression?, period? }" },
        returns: "{ status, reminder_id }",
        example: 'set_reminder(condition={"type":"price","ticker":"600519","target":1400,"rule":"below"})',
      },
      {
        name: "get_reminders",
        params: { status: "active|expired" },
        returns: "list of reminders",
        example: 'get_reminders(status="active")',
      },
      {
        name: "delete_reminder",
        params: { id: "reminder id" },
        returns: "{ status }",
        example: 'delete_reminder(id="r_xxxxx")',
      },
    ],
    prompt: `请用 InvestBrain 的提醒 skill 帮我设置投资提醒：
- 价格触发：跌破/涨到某价位
- 时间触发：每周/月检查
- 条件触发：PE 分位、波动率等指标到阈值
- 支持飞书通知`,
  },
  {
    id: "memory-keeper",
    cn: "记忆管理",
    eng: "memory-keeper",
    emoji: "🧠",
    category: "记录",
    shortDesc: "持仓、决策、行为模式全存储",
    description:
      "维护用户画像、历史投资决策、行为模式。支持语义检索（「我上次关于茅台的想法」）和模式发现（「你最近3次买入都是在PE分位<15%时」）。",
    triggers: ["我的持仓", "我之前", "关于", "我的投资原则", "行为模式"],
    tools: [
      {
        name: "get_user_profile",
        params: {},
        returns: "{ user_profile, total_thoughts, total_decisions, total_patterns }",
        example: "get_user_profile()",
      },
      {
        name: "record_decision",
        params: { data: "{ ticker, action, price, reason }" },
        returns: "{ status, decision_id }",
        example: 'record_decision(data={"ticker":"600519","action":"buy","price":1400,"reason":"护城河深"})',
      },
      {
        name: "get_behavior_patterns",
        params: {},
        returns: "list of detected patterns",
        example: "get_behavior_patterns()",
      },
    ],
    prompt: `请用 InvestBrain 的记忆 skill 帮我管理投资历史：
- 查询我的持仓、之前的想法、决策
- 记录新的交易决策
- 发现我的重复行为模式（追高/止损过早/割肉等）`,
  },
  {
    id: "pattern-detector",
    cn: "行为模式",
    eng: "pattern-detector",
    emoji: "🪞",
    category: "分析",
    shortDesc: "自动识别追高/止损过早等行为偏差",
    description:
      "自动识别用户的重复投资行为偏差：追高、止损过早、割在最低点。生成周/月报告，给出针对性建议。",
    triggers: ["行为模式", "生成我的报告", "我最近是不是"],
    tools: [
      {
        name: "run_pattern_detection",
        params: {},
        returns: "{ status, patterns_detected, report }",
        example: "run_pattern_detection()",
      },
      {
        name: "get_pattern_report",
        params: { period: "weekly|monthly|quarterly" },
        returns: "{ period, summary, top_patterns, recommendations }",
        example: 'get_pattern_report(period="monthly")',
      },
    ],
    prompt: `请用 InvestBrain 的行为模式 skill 帮我做投资复盘：
- 扫描我的历史决策
- 识别重复偏差（追高/止损过早/割在最低点等）
- 生成周/月报告
- 给出针对性改进建议`,
  },
];

const CATEGORIES = ["全部", "记录", "辅导", "检索", "提醒", "分析"];

export default function OpenApiPage() {
  const [filter, setFilter] = useState("全部");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [tab, setTab] = useState<"human" | "agent">("human");

  const filtered = filter === "全部" ? SKILLS : SKILLS.filter((s) => s.category === filter);

  const copyPrompt = (skill: Skill) => {
    if (!skill.prompt) return;
    navigator.clipboard.writeText(skill.prompt);
    setCopiedId(skill.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <main className="min-h-screen pt-[72px] pb-24">
      {/* ===== Hero ===== */}
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

      {/* ===== Filter ===== */}
      <section className="px-8 max-w-6xl mx-auto mb-8">
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-all ${
                filter === cat
                  ? "bg-vermillion text-white"
                  : "bg-white border border-border text-ink-light hover:border-vermillion hover:text-ink"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </section>

      {/* ===== Skill Grid ===== */}
      <section className="px-8 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((skill) => (
            <div
              key={skill.id}
              className="bg-white border border-border rounded-xl p-6 hover:shadow-lg hover:-translate-y-1 hover:border-vermillion-light transition-all flex flex-col"
            >
              {/* Icon + title */}
              <div className="flex items-start justify-between mb-3">
                <div className="text-4xl">{skill.emoji}</div>
                <span className="text-ink-faint text-[10px] font-mono tracking-wide bg-paper-warm px-2 py-1 rounded">
                  {skill.category}
                </span>
              </div>

              <h3 className="font-serif text-2xl font-bold mb-1">{skill.cn}</h3>
              <div className="text-ink-faint text-xs font-mono tracking-wide mb-3">{skill.eng}</div>

              <p className="text-ink-light text-sm leading-relaxed mb-4 flex-1">
                {skill.shortDesc}
              </p>

              {/* Triggers preview */}
              <div className="mb-4">
                <div className="text-ink-faint text-[10px] tracking-wide mb-1.5">触发词</div>
                <div className="flex flex-wrap gap-1">
                  {skill.triggers.slice(0, 3).map((t) => (
                    <span key={t} className="bg-paper-warm text-ink-light text-[11px] px-2 py-0.5 rounded">
                      {t}
                    </span>
                  ))}
                  {skill.triggers.length > 3 && (
                    <span className="text-ink-faint text-[11px]">+{skill.triggers.length - 3}</span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-3 border-t border-border">
                {skill.prompt && (
                  <button
                    onClick={() => copyPrompt(skill)}
                    className="flex-1 bg-vermillion text-white text-xs px-3 py-2 rounded hover:bg-[#A8322A] transition-colors font-medium"
                  >
                    {copiedId === skill.id ? "✓ 已复制" : "📋 复制 Prompt"}
                  </button>
                )}
                <button
                  onClick={() => setExpandedId(expandedId === skill.id ? null : skill.id)}
                  className="border border-border text-ink-light text-xs px-3 py-2 rounded hover:border-vermillion hover:text-ink transition-colors"
                >
                  {expandedId === skill.id ? "收起" : "详情"}
                </button>
              </div>

              {/* Expanded details */}
              {expandedId === skill.id && (
                <div className="mt-4 pt-4 border-t border-border space-y-3 text-xs">
                  <p className="text-ink-light leading-relaxed">{skill.description}</p>

                  {skill.highlights && (
                    <div className="bg-vermillion/[0.04] border border-vermillion/20 rounded p-3 space-y-1.5">
                      <div className="text-vermillion text-[10px] tracking-wide font-medium">CORE</div>
                      <div><strong className="text-ink">框架:</strong> <span className="text-ink-light">{skill.highlights.framework}</span></div>
                      <div><strong className="text-ink">安全:</strong> <span className="text-ink-light">{skill.highlights.safeguards}</span></div>
                      <div><strong className="text-ink">归档:</strong> <span className="text-ink-light">{skill.highlights.archive}</span></div>
                    </div>
                  )}

                  <div>
                    <div className="text-ink-faint text-[10px] tracking-wide mb-1.5">TOOLS ({skill.tools.length})</div>
                    <div className="space-y-1">
                      {skill.tools.map((t) => (
                        <div key={t.name} className="bg-paper-warm px-2 py-1 rounded font-mono text-[11px] text-ink">
                          {t.name}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

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

      {/* ===== Footer ===== */}
      <section className="px-8 max-w-6xl mx-auto text-xs text-ink-faint leading-relaxed">
        <p>
          <strong className="text-ink-light">协议:</strong> MCP (Model Context Protocol) ·
          <strong className="text-ink-light ml-2">传输:</strong> stdio / HTTP ·
          <strong className="text-ink-light ml-2">存储:</strong> 本地 SQLite
        </p>
        <p className="mt-1">
          <strong className="text-ink-light">GitHub:</strong>{" "}
          <a href="https://github.com/lj22503/invest-brain" className="text-vermillion hover:underline">
            lj22503/invest-brain
          </a>
        </p>
      </section>
    </main>
  );
}