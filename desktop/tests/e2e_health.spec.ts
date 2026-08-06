import { test, expect } from '@playwright/test';

/**
 * Plan 1 占位 e2e：实际跑通过 tauri-driver。
 * Plan 5 (CI/CD) 配置完整 Tauri 自动化。
 */
test('health_check returns ok (placeholder)', async ({ page }) => {
  // 真正驱动 Tauri WebView 由 Plan 5 配置
  // 此处跳过，标 pending
  test.skip();
  expect(true).toBe(true);
});
