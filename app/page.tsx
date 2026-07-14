'use client';
import HeroDemo from './components/HeroDemo';

export default function Home() {
  return (
    <main className="min-h-screen">

      {/* ========== Hero ========== */}
      <section className="min-h-[90vh] flex items-center px-6 md:px-12 lg:px-20 py-12 md:py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(232,160,144,0.08)_0%,transparent_70%)] pointer-events-none" />
        <div className="absolute top-1/3 right-[35%] w-[300px] h-[400px] bg-[radial-gradient(ellipse_at_center,rgba(184,178,166,0.06)_0%,transparent_70%)] rotate-[-12deg] pointer-events-none" />

        <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-10 lg:gap-16">
          {/* Left: 文案 */}
          <div className="flex-1 text-center lg:text-left">
            <div className="text-ink-light text-xs tracking-wide mb-4 max-w-lg lg:max-w-none leading-relaxed">
              Brain 不是 App — 是给 AI 用的 <span className="text-vermillion font-medium">35 个投资纪律 Skill 库</span><br />
              通过 MCP 协议接入 Claude / Cursor / 任意 AI，立即获得「镜子 + 纪律锚点」能力
            </div>
            <div className="text-vermillion text-xs tracking-[0.2em] uppercase mb-8 font-medium">
              by mangoFolio
            </div>
            <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight tracking-wide">
              锚定<span className="relative inline-block">最重要的事
                <span className="absolute bottom-1 left-0 right-0 h-3 bg-vermillion/10 z-[-1]" />
              </span><br />不被市场吹走
            </h1>
            <p className="text-ink-light text-lg md:text-xl font-light mb-10 max-w-lg lg:max-w-none">
              不是投顾，不给建议。是一个让你「越用越聪明」的投资大脑 —— 通过 AI 帮你建立自己的投研纪律。
            </p>
            <div className="flex gap-4 justify-center lg:justify-start flex-wrap">
              <a href="/openapi" className="bg-vermillion text-white px-8 py-4 rounded text-base font-medium hover:bg-[#A8322A] transition-all hover:-translate-y-px hover:shadow-md">
                进入 Skill 市场
              </a>
              <a href="#coaching" className="border border-border text-ink px-8 py-4 rounded text-base hover:border-ink transition-colors">
                了解学习辅导
              </a>
            </div>
          </div>

          {/* Right: 自动演示手机 */}
          <div className="flex-shrink-0 hidden lg:block">
            <HeroDemo />
          </div>
        </div>
      </section>

      {/* ========== Problem ========== */}
      <section className="py-24 px-6 md:px-16 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">问题</div>
          <h2 className="font-serif text-4xl font-bold mb-4">每天市场都在喊你</h2>
          <p className="text-ink-light text-lg max-w-xl mx-auto">
            涨停、利好、放水、恐慌、FOMO——信息像潮水一样涌来，但真正重要的是什么？
          </p>
        </div>

        <div className="grid grid-cols-2 md:flex md:flex-wrap gap-6 mt-12">
          {[
            { source: '消息推送', quote: '"茅台涨停了！快追！"' },
            { source: '朋友圈', quote: '"新能源政策重大利好！"' },
            { source: '财经头条', quote: '"央行放水，流动性拐点来了"' },
            { source: '群聊', quote: '"听说明天要暴跌，先跑吗？"' },
          ].map((item) => (
            <div key={item.source} className="flex-1 min-w-[200px] bg-white border border-border rounded-lg p-6 relative shadow-sm">
              <div className="text-ink-faint text-xs tracking-[0.08em] mb-3">{item.source}</div>
              <p className="text-ink font-serif">{item.quote}</p>
            </div>
          ))}
        </div>

        <div className="text-center mt-10 text-ink-faint font-serif text-sm tracking-wide">
          但这些都不是最重要的事 ↓
        </div>
      </section>

      {/* ========== Solution: Investment Anchor ========== */}
      <div className="bg-white py-24 px-6 md:px-16">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">解决方案</div>
            <h2 className="font-serif text-4xl font-bold mb-4">投资锚 · 三件事</h2>
            <p className="text-ink-light text-lg max-w-xl mx-auto">
              锚定你的投资纪律，让规则替你决策，而非情绪。
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mt-12 text-center">
            {[
              { num: '01', title: '记下来', desc: '锚定你的计划。不是记大盘点位，而是记：「我觉得茅台可以买，理由是……」「我设置了这个提醒条件……」' },
              { num: '02', title: '映照', desc: '看见真实的自己。你说过「不追涨」，做到了吗？你说「长期持有」，每次跌了在想什么？' },
              { num: '03', title: '提醒', desc: '让纪律不被忘记。到了设定的价格才动，到了设定的条件才检查——不被每天的波动牵着走。' },
            ].map((item) => (
              <div key={item.num}>
                <div className="font-serif text-7xl font-black text-vermillion opacity-20 leading-none mb-2">{item.num}</div>
                <h3 className="font-serif text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-ink-light text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ========== Core Positioning ========== */}
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

      {/* ========== Features ========== */}
      <section id="features" className="py-24 px-6 md:px-16 bg-white scroll-mt-16">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">功能</div>
            <h2 className="font-serif text-4xl font-bold">五大核心 Skill</h2>
            <p className="text-ink-light text-base mt-3">
              每个 Skill 都可独立使用，复制 Prompt 给任何 AI 立即生效。
              <a href="/openapi" className="text-vermillion hover:underline ml-1">浏览全部 →</a>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
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
              <a
                key={f.eng}
                href="/openapi"
                className={`block ${f.highlight ? 'border-vermillion border-2 bg-vermillion/[0.02]' : 'bg-paper border border-border'} rounded-lg p-8 hover:shadow-md hover:-translate-y-1 hover:border-vermillion-light transition-all`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="font-serif text-4xl text-vermillion opacity-40 leading-none">{f.iconChar}</div>
                  {f.highlight && (
                    <span className="bg-vermillion text-white text-xs px-2 py-1 rounded font-medium">NEW</span>
                  )}
                </div>
                <h3 className="font-serif text-xl font-bold mb-1">{f.title}</h3>
                <div className="text-ink-faint text-xs font-mono tracking-wide mb-3">{f.eng}</div>
                <p className="text-ink-light text-sm leading-relaxed">{f.desc}</p>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* ========== Learning Coaching Showcase ========== */}
      <section id="coaching" className="py-24 px-6 md:px-16 bg-gradient-to-b from-paper to-white scroll-mt-16">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">学习辅导</div>
            <h2 className="font-serif text-4xl font-bold mb-4">投研教练陪跑，建立你自己的投资系统</h2>
            <p className="text-ink-light text-lg max-w-2xl mx-auto">
              不是给答案，是陪你想清楚。简单问题直接 10 步框架输出；复杂主题进入 Socratic 多轮对话，逐步暴露认知 gap。
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mt-12">
            <div>
              <h3 className="font-serif text-2xl font-bold mb-6">10 步标准框架</h3>
              <ol className="space-y-2 text-sm text-ink-light">
                {[
                  '变量拆解（按重要性排序）',
                  '因果链（带箭头）',
                  '资产影响（利率/汇率/股/商品）',
                  '历史相似情景',
                  '情景推演（变量背离）',
                  '市场隐含逻辑识别',
                  '可落地的交易方案',
                  '反向校验（漏洞在哪）',
                  '失效条件（何时必须离场）',
                  '3 句话归档',
                ].map((step, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="text-vermillion font-mono font-bold">{String(i + 1).padStart(2, '0')}</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>

            <div>
              <h3 className="font-serif text-2xl font-bold mb-6">Socratic 多轮对话</h3>
              <div className="space-y-3 text-sm">
                <div className="bg-white border border-border rounded-lg p-4">
                  <div className="text-ink-faint text-xs mb-1">步骤 1/10</div>
                  <div className="text-ink mb-3">黄金的核心驱动变量是什么？</div>
                  <div className="text-ink-light text-xs leading-relaxed">
                    A. 实际利率与美元<br/>
                    B. 中国黄金需求<br/>
                    C. 美联储降息预期
                  </div>
                </div>
                <div className="bg-paper-warm border border-vermillion/20 rounded-lg p-4">
                  <div className="text-vermillion text-xs mb-1">用户选 A → 继续追问</div>
                  <div className="text-ink">实际利率上行的传导路径是什么？</div>
                </div>
                <p className="text-ink-faint text-xs leading-relaxed pt-2">
                  不告诉答案，只引导思考。每次辅导自动写入情景库，下次类似事件可对比历史。
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <a href="/openapi" className="inline-block bg-vermillion text-white px-10 py-3 rounded text-base font-medium hover:bg-[#A8322A] transition-colors">
              查看学习辅导 Skill →
            </a>
          </div>
        </div>
      </section>

      {/* ========== About ========== */}
      <section id="about" className="py-24 px-6 md:px-16 scroll-mt-16">
        <div className="max-w-3xl mx-auto">

          {/* Problem Origin */}
          <div className="mb-16">
            <h2 className="font-serif text-3xl font-bold mb-6">我们发现了什么问题</h2>
            <div className="space-y-4 text-ink-light leading-loose">
              <p>投资者最常见的困境，不是选不出好股票，而是<strong className="text-ink">知道却做不到</strong>。</p>
              <p>制定好的投资计划，一看到涨停就想追；说好长期持有，一跌就开始慌。不是因为不懂，是因为<strong className="text-ink">没有纪律锚点</strong>。</p>
            </div>
          </div>

          {/* Product Principles */}
          <div className="mb-16">
            <h2 className="font-serif text-3xl font-bold mb-6">产品原则</h2>
            <div className="space-y-4">
              {[
                { title: '不做交易执行', desc: '只做决策辅助，不执行任何买卖操作' },
                { title: '不做收费投顾', desc: '不提供选股建议、买卖点位、组合配置' },
                { title: '数据本地存储', desc: 'SQLite 本地存储，不经服务器，不上传云端' },
              ].map((item) => (
                <div key={item.title} className="flex gap-4 items-start">
                  <div className="w-1 h-1 rounded-full bg-vermillion mt-2 flex-shrink-0" />
                  <div>
                    <span className="font-medium">{item.title}</span>
                    <span className="text-ink-light text-sm"> — {item.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Models + 16 Masters side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-serif font-bold text-lg mb-3">支持的 AI</h3>
              <div className="space-y-2 text-sm text-ink-light">
                <p><span className="text-ink font-medium">DeepSeek</span> — deepseek-chat / reasoner</p>
                <p><span className="text-ink font-medium">OpenAI</span> — GPT-4o / GPT-4o-mini</p>
                <p><span className="text-ink font-medium">Anthropic</span> — Claude Sonnet / Opus</p>
                <p className="text-ink-faint text-xs">支持自定义 OpenAI Compatible Provider</p>
              </div>
            </div>
            <div>
              <h3 className="font-serif font-bold text-lg mb-3">16 位投资大师</h3>
              <p className="text-ink-light text-sm leading-relaxed mb-3">
                巴菲特、芒格、段永平、霍华德·马克斯、彼得·林奇、索罗斯、达利欧……
              </p>
              <div className="flex flex-wrap gap-2">
                {['巴菲特', '芒格', '段永平', '霍华德·马克斯', '彼得·林奇'].map((n) => (
                  <span key={n} className="bg-paper-warm text-ink-faint text-xs px-2 py-1 rounded-full">{n}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== FAQ ========== */}
      <section id="faq" className="py-24 px-6 md:px-16 bg-white scroll-mt-16">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <div className="text-vermillion text-xs tracking-[0.24em] font-medium mb-4">FAQ</div>
            <h2 className="font-serif text-4xl font-bold">常见问题</h2>
          </div>

          <div className="space-y-10">
            {[
              {
                q: '如何使用？',
                a: '两种方式：\n1. 进入 Skill 市场，复制任意 Skill 的 Prompt 给你的 AI（Claude / ChatGPT / DeepSeek 等）即可立即使用。\n2. 通过 MCP 协议本地部署 InvestBrain，数据完全在你的电脑上运行。',
              },
              {
                q: '数据安全吗？',
                a: '完全本地存储。SQLite 数据库保存在本地，不上传任何云端服务器，不经我们访问。InvestBrain 不执行任何交易，不连接券商账户。',
              },
              {
                q: '学习辅导是什么？',
                a: '投研教练模式。简单问题（如「茅台怎么看」）直接生成 10 步标准分析；复杂主题（如「黄金为什么一直涨」）进入 Socratic 多轮对话，逐步引导你暴露认知盲点。每次辅导自动归档到你的专属情景库。',
              },
              {
                q: '想提需求或反馈，怎么联系？',
                a: 'GitHub: https://github.com/lj22503/invest-brain\n邮件: brain@mangofolio.com',
              },
            ].map((item) => (
              <div key={item.q}>
                <h3 className="font-medium mb-3">{item.q}</h3>
                <p className="text-ink-light text-sm leading-loose whitespace-pre-line">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== Trust Bar ========== */}
      <div className="py-16 px-6 md:px-16 text-center border-t border-b border-border">
        <div className="flex justify-center gap-12 md:gap-20 flex-wrap">
          {[
            { num: '5', label: '个核心 Skill' },
            { num: '16', label: '位投资大师' },
            { num: '多模型', label: 'AI 引擎' },
            { num: '本地', label: '数据存储' },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="font-serif text-5xl font-black text-ink leading-none">{stat.num}</div>
              <div className="text-ink-light text-sm mt-2 tracking-wide">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ========== CTA ========== */}
      <section id="cta" className="py-24 px-6 md:px-16 text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(196,58,49,0.04)_0%,transparent_70%)] pointer-events-none" />
        <div className="w-10 h-px bg-vermillion opacity-30 mx-auto mb-8" />
        <div className="relative z-10">
          <h2 className="font-serif text-5xl font-bold mb-4 leading-relaxed">
            回到你的投资纪律<br />不忘，不慌，不飘
          </h2>
          <p className="text-ink-light text-lg mb-10">市场每天都在变，你的锚是什么？</p>
          <div className="flex gap-4 justify-center flex-wrap">
            <a href="/openapi" className="inline-block bg-vermillion text-white px-10 py-4 rounded text-lg font-medium hover:bg-[#A8322A] transition-colors">
              查看安装方法
            </a>
            <a href="https://github.com/lj22503/invest-brain" className="inline-block border border-border text-ink px-10 py-4 rounded text-lg hover:border-ink transition-colors">
              GitHub 部署
            </a>
          </div>
          <p className="text-ink-faint text-xs mt-6">
            Skill 市场：复制 Prompt 给任意 AI 立即使用 ·  GitHub 部署：本地运行，数据完全在你电脑上
          </p>
        </div>
      </section>

    </main>
  )
}