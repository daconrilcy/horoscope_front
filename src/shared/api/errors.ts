/**
 * Types d'erreurs HTTP personnalisées
 * ApiError pour les erreurs HTTP, NetworkError pour les erreurs réseau
 */

/**
 * Erreur HTTP standardisée avec status code et request_id
 */
export class ApiError extends Error {
  public readonly status?: number;
  public readonly code?: string;
  public readonly requestId?: string;
  public readonly details?: unknown;

  constructor(
    message: string,
    status?: number,
    code?: string,
    requestId?: string,
    details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.requestId = requestId;
    this.details = details;

    // Maintenir le prototype pour instanceof
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

/**
 * Erreur réseau (timeout, offline, abort)
 */
export class NetworkError extends Error {
  public readonly reason: 'timeout' | 'offline' | 'aborted';

  constructor(reason: 'timeout' | 'offline' | 'aborted', message?: string) {
    super(message || `Network error: ${reason}`);
    this.name = 'NetworkError';
    this.reason = reason;

    // Maintenir le prototype pour instanceof
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

/**
 * Extrait le request_id depuis les headers puis le body
 * Cherche dans les headers : x-request-id, x-trace-id, x-correlation-id
 * Puis dans le body : request_id, trace_id
 */
export function extractRequestId(
  responseOrBody: Response | Record<string, unknown>
): string | undefined {
  // Si c'est une Response (ou un objet avec headers pour les mocks de tests)
  if (
    responseOrBody instanceof Response ||
    (typeof responseOrBody === 'object' &&
      responseOrBody !== null &&
      'headers' in responseOrBody)
  ) {
    const headers = (
      responseOrBody as {
        headers: Headers | { get: (key: string) => string | null };
      }
    ).headers;
    const headerId =
      (headers instanceof Headers
        ? headers.get('x-request-id')
        : headers.get?.('x-request-id')) ||
      (headers instanceof Headers
        ? headers.get('x-trace-id')
        : headers.get?.('x-trace-id')) ||
      (headers instanceof Headers
        ? headers.get('x-correlation-id')
        : headers.get?.('x-correlation-id'));
    if (headerId) {
      return headerId;
    }
    // On ne peut pas lire le body ici car il a déjà été consommé
    return undefined;
  }

  // Si c'est un objet (body parsé), chercher dans les propriétés
  if (typeof responseOrBody === 'object' && responseOrBody !== null) {
    const body = responseOrBody;
    return (
      (body.request_id as string | undefined) ||
      (body.trace_id as string | undefined) ||
      (body.requestId as string | undefined) ||
      (body.traceId as string | undefined)
    );
  }

  return undefined;
}
