// 全局样式由 app/layout.tsx（root layout）统一导入，此处不再重复 import '../globals.css'
import { Sidebar } from '@/components/sidebar/Sidebar';
import { TauriProvider } from '@/components/providers/TauriProvider';
import { OnboardingGuard } from '@/components/onboarding/OnboardingGuard';
import Analytics from '@/components/providers/Analytics';
import { Analytics as VercelAnalytics } from '@vercel/analytics/next';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <TauriProvider>
      <Analytics />
      <VercelAnalytics />
      <div className="flex h-screen overflow-hidden bg-paper text-ink">
        <Sidebar />
        <OnboardingGuard>
          <main className="flex-1 flex flex-col">{children}</main>
        </OnboardingGuard>
      </div>
    </TauriProvider>
  );
}
