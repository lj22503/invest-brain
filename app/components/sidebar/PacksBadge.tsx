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
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const tryRefresh = (attempt: number) => {
      callHealthCheck()
        .then(h => {
          if (!cancelled) {
            setHealth({ status: h.status, version: h.version });
            setError(null);
          }
        })
        .catch(e => {
          if (cancelled) return;
          // sidecar 拉起需要数秒，前 15 次每 500ms 重试，之后交给 packs-updated 事件刷新
          if (attempt < 15) {
            timer = setTimeout(() => tryRefresh(attempt + 1), 500);
          } else {
            setError(String(e));
          }
        });
    };

    tryRefresh(0);
    // 监听 packs 更新事件：packs 页 update 成功后通知侧栏刷新
    const onUpdated = () => tryRefresh(0);
    window.addEventListener('packs-updated', onUpdated);
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
      window.removeEventListener('packs-updated', onUpdated);
    };
  }, []);

  if (error) {
    return (
      <div className="text-xs text-red-500 px-2" title={error}>
        ⚠ sidecar 离线
      </div>
    );
  }
  if (!health) {
    return <div className="text-xs text-ink-faint px-2">⏳ sidecar 启动中</div>;
  }
  return (
    <div className="text-xs text-ink-light px-2">
      ⓘ 知识包 <span className="text-ink-faint">v{health.version}</span>
      <span className="ml-2 text-green-500">{health.status}</span>
    </div>
  );
}