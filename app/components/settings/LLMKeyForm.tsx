'use client';

import { useEffect, useState } from 'react';
import { useLLMKey, Provider } from '@/lib/llm-key-store';
import { saveLLMConfig, getMeta, getLLMConfig, callLLMRemote } from '@/lib/api';

const PROVIDER_LIST: { id: Provider; label: string; hint: string; baseUrl?: string }[] = [
  { id: 'deepseek', label: 'DeepSeek', hint: 'sk-... (https://platform.deepseek.com)', baseUrl: 'https://api.deepseek.com/v1' },
  { id: 'anthropic', label: 'Anthropic', hint: 'sk-ant-... (https://console.anthropic.com)' },
  { id: 'openai', label: 'OpenAI', hint: 'sk-... (https://platform.openai.com)', baseUrl: 'https://api.openai.com/v1' },
];

export function LLMKeyForm() {
  const stored = useLLMKey();
  const [provider, setProvider] = useState<Provider>(stored.provider ?? 'deepseek');
  const [key, setKey] = useState('');
  const [status, setStatus] = useState<string>('');
  const [backend, setBackend] = useState<{ configured: boolean; path?: string; dataDir?: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [meta, cfg] = await Promise.all([getMeta(), getLLMConfig()]);
        setBackend({ configured: !!cfg.configured, path: (cfg as { path?: string }).path, dataDir: meta.data_dir });
      } catch {
        setBackend(null); // sidecar 不可达（如纯 Web 预览）
      }
    })();
  }, [status]);

  const submit = async () => {
    if (!key.trim()) return;
    setBusy(true);
    setStatus('');
    try {
      const providerInfo = PROVIDER_LIST.find(p => p.id === provider);
      const res = await saveLLMConfig({
        provider,
        api_key: key.trim(),
        ...(providerInfo?.baseUrl ? { base_url: providerInfo.baseUrl } : {}),
      });
      stored.setKey(provider, key.trim());
      setKey('');
      setStatus(`已保存并落盘：${res.path}（仅存本地，不上传云端）`);
    } catch (e) {
      setStatus(`保存失败：${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setBusy(false);
    }
  };

  const testConnection = async () => {
    setTesting(true);
    setStatus('');
    try {
      const res = await callLLMRemote([], 'ping');
      if (res.status === 'ok') setStatus('连接正常：真实模型已就绪。');
      else if (res.status === 'no_key') setStatus('尚未配置 Key：先保存 Key 再测试。');
      else setStatus(`连接失败：${res.message ?? '未知错误'}${res.detail ? ` ${res.detail}` : ''}`);
    } catch (e) {
      setStatus(`无法连接本地服务：${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="max-w-lg space-y-4">
      <h2 className="text-lg font-semibold">LLM 配置</h2>

      {backend?.configured ? (
        <p className="text-sm text-green-700">
          后端已启用：{stored.provider || 'DeepSeek'}（Key 已落盘本地，配置即生效）
        </p>
      ) : (
        <p className="text-sm text-amber-700">
          尚未配置 Key：当前对话为演示模式，配置后立即解锁真实模型。
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
        <p className="text-xs text-ink-faint mt-1">
          Key 仅写入本地数据目录（{backend?.dataDir ?? '启动后显示'}），不上传任何服务器。
        </p>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={submit}
          disabled={busy}
          className="bg-vermillion text-white rounded px-4 py-2 hover:bg-[#A8322A] disabled:opacity-50 transition-colors"
        >
          {busy ? '保存中…' : '保存并启用'}
        </button>
        <button
          onClick={testConnection}
          disabled={testing}
          className="border border-border rounded px-4 py-2 text-sm hover:bg-paper-warm disabled:opacity-50 transition-colors"
        >
          {testing ? '测试中…' : '测试连接'}
        </button>
        {stored.provider && (
          <button onClick={() => stored.clear()} className="ml-auto text-sm text-red-500 hover:underline">
            清除
          </button>
        )}
      </div>

      {status && <p className="text-sm text-ink-light break-all">{status}</p>}

      {backend?.path && (
        <p className="text-xs text-ink-faint">配置文件：{backend.path}</p>
      )}
    </div>
  );
}
