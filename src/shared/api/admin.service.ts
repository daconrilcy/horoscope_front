import { z } from 'zod';
import { http } from './client';

/**
 * Schéma Zod pour la réponse de clear price_lookup cache
 */
export const ClearPriceLookupCacheResponseSchema = z.object({
  cleared: z.boolean(),
  message: z.string().optional(),
});

/**
 * Type inféré depuis le schéma Zod
 */
export type ClearPriceLookupCacheResponse = z.infer<
  typeof ClearPriceLookupCacheResponseSchema
>;

/**
 * Service admin pour les opérations de développement/maintenance
 */
export const adminService = {
  /**
   * Clear le cache price_lookup côté backend
   * Endpoint : POST /v1/admin/clear-price-lookup-cache
   * @returns Réponse validée avec cleared et message optionnel
   * @throws ApiError si erreur API (401, 403, 500, etc.)
   * @throws NetworkError si erreur réseau
   */
  async clearPriceLookupCache(): Promise<ClearPriceLookupCacheResponse> {
    try {
      const response = await http.post<unknown>(
        '/v1/admin/clear-price-lookup-cache',
        {},
        {
          auth: true, // Requiert authentification
        }
      );

      // Validation Zod stricte (fail-fast)
      const validated = ClearPriceLookupCacheResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        // Erreur de validation Zod
        throw new Error(
          `Invalid clear price_lookup cache response: ${error.message}`
        );
      }
      throw error;
    }
  },
};
