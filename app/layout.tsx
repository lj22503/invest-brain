import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'InvestBrain — 投资第二大脑',
  description: '有经验投资者的纪律自主工具。锚定最重要的事，不被市场吹走。',
  keywords: ['投资', '纪律', '行为审计', '投资锚点', '大师思想库'],
  openGraph: {
    title: 'InvestBrain — 投资第二大脑',
    description: '有经验投资者的纪律自主工具',
    type: 'website',
    locale: 'zh_CN',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        <script defer src="https://cloud.umami.is/script.js" data-website-id="fa3ce74-eb17-412d-abd1-348e1228231c"></script>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Product',
              name: 'InvestBrain',
              description: '投资第二大脑，有经验投资者的纪律自主工具',
              brand: {
                '@type': 'Brand',
                name: 'mangoFolio',
              },
              url: 'https://brain.mangofolio.com',
              areaServed: 'CN',
              hasCatalog: {
                '@type': 'Service',
                name: '想法记录',
                description: 'AI 自动解析标的、价格、指标，生成结构化卡片',
              },
            }),
          }}
        />
      </head>
      <body className="bg-paper text-ink font-sans antialiased">
        {/* Plan 4：营销 nav 移到各页面（TopNav），不再放 root 避免污染 /app in-app UI */}
        <main>{children}</main>

        {/* Footer */}
        <footer className="px-16 py-12 border-t border-border flex justify-between items-center text-xs text-ink-faint">
          <div>Brain by <a href="https://mangofolio.com" className="hover:text-ink transition-colors">mangoFolio</a></div>
          <div className="flex gap-8">
            <a href="/openapi" className="hover:text-ink transition-colors">Skill 市场</a>
            <a href="/openapi/schema.json" className="hover:text-ink transition-colors">JSON Schema</a>
            <a href="https://github.com/lj22503/invest-brain" className="hover:text-ink transition-colors">GitHub</a>
          </div>
        </footer>
      </body>
    </html>
  )
}
