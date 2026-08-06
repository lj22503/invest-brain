import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  use: {
    // Tauri WebView 不能用 Playwright 浏览器驱动直接访问，
    // 需要 tauri-driver；这是 plan 1 之后的配置占位。
    baseURL: 'tauri://localhost',
  },
});
