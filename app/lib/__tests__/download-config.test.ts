// app/lib/__tests__/download-config.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { detectOS, DOWNLOAD_ASSETS, FALLBACK_ASSETS, fetchAssets } from '../download-config';

const originalNavigator = (globalThis as any).navigator;

describe('detectOS', () => {
  beforeEach(() => {
    Object.defineProperty(globalThis, 'navigator', {
      value: undefined,
      configurable: true,
      writable: true,
    });
  });
  afterEach(() => {
    if (originalNavigator !== undefined) {
      Object.defineProperty(globalThis, 'navigator', {
        value: originalNavigator,
        configurable: true,
        writable: true,
      });
    }
  });

  it.each([
    [{ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }, 'windows'],
    [{ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' }, 'macos'],
    [{ userAgent: 'Mozilla/5.0 (X11; Linux x86_64)' }, 'linux'],
    [{}, 'windows'],
  ] as Array<[Record<string, unknown>, string]>)('detects %o as %s', (nav, expected) => {
    Object.defineProperty(globalThis, 'navigator', {
      value: nav,
      configurable: true,
    });
    expect(detectOS()).toBe(expected);
  });

  it('returns windows when navigator is undefined', () => {
    delete (globalThis as any).navigator;
    expect(detectOS()).toBe('windows');
  });
});

describe('DOWNLOAD_ASSETS', () => {
  it('covers all 3 OS', () => {
    const osSet = new Set(DOWNLOAD_ASSETS.map(a => a.os));
    expect(osSet.has('windows')).toBe(true);
    expect(osSet.has('macos')).toBe(true);
    expect(osSet.has('linux')).toBe(true);
  });

  it('uses github.com/lj22503 release URL', () => {
    for (const a of DOWNLOAD_ASSETS) {
      expect(a.url).toMatch(/^https:\/\/github\.com\/lj22503\/invest-brain\/releases\//);
    }
  });

  it('FALLBACK_ASSETS matches DOWNLOAD_ASSETS (alias)', () => {
    expect(DOWNLOAD_ASSETS).toBe(FALLBACK_ASSETS);
  });
});

describe('fetchAssets', () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('returns fallback when fetch fails', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('network'));
    const list = await fetchAssets();
    expect(list).toBe(FALLBACK_ASSETS);
  });

  it('returns fallback when response is not ok', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: false, status: 404 });
    const list = await fetchAssets();
    expect(list).toBe(FALLBACK_ASSETS);
  });

  it('parses releases.json correctly', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        version: '1.2.3',
        generated_at: '2026-08-06',
        assets: [
          { os: 'windows', url: 'https://example.com/win.msi', size_hint: '4.5MB' },
          { os: 'macos', url: 'https://example.com/mac.dmg', size_hint: 'pending' },
          { os: 'linux', url: 'https://example.com/linux.AppImage', size_hint: 'pending' },
        ],
      }),
    });
    const list = await fetchAssets();
    expect(list).toHaveLength(3);
    expect(list[0].os).toBe('windows');
    expect(list[0].label).toBe('Windows');
    expect(list[0].filename).toBe('win.msi');
    expect(list[0].sizeHint).toBe('4.5MB');
  });
});