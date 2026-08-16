'use client';

import Link from 'next/link';
import { SCENARIOS } from '@/lib/demo-data';

// 试聊引导页：不再是本地 mock 演示，而是引导页。
// 点击场景 → 带问题跳转工作台对话页，由真实链路（无 Key 走演示闭环，有 Key 走真实 LLM）作答。
export function TryGuide() {
  return (
    <div className="max-w-2xl mx-auto py-10 px-6">
      {/* 头部引导 */}
      <div className="text-center space-y-3 mb-8">
        <h1 className="text-2xl font-semibold text-ink">先试试，再上手</h1>
        <p className="text-sm text-ink-light leading-relaxed">
          这里是指南页，带你快速体验 InvestBrain 的典型场景。
          点击下方任意场景，会自动带着问题进入工作台对话。
        </p>
      </div>

      {/* 场景入口 */}
      <div className="grid grid-cols-2 gap-3 mb-8">
        {SCENARIOS.map(sc => (
          <Link
            key={sc.key}
            href={`/chat?ask=${encodeURIComponent(sc.ask)}`}
            className="text-left bg-white border border-border rounded-lg p-4 hover:border-vermillion/60 hover:shadow-sm transition-all"
          >
            <p className="text-sm font-medium text-ink">{sc.title}</p>
            <p className="text-xs text-ink-faint mt-1 font-serif">{sc.desc}</p>
          </Link>
        ))}
      </div>

      {/* 进入工作台 */}
      <div className="bg-paper-warm border border-vermillion/20 rounded-lg p-5 text-center space-y-3">
        <p className="text-sm text-ink-light font-serif">
          想直接开始？进入工作台，自由对话或按需体验档案、知识包。
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link
            href="/chat"
            className="bg-vermillion text-white text-sm rounded px-5 py-2.5 hover:bg-[#A8322A] transition-colors"
          >
            进入工作台
          </Link>
          <a
            href="https://brain.mangofolio.com"
            target="_blank"
            rel="noreferrer"
            className="border border-vermillion/40 text-vermillion text-sm rounded px-5 py-2.5 hover:bg-vermillion/5 transition-colors"
          >
            下载桌面客户端
          </a>
        </div>
      </div>

      {/* 模式说明 */}
      <p className="mt-8 text-center text-xs text-ink-faint font-serif">
        未配置 API Key 时，对话页会以预置演示数据回应，方便你完整体验闭环；配置后即为真实对话。
      </p>
    </div>
  );
}
