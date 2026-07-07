import Link from "next/link";

// ===== Skill / Tool Catalog (machine-readable) =====
// Sourced from skill.yaml + src/mcp_server/tools/*.py

type Tool = {
  name: string;
  params: Record<string, unknown>;
  returns: string;
  example: string;
  note?: string;
};

type Skill = {
  name: string;
  cn: string;
  description: string;
  triggers: string[];
  tools: Tool[];
  highlights?: {
    framework: string;
    safeguards: string;
    archive: string;
  };
};

const SKILLS: Skill[] = [
  {
    name: "idea-recorder",
    cn: "想法记录",
    description: "解析用户一句话投资想法，识别标的/价格/指标，关联历史决策和大师思想，生成结构化想法卡片。",
    triggers: ["我觉得", "想看看", "考虑买入", "准备卖出", "关注", "茅台可以买"],
    tools: [
      {
        name: "record_thought",
        params: { text: "string — 用户原始想法文本" },
        returns: "{ card_id, parsed_entities: {ticker, price, indicator, master_alignment}, created_at }",
        example: 'record_thought(text="茅台跌到1400可以考虑买入")',
      },
      {
        name: "search_memories",
        params: { query: "string — 搜索关键词" },
        returns: "list of matching thought cards",
        example: 'search_memories(query="茅台")',
      },
      {
        name: "get_thought_cards",
        params: { ticker: "string — 股票名称或代码" },
        returns: "all thought cards for this ticker",
        example: 'get_thought_cards(ticker="贵州茅台")',
      },
    ],
  },
  {
    name: "knowledge-rag",
    cn: "投资问答",
    description: "基于 16 位大师思想库（巴菲特/芒格/段永平/霍华德·马克斯等）和投资理论，回答投资问题。",
    triggers: ["什么是", "如何看待", "如何分析", "护城河", "安全边际", "周期理论"],
    tools: [
      {
        name: "ask_investment",
        params: { question: "string — 投资问题" },
        returns: "{ answer, sources: [{id, name, type}], master_views }",
        example: 'ask_investment(question="什么是护城河？")',
      },
      {
        name: "get_master_view",
        params: { master: "string — 大师名", topic: "string — 话题" },
        returns: "{ master, master_id, topic, view, source, related_topics }",
        example: 'get_master_view(master="巴菲特", topic="护城河")',
      },
      {
        name: "search_knowledge",
        params: { query: "string — 关键词" },
        returns: "list of matching concepts/masters/relationships",
        example: 'search_knowledge(query="价值投资")',
      },
    ],
  },
  {
    name: "memory-keeper",
    cn: "记忆管理",
    description: "维护用户画像、历史投资决策、行为模式，支持语义检索和模式发现。",
    triggers: ["我的持仓", "我之前", "关于", "行为模式", "我的投资原则"],
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
  },
  {
    name: "reminder-scheduler",
    cn: "提醒调度",
    description: "管理价格提醒、时间提醒、条件提醒，支持条件触发和通知。",
    triggers: ["提醒我", "跌破", "涨到", "当PE分位", "每周检查", "每月总结"],
    tools: [
      {
        name: "set_reminder",
        params: {
          condition: "{ type: price|time|condition, ticker, target?, rule?, expression?, period? }",
        },
        returns: "{ status, reminder_id }",
        example: 'set_reminder(condition={"type":"price","ticker":"600519","target":1400,"rule":"below"})',
      },
      {
        name: "get_reminders",
        params: { status: "string — active|expired (default active)" },
        returns: "list of reminders",
        example: 'get_reminders(status="active")',
      },
      {
        name: "delete_reminder",
        params: { id: "string — reminder id" },
        returns: "{ status }",
        example: 'delete_reminder(id="r_xxxxx")',
      },
    ],
  },
  {
    name: "master-analyst",
    cn: "大师思想",
    description: "提供巴菲特、芒格、段永平、霍华德·马克斯等投资大师的思想分析和对照。",
    triggers: ["巴菲特怎么看", "芒格说", "段永平思想", "大师观点"],
    tools: [
      {
        name: "get_master_view",
        params: { master: "string", topic: "string" },
        returns: "{ master, view, source, related_topics }",
        example: 'get_master_view(master="芒格", topic="好生意")',
      },
    ],
  },
  {
    name: "learning-coaching",
    cn: "学习辅导",
    description: "投研教练陪跑。简单问题直接 10 步框架输出；复杂主题进入 Socratic 多轮对话，逐步建立用户自己的投资系统。每次辅导自动写入情景库。",
    triggers: [
      "为什么.*涨", "为什么.*跌", "为什么.*不一样",
      "对.*什么影响", "怎么看.*趋势", "我觉得.*",
      "宏观", "利率", "汇率", "黄金", "原油", "美联储", "央行",
    ],
    tools: [
      {
        name: "start_coaching",
        params: { user_input: "string — 投资主题或问题" },
        returns: "{ session_id, current_step, total_steps, question, options, focus, answer }",
        example: 'start_coaching(user_input="黄金为什么一直涨")',
        note: "Phase 2 已上线 Socratic 多轮；Phase 1 fallback 为直接 10 步。",
      },
      {
        name: "continue_coaching",
        params: {
          session_id: "string",
          user_input: "string — 用户选择（A/B/C/D 或自由文本）",
        },
        returns: "{ session_id, current_step, question, options, acknowledgement, feedback, answer }",
        example: 'continue_coaching(session_id="session_xxx", user_input="A")',
      },
      {
        name: "abandon_coaching",
        params: { session_id: "string" },
        returns: "{ session_id, scenario_id, status: abandoned }",
        example: 'abandon_coaching(session_id="session_xxx")',
      },
      {
        name: "switch_to_simple",
        params: { session_id: "string" },
        returns: "{ mode: simple, answer (full 10-step), scenario_id }",
        example: 'switch_to_simple(session_id="session_xxx")',
      },
      {
        name: "list_scenarios",
        params: { limit: "int (default 20)" },
        returns: "list of archived scenarios: { id, trigger_event, causal_chain, predicted_outcome, actual_outcome, lesson }",
        example: "list_scenarios(limit=10)",
      },
    ],
    highlights: {
      framework: "10 步标准：变量拆解 → 因果链 → 资产影响 → 历史情景 → 情景推演 → 市场逻辑 → 交易方案 → 反向校验 → 失效条件 → 3 句归档",
      safeguards: "A. 自动校验（来源引用） B. 用户把关（仅参考） D. 不确定时降级为普通RAG",
      archive: "每次辅导自动写入 scenarios 表（触发事件/因果链/教训），可关联想法卡片",
    },
  },
  {
    name: "pattern-detector",
    cn: "行为模式",
    description: "自动识别用户的重复投资行为偏差：追高、止损过早、割在最低点。",
    triggers: ["行为模式", "我最近是不是", "生成我的报告"],
    tools: [
      {
        name: "run_pattern_detection",
        params: {},
        returns: "{ status, patterns_detected, report }",
        example: "run_pattern_detection()",
      },
      {
        name: "get_pattern_report",
        params: { period: "string — weekly|monthly|quarterly" },
        returns: "{ period, summary, top_patterns, recommendations }",
        example: 'get_pattern_report(period="monthly")',
      },
    ],
  },
];

