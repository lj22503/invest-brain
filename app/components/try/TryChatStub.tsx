'use client';

import { useState } from 'react';

interface Msg {
  role: 'user' | 'demo';
  text: string;
}

// ===== Demo 铺底数据（与 data/memory/memory.db、data/graph/masters、data/demo/market_snapshot.json 一致）=====
const DEMO_USER = {
  name: '演示投资者',
  style: '稳健型',
  principles: [
    '稳健投资，控制仓位，不满仓不杠杆',
    '不懂不投，只买看得懂的公司（消费、银行）',
    '好公司要拿得住，不赚快钱',
    '股价波动是常态，跌到安全边际才分批买入',
  ],
  thoughts: [
    '茅台跌到1400可以考虑买入，安全边际足够了，分批建仓更稳健',
    '宁德时代这波涨太多了，追高风险大，等回调再说',
    '招商银行股息率不错，分红稳定，适合稳健配置',
    '今天看到新能源板块大涨，忍不住想追一点，但记得自己说过要保守',
    '茅台最近回调到1380，有点担心是不是逻辑变了，犹豫要不要加仓',
    '段永平说不懂不投，我对AI芯片确实看不懂，还是拿住消费和银行',
    '芒格说好生意要拿住，招行和茅台都是好生意，耐心持有',
    '今天宁德又创新高，后悔没早点买，但追进去又怕站岗',
  ],
  decisions: [
    { ticker: '宁德时代', action: '买入', price: 265, reason: '连续涨了两周没忍住，追高了', date: '07-21' },
    { ticker: '贵州茅台', action: '买入', price: 1420, reason: '跌破1400没敢买，涨回1420忍不住追进去了', date: '07-24' },
    { ticker: '宁德时代', action: '买入', price: 278, reason: '看大家都在买新能源，冲动追涨', date: '08-04' },
  ],
  patterns: [
    { type: '追高', count: 3, severity: '中', note: '最近 3 笔买入均在高点附近成交' },
    { type: '情绪化交易', count: 2, severity: '高', note: '触发词：忍不住 / 冲动 / 大家都在买' },
  ],
  masters: {
    buffett: '以合理价格买入伟大的公司，远胜于以伟大价格买入合理的公司。对新能源赛道保持谨慎：资本开支大、盈利模式尚未稳定，更偏好现金流确定的消费与金融龙头。',
    munger: '好生意要拿得住，买之前多想想，买之后少动动。新能源长期是好赛道，但竞争激烈、技术迭代快，应聚焦有成本优势与差异化壁垒的龙头。',
    duanyongping: '不懂不投，看得懂才拿得住。坦言看不懂新能源的技术路线与行业格局，选择回避，坚持只投能力圈内的消费与互联网龙头。',
  },
  snapshot: {
    asOf: '2026-08-07',
    total: 500000,
    position: '65%',
    holdings: [
      { name: '贵州茅台', price: 1380, pe: 24.5, pePct: 18, note: 'PE 处于近 10 年 18% 分位，估值偏低' },
      { name: '宁德时代', price: 278, pe: 32, pePct: 78, note: 'PE 处于近 10 年 78% 分位，估值偏高' },
      { name: '招商银行', price: 32.8, pe: 6.2, pb: 0.9, note: 'PB 约 0.9 倍，股息率约 5.2%，估值低位' },
    ],
  },
};

// ===== 预置场景入口：点击即触发一段完整演示对话 =====
const SCENARIOS: { key: string; title: string; desc: string; ask: string }[] = [
  {
    key: 'chasing',
    title: '我最近又追高了吗',
    desc: '行为诊断 · 识别追高与情绪化交易',
    ask: '我最近是不是又在追高？帮我看看。',
  },
  {
    key: 'maotai',
    title: '茅台 1380 能买吗',
    desc: '估值快照 · 安全边际判断',
    ask: '茅台现在跌到 1380 了，能不能买？',
  },
  {
    key: 'ningde',
    title: '宁德还能追吗',
    desc: '大师视角 · 新能源观点',
    ask: '宁德时代又涨了，我还想追一点，你怎么看？',
  },
  {
    key: 'portrait',
    title: '我的投资画像',
    desc: '记忆画像 · 想法 / 决策 / 原则',
    ask: '帮我总结一下我的投资画像。',
  },
];

