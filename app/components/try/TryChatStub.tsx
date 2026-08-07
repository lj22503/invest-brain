'use client';

import { useState } from 'react';

interface Msg {
  role: 'user' | 'demo';
  text: string;
}

const DEMO_REPLIES: Record<string, string> = {
  '巴菲特': '巴菲特说过："以合理价格买入一家伟大的公司，远胜于以伟大价格买入一家合理的公司。"（这是 demo 回复，不会真调大师模型）',
  '茅台': '茅台当前 PE 约 25 倍（demo 数据）。从大师视角看，需要判断这是否在合理区间。',
};

export function TryChatStub() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: 'demo', text: '你好，这只是**试聊 Demo**，不调真实 LLM，不存你的对话。请下载 InvestBrain 客户端体验完整功能。' },
  ]);
  const [input, setInput] = useState('');

  const send = () => {
    const t = input.trim();
    if (!t) return;
    const replyKey = Object.keys(DEMO_REPLIES).find(k => t.includes(k));
    const reply = replyKey ? DEMO_REPLIES[replyKey] : `[Stub] 你说的是 "${t}"。真实对话请下载桌面 App。`;
    setMessages(m => [...m, { role: 'user', text: t }, { role: 'demo', text: reply }]);
    setInput('');
  };

  return (
    <div className="max-w-2xl mx-auto py-12 px-6">
      <div className="mb-4 p-3 bg-paper-warm border border-vermillion/20 rounded text-sm text-ink-light font-serif">
        ⚠ Demo 模式：不调真实 LLM，所有回复为占位字符串。
      </div>

      <div className="bg-white border border-border rounded-lg p-4 h-96 overflow-y-auto mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`mb-3 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-md rounded px-3 py-2 ${m.role === 'user' ? 'bg-vermillion/10 border border-vermillion/20' : 'bg-paper-warm'}`}>
              <p className="text-xs text-ink-faint mb-1">{m.role === 'user' ? '你' : 'Demo'}</p>
              <p className="whitespace-pre-wrap">{m.text}</p>
            </div>
          </div>
        ))}
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
          placeholder="试着问点什么，比如 巴菲特 / 茅台"
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
    </div>
  );
}