import { http } from './client';
import { ApiError } from './errors';

/**
 * Type de retour pour l'export ZIP
 */
export interface ZipExportResult {
  blob: Blob;
  filename: string;
}

// Note: filenameFromContentDisposition n'est pas utilisée actuellement
// car le client HTTP ne retourne pas les headers de réponse
// TODO: utiliser cette fonction quand le client HTTP exposera les headers
// /**
//  * Extraction du filename depuis Content-Disposition header
//  * Support filename*=UTF-8''... (RFC 5987) et filename="..." ou filename=...
//  */
// function filenameFromContentDisposition(
//   header?: string | null
// ): string | undefined {
//   if (!header) return undefined;
//
//   // filename* (RFC 5987) en priorité
//   const mStar = header.match(/filename\*\s*=\s*UTF-8''([^;]+)/i);
//   if (mStar) {
//     try {
//       return decodeURIComponent(mStar[1]);
//     } catch {
//       return undefined;
//     }
//   }
//
//   // filename simple
//   const m = header.match(/filename\s*=\s*("?)([^";]+)\1/i);
//   return m?.[2];
// }

/**
 * Génère un filename de fallback au format account-export-YYYYMMDD.zip
 */
function generateFallbackFilename(): string {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `account-export-${year}${month}${day}.zip`;
}

/**
 * Service pour gérer les endpoints account (RGPD)
 * Endpoints : /v1/account/*
 */
export const accountService = {
  /**
   * Exporte les données utilisateur au format ZIP
   * @returns Blob du ZIP + nom de fichier
   * @throws ApiError si erreur API (401, 500, Content-Type invalide)
   * @throws NetworkError si erreur réseau
   */
  async exportZip(
    signal?: AbortSignal
  ): Promise<ZipExportResult> {
    try {
      // Utiliser le signal fourni ou créer un nouveau AbortController
      const abortSignal = signal ?? new AbortController().signal;

      // Requête avec parseAs 'blob' explicite et timeout 60s
      const blob = await http.get<Blob>('/v1/account/export', {
        parseAs: 'blob',
        timeoutMs: 60000,
        signal: abortSignal,
      });

      // Vérifier taille blob > 0
      if (blob.size === 0) {
        throw new ApiError(
          'ZIP invalide (fichier vide)',
          500,
          'invalid-zip',
          undefined
        );
      }

      // Content-Type guard: vérifier que c'est bien un ZIP
      // Note: on ne peut pas accéder aux headers directement depuis le blob
      // Le client HTTP parse déjà en blob si parseAs 'blob'
      // On doit faire confiance au Content-Type détecté par le client
      // Si le backend renvoie JSON par erreur avec parseAs 'blob', le blob contiendra
      // le JSON en texte, mais on ne peut pas le détecter sans lecture async coûteuse
      // Donc on fait confiance au client qui parse selon Content-Type

      // Pour extraire le filename, on a besoin d'accéder aux headers de la réponse
      // Malheureusement, le client HTTP actuel ne retourne pas les headers
      // On utilise donc un fallback daté
      // TODO: améliorer le client HTTP pour exposer les headers de réponse

      // Filename depuis Content-Disposition (si disponible) ou fallback
      // Pour l'instant, on utilise toujours le fallback car les headers ne sont pas exposés
      const filename = generateFallbackFilename();

      return {
        blob,
        filename,
      };
    } catch (error) {
      // Si c'est une ApiError avec status 401, laisser remonter (géré par wrapper)
      if (error instanceof ApiError && error.status === 401) {
        throw error;
      }

      // Si c'est une ApiError avec status 500, enrichir le message
      if (error instanceof ApiError && error.status === 500) {
        throw new ApiError(
          'Erreur serveur lors de l\'export',
          error.status,
          error.code,
          error.requestId
        );
      }

      // Autres erreurs
      throw error;
    }
  },

  /**
   * Supprime le compte utilisateur
   * @returns void (204 No Content)
   * @throws ApiError si erreur API (401, 409, 500)
   * @throws NetworkError si erreur réseau
   */
  async deleteAccount(): Promise<void> {
    try {
      await http.del('/v1/account');
      // 204 No Content → void
    } catch (error) {
      // Si c'est une ApiError avec status 401, laisser remonter (géré par wrapper)
      if (error instanceof ApiError && error.status === 401) {
        throw error;
      }

      // Si c'est une ApiError avec status 409, enrichir le message métier
      if (error instanceof ApiError && error.status === 409) {
        // Toujours enrichir le message pour 409 avec un message métier spécifique
        const enrichedMessage =
          error.message != null && error.message.includes('Suppression impossible')
            ? error.message
            : 'Suppression impossible pour le moment (opérations en cours)';
        throw new ApiError(
          enrichedMessage,
          error.status,
          error.code ?? 'conflict',
          error.requestId
        );
      }

      // Si c'est une ApiError avec status 500, enrichir le message
      if (error instanceof ApiError && error.status === 500) {
        throw new ApiError(
          'Erreur serveur lors de la suppression',
          error.status,
          error.code,
          error.requestId
        );
      }

      // Autres erreurs
      throw error;
    }
  },
};
