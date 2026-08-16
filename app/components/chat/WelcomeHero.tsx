'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { SCENARIOS } from '@/lib/demo-data';
import { isLLMConfigured } from '@/lib/llm-router';

// 三场景真实功能引导：语义对齐试聊页，让用户一上来就知道"能干嘛"
const GUIDE = [
  {
    title: '行为体检',
    desc: '识别追高、情绪化交易等坏习惯',
    ask: SCENARIOS[0].ask,
  },
  {
    title: '查估值',
    desc: '问一家公司现在贵不贵，值不值得买',
    ask: SCENARIOS[1].ask,
  },
  {
    title: '大师视角',
    desc: '巴菲特、芒格、段永平怎么看你的标的',
    ask: SCENARIOS[2].ask,
  },
];

export function WelcomeHero({ onSend }: { onSend: (text: string) => void }) {
  const [configured, setConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    let alive = true;
    isLLMConfigured().then(v => { if (alive) setConfigured(v); });
    return () => { alive = false; };
  }, []);
  const hasKey = configured === true;

  return (
    <div className="flex-1 overflow-y-auto flex items-center justify-center p-8">
      <div className="max-w-xl w-full space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold text-ink">欢迎使用 InvestBrain</h1>
          <p className="text-sm text-ink-light leading-relaxed">
            你的投资第二大脑：结合你的持仓、决策记录与大师投资框架，
            帮你做行为审计、估值判断与决策复盘。
          </p>
        </div>

        {!hasKey ? (
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <p className="text-sm font-medium text-emerald-800">当前为演示模式，功能立即可用</p>
            <p className="text-xs text-emerald-700 mt-1 leading-relaxed">
              你可以直接点击下面的场景体验真实闭环（基于你的档案数据），也可以自由输入问题。
              等你想开启真实 AI 对话时，再到设置页配置 Key。
            </p>
          </div>
        ) : (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-amber-800">已配置 LLM Key</p>
              <p className="text-xs text-amber-700 mt-1">
                真实对话已解锁：行情、知识包、行为体检等本地功能均可调用。
              </p>
            </div>
            <Link
              href="/settings"
              className="shrink-0 bg-amber-600 text-white text-sm rounded px-4 py-2 hover:bg-amber-700 transition-colors"
            >
              设置
            </Link>
          </div>
        )}

        <div>
          <p className="text-sm text-ink-light mb-3">试试这些场景：</p>
          <div className="grid gap-3">
            {GUIDE.map(sc => (
              <button
                key={sc.title}
                onClick={() => onSend(sc.ask)}
                className="text-left bg-white border border-border rounded-lg p-4 hover:border-vermillion/60 hover:shadow-sm transition-all"
              >
                <p className="text-sm font-medium text-ink">{sc.title}</p>
                <p className="text-xs text-ink-faint mt-1">{sc.desc}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="text-center space-x-4">
          <Link
            href="/try"
            className="text-sm text-ink-light hover:text-vermillion underline underline-offset-4"
          >
            想先无配置体验？去试聊 Demo
          </Link>
          <Link
            href="/archive"
            className="text-sm text-ink-light hover:text-vermillion underline underline-offset-4"
          >
            查看我的档案
          </Link>
        </div>
      </div>
    </div>
  );
}
