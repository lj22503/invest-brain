'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useLLMKey } from '@/lib/llm-key-store';

export function LLMKeyWizard() {
  const router = useRouter();
  const setKey = useLLMKey(s => s.setKey);
  const [done, setDone] = useState(false);

  const onFinish = (provider: string, key: string) => {
    setKey(provider as any, key);
    setDone(true);
    setTimeout(() => router.push('/app'), 1200);
  };

  if (done) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-green-600 text-lg">✓ 已保存，进入对话</p>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <div className="bg-white rounded-lg shadow p-8 max-w-md w-full">
        <h1 className="text-2xl font-bold mb-2">欢迎使用 InvestBrain</h1>
        <p className="text-sm text-gray-600 mb-6">
          首次启动请设置 LLM Key。所有数据完全本地，不会被上传。
        </p>
        <LLMKeyFormInline onFinish={onFinish} />
      </div>
    </div>
  );
}

function LLMKeyFormInline({ onFinish }: { onFinish: (p: string, k: string) => void }) {
  const [provider, setProvider] = useState('deepseek');
  const [key, setKey] = useState('');

  return (
    <div className="space-y-3">
      <select
        value={provider}
        onChange={e => setProvider(e.target.value)}
        className="border rounded px-3 py-2 w-full"
      >
        <option value="deepseek">DeepSeek</option>
        <option value="anthropic">Anthropic</option>
        <option value="openai">OpenAI</option>
      </select>
      <input
        type="password"
        value={key}
        onChange={e => setKey(e.target.value)}
        placeholder="sk-..."
        className="border rounded px-3 py-2 w-full font-mono"
      />
      <button
        onClick={() => onFinish(provider, key)}
        disabled={!key.trim()}
        className="w-full bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600 disabled:opacity-50"
      >
        开始使用
      </button>
    </div>
  );
}
