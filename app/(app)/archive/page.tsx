'use client';

import { useEffect, useState } from 'react';
import { getArchive, getMeta, ArchiveSection } from '@/lib/api';

function fmtTime(v?: string) {
  if (!v) return '—';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? v : d.toLocaleString('zh-CN', { hour12: false });
}

export default function ArchivePage() {
  const [data, setData] = useState<ArchiveSection | null>(null);
  const [meta, setMeta] = useState<{ version: string; data_dir: string } | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [a, m] = await Promise.all([getArchive(), getMeta()]);
        setData(a);
        setMeta(m);
      } catch (e) {
        setError(`无法连接本地数据服务：${e instanceof Error ? e.message : String(e)}`);
      }
    })();
  }, []);

  if (error) {
    return (
      <div className="p-8 overflow-y-auto flex-1">
        <h1 className="text-xl font-semibold mb-4">我的档案</h1>
        <p className="text-amber-700 bg-amber-50 border border-amber-200 rounded p-4 text-sm">
          {error}
          <br />请确认桌面端后端已启动（设置页可测试连接）。
        </p>
      </div>
    );
  }

  if (!data) {
    return <div className="p-8 overflow-y-auto flex-1 text-sm text-ink-light">正在读取本地档案…</div>;
  }

  const thoughts = data.sections.thoughts ?? [];
  const decisions = data.sections.decisions ?? [];
  const patterns = data.sections.behavior_patterns ?? [];
  const sessions = data.sections.dialogue_sessions ?? [];

  return (
    <div className="p-8 overflow-y-auto flex-1 space-y-8">
      <div>
        <h1 className="text-xl font-semibold">我的档案</h1>
        <p className="text-sm text-ink-light mt-1">
          你在本机留下的想法、决策与行为记录，全部存在本地，不上传云端。
        </p>
      </div>

      <div className="bg-paper-warm border border-border rounded p-4 text-sm space-y-1">
        <p className="font-medium text-ink">数据存放位置</p>
        <p className="text-ink-light break-all">数据目录：{data.data_dir}</p>
        <p className="text-ink-light break-all">数据库：{data.database}</p>
        <p className="text-ink-faint text-xs">Sidecar v{meta?.version ?? '?'} · 直接打开目录即可查看原始数据</p>
      </div>

      <section className="space-y-3">
        <div className="flex items-baseline justify-between">
          <h2 className="font-semibold">想法记录</h2>
          <span className="text-xs text-ink-faint">{data.counts.thoughts ?? 0} 条</span>
        </div>
        {thoughts.length === 0 ? (
          <p className="text-sm text-ink-faint">暂无记录。在对话中记录想法后会自动入档。</p>
        ) : (
          <ul className="space-y-2">
            {thoughts.map(t => (
              <li key={String(t.id)} className="border rounded p-3 text-sm bg-white">
                <p className="text-ink">{String(t.text)}</p>
                <p className="text-xs text-ink-faint mt-1">
                  {[t.ticker, t.price, t.indicator].filter(Boolean).join(' · ') || '—'}
                  <span className="ml-2">{fmtTime(String(t.created_at))}</span>
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-baseline justify-between">
          <h2 className="font-semibold">决策记录</h2>
          <span className="text-xs text-ink-faint">{data.counts.decisions ?? 0} 条</span>
        </div>
        {decisions.length === 0 ? (
          <p className="text-sm text-ink-faint">暂无记录。买卖决策会自动入档。</p>
        ) : (
          <ul className="space-y-2">
            {decisions.map(d => (
              <li key={String(d.id)} className="border border-border rounded p-3 text-sm bg-white">
                <p className="text-ink">
                  <span className="font-medium">{String(d.ticker)}</span>{' '}
                  <span className={String(d.action).toLowerCase().includes('卖') ? 'text-red-600' : 'text-green-700'}>
                    {String(d.action)}
                  </span>{' '}
                  {d.price ? `@ ${String(d.price)}` : ''}
                </p>
                {Boolean(d.reason) && <p className="text-ink-light mt-1">{String(d.reason)}</p>}
                <p className="text-xs text-ink-faint mt-1">{fmtTime(String(d.created_at))}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-baseline justify-between">
          <h2 className="font-semibold">行为体检</h2>
          <span className="text-xs text-ink-faint">{data.counts.behavior_patterns ?? 0} 条</span>
        </div>
        {patterns.length === 0 ? (
          <p className="text-sm text-ink-faint">暂无记录。行为体检会自动识别并留存。</p>
        ) : (
          <ul className="space-y-2">
            {patterns.map(p => (
              <li key={String(p.id)} className="border border-border rounded p-3 text-sm bg-white">
                <p className="text-ink">
                  <span className="font-medium">{String(p.pattern_type)}</span>
                  {p.severity ? <span className="ml-2 text-xs text-amber-600">严重度 {String(p.severity)}</span> : null}
                </p>
                {Boolean(p.trigger_content) && <p className="text-ink-light mt-1">{String(p.trigger_content)}</p>}
                <p className="text-xs text-ink-faint mt-1">
                  出现 {String(p.times_count ?? 1)} 次 · {fmtTime(String(p.happened_at ?? p.created_at))}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {sessions.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-baseline justify-between">
            <h2 className="font-semibold">最近会话</h2>
            <span className="text-xs text-ink-faint">{sessions.length} 条</span>
          </div>
          <ul className="space-y-2">
            {sessions.map(s => (
              <li key={String(s.id)} className="border border-border rounded p-3 text-sm bg-white">
                <p className="text-ink">{String(s.user_input)}</p>
                <p className="text-xs text-ink-faint mt-1">
                  {String(s.mode)} · {String(s.status)} · {fmtTime(String(s.created_at))}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
