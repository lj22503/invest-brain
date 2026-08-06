import '../globals.css';
import { Sidebar } from '@/components/sidebar/Sidebar';
import { TauriProvider } from '@/components/providers/TauriProvider';
import { OnboardingGuard } from '@/components/onboarding/OnboardingGuard';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <TauriProvider>
      <div className="flex h-screen overflow-hidden bg-white text-gray-900">
        <Sidebar />
        <OnboardingGuard>
          <main className="flex-1 flex flex-col">{children}</main>
        </OnboardingGuard>
      </div>
    </TauriProvider>
  );
}
