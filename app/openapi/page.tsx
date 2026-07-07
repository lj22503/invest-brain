"use client";

import { useState } from "react";
import Link from "next/link";

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
        <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-3">SKILL MARKET</div>
        <h1 className="font-serif text-5xl md:text-6xl font-black mb-4 leading-tight tracking-wide">
          投资大脑 · Skill 市场
        </h1>
        <p className="text-ink-light text-lg max-w-2xl leading-relaxed">
          InvestBrain 提供的全部 Skills —— 复制 Prompt 给你的 AI，立即获得「镜子 + 纪律锚点」能力。
          所有 Skill 本地运行，数据不出你的电脑。
        </p>
      </section>

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