'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useLLMKey } from '@/lib/llm-key-store';

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const provider = useLLMKey(s => s.provider);
  const apiKey = useLLMKey(s => s.apiKey);

  useEffect(() => {
    if (!provider && !apiKey && pathname !== '/app/onboarding') {
      router.push('/app/onboarding');
    }
  }, [provider, apiKey, pathname, router]);

  return <>{children}</>;
}
