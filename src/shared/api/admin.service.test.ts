import { describe, it, expect, beforeEach, vi } from 'vitest';
import { adminService } from './admin.service';
import { http } from './client';
import { ApiError } from './errors';

// Mock http client
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

describe('adminService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('clearPriceLookupCache', () => {
    it('devrait clear le cache price_lookup avec succès', async () => {
      const mockResponse = {
        cleared: true,
        message: 'Cache cleared successfully',
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      vi.mocked(http.post).mockResolvedValue(mockResponse);

      const result = await adminService.clearPriceLookupCache();

      expect(result).toEqual(mockResponse);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      expect(http.post).toHaveBeenCalledWith(
        '/v1/admin/clear-price-lookup-cache',
        {},
        {
          auth: true,
        }
      );
    });

    it('devrait retourner une réponse sans message', async () => {
      const mockResponse = {
        cleared: true,
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      vi.mocked(http.post).mockResolvedValue(mockResponse);

      const result = await adminService.clearPriceLookupCache();

      expect(result).toEqual(mockResponse);
      expect(result.cleared).toBe(true);
    });

    it('devrait échouer si la réponse est invalide', async () => {
      const mockResponse = {
        cleared: 'invalid', // Invalide
      };
      // eslint-disable-next-line @typescript-eslint/unbound-method
      vi.mocked(http.post).mockResolvedValue(mockResponse);

      await expect(adminService.clearPriceLookupCache()).rejects.toThrow(
        'Invalid clear price_lookup cache response'
      );
    });

    it('devrait propager les erreurs API', async () => {
      const apiError = new ApiError('Unauthorized', 401);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      vi.mocked(http.post).mockRejectedValue(apiError);

      await expect(adminService.clearPriceLookupCache()).rejects.toThrow(
        ApiError
      );
    });

    it('devrait propager les erreurs réseau', async () => {
      const networkError = new Error('Network error');
      // eslint-disable-next-line @typescript-eslint/unbound-method
      vi.mocked(http.post).mockRejectedValue(networkError);

      await expect(adminService.clearPriceLookupCache()).rejects.toThrow(
        'Network error'
      );
    });
  });
});
