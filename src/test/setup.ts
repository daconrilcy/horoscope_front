import '@testing-library/jest-dom';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import { vi } from 'vitest';

// Mock global.fetch pour les tests
if (typeof globalThis.fetch === 'undefined') {
  globalThis.fetch = vi.fn();
}

// Mock window.scrollTo pour les tests (jsdom ne l'implémente pas)
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true,
});

// Mock env pour les tests
interface ProcessLike {
  process?: {
    env?: Record<string, string | undefined>;
  };
}
// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
const processEnv: unknown =
  typeof (globalThis as ProcessLike).process !== 'undefined'
    ? (
        (globalThis as ProcessLike).process as {
          env?: Record<string, string | undefined>;
        }
      ).env
    : null;
const env =
  (processEnv as Record<string, string | undefined>) ??
  ({} as Record<string, string | undefined>);
if (env.VITE_API_BASE_URL == null || env.VITE_API_BASE_URL === '') {
  env.VITE_API_BASE_URL = 'http://localhost:8000';
}

// Cleanup after each test
afterEach(() => {
  cleanup();
});
