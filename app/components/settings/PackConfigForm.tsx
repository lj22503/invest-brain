'use client';

import { useEffect, useState } from 'react';
import { invoke } from '@/lib/tauri';

const PACK_FIELDS = [
  { id: 'master_views', label: '大师观点（master_views）', placeholder: 'https://<blob-url>/master_views.json' },
  { id: 'industry_concepts', label: '行业概念（industry_concepts）', placeholder: 'https://<blob-url>/industry_concepts.json' },
] as const;

interface PackConfigResult {
  [packId: string]: {
    configured: boolean;
    url: string;
    env_url: string;
  };
}

export function PackConfigForm() {
  const [values, setValues] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await invoke<PackConfigResult>('get_pack_config');
        const next: Record<string, string> = {};
        for (const f of PACK_FIELDS) {
          const item = res[f.id];
          next[f.id] = item?.url || item?.env_url || '';
        }
        setValues(next);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const submit = async () => {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      await invoke('set_pack_config', {
        masterViews: values.master_views || null,
        industryConcepts: values.industry_concepts || null,
      });
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-lg space-y-4">
        <h2 className="text-lg font-semibold">知识包源配置</h2>
        <p className="text-sm text-gray-400">加载中...</p>
      </div>
    );
  }

  return (
    <div className="max-w-lg space-y-4">
      <h2 className="text-lg font-semibold">知识包源配置</h2>
      <p className="text-sm text-gray-500">
        配置服务包的 BLOB URL（master_views / industry_concepts），保存到本地配置文件；留空则回退到环境变量。
      </p>

      {PACK_FIELDS.map(f => (
        <div key={f.id}>
          <label className="block text-sm mb-1">{f.label}</label>
          <input
            type="url"
            value={values[f.id] ?? ''}
            onChange={e => {
              setValues(v => ({ ...v, [f.id]: e.target.value }));
              setSaved(false);
            }}
            placeholder={f.placeholder}
            className="border rounded px-3 py-2 w-full font-mono text-sm"
          />
        </div>
      ))}

      {error && <p className="text-sm text-red-500">保存失败：{error}</p>}
      {saved && <p className="text-sm text-green-600">已保存，可在知识包管理页检查更新。</p>}

      <button
        onClick={submit}
        disabled={saving}
        className="bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600 disabled:opacity-50"
      >
        {saving ? '保存中...' : '保存'}
      </button>
    </div>
  );
}
