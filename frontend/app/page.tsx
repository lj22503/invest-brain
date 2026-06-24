export default function Home() {
  return (
    <main className="min-h-screen">
      <section className="hero text-center py-20 px-6">
        <h1 className="font-serif text-5xl font-bold mb-6">
          投资锚 · 三件事
        </h1>
        <p className="text-ink-light text-lg max-w-xl mx-auto">
          锚定你的投资纪律，让规则替你决策，而非情绪
        </p>
        <div className="mt-10 flex gap-4 justify-center">
          <a href="/chat" className="px-6 py-3 bg-ink text-paper rounded-full">
            开始使用
          </a>
          <a href="/settings" className="px-6 py-3 border border-ink rounded-full">
            配置LLM
          </a>
        </div>
      </section>
    </main>
  )
}