function renderScenario(key: string): string[] {
  switch (key) {
    case 'chasing':
      return [
        '我查了你的近期决策记录，结果不太妙：**最近 3 笔买入全部发生在阶段高点**。',
        '📋 决策回放\n• 07-21 宁德时代 @265 —— "连续涨了两周没忍住，追高了"\n• 07-24 贵州茅台 @1420 —— "跌破1400没敢买，涨回1420忍不住追进去了"\n• 08-04 宁德时代 @278 —— "看大家都在买新能源，冲动追涨"',
        '🧠 行为诊断：\n🔴 **追高** ×3（中风险）—— 总是在连涨后买入\n🔴 **情绪化交易** ×2（高风险）—— 触发词：忍不住 / 冲动 / 大家都在买',
        '💡 和你的原则对照：你说过"跌到安全边际才分批买入"，但 3 笔买入都发生在涨势中。建议下次下单前先打开这张检查单：\n□ 这是计划内买入还是临时起意？\n□ 现在比 30 天前便宜吗？\n□ 如果明天跌 10%，我能拿住吗？',
      ];
    case 'maotai':
      return [
        '先看估值快照（demo 数据，截至 2026-08-07）：\n**贵州茅台** 现价 1380，PE 24.5，处于近 10 年 **18% 分位**——估值处于历史偏低区间。',
        '📖 大师怎么说：\n巴菲特："以合理价格买入伟大的公司，远胜于以伟大价格买入合理的公司。"\n按这个框架，茅台品牌壁垒强、现金流稳定，当前估值不算贵。',
        '🧠 但提醒你：你 07-24 刚在 1420 追过一次。上次"跌破1400没敢买，涨回去才追"，这次同样在 1380 附近——小心同样的锚定心理，别把"跌了"当"便宜了"。',
        '💡 建议：如果相信安全边际，按你的原则应该是**分批建仓**而非一把梭；设好每档加仓价，别临场改主意。',
      ];
    case 'ningde':
      return [
        '宁德时代现价 278，PE 32，处于近 10 年 **78% 分位**——估值偏高。你的持仓里它已经涨了不少。',
        '📖 大师们对新能源的观点：\n巴菲特：谨慎。资本开支大、盈利模式尚未稳定，更偏好现金流确定的消费与金融龙头。\n芒格：长期是好赛道，但竞争激烈、技术迭代快，应聚焦有成本优势与差异化壁垒的龙头。\n段永平：坦言看不懂新能源的技术路线与行业格局，选择回避，坚持只投能力圈。',
        '🧠 你的记录里已经有 **2 次**在宁德时代上追高的决策（07-21 @265、08-04 @278），且 08-04 那次被标记为高风险情绪化交易。',
        '💡 三位大师没有一位建议在 78% 估值分位追高。如果你真的看好，等回调到合理区间再按纪律分批，而不是在创新高时冲动入场。',
      ];
    case 'portrait':
      return [
        '这是你的投资画像（demo 铺底数据）：\n\n🎯 **风格：稳健型**\n📌 原则 ×4：\n• 稳健投资，控制仓位，不满仓不杠杆\n• 不懂不投，只买看得懂的公司\n• 好公司要拿得住，不赚快钱\n• 跌到安全边际才分批买入',
        '💭 近期想法 ×8（节选）：\n• "茅台跌到1400可以考虑买入，安全边际足够了"\n• "宁德时代这波涨太多了，追高风险大"\n• "今天看到新能源板块大涨，忍不住想追一点…"\n• "段永平说不懂不投，我对AI芯片确实看不懂"',
        '📋 决策 ×3：全部为买入，其中 **3 笔追高、2 笔情绪化交易**——你的"知"和"行"有差距。',
        '🧠 诊断：理念是稳健派，行为却频繁在高点冲动入场。这正是 InvestBrain 要帮你盯住的地方：**让纪律追上理念**。',
      ];
    default:
      return ['（demo 占位回复）'];
  }
}

