// 桌面 in-app UI 布局。
// 与营销首页 layout.tsx 区分：仅供 Tauri 加载使用。

import '../globals.css';

export const metadata = {
  title: 'InvestBrain',
  description: '你的投资第二大脑',
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-white text-gray-900">
      {children}
    </div>
  );
}
