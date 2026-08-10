'use client';

import { useLLMKey } from '@/lib/llm-key-store';

// 首启引导策略：不再强制跳转 onboarding 填 Key。
// 未配置 Key 时由 ChatView 内的 WelcomeHero 展示友好引导（3 个场景入口 + 去设置按钮），
// 用户可自由浏览知识包 / 试聊 Demo，不会被流程卡住。
export function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const provider = useLLMKey(s => s.provider);
  const apiKey = useLLMKey(s => s.apiKey);

  void provider;
  void apiKey;

  return <>{children}</>;
}
