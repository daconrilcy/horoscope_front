import { describe, it, expect, beforeEach, vi } from 'vitest';
import { accountService } from './account.service';
import { ApiError } from './errors';
import { NetworkError } from './errors';
import { http } from './client';

// Mock le client HTTP
vi.mock('./client', () => ({
  configureHttp: vi.fn(),
  http: {
    get: vi.fn(),
    del: vi.fn(),
  },
}));

describe('accountService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('exportZip', () => {
    it('devrait réussir avec blob ZIP valide', async () => {
      const mockBlob = new Blob(['zip content'], { type: 'application/zip' });

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
       
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockBlob as unknown
      );

      const result = await accountService.exportZip();

      expect(result.blob).toBe(mockBlob);
      expect(result.filename).toMatch(/^account-export-\d{8}\.zip$/);
      expect(mockHttpGet).toHaveBeenCalledWith('/v1/account/export', {
        parseAs: 'blob',
        timeoutMs: 60000,
        signal: expect.any(AbortSignal),
      });
    });

    it('devrait utiliser le signal AbortController fourni', async () => {
      const mockBlob = new Blob(['zip content'], { type: 'application/zip' });
      const customSignal = new AbortController().signal;

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockBlob as unknown
      );

      await accountService.exportZip(customSignal);

      expect(mockHttpGet).toHaveBeenCalledWith(
        '/v1/account/export',
        expect.objectContaining({
          signal: customSignal,
        })
      );
    });

    it('devrait échouer si blob est vide (0 bytes)', async () => {
      const mockBlob = new Blob([], { type: 'application/zip' });

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockBlob);

      await expect(accountService.exportZip()).rejects.toThrow(ApiError);

      try {
        await accountService.exportZip();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(500);
          expect(error.code).toBe('invalid-zip');
        }
      }
    });

    it('devrait laisser passer ApiError 401', async () => {
      const mockError = new ApiError('Unauthorized', 401, undefined, undefined);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.exportZip()).rejects.toThrow(ApiError);

      try {
        await accountService.exportZip();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(401);
        }
      }
    });

    it('devrait enrichir ApiError 500', async () => {
      const mockError = new ApiError(
        'Internal Server Error',
        500,
        undefined,
        'req-123'
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.exportZip()).rejects.toThrow(ApiError);

      try {
        await accountService.exportZip();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(500);
          expect(error.message).toContain('Erreur serveur');
          expect(error.requestId).toBe('req-123');
        }
      }
    });

    it('devrait laisser passer NetworkError', async () => {
      const mockError = new NetworkError('timeout', 'Request timeout');

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.exportZip()).rejects.toThrow(NetworkError);
    });
  });

  describe('deleteAccount', () => {
    it('devrait réussir avec 204 No Content', async () => {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpDel = vi.mocked(http.del);
      (mockHttpDel as ReturnType<typeof vi.fn>).mockResolvedValue(undefined);

      await accountService.deleteAccount();

      expect(mockHttpDel).toHaveBeenCalledWith('/v1/account');
    });

    it('devrait laisser passer ApiError 401', async () => {
      const mockError = new ApiError('Unauthorized', 401, undefined, undefined);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpDel = vi.mocked(http.del);
      (mockHttpDel as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.deleteAccount()).rejects.toThrow(ApiError);

      try {
        await accountService.deleteAccount();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(401);
        }
      }
    });

    it('devrait enrichir ApiError 409 avec message métier', async () => {
      const mockError = new ApiError('Conflict', 409, undefined, 'req-123');

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpDel = vi.mocked(http.del);
      (mockHttpDel as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.deleteAccount()).rejects.toThrow(ApiError);

      try {
        await accountService.deleteAccount();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(409);
          expect(error.code).toBe('conflict');
          // Le message devrait être enrichi avec le message métier
          expect(error.message).toBe('Suppression impossible pour le moment (opérations en cours)');
          expect(error.requestId).toBe('req-123');
        }
      }
    });

    it('devrait enrichir ApiError 500', async () => {
      const mockError = new ApiError(
        'Internal Server Error',
        500,
        undefined,
        'req-123'
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpDel = vi.mocked(http.del);
      (mockHttpDel as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.deleteAccount()).rejects.toThrow(ApiError);

      try {
        await accountService.deleteAccount();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(500);
          expect(error.message).toContain('Erreur serveur');
          expect(error.requestId).toBe('req-123');
        }
      }
    });

    it('devrait laisser passer NetworkError', async () => {
      const mockError = new NetworkError('timeout', 'Request timeout');

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpDel = vi.mocked(http.del);
      (mockHttpDel as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(accountService.deleteAccount()).rejects.toThrow(NetworkError);
    });
  });
});
