import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'InvestBrain — 投资第二大脑',
  description: '有经验投资者的纪律自主工具',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}
