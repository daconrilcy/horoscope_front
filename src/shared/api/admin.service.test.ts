import { describe, it, expect, beforeEach, vi } from 'vitest';
import { adminService } from './admin.service';
import { http } from './client';
import { ApiError } from './errors';

// Mock le client HTTP
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

// Mock import.meta.env.DEV
vi.mock('import.meta', () => ({
  env: {
    DEV: true,
  },
}));

describe('adminService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('clearPriceLookupCache', () => {
    it('devrait appeler POST /v1/admin/price-lookup/clear et retourner void', async () => {
      // Mock une réponse 204 No Content (pas de body)
      const mockResponse = undefined;
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await adminService.clearPriceLookupCache();

      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/admin/price-lookup/clear',
        {},
        {}
      );
    });

    it("devrait propager ApiError en cas d'erreur API", async () => {
      const apiError = new ApiError('Forbidden', 403);
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(apiError);

      await expect(adminService.clearPriceLookupCache()).rejects.toThrow(
        ApiError
      );
      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/admin/price-lookup/clear',
        {},
        {}
      );
    });

    it("devrait propager NetworkError en cas d'erreur réseau", async () => {
      const networkError = new Error('Network error');
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(
        networkError
      );

      await expect(adminService.clearPriceLookupCache()).rejects.toThrow(
        networkError
      );
    });
  });
});
