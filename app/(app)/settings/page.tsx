'use client';

import { useEffect, useState } from 'react';
import { LLMKeyForm } from '@/components/settings/LLMKeyForm';
import { PackConfigForm } from '@/components/settings/PackConfigForm';
import { getMeta } from '@/lib/api';

export default function SettingsPage() {
  const [dataDir, setDataDir] = useState<string>('');
  const [dataDirError, setDataDirError] = useState('');

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const MAX_ATTEMPTS = 5;

    async function load() {
      try {
        const m = await getMeta();
        if (cancelled) return;
        setDataDir(m.data_dir ?? '');
        setDataDirError('');
      } catch {
        attempts += 1;
        if (cancelled) return;
        if (attempts < MAX_ATTEMPTS) {
          // sidecar 可能晚于 UI 启动，延迟重试
          setTimeout(load, 1500);
        } else {
          setDataDirError('本地服务未连接，可到服务端确认后重进本页');
        }
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="p-8 overflow-y-auto flex-1 space-y-10 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">设置</h1>
        <p className="text-sm text-ink-light mt-1">
          配置大模型 Key 解锁真实对话；不配置也能用演示模式体验全部功能。
        </p>
      </div>

      <div className="bg-paper-warm border border-border rounded-lg p-4 space-y-1">
        <p className="text-sm font-medium text-ink">本地数据存哪里</p>
        <p className="text-xs text-ink-light leading-relaxed">
          你的档案、想法、决策记录与知识包都只存在本机，不上传任何服务器。
        </p>
        <p className="text-xs font-mono text-ink-light break-all">
          {dataDir || dataDirError || '正在读取…'}
        </p>
      </div>

      <LLMKeyForm />
      <PackConfigForm />
    </div>
  );
}
