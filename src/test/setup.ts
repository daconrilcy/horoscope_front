import '@testing-library/jest-dom';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import { vi } from 'vitest';

// Mock global.fetch pour les tests
if (typeof globalThis.fetch === 'undefined') {
  globalThis.fetch = vi.fn();
}

// Mock env pour les tests
process.env.VITE_API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Cleanup after each test
afterEach(() => {
  cleanup();
});
