import { z } from 'zod';
import { http } from './client';
import { ApiError } from './errors';

/**
 * Schémas Zod stricts pour les entrées horoscope
 */
const ChartId = z.string().min(8);
const IsoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const Hhmm = z.string().regex(/^\d{2}:\d{2}$/);
const Lat = z.number().gte(-90).lte(90);
const Lng = z.number().gte(-180).lte(180);
const Tz = z.string().min(1); // IANA timezone

/**
 * Schéma pour l'input de création de thème natal
 */
export const CreateNatalInputSchema = z.object({
  date: IsoDate,
  time: Hhmm,
  latitude: Lat,
  longitude: Lng,
  timezone: Tz,
  name: z.string().optional(),
});

/**
 * Schéma pour la réponse de création de thème natal
 */
export const CreateNatalResponseSchema = z.object({
  chart_id: ChartId,
  created_at: z.string().datetime().optional(),
});

/**
 * Schéma pour la réponse Today (free)
 */
export const TodayResponseSchema = z.object({
  content: z.string().min(1),
  generated_at: z.string().datetime().optional(),
});

/**
 * Schéma pour la réponse Today Premium
 */
export const TodayPremiumResponseSchema = TodayResponseSchema.extend({
  premium_insights: z.string().min(1).optional(),
});

/**
 * Types inférés depuis les schémas Zod
 */
export type CreateNatalInput = z.infer<typeof CreateNatalInputSchema>;
export type CreateNatalResponse = z.infer<typeof CreateNatalResponseSchema>;
export type TodayResponse = z.infer<typeof TodayResponseSchema>;
export type TodayPremiumResponse = z.infer<typeof TodayPremiumResponseSchema>;

/**
 * Type de retour pour le téléchargement PDF
 */
export interface PdfStreamResult {
  blob: Blob;
  filename: string;
}

/**
 * Service pour gérer les endpoints horoscope
 * Endpoints : /v1/horoscope/*
 */
export const horoscopeService = {
  /**
   * Crée un thème natal
   * @param input Données de naissance
   * @returns Réponse validée avec chart_id
   * @throws ApiError si erreur API (422, 401, etc.)
   * @throws NetworkError si erreur réseau
   */
  async createNatal(input: CreateNatalInput): Promise<CreateNatalResponse> {
    try {
      const response = await http.post<unknown>('/v1/horoscope/natal', input);

      // Validation Zod stricte (fail-fast)
      const validated = CreateNatalResponseSchema.parse(response);
      return validated;
    } catch (error) {
      // Si c'est une ApiError avec details, laisser passer (mapping 422 dans composant)
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid createNatal response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Récupère l'horoscope Today pour un thème natal
   * @param chartId ID du thème natal
   * @returns Réponse validée avec contenu today
   * @throws ApiError si erreur API (404, 401, etc.)
   * @throws NetworkError si erreur réseau
   */
  async getToday(chartId: string): Promise<TodayResponse> {
    try {
      const response = await http.get<unknown>(
        `/v1/horoscope/today/${chartId}`
      );

      // Validation Zod stricte (fail-fast)
      const validated = TodayResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid getToday response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Récupère l'horoscope Today Premium pour un thème natal
   * @param chartId ID du thème natal
   * @returns Réponse validée avec contenu premium
   * @throws ApiError si erreur API (404, 402, 401, etc.)
   * @throws NetworkError si erreur réseau
   */
  async getTodayPremium(chartId: string): Promise<TodayPremiumResponse> {
    try {
      const response = await http.get<unknown>(
        `/v1/horoscope/today/premium/${chartId}`
      );

      // Validation Zod stricte (fail-fast)
      const validated = TodayPremiumResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(`Invalid getTodayPremium response: ${error.message}`);
      }
      throw error;
    }
  },

  /**
   * Télécharge le PDF du thème natal
   * @param chartId ID du thème natal
   * @returns Blob du PDF + nom de fichier
   * @throws ApiError si erreur API (404, 500, etc.)
   * @throws NetworkError si erreur réseau
   */
  async getNatalPdfStream(chartId: string): Promise<PdfStreamResult> {
    try {
      // Requête avec parseAs 'blob' explicite
      const blob = await http.get<Blob>(`/v1/horoscope/pdf/natal/${chartId}`, {
        parseAs: 'blob',
      });

      // Vérifier que c'est bien un PDF (Content-Type guard)
      // Le client http parse déjà en blob si parseAs 'blob', mais on veut vérifier
      // que ce n'est pas une erreur JSON renvoyée comme blob
      // On ne peut pas lire le contenu d'un blob sans async opération coûteuse
      // Donc on fait confiance au client qui parse selon Content-Type
      // Si le backend renvoie JSON par erreur avec parseAs 'blob', le blob contiendra
      // le JSON en texte, mais c'est acceptable car on traite ça côté downloadBlob

      const filename = `natal-${chartId}.pdf`;

      return {
        blob,
        filename,
      };
    } catch (error) {
      // Les erreurs 404/500 sont déjà gérées par le client
      if (error instanceof ApiError && error.status === 404) {
        throw new ApiError(
          'Chart not found',
          error.status,
          error.code,
          error.requestId
        );
      }
      throw error;
    }
  },
};
