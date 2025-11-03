import '@testing-library/jest-dom';
import { afterEach, beforeAll, afterAll, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './msw.server';

// Force TZ à Europe/Paris pour tests déterministes
// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-assignment
process.env.TZ = 'Europe/Paris';

// Mock global.fetch si non défini (fallback)
if (typeof globalThis.fetch === 'undefined') {
  globalThis.fetch = vi.fn();
}

// Mock window.scrollTo pour les tests (jsdom ne l'implémente pas)
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true,
});

// Polyfill crypto.randomUUID
// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/strict-boolean-expressions
if (!globalThis.crypto?.randomUUID) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
  (globalThis.crypto as any) = {
    ...globalThis.crypto,
    randomUUID: (): string => '00000000-0000-4000-8000-000000000000',
  };
}

// Mock URL.createObjectURL et revokeObjectURL (si non définis)
if (typeof URL.createObjectURL !== 'undefined') {
  vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock');
}
// eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
if (typeof URL.revokeObjectURL !== 'undefined') {
  vi.spyOn(URL, 'revokeObjectURL').mockReturnValue();
} else {
  // Polyfill si non défini
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-assignment
  (URL as any).revokeObjectURL = vi.fn();
}

// Mock window.location.assign (supprimer d'abord si existe déjà)
try {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
  delete (window.location as any).assign;
} catch {
  // Ignore si ne peut pas être supprimé
}
try {
  Object.defineProperty(window.location, 'assign', {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-assignment
    value: vi.fn(),
    writable: true,
    configurable: true,
  });
} catch {
  // Ignore si ne peut pas être défini (déjà mocké ailleurs)
}

// Mock window.print
vi.spyOn(window, 'print').mockImplementation(() => {});

// Mock matchMedia pour les tests
// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock Clipboard API
// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call
Object.assign(navigator as any, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
    readText: vi.fn().mockResolvedValue(''),
  },
});

// Mock env pour les tests
interface ProcessLike {
  process?: {
    env?: Record<string, string | undefined>;
  };
}

const processEnv: unknown =
  typeof (globalThis as ProcessLike).process !== 'undefined'
    ? (
        (globalThis as ProcessLike).process as {
          env?: Record<string, string | undefined>;
        }
      ).env
    : null;
// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
const env: Record<string, string | undefined> =
  (processEnv as Record<string, string | undefined>) ??
  ({} as Record<string, string | undefined>);
// eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
if (!env.VITE_API_BASE_URL || env.VITE_API_BASE_URL === '') {
  env.VITE_API_BASE_URL = 'http://localhost:8000';
}

// Setup MSW server
// Utiliser 'warn' au lieu de 'error' pour permettre aux tests existants
// qui utilisent mockFetch directement de continuer à fonctionner
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' });
});

// Reset handlers après chaque test
afterEach(() => {
  cleanup();
  server.resetHandlers();
});

// Fermer le serveur après tous les tests
afterAll(() => {
  server.close();
});
