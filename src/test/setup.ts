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
// @ts-expect-error - process.env est disponible dans l'environnement de test
// eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
const processEnv = typeof globalThis.process !== 'undefined' ? globalThis.process.env : null;
// eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
const env = processEnv as Record<string, string | undefined> | null;
if (env != null && (env.VITE_API_BASE_URL == null || env.VITE_API_BASE_URL === '')) {
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  env.VITE_API_BASE_URL = 'http://localhost:8000';
}

// Cleanup after each test
afterEach(() => {
  cleanup();
});
