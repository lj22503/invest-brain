'use client';

import { useState } from 'react';
import { useLLMKey, Provider } from '@/lib/llm-key-store';

const PROVIDER_LIST: { id: Provider; label: string; hint: string }[] = [
  { id: 'deepseek', label: 'DeepSeek', hint: 'sk-... (https://platform.deepseek.com)' },
  { id: 'anthropic', label: 'Anthropic', hint: 'sk-ant-... (https://console.anthropic.com)' },
  { id: 'openai', label: 'OpenAI', hint: 'sk-... (https://platform.openai.com)' },
];

export function LLMKeyForm() {
  const stored = useLLMKey();
  const [provider, setProvider] = useState<Provider>(stored.provider ?? 'deepseek');
  const [key, setKey] = useState('');

  const submit = () => {
    if (!key.trim()) return;
    stored.setKey(provider, key.trim());
    setKey('');
    alert('LLM Key 已保存（仅存本地）');
  };

  return (
    <div className="max-w-lg space-y-4">
      <h2 className="text-lg font-semibold">LLM 配置</h2>

      {stored.provider && (
        <p className="text-sm text-gray-600">
          当前 Provider：<strong>{stored.provider}</strong>（key 已存本地，不上传云端）
        </p>
      )}

      <div>
        <label className="block text-sm mb-1">Provider</label>
        <select
          value={provider}
          onChange={e => setProvider(e.target.value as Provider)}
          className="border rounded px-3 py-2 w-full"
        >
          {PROVIDER_LIST.map(p => (
            <option key={p.id} value={p.id}>{p.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm mb-1">API Key</label>
        <input
          type="password"
          value={key}
          onChange={e => setKey(e.target.value)}
          placeholder={PROVIDER_LIST.find(p => p.id === provider)!.hint}
          className="border rounded px-3 py-2 w-full font-mono"
        />
        <p className="text-xs text-gray-400 mt-1">
          存本地浏览器/Zustand，不上传任何服务器。
        </p>
      </div>

      <button
        onClick={submit}
        className="bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600"
      >
        保存
      </button>

      {stored.provider && (
        <button
          onClick={() => stored.clear()}
          className="ml-2 text-sm text-red-500 hover:underline"
        >
          清除
        </button>
      )}
    </div>
  );
}
