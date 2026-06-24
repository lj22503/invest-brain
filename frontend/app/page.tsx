export default function Home() {
  return (
    <main className="min-h-screen bg-paper text-ink">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-paper/90 backdrop-blur-sm border-b border-ink-faint/20">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="text-2xl font-serif font-bold">
            Brain<span className="text-vermillion">.</span>
          </div>
          <ul className="hidden md:flex items-center gap-8 text-ink-light">
            <li className="cursor-pointer hover:text-ink transition-colors">功能</li>
            <li className="cursor-pointer hover:text-ink transition-colors">投资锚</li>
            <li className="cursor-pointer hover:text-ink transition-colors">关于</li>
          </ul>
          <button className="px-5 py-2 bg-vermillion text-paper rounded-full text-sm font-medium hover:bg-vermillion/90 transition-colors">
            免费开始
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-6 text-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-paper-warm/50 to-transparent pointer-events-none" />
        <div className="relative max-w-4xl mx-auto">
          <div className="inline-block px-4 py-1 bg-paper-warm rounded-full text-sm text-ink-light mb-8">
            by mangoFolio
          </div>
          <h1 className="font-serif text-5xl md:text-6xl font-bold mb-6 leading-tight">
            锚定<span className="text-vermillion">最重要的事</span><br />不被市场吹走
          </h1>
          <p className="text-ink-light text-lg md:text-xl max-w-2xl mx-auto mb-10">
            市场每天都在变，茅台涨停、政策利好、央行放水——但这些都不是最重要的事。你的投资锚是什么？
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-4 bg-vermillion text-paper rounded-full text-lg font-medium hover:bg-vermillion/90 transition-colors">
              开始锚定
            </button>
            <button className="px-8 py-4 border border-ink text-ink rounded-full text-lg font-medium hover:bg-ink/5 transition-colors">
              了解投资锚 →
            </button>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-6 bg-paper-warm">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block px-3 py-1 bg-vermillion/10 text-vermillion rounded-full text-sm font-medium mb-6">
            问题
          </div>
          <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4">
            每天市场都在喊你
          </h2>
          <p className="text-ink-light text-lg mb-12 max-w-2xl mx-auto">
            涨停、利好、放水、恐慌、FOMO——信息像潮水一样涌来，但真正重要的是什么？
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-paper p-6 rounded-2xl text-left shadow-sm border border-ink-faint/10">
              <div className="text-xs text-ink-faint uppercase tracking-wider mb-2">消息推送</div>
              <p className="text-ink font-medium">&ldquo;茅台涨停了！快追！&rdquo;</p>
            </div>
            <div className="bg-paper p-6 rounded-2xl text-left shadow-sm border border-ink-faint/10">
              <div className="text-xs text-ink-faint uppercase tracking-wider mb-2">朋友圈</div>
              <p className="text-ink font-medium">&ldquo;新能源政策重大利好！&rdquo;</p>
            </div>
            <div className="bg-paper p-6 rounded-2xl text-left shadow-sm border border-ink-faint/10">
              <div className="text-xs text-ink-faint uppercase tracking-wider mb-2">财经头条</div>
              <p className="text-ink font-medium">&ldquo;央行放水，流动性拐点来了&rdquo;</p>
            </div>
            <div className="bg-paper p-6 rounded-2xl text-left shadow-sm border border-ink-faint/10">
              <div className="text-xs text-ink-faint uppercase tracking-wider mb-2">群聊</div>
              <p className="text-ink font-medium">&ldquo;听说明天要暴跌，先跑吗？&rdquo;</p>
            </div>
          </div>

          <div className="text-ink-light text-lg">
            但这些都不是最重要的事 ↓
          </div>
        </div>
      </section>

      {/* Anchor Section */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-block px-3 py-1 bg-vermillion/10 text-vermillion rounded-full text-sm font-medium mb-6">
              解决方案
            </div>
            <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4">
              投资锚 · 三件事
            </h2>
            <p className="text-ink-light text-lg max-w-xl mx-auto">
              锚定你的投资纪律，让规则替你决策，而非情绪。
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 bg-paper-warm rounded-2xl">
              <div className="text-5xl font-serif font-bold text-vermillion/30 mb-4">01</div>
              <h3 className="text-xl font-bold mb-3">记下来</h3>
              <p className="text-ink-light leading-relaxed">
                锚定你的计划。不是记大盘点位，而是记：「我觉得茅台可以买，理由是……」「我设置了这个提醒条件……」
              </p>
            </div>
            <div className="p-8 bg-paper-warm rounded-2xl">
              <div className="text-5xl font-serif font-bold text-vermillion/30 mb-4">02</div>
              <h3 className="text-xl font-bold mb-3">映照</h3>
              <p className="text-ink-light leading-relaxed">
                看见真实的自己。你说过「不追涨」，做到了吗？你说「长期持有」，每次跌了在想什么？
              </p>
            </div>
            <div className="p-8 bg-paper-warm rounded-2xl">
              <div className="text-5xl font-serif font-bold text-vermillion/30 mb-4">03</div>
              <h3 className="text-xl font-bold mb-3">提醒</h3>
              <p className="text-ink-light leading-relaxed">
                让纪律不被忘记。到了设定的价格才动，到了设定的条件才检查——不被每天的波动牵着走。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-paper-warm text-center">
        <div className="max-w-2xl mx-auto">
          <div className="w-16 h-px bg-ink-faint/30 mx-auto mb-12" />
          <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4">
            回到你的投资纪律<br />不忘，不慌，不飘
          </h2>
          <p className="text-ink-light text-lg mb-10">
            市场每天都在变，你的锚是什么？
          </p>
          <button className="px-12 py-4 bg-vermillion text-paper rounded-full text-lg font-medium hover:bg-vermillion/90 transition-colors">
            免费开始使用
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-ink-faint/20">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-ink-light text-sm">
          <div>Brain by mangoFolio</div>
          <div className="flex gap-6">
            <a href="https://brain.mangofolio.com" className="hover:text-ink transition-colors">brain.mangofolio.com</a>
            <a href="#" className="hover:text-ink transition-colors">隐私政策</a>
            <a href="#" className="hover:text-ink transition-colors">联系我们</a>
          </div>
        </div>
      </footer>
    </main>
  )
}
