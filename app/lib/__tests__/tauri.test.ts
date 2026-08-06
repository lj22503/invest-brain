// app/lib/__tests__/tauri.test.ts
import { describe, it, expect } from 'vitest';
import { isTauri } from '../tauri';

describe('isTauri', () => {
  it('returns false in jsdom', () => {
    expect(isTauri()).toBe(false);
  });

  it('returns true when __TAURI__ present', () => {
    (global as any).__TAURI__ = {};
    expect(isTauri()).toBe(true);
    delete (global as any).__TAURI__;
  });
});