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
      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
        ⚠ Demo 模式：不调真实 LLM，所有回复为占位字符串。
      </div>

      <div className="bg-white rounded-lg shadow p-4 h-96 overflow-y-auto mb-4 border">
        {messages.map((m, i) => (
          <div key={i} className={`mb-3 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-md rounded px-3 py-2 ${m.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'}`}>
              <p className="text-xs text-gray-500 mb-1">{m.role === 'user' ? '你' : 'Demo'}</p>
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
          className="flex-1 border rounded px-3 py-2 resize-none"
          rows={2}
        />
        <button onClick={send} className="bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600">
          ⏎ 发送
        </button>
      </div>
    </div>
  );
}