export function TryChatStub() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: 'demo', text: '你好，这里是 **InvestBrain 试聊 Demo** 🧠\n\n我预置了一位演示投资者的完整记忆（8 条想法、3 笔决策、行为诊断、大师图谱、行情快照），点击下面的场景即可看到完整闭环。\n\n⚠️ 不调真实 LLM、不配 API Key、不存你的对话；体验完整功能请下载桌面客户端。' },
  ]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState(false);

  const runScenario = (key: string) => {
    const sc = SCENARIOS.find(s => s.key === key);
    if (!sc || pending) return;
    setPending(true);
    setMessages(m => [...m, { role: 'user', text: sc.ask }]);
    const replies = renderScenario(key);
    replies.forEach((r, i) => {
      setTimeout(() => {
        setMessages(m => [...m, { role: 'demo', text: r }]);
        if (i === replies.length - 1) setPending(false);
      }, 500 + i * 650);
    });
  };

  const send = () => {
    const t = input.trim();
    if (!t || pending) return;
    const hit = SCENARIOS.find(s => t.includes(s.title.slice(0, 4)) || t.includes(s.ask.slice(0, 6)));
    const key = hit ? hit.key : 'portrait';
    runScenario(key);
    setInput('');
  };

  return (
    <div className="h-[calc(100vh-72px)] max-w-2xl mx-auto flex flex-col py-6 px-6">
      {/* 场景入口 */}
      <div className="shrink-0 mb-4">
        <p className="text-sm text-ink-light font-serif mb-2">点击场景，体验完整闭环：</p>
        <div className="grid grid-cols-2 gap-3">
          {SCENARIOS.map(sc => (
            <button
              key={sc.key}
              onClick={() => runScenario(sc.key)}
              disabled={pending}
              className="text-left bg-white border border-border rounded-lg p-3 hover:border-vermillion/60 hover:shadow-sm transition-all disabled:opacity-50"
            >
              <p className="text-sm font-medium text-ink">{sc.title}</p>
              <p className="text-xs text-ink-faint mt-1 font-serif">{sc.desc}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="shrink-0 mb-4 p-3 bg-paper-warm border border-vermillion/20 rounded text-sm text-ink-light font-serif">
        ⚠ Demo 模式：不调真实 LLM、无需 API Key，所有回复来自预置演示数据。
      </div>

      <div className="flex-1 min-h-0 bg-white border border-border rounded-lg p-4 overflow-y-auto mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`mb-3 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-md rounded px-3 py-2 whitespace-pre-wrap ${m.role === 'user' ? 'bg-vermillion/10 border border-vermillion/20' : 'bg-paper-warm'}`}>
              <p className="text-xs text-ink-faint mb-1">{m.role === 'user' ? '你' : 'Demo'}</p>
              <p className="text-sm leading-relaxed">{m.text}</p>
            </div>
          </div>
        ))}
        {pending && (
          <div className="flex items-center gap-2 text-xs text-ink-faint pl-1">
            <span className="w-3 h-3 border-2 border-vermillion/40 border-t-vermillion rounded-full animate-spin" />
            Demo 正在检索你的记忆…
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          placeholder="或直接输入：我最近是不是又在追高？"
          className="flex-1 border border-border rounded px-3 py-2 resize-none focus:outline-none focus:border-vermillion transition-colors"
          rows={2}
        />
        <button
          onClick={send}
          className="bg-vermillion text-white rounded px-4 py-2 hover:bg-[#A8322A] transition-colors"
        >
          ⏎ 发送
        </button>
      </div>

      {/* 底部引导下载客户端 */}
      <div className="shrink-0 mt-4 p-4 bg-white border border-border rounded-lg flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-ink">想要完整版？</p>
          <p className="text-xs text-ink-faint mt-1 font-serif">真实对话 · 你的专属记忆 · 行为审计与大师图谱，都在桌面客户端里。</p>
        </div>
        <a
          href="https://brain.mangofolio.com"
          target="_blank"
          rel="noreferrer"
          className="shrink-0 bg-vermillion text-white text-sm rounded px-4 py-2 hover:bg-[#A8322A] transition-colors"
        >
          下载客户端
        </a>
      </div>
    </div>
  );
}