// ===== Endpoint metadata =====
const ENDPOINT_INFO = {
  base_url: "https://brain.mangofolio.com",
  protocol: "MCP (Model Context Protocol)",
  transport: "stdio (Claude Desktop, OpenClaw) or HTTP (custom clients)",
  auth: "DEEPSEEK_API_KEY (set by user locally; no server-side auth)",
  data_storage: "Local SQLite (data/memory/memory.db); no cloud upload",
  description:
    "InvestBrain 是一个面向个人投资者的 Skill/MCP 服务。不给投顾建议，而是「镜子 + 纪律锚点」。所有数据本地存储，可被 Claude Desktop、OpenClaw 等 AI Agent 调用。",
};

export default function OpenApiPage() {
  return (
    <main className="min-h-screen pt-[72px] pb-24 px-8 max-w-5xl mx-auto font-mono text-sm">
      {/* Header */}
      <div className="mb-12">
        <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-3">OPENAPI · SKILL</div>
        <h1 className="font-serif text-5xl font-black mb-4 leading-tight tracking-wide">
          InvestBrain Skill Catalog
        </h1>
        <p className="text-ink-light text-base leading-relaxed mb-6 font-sans">
          给 AI 看的技能说明。InvestBrain 通过 MCP 协议暴露以下 Skills，供 Claude Desktop、OpenClaw 等 Agent 调用。
        </p>
        <div className="bg-paper border border-border rounded-lg p-4 text-xs space-y-1">
          <div><span className="text-ink-faint">protocol:</span> {ENDPOINT_INFO.protocol}</div>
          <div><span className="text-ink-faint">transport:</span> {ENDPOINT_INFO.transport}</div>
          <div><span className="text-ink-faint">auth:</span> {ENDPOINT_INFO.auth}</div>
          <div><span className="text-ink-faint">data_storage:</span> {ENDPOINT_INFO.data_storage}</div>
        </div>
      </div>

      {/* Skills */}
      {SKILLS.map((skill) => (
        <section key={skill.name} className="mb-16 border-t border-border pt-8">
          <div className="flex items-baseline justify-between mb-2">
            <h2 className="font-serif text-3xl font-bold">
              {skill.cn}
              <span className="text-ink-faint text-base ml-3 font-mono">{skill.name}</span>
            </h2>
          </div>
          <p className="text-ink-light text-sm leading-relaxed mb-4 font-sans">{skill.description}</p>

          {/* Triggers */}
          <div className="mb-6">
            <div className="text-vermillion text-xs tracking-wide mb-2 font-medium">TRIGGERS</div>
            <div className="flex flex-wrap gap-2">
              {skill.triggers.map((t) => (
                <span key={t} className="bg-paper-warm text-ink-light text-xs px-2 py-1 rounded border border-border">
                  {t}
                </span>
              ))}
            </div>
          </div>

          {/* Highlights (coaching only) */}
          {skill.highlights && (
            <div className="mb-6 bg-vermillion/[0.03] border border-vermillion/20 rounded-lg p-4 space-y-2">
              <div className="text-vermillion text-xs tracking-wide font-medium">CORE</div>
              <div className="text-ink text-xs leading-relaxed font-sans">
                <strong>framework:</strong> {skill.highlights.framework}
              </div>
              <div className="text-ink text-xs leading-relaxed font-sans">
                <strong>safeguards:</strong> {skill.highlights.safeguards}
              </div>
              <div className="text-ink text-xs leading-relaxed font-sans">
                <strong>archive:</strong> {skill.highlights.archive}
              </div>
            </div>
          )}

          {/* Tools */}
          <div className="space-y-4">
            {skill.tools.map((tool) => (
              <div key={tool.name} className="bg-white border border-border rounded-lg overflow-hidden">
                <div className="bg-paper px-4 py-2 border-b border-border flex items-center justify-between">
                  <span className="font-mono font-bold text-ink">{tool.name}</span>
                  {tool.note && <span className="text-vermillion text-xs">{tool.note}</span>}
                </div>
                <div className="p-4 space-y-3 text-xs">
                  <div>
                    <div className="text-ink-faint text-[10px] tracking-wide mb-1">PARAMS</div>
                    <pre className="bg-paper-warm text-ink p-2 rounded overflow-x-auto whitespace-pre-wrap">{JSON.stringify(tool.params, null, 2)}</pre>
                  </div>
                  <div>
                    <div className="text-ink-faint text-[10px] tracking-wide mb-1">RETURNS</div>
                    <pre className="bg-paper-warm text-ink p-2 rounded overflow-x-auto whitespace-pre-wrap">{tool.returns}</pre>
                  </div>
                  <div>
                    <div className="text-ink-faint text-[10px] tracking-wide mb-1">EXAMPLE</div>
                    <pre className="bg-ink text-paper p-2 rounded overflow-x-auto whitespace-pre-wrap">{tool.example}</pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}

      {/* Raw JSON / Schema link */}
      <section className="border-t border-border pt-8 mt-8">
        <h2 className="font-serif text-2xl font-bold mb-4">机器可读 Schema</h2>
        <p className="text-ink-light text-sm mb-4 font-sans">
          完整 JSON schema（用于 Agent 自动加载）：
        </p>
        <div className="flex gap-4 text-sm">
          <Link
            href="/openapi/schema.json"
            className="bg-vermillion text-white px-6 py-3 rounded hover:bg-[#A8322A] transition-colors"
          >
            📄 下载 schema.json
          </Link>
          <Link
            href="/llms.txt"
            className="border border-border text-ink px-6 py-3 rounded hover:border-ink transition-colors"
          >
            llms.txt
          </Link>
        </div>
      </section>

      {/* Footer note */}
      <section className="border-t border-border pt-8 mt-12 text-xs text-ink-faint leading-relaxed font-sans">
        <p>
          <strong>调用方式：</strong> 用户在 Claude Desktop / OpenClaw 中加载本服务（通过 MCP 配置），
          Agent 检测到触发词后自动路由到对应 skill。Skill 内部调用 mcp_server/tools/ 下的对应工具。
        </p>
        <p className="mt-2">
          <strong>本地部署：</strong> 克隆仓库 → 配置 DEEPSEEK_API_KEY → 启动 MCP Server → 在 Claude Desktop 中配置 mcpServers。
        </p>
        <p className="mt-2">
          <strong>GitHub:</strong> <a href="https://github.com/lj22503/invest-brain" className="text-vermillion hover:underline">lj22503/invest-brain</a>
        </p>
      </section>
    </main>
  );
}