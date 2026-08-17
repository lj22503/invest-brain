'use client';

import { useEffect, useState } from 'react';
import { getContext, BrainContext } from '@/lib/api';

// 对话页顶部的「大脑状态条」：告诉用户本地记忆已加载了哪些内容，
// 让「它认识我」这件事一眼可见；每次对话后由页面刷新。
export function BrainContextBar({ refreshKey }: { refreshKey: number }) {
  const [ctx, setCtx] = useState<BrainContext | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let alive = true;
    getContext()
      .then(c => {
        if (alive) {
          setCtx(c);
          setOffline(false);
        }
      })
      .catch(() => {
        if (alive) setOffline(true);
      });
    return () => {
      alive = false;
    };
  }, [refreshKey]);

  if (offline) {
    return (
      <div className="px-4 py-1.5 text-xs text-gray-500 border-b border-border">
        本地记忆服务未连接，当前对话不会入档
      </div>
    );
  }
  if (!ctx) {
    return (
      <div className="px-4 py-1.5 text-xs text-gray-500 border-b border-border">
        大脑加载中…
      </div>
    );
  }
  if (!ctx.loaded) {
    return (
      <div className="px-4 py-1.5 text-xs text-gray-500 border-b border-border">
        本地暂无入档数据，聊几句就会开始沉淀
      </div>
    );
  }
  const mem = ctx.thoughts.length + ctx.decisions.length;
  return (
    <div className="px-4 py-1.5 text-xs text-gray-500 border-b border-border">
      大脑已加载：原则 {ctx.principles.length} · 画像 {ctx.patterns.length} · 记忆 {mem}
    </div>
  );
}
