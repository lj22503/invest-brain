'use client';

import { useEffect } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { usePacks, ALL_PACKS } from '@/lib/packs-store';

const PACK_LABELS: Record<string, string> = {
  master_views: '大师观点（Master Views）',
  industry_concepts: '行业概念（Industry Concepts）',
};

const PACK_DESC: Record<string, string> = {
  master_views: '巴菲特、芒格、段永平等大师的核心理念与语录，用于"问大师"和决策参考。',
  industry_concepts: '行业与概念板块的基础知识图谱，用于理解行情异动背后的产业逻辑。',
};

export default function PacksPage() {
  const { local, remote, updates, checking, updating, check, update } = usePacks();

  useEffect(() => {
    check().catch(() => {
      /* error 在 store 里 */
    });
  }, [check]);

  const onUpdate = async (id: string) => {
    try {
      await update(id);
      toast.success(`已更新 ${id}，知识库将在重启后生效`);
      window.dispatchEvent(new CustomEvent('packs-updated'));
    } catch (e) {
      toast.error(`更新失败: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  return (
    <div className="p-8 max-w-3xl overflow-y-auto flex-1">
      <Toaster position="top-right" />

      <div className="flex justify-between items-center mb-2">
        <h1 className="text-2xl font-bold">知识包</h1>
        <button
          onClick={() => check().catch(() => {})}
          disabled={checking}
          className="bg-vermillion text-white rounded px-3 py-1 text-sm hover:bg-[#A8322A] disabled:opacity-50 transition-colors"
        >
          {checking ? '检查中...' : '立即检查更新'}
        </button>
      </div>
      <p className="text-sm text-ink-light mb-6">
        知识包是 InvestBrain 的离线知识底座，供"问投资 / 问大师 / 行为体检"等场景检索引用。
        保持最新版本可以提升回答质量；更新后重启 App 生效。
      </p>

      <table className="w-full text-sm">
        <thead className="text-left text-ink-light border-b border-border">
          <tr>
            <th className="py-2">名称</th>
            <th>用途</th>
            <th>本地版本</th>
            <th>远程版本</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ALL_PACKS.map((id) => {
            const upd = updates.find((u) => u.pack_id === id);
            return (
              <tr key={id} className="border-b border-border align-top">
                <td className="py-3 whitespace-nowrap">{PACK_LABELS[id] ?? id}</td>
                <td className="py-3 text-xs text-ink-light pr-4">{PACK_DESC[id] ?? ''}</td>
                <td className="py-3 text-ink-light font-mono">{local[id] ?? '?'}</td>
                <td className="py-3 text-ink-light font-mono">{remote[id] ?? '?'}</td>
                <td className="py-3">
                  {upd ? (
                    <button
                      onClick={() => onUpdate(id)}
                      disabled={updating === id}
                      className="text-vermillion hover:underline disabled:opacity-50 whitespace-nowrap"
                    >
                      {updating === id ? '更新中...' : `升级到 ${upd.to}`}
                    </button>
                  ) : (
                    <span className="text-ink-faint">最新</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <p className="mt-6 text-xs text-ink-faint">
        更新后请重启 App 让 Chroma 索引重建生效（Plan 3 MVP 接受重启生效）。
      </p>
    </div>
  );
}
