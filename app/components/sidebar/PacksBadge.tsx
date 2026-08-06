'use client';

import { useEffect, useState } from 'react';
import { callHealthCheck } from '@/lib/tauri';

export function PacksBadge() {
  const [health, setHealth] = useState<{ status: string; version: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = () => {
    callHealthCheck()
      .then(h => setHealth({ status: h.status, version: h.version }))
      .catch(e => setError(String(e)));
  };

  useEffect(() => {
    refresh();
    // 监听 packs 更新事件：packs 页 update 成功后通知侧栏刷新
    const onUpdated = () => refresh();
    window.addEventListener('packs-updated', onUpdated);
    return () => window.removeEventListener('packs-updated', onUpdated);
  }, []);

  if (error) {
    return (
      <div className="text-xs text-red-500 px-2" title={error}>
        ⚠ sidecar 离线
      </div>
    );
  }
  if (!health) {
    return <div className="text-xs text-gray-400 px-2">⏳ sidecar 启动中</div>;
  }
  return (
    <div className="text-xs text-gray-500 px-2">
      ⓘ 知识包 <span className="text-gray-400">v{health.version}</span>
      <span className="ml-2 text-green-500">{health.status}</span>
    </div>
  );
}