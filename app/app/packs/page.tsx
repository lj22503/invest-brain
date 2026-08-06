'use client';

import { useEffect } from 'react';
import { usePacks, ALL_PACKS } from '@/lib/packs-store';

const PACK_LABELS: Record<string, string> = {
  master_views: '大师观点（Master Views）',
  industry_concepts: '行业概念（Industry Concepts）',
};

export default function PacksPage() {
  const { local, remote, updates, checking, updating, error, check, update } = usePacks();

  useEffect(() => {
    check().catch(() => {
      /* error 在 store 里 */
    });
  }, [check]);

  return (
    <div className="p-8 max-w-3xl overflow-y-auto flex-1">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">知识包管理</h1>
        <button
          onClick={() => check().catch(() => {})}
          disabled={checking}
          className="bg-blue-500 text-white rounded px-3 py-1 text-sm hover:bg-blue-600 disabled:opacity-50"
        >
          {checking ? '检查中...' : '立即检查更新'}
        </button>
      </div>

      {error && (
        <div className="mb-4 text-sm text-red-600 bg-red-50 rounded p-2">{error}</div>
      )}

      <table className="w-full text-sm">
        <thead className="text-left text-gray-600 border-b">
          <tr>
            <th className="py-2">名称</th>
            <th>本地版本</th>
            <th>远程版本</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {ALL_PACKS.map((id) => {
            const upd = updates.find((u) => u.pack_id === id);
            return (
              <tr key={id} className="border-b">
                <td className="py-3">{PACK_LABELS[id] ?? id}</td>
                <td className="text-gray-500 font-mono">{local[id] ?? '?'}</td>
                <td className="text-gray-500 font-mono">{remote[id] ?? '?'}</td>
                <td>
                  {upd ? (
                    <button
                      onClick={() => update(id).catch(() => {})}
                      disabled={updating === id}
                      className="text-blue-500 hover:underline disabled:opacity-50"
                    >
                      {updating === id ? '更新中...' : `升级到 ${upd.to}`}
                    </button>
                  ) : (
                    <span className="text-gray-300">最新</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}