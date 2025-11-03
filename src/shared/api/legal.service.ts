import { ApiError, NetworkError } from './errors';
import { env } from '../config/env';

/**
 * Type de retour pour le contenu légal avec métadonnées
 */
export interface LegalContent {
  /** HTML sanitizé */
  html: string;
  /** ETag pour validation conditionnelle (si disponible) */
  etag?: string;
  /** Date de dernière modification (si disponible) */
  lastModified?: string;
  /** Version du contenu légal (si disponible) */
  version?: string;
}

/**
 * Service pour gérer les endpoints légaux
 * Endpoints : /v1/legal/*
 */
export const legalService = {
  /**
   * Récupère le HTML des Conditions d'utilisation
   * @returns Contenu HTML avec métadonnées (ETag, Last-Modified, Version)
   * @throws ApiError si erreur API (404, 500, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si Content-Type n'est pas text/html ou text/plain
   */
  async getTos(): Promise<LegalContent> {
    return this.fetchLegalContent('/v1/legal/tos');
  },

  /**
   * Récupère le HTML de la Politique de confidentialité
   * @returns Contenu HTML avec métadonnées (ETag, Last-Modified, Version)
   * @throws ApiError si erreur API (404, 500, etc.)
   * @throws NetworkError si erreur réseau
   * @throws Error si Content-Type n'est pas text/html ou text/plain
   */
  async getPrivacy(): Promise<LegalContent> {
    return this.fetchLegalContent('/v1/legal/privacy');
  },

  /**
   * Récupère le contenu légal avec métadonnées
   * Utilise fetch directement pour accéder aux headers (ETag, Last-Modified, X-Legal-Version)
   * @param endpoint Endpoint à appeler
   * @returns Contenu HTML avec métadonnées
   * @private
   */
  async fetchLegalContent(endpoint: string): Promise<LegalContent> {
    try {
      // Utiliser fetch directement pour accéder aux headers de réponse
      const baseURL = env.VITE_API_BASE_URL.replace(/\/+$/, '');
      const url = endpoint.startsWith('/')
        ? `${baseURL}${endpoint}`
        : `${baseURL}/${endpoint}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Vérifier le status
      if (!response.ok) {
        const body = await response.text().catch(() => '');
        let parsedBody: unknown;
        try {
          parsedBody = body ? JSON.parse(body) : {};
        } catch {
          parsedBody = body;
        }

        const requestId =
          response.headers.get('x-request-id') ||
          response.headers.get('x-trace-id') ||
          response.headers.get('x-correlation-id') ||
          undefined;

        throw new ApiError(
          (parsedBody as { message?: string })?.message ||
            response.statusText ||
            'Unknown error',
          response.status,
          undefined,
          requestId
        );
      }

      // Vérifier le Content-Type
      const contentType = response.headers.get('content-type') || '';
      if (
        !contentType.includes('text/html') &&
        !contentType.includes('text/plain')
      ) {
        const requestId =
          response.headers.get('x-request-id') ||
          response.headers.get('x-trace-id') ||
          response.headers.get('x-correlation-id') ||
          undefined;

        throw new ApiError(
          `Invalid content type: expected text/html or text/plain, got ${contentType}`,
          response.status,
          undefined,
          requestId
        );
      }

      // Lire le HTML
      const html = await response.text();

      // Extraire les métadonnées depuis les headers
      const etag = response.headers.get('etag') || undefined;
      const lastModified = response.headers.get('last-modified') || undefined;
      const version = response.headers.get('x-legal-version') || undefined;

      return {
        html,
        etag: etag ? etag.replace(/^"|"$/g, '') : undefined, // Retirer guillemets ETag
        lastModified,
        version,
      };
    } catch (error) {
      // Si c'est déjà une ApiError, la propager
      if (error instanceof ApiError) {
        throw error;
      }

      // Gestion des erreurs réseau
      if (
        (error as { name?: string })?.name === 'AbortError' ||
        (error as Error).message.includes('aborted')
      ) {
        throw new NetworkError('aborted', 'Request aborted');
      }

      if (error instanceof TypeError) {
        throw new NetworkError('offline', 'Network error: offline');
      }

      throw error;
    }
  },
};
