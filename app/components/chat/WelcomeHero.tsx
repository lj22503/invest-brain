'use client';

import Link from 'next/link';
import { useLLMKey } from '@/lib/llm-key-store';

const SCENARIOS: { title: string; desc: string; ask: string }[] = [
  {
    title: '审视我的持仓',
    desc: '让 AI 帮你复盘最近的操作',
    ask: '我刚买了贵州茅台，帮我审视一下这笔操作',
  },
  {
    title: '查估值',
    desc: '问一家公司现在贵不贵',
    ask: '贵州茅台现在的估值贵不贵？',
  },
  {
    title: '行为审计',
    desc: '识别追高、情绪化交易等坏习惯',
    ask: '我最近有没有追高或者情绪化交易？',
  },
];

export function WelcomeHero({ onSend }: { onSend: (text: string) => void }) {
  const hasKey = useLLMKey(s => !!s.provider && !!s.apiKey);

  return (
    <div className="flex-1 overflow-y-auto flex items-center justify-center p-8">
      <div className="max-w-xl w-full space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold text-gray-800">欢迎使用 InvestBrain</h1>
          <p className="text-sm text-gray-500 leading-relaxed">
            你的投资第二大脑：结合你的持仓、决策记录与大师投资框架，
            帮你做行为审计、估值判断与决策复盘。
          </p>
        </div>

        {!hasKey && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-amber-800">尚未配置 LLM Key</p>
              <p className="text-xs text-amber-700 mt-1">
                配置后即可开始真实对话；不配置也能自由浏览知识包与试聊 Demo。
              </p>
            </div>
            <Link
              href="/settings"
              className="shrink-0 bg-amber-600 text-white text-sm rounded px-4 py-2 hover:bg-amber-700 transition-colors"
            >
              去设置
            </Link>
          </div>
        )}

        <div>
          <p className="text-sm text-gray-500 mb-3">试试这些场景：</p>
          <div className="grid gap-3">
            {SCENARIOS.map(sc => (
              <button
                key={sc.title}
                onClick={() => onSend(sc.ask)}
                className="text-left bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-400 hover:shadow-sm transition-all"
              >
                <p className="text-sm font-medium text-gray-800">{sc.title}</p>
                <p className="text-xs text-gray-400 mt-1">{sc.desc}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="text-center">
          <Link
            href="/try"
            className="text-sm text-gray-500 hover:text-gray-700 underline underline-offset-4"
          >
            想先无配置体验？去试聊 Demo
          </Link>
        </div>
      </div>
    </div>
  );
}
