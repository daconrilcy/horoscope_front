import { z } from 'zod';
import { http } from './client';

/**
 * Schémas Zod stricts pour les entrées chat
 */
const ChartId = z.string().min(8);
const Question = z.string().trim().min(3).max(1000);

/**
 * Schéma pour l'input de conseil chat
 */
export const AdviseInputSchema = z.object({
  chart_id: ChartId,
  question: Question,
});

/**
 * Schéma pour la réponse de conseil chat
 */
export const AdviseResponseSchema = z.object({
  answer: z.string().min(1),
  generated_at: z.string().datetime().optional(),
  request_id: z.string().optional(),
});

/**
 * Types inférés depuis les schémas Zod
 */
export type AdviseInput = z.infer<typeof AdviseInputSchema>;
export type AdviseResponse = z.infer<typeof AdviseResponseSchema>;

/**
 * Service pour gérer les endpoints chat
 * Endpoint : POST /v1/chat/advise
 */
export const chatService = {
  /**
   * Demande un conseil basé sur le thème natal
   * @param input Données de requête (chart_id, question)
   * @returns Réponse validée avec answer, generated_at, request_id
   * @throws ApiError si erreur API (401, 402, 429, 500, etc.)
   * @throws NetworkError si erreur réseau
   */
  async advise(input: AdviseInput): Promise<AdviseResponse> {
    try {
      const response = await http.post<unknown>('/v1/chat/advise', input);

      // Validation Zod stricte (fail-fast)
      const validated = AdviseResponseSchema.parse(response);
      return validated;
    } catch (error) {
      // Si c'est une ApiError avec details, laisser passer (mapping 422 dans composant)
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid advise response: ${error.message}`);
      }
      throw error;
    }
  },
};
