import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  readPersistedToken,
  writePersistedToken,
  clearPersistedToken,
} from './token';

const STORAGE_KEY = 'APP_AUTH_TOKEN';

describe('token helpers', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('readPersistedToken', () => {
    it('devrait retourner null si localStorage vide', () => {
      expect(readPersistedToken()).toBeNull();
    });

    it('devrait lire le token depuis localStorage (format JSON)', () => {
      const token = 'test-token-123';
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token }));

      expect(readPersistedToken()).toBe(token);
    });

    it('devrait lire le token depuis localStorage (format string directe)', () => {
      const token = 'test-token-123';
      localStorage.setItem(STORAGE_KEY, JSON.stringify(token));

      expect(readPersistedToken()).toBe(token);
    });

    it('devrait retourner null si JSON invalide (fallback)', () => {
      localStorage.setItem(STORAGE_KEY, 'invalid-json{');

      // La fonction essaie de parser JSON, puis retourne null si invalide
      // ou retourne la string si elle ne commence pas par { ou [
      const result = readPersistedToken();
      // Le comportement actuel retourne null si le JSON est invalide
      // car il essaie JSON.parse et catch retourne null
      expect(result).toBeNull();
    });

    it('devrait gérer gracieusement si localStorage bloqué', () => {
      // Simuler localStorage.getItem qui throw
      const originalGetItem = localStorage.getItem.bind(localStorage);
      vi.spyOn(localStorage, 'getItem').mockImplementation(() => {
        throw new Error('QuotaExceededError');
      });

      expect(readPersistedToken()).toBeNull();

      localStorage.getItem = originalGetItem;
    });

    it('devrait utiliser la clé namespacée APP_AUTH_TOKEN', () => {
      const token = 'test-token';
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token }));

      expect(localStorage.getItem(STORAGE_KEY)).toBeTruthy();
      expect(readPersistedToken()).toBe(token);
    });
  });

  describe('writePersistedToken', () => {
    it('devrait stocker le token dans localStorage (format JSON)', () => {
      const token = 'test-token-123';

      writePersistedToken(token);

      const stored = localStorage.getItem(STORAGE_KEY);
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored!) as { token: string };
      expect(parsed.token).toBe(token);
    });

    it('devrait gérer gracieusement si localStorage plein', () => {
      // Simuler localStorage.setItem qui throw
      const originalSetItem = localStorage.setItem.bind(localStorage);
      vi.spyOn(localStorage, 'setItem').mockImplementation(() => {
        throw new Error('QuotaExceededError');
      });

      // Ne devrait pas throw
      expect(() => writePersistedToken('test-token')).not.toThrow();

      localStorage.setItem = originalSetItem;
    });
  });

  describe('clearPersistedToken', () => {
    it('devrait supprimer le token de localStorage', () => {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ token: 'test-token' })
      );

      clearPersistedToken();

      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    });

    it('devrait gérer gracieusement si localStorage bloqué', () => {
      // Simuler localStorage.removeItem qui throw
      const originalRemoveItem = localStorage.removeItem.bind(localStorage);
      vi.spyOn(localStorage, 'removeItem').mockImplementation(() => {
        throw new Error('SecurityError');
      });

      // Ne devrait pas throw
      expect(() => clearPersistedToken()).not.toThrow();

      localStorage.removeItem = originalRemoveItem;
    });

    it('devrait ne rien faire si token absent', () => {
      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();

      clearPersistedToken();

      expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    });
  });
});
