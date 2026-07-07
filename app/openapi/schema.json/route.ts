// Raw JSON schema for agent consumption
// URL: /openapi/schema.json

const SCHEMA = {
  service: {
    name: "investbrain",
    version: "0.2.0",
    description:
      "面向个人投资者的 Skill/MCP 服务。不给投顾建议，而是「镜子 + 纪律锚点」。",
    homepage: "https://brain.mangofolio.com",
    protocol: "MCP",
    auth: "user-provided DEEPSEEK_API_KEY (local)",
    data_storage: "local SQLite",
  },
  skills: [
    {
      name: "idea-recorder",
      cn: "想法记录",
      triggers: ["我觉得", "想看看", "考虑买入", "准备卖出", "关注"],
      tools: [
        {
          name: "record_thought",
          params: { text: "string" },
          returns: { card_id: "string", parsed_entities: "object", created_at: "datetime" },
        },
        {
          name: "search_memories",
          params: { query: "string" },
          returns: { type: "array", items: "thought_card" },
        },
        {
          name: "get_thought_cards",
          params: { ticker: "string" },
          returns: { type: "array", items: "thought_card" },
        },
      ],
    },
    {
      name: "knowledge-rag",
      cn: "投资问答",
      triggers: ["什么是", "如何看待", "护城河", "安全边际"],
      tools: [
        {
          name: "ask_investment",
          params: { question: "string" },
          returns: { answer: "string", sources: "array", master_views: "array" },
        },
        {
          name: "get_master_view",
          params: { master: "string", topic: "string" },
          returns: { master: "string", view: "string", source: "string" },
        },
      ],
    },
    {
      name: "learning-coaching",
      cn: "学习辅导",
      version: "0.2.0",
      status: "Phase 2 (Socratic 多轮对话) 已上线",
      triggers: [
        "为什么.*涨", "为什么.*跌", "为什么.*不一样",
        "对.*什么影响", "怎么看.*趋势",
        "宏观", "利率", "汇率", "黄金", "原油", "美联储", "央行",
      ],
      framework: [
        "1. 变量拆解",
        "2. 因果链",
        "3. 资产影响",
        "4. 历史情景",
        "5. 情景推演",
        "6. 市场逻辑",
        "7. 交易方案",
        "8. 反向校验",
        "9. 失效条件",
        "10. 3句归档",
      ],
      safeguards: {
        A: "自动校验（来源引用）",
        B: "用户把关（仅参考，不构成投资建议）",
        D: "不确定时降级为普通RAG",
      },
      tools: [
        {
          name: "start_coaching",
          params: { user_input: "string" },
          returns: {
            session_id: "string",
            mode: "simple|complex",
            current_step: "int",
            total_steps: 10,
            question: "string (complex only)",
            options: "array (complex only)",
            answer: "string",
          },
        },
        {
          name: "continue_coaching",
          params: { session_id: "string", user_input: "string" },
          returns: {
            session_id: "string",
            current_step: "int",
            question: "string",
            options: "array",
            acknowledgement: "string",
            feedback: "string",
            answer: "string",
          },
        },
        {
          name: "abandon_coaching",
          params: { session_id: "string" },
          returns: { session_id: "string", status: "abandoned" },
        },
        {
          name: "switch_to_simple",
          params: { session_id: "string" },
          returns: { mode: "simple", answer: "string", scenario_id: "string" },
        },
        {
          name: "list_scenarios",
          params: { limit: "int (default 20)" },
          returns: { type: "array", items: "scenario" },
        },
      ],
    },
    {
      name: "reminder-scheduler",
      cn: "提醒调度",
      tools: [
        {
          name: "set_reminder",
          params: { condition: "object" },
          returns: { reminder_id: "string" },
        },
        { name: "get_reminders", params: { status: "string" }, returns: { type: "array" } },
        { name: "delete_reminder", params: { id: "string" }, returns: { status: "string" } },
      ],
    },
    {
      name: "memory-keeper",
      cn: "记忆管理",
      tools: [
        { name: "get_user_profile", params: {}, returns: { user_profile: "object" } },
        { name: "record_decision", params: { data: "object" }, returns: { decision_id: "string" } },
        { name: "get_behavior_patterns", params: {}, returns: { type: "array" } },
      ],
    },
    {
      name: "pattern-detector",
      cn: "行为模式",
      tools: [
        { name: "run_pattern_detection", params: {}, returns: { patterns: "array" } },
        { name: "get_pattern_report", params: { period: "string" }, returns: { report: "object" } },
      ],
    },
  ],
};

export async function GET() {
  return new Response(JSON.stringify(SCHEMA, null, 2), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
}