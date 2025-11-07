import { http } from './client';

/**
 * Service pour les opérations admin (dev-only)
 */
export const adminService = {
  /**
   * Vide le cache price_lookup côté backend
   * Endpoint : POST /v1/admin/price-lookup/clear
   * @throws ApiError si erreur API
   * @throws NetworkError si erreur réseau
   */
  async clearPriceLookupCache(): Promise<void> {
    // Vérifier que nous sommes en dev
    if (!import.meta.env.DEV) {
      throw new Error('Admin service is only available in development');
    }

    // POST /v1/admin/price-lookup/clear attendu 204 No Content
    await http.post<unknown>('/v1/admin/price-lookup/clear', {}, {});
  },
};
