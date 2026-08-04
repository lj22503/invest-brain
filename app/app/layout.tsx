// 桌面 in-app UI 布局。
// 与营销首页 layout.tsx 区分：仅供 Tauri 加载使用。

import '../globals.css';
import { Sidebar } from '@/components/sidebar/Sidebar';
import { TauriProvider } from '@/components/providers/TauriProvider';

export const metadata = {
  title: 'InvestBrain',
  description: '你的投资第二大脑',
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <TauriProvider>
      <div className="flex h-screen overflow-hidden bg-white text-gray-900">
        <Sidebar />
        <main className="flex-1 flex flex-col">{children}</main>
      </div>
    </TauriProvider>
  );
}