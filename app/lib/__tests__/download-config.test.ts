// app/lib/__tests__/download-config.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { detectOS, DOWNLOAD_ASSETS } from '../download-config';

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
      expect(a.url).toMatch(/^https:\/\/github\.com\/lj22503\/invest-brain\/releases\/latest\/download\//);
    }
  });
});