'use client'

import { useState } from 'react'
import { saveLLMConfig } from '@/lib/api'

const PROVIDERS = [
  { id: 'deepseek', name: 'DeepSeek', models: ['deepseek-chat', 'deepseek-reasoner'] },
  { id: 'openai', name: 'OpenAI', models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'] },
  { id: 'anthropic', name: 'Claude', models: ['claude-sonnet-4-20250514', 'claude-opus-4-20250514'] },
  { id: 'custom', name: '自定义', models: [] },
]

export default function SettingsPage() {
  const [provider, setProvider] = useState('deepseek')
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    await saveLLMConfig({ provider, api_key: apiKey, base_url: baseUrl })
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="min-h-screen bg-paper py-12 px-6">
      <div className="max-w-xl mx-auto">
        <h1 className="font-serif text-3xl font-bold mb-8">LLM 配置</h1>

        {/* Provider选择 */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">提供商</label>
          <div className="grid grid-cols-2 gap-3">
            {PROVIDERS.map(p => (
              <button
                key={p.id}
                onClick={() => setProvider(p.id)}
                className={`p-4 rounded-lg border text-left transition-colors ${
                  provider === p.id
                    ? 'border-ink bg-ink text-paper'
                    : 'border-ink-faint/20 hover:border-ink-light'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* API Key */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-4 py-3 border border-ink-faint/20 rounded-lg bg-paper focus:border-ink outline-none"
          />
        </div>

        {/* Base URL (自定义Provider) */}
        {provider === 'custom' && (
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Base URL</label>
            <input
              type="text"
              value={baseUrl}
              onChange={e => setBaseUrl(e.target.value)}
              placeholder="https://api.example.com/v1"
              className="w-full px-4 py-3 border border-ink-faint/20 rounded-lg bg-paper focus:border-ink outline-none"
            />
          </div>
        )}

        <button
          onClick={handleSave}
          className="w-full py-3 bg-ink text-paper rounded-lg font-medium hover:bg-ink-light transition-colors"
        >
          保存配置
        </button>

        {saved && (
          <p className="mt-4 text-green-600 text-center text-sm">配置已保存</p>
        )}
      </div>
    </div>
  )
}
