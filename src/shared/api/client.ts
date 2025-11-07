import { v4 as uuidv4 } from 'uuid';
import { useAuthStore } from '@/stores/authStore';
import { eventBus } from './eventBus';
import { ApiError, NetworkError, extractRequestId } from './errors';
import type { PaywallPayload } from './types';
import { CLIENT_VERSION, REQUEST_SOURCE } from '@/shared/config/version';

/**
 * Options de requête HTTP
 */
export interface RequestOptions {
  /** Injecter automatiquement le token Bearer */
  auth?: boolean;
  /** Ajouter Idempotency-Key (UUID v4) sur demande, uniquement pour mutations (POST/PUT/PATCH/DELETE) */
  /** Usage courant : /v1/billing/checkout */
  idempotency?: boolean;
  /** Signal AbortController personnalisé */
  signal?: AbortSignal;
  /** Headers supplémentaires */
  headers?: HeadersInit;
  /** Timeout en millisecondes (défaut: 15000) */
  timeoutMs?: number;
  /** Forcer le type de parsing */
  parseAs?: 'json' | 'blob' | 'text';
  /** Désactiver le retry automatique */
  noRetry?: boolean;
}

/**
 * Configuration du client HTTP
 */
interface HttpClientConfig {
  baseURL: string;
  onUnauthorized?: () => void;
}

// Configuration globale
let baseURL = '';
let onUnauthorized: (() => void) | null = null;

// Debounce global 401 (60s par défaut)
let unauthorizedFiredAt = 0;
let unauthorizedEmissionInProgress = false; // Verrou pour éviter les émissions simultanées
const UNAUTHORIZED_DEBOUNCE_MS = 60_000; // 60 secondes

/**
 * Émet un événement auth:unauthorized seulement si >60s depuis le dernier
 * Anti-spam pour éviter les avalanches de toasts
 * Utilise une approche avec mise à jour atomique du timestamp pour éviter les émissions simultanées
 *
 * Stratégie : mettre à jour le timestamp AVANT de vérifier si on doit émettre.
 * Si plusieurs requêtes arrivent simultanément, seule la première verra
 * `previousFiredAt < now - DEBOUNCE_MS` et mettra à jour le timestamp.
 * Les autres verront déjà `unauthorizedFiredAt >= now - DEBOUNCE_MS` et ne déclencheront pas.
 */
function fireUnauthorizedOnce(): void {
  const now = Date.now();
  const previousFiredAt = unauthorizedFiredAt;

  // Vérifier le debounce
  if (now - previousFiredAt <= UNAUTHORIZED_DEBOUNCE_MS) {
    return; // Trop tôt, ne pas émettre
  }

  // Vérifier le verrou
  if (unauthorizedEmissionInProgress) {
    return; // Une émission est déjà en cours, ne pas émettre
  }

  // Acquérir le verrou immédiatement (synchrone)
  unauthorizedEmissionInProgress = true;

  // Mettre à jour le timestamp immédiatement (synchrone)
  // Cette mise à jour atomique garantit qu'une seule requête peut passer
  unauthorizedFiredAt = now;

  // Vérifier si on était la première à mettre à jour
  // Si unauthorizedFiredAt === now ET qu'il était différent de previousFiredAt,
  // c'est qu'on était la première requête
  if (unauthorizedFiredAt === now && unauthorizedFiredAt !== previousFiredAt) {
    // Émettre l'événement
    eventBus.emit('auth:unauthorized');
  }

  // Libérer le verrou immédiatement après (synchrone)
  unauthorizedEmissionInProgress = false;
}

/**
 * Réinitialise le debounce 401 (utile pour les tests)
 * @internal
 */
export function resetUnauthorizedDebounce(): void {
  unauthorizedFiredAt = 0;
  unauthorizedEmissionInProgress = false;
}

/**
 * Configure le client HTTP
 */
export function configureHttp(config: HttpClientConfig): void {
  baseURL = config.baseURL.replace(/\/+$/, '');
  onUnauthorized = config.onUnauthorized ?? null;
}

/**
 * Construit l'URL complète à partir d'un path
 */
function buildUrl(path: string): string {
  if (path.startsWith('http')) {
    return path;
  }
  const separator = path.startsWith('/') ? '' : '/';
  return `${baseURL}${separator}${path}`;
}

/**
 * Vérifie si la méthode HTTP est une mutation
 */
function isMutationMethod(method: string): boolean {
  return ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
}

/**
 * Détermine si on doit ajouter Idempotency-Key
 * Uniquement pour mutations (POST/PUT/PATCH/DELETE)
 * Usage courant : /v1/billing/checkout
 */
function shouldAddIdempotencyKey(
  method: string,
  idempotency?: boolean
): boolean {
  if (idempotency !== true) {
    return false;
  }
  // Uniquement sur mutations
  return isMutationMethod(method);
}

/**
 * Construit les headers de la requête
 */
function buildHeaders(
  method: string,
  _url: string,
  options: RequestOptions,
  existingHeaders?: HeadersInit
): HeadersInit {
  const headers = new Headers(existingHeaders);

  // Headers standard pour corrélation backend (toutes requêtes)
  headers.set('X-Client-Version', CLIENT_VERSION);
  headers.set('X-Request-Source', REQUEST_SOURCE);

  // Content-Type par défaut pour JSON (sauf si blob/text explicite)
  if (
    !headers.has('Content-Type') &&
    options.parseAs !== 'blob' &&
    options.parseAs !== 'text'
  ) {
    headers.set('Content-Type', 'application/json');
  }

  // Injection Bearer si auth: true
  if (options.auth !== false) {
    const token = useAuthStore.getState().getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  // Idempotency-Key uniquement sur mutations (POST/PUT/PATCH/DELETE)
  // Ne jamais écraser un header Idempotency-Key fourni par l'appelant
  if (options.idempotency === true) {
    // Warning en dev si utilisé sur GET
    if (method === 'GET' && import.meta.env.DEV) {
      console.warn('Idempotency-Key on GET: avoid unless you know why.');
    }
    // Injecter uniquement sur mutations et seulement si le header n'existe pas déjà
    if (
      shouldAddIdempotencyKey(method, options.idempotency) &&
      !headers.has('Idempotency-Key')
    ) {
      headers.set('Idempotency-Key', uuidv4());
    }
  }

  return headers;
}

/**
 * Parse la réponse selon le Content-Type ou l'option parseAs
 */
async function parseResponse<T>(
  response: Response,
  parseAs?: 'json' | 'blob' | 'text'
): Promise<T> {
  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') || '';

  // Parsing explicite
  if (parseAs === 'blob') {
    const blob = await response.blob();
    // Cas blob JSON : si content-type annonce JSON, reparser JSON et lever ApiError avec request_id
    if (contentType.includes('application/json')) {
      try {
        const text = await blob.text();
        const json: unknown = JSON.parse(text);
        // Si c'est une erreur (status >= 400), lever ApiError avec request_id
        if (response.status >= 400) {
          const requestId = extractRequestId(response);
          const errorBody = json as { message?: string };
          const message =
            errorBody.message ?? response.statusText ?? 'Unknown error';
          throw new ApiError(message, response.status, undefined, requestId);
        }
      } catch (error) {
        // Si c'est déjà une ApiError, la relancer
        if (error instanceof ApiError) {
          throw error;
        }
        // Sinon, c'est une erreur de parsing JSON → utiliser le blob
      }
    }
    return blob as T;
  }
  if (parseAs === 'text') {
    return (await response.text()) as T;
  }

  // Autodétection par Content-Type
  if (
    contentType.includes('application/pdf') ||
    contentType.includes('application/zip')
  ) {
    return (await response.blob()) as T;
  }
  if (contentType.includes('text/html') || contentType.includes('text/plain')) {
    return (await response.text()) as T;
  }

  // JSON par défaut (défensif)
  // Lire le texte une fois pour pouvoir le réutiliser
  const text = await response.text();
  if (!text) {
    return undefined as T;
  }

  // Si Content-Type annonce JSON, parser strictement
  if (contentType.includes('application/json')) {
    try {
      return JSON.parse(text) as T;
    } catch {
      // JSON invalide alors que Content-Type annonce JSON
      const requestId = extractRequestId(response);
      throw new ApiError('invalid-json', response.status, undefined, requestId);
    }
  }

  // Tentative de parsing JSON si pas de Content-Type spécifique
  try {
    return JSON.parse(text) as T;
  } catch {
    // Si le parsing échoue, retourner le text brut
    return text as unknown as T;
  }
}

/**
 * Convertit une erreur HTTP en ApiError avec mapping des événements
 */
function toApiError(response: Response, body: unknown, url: string): ApiError {
  // Extraire request_id depuis les headers AVANT le parsing du body
  const headerRequestId = extractRequestId(response);
  const bodyRequestId =
    typeof body === 'object' && body !== null
      ? extractRequestId(body as Record<string, unknown>)
      : undefined;
  const requestId = headerRequestId || bodyRequestId;
  const status = response.status;

  // Message brut du serveur (non exposé en clair)
  const rawMessage =
    (body as { message?: string })?.message ??
    response.statusText ??
    'Unknown error';

  // Message UX générique sécurisé
  let userMessage: string;
  if (status >= 500) {
    userMessage = requestId
      ? `Une erreur est survenue. Request ID: ${requestId}`
      : 'Une erreur est survenue. Veuillez réessayer plus tard.';
  } else if (status === 401) {
    userMessage = 'Session expirée';
  } else if (status === 402) {
    userMessage = 'Plan insuffisant';
  } else if (status === 429) {
    userMessage = 'Quota atteint';
  } else {
    // Pour les autres erreurs (400, 422, etc.), utiliser le message brut
    // mais le stocker aussi dans meta pour sécurité
    userMessage = rawMessage;
  }

  let code: string | undefined;
  let details: unknown;

  // Extraction des détails pour 400/422
  if (status === 400 || status === 422) {
    details =
      (body as { errors?: unknown; details?: unknown })?.errors ||
      (body as { errors?: unknown; details?: unknown })?.details ||
      body;
  }

  // Création de l'erreur avec message UX générique et meta.debugMessage
  const error = new ApiError(userMessage, status, code, requestId, details, {
    debugMessage: rawMessage,
  });

  // Extraction Retry-After depuis headers (seconds)
  const retryAfterHeader = response.headers.get('Retry-After');
  const retryAfterSeconds = retryAfterHeader
    ? parseInt(retryAfterHeader, 10)
    : undefined;

  // Mapping des événements selon le status
  if (status === 401) {
    // Debounce global 401 (60s)
    fireUnauthorizedOnce();
    // Ne pas rediriger si déjà sur /login (éviter les boucles)
    if (onUnauthorized && !url.includes('/login')) {
      onUnauthorized();
    }
  } else if (status === 402) {
    const bodyObj = body as {
      feature?: string;
      upgrade_url?: string;
    };
    const payload: PaywallPayload = {
      reason: 'plan',
      upgradeUrl: bodyObj.upgrade_url,
      feature: bodyObj.feature,
    };
    eventBus.emit('paywall:plan', payload);
  } else if (status === 429) {
    const bodyObj = body as {
      feature?: string;
      upgrade_url?: string;
      retry_after?: number;
    };
    const retryAfter = retryAfterSeconds ?? bodyObj.retry_after ?? undefined;
    const payload: PaywallPayload = {
      reason: 'rate',
      upgradeUrl: bodyObj.upgrade_url,
      feature: bodyObj.feature,
      retry_after: retryAfter,
    };
    eventBus.emit('paywall:rate', payload);
  }

  return error;
}

/**
 * Effectue une requête HTTP avec retry automatique (uniquement GET/HEAD)
 * Jamais de retry sur mutations (POST/PUT/PATCH/DELETE), même avec Idempotency
 */
async function request<T>(
  method: string,
  url: string,
  body?: unknown,
  options: RequestOptions = {}
): Promise<T> {
  const timeoutMs = options.timeoutMs ?? 15000;
  // Jamais de retry sur mutations
  const isMutation = isMutationMethod(method);
  // Ne pas retry pour /v1/billing/checkout même pour GET
  const isBillingCheckout = url.includes('/v1/billing/checkout');
  const isRetryable =
    !isMutation &&
    (method === 'GET' || method === 'HEAD') &&
    !isBillingCheckout;
  const maxRetries = isRetryable && !options.noRetry ? 2 : 0;
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await performRequest<T>(method, url, body, {
        ...options,
        timeoutMs,
      });
    } catch (error) {
      lastError = error as Error;

      // Retry uniquement pour NetworkError (timeout, offline, abort)
      if (error instanceof NetworkError && attempt < maxRetries) {
        // Retry exponentiel simple : 500ms * (2^attempt)
        const delay = 500 * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
        continue;
      }

      // Pas de retry ou erreur non-réessayable
      throw error;
    }
  }

  throw lastError;
}

/**
 * Effectue une requête HTTP unique (sans retry)
 */
async function performRequest<T>(
  method: string,
  url: string,
  body?: unknown,
  options: RequestOptions = {}
): Promise<T> {
  const fullUrl = buildUrl(url);
  const startTime = Date.now();
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(7)}`;

  // Émettre événement start
  eventBus.emit('api:request', {
    id: requestId,
    ts: startTime,
    phase: 'start',
    method,
    url,
    fullUrl,
    headers: options.headers
      ? Object.fromEntries(new Headers(options.headers).entries())
      : undefined,
    body: body != null ? body : undefined,
  });

  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(),
    options.timeoutMs ?? 15000
  );

  // Utiliser le signal personnalisé ou créer un nouveau
  // Note: AbortSignal.any n'est pas disponible partout, on utilise controller.signal si pas de signal personnalisé
  let signal: AbortSignal = controller.signal;
  if (options.signal) {
    // Si un signal personnalisé est fourni, on l'utilise
    // Le timeout controller sera ignoré dans ce cas (l'appelant doit gérer le timeout)
    signal = options.signal;
    // Si le signal personnalisé est aborté, on annule aussi le timeout
    options.signal.addEventListener('abort', () => {
      clearTimeout(timeout);
    });
  }

  try {
    const headers = buildHeaders(method, fullUrl, options, options.headers);

    // Extraire les headers finals pour l'observabilité (exclure Authorization)
    const finalHeaders =
      headers instanceof Headers ? headers : new Headers(headers);
    const headersForObservability: Record<string, string> = {};
    finalHeaders.forEach((value, key) => {
      // Exclure Authorization et autres données sensibles
      if (
        key.toLowerCase() !== 'authorization' &&
        !key.toLowerCase().includes('secret') &&
        !key.toLowerCase().includes('password')
      ) {
        headersForObservability[key] = value;
      }
    });

    const requestInit: RequestInit = {
      method,
      headers,
      signal,
    };

    if (body !== undefined && method !== 'GET' && method !== 'HEAD') {
      requestInit.body = JSON.stringify(body);
    }

    const response = await fetch(fullUrl, requestInit);
    const durationMs = Date.now() - startTime;
    const responseRequestId = extractRequestId(response);

    // Parsing de la réponse
    const data = await parseResponse<T>(response, options.parseAs);

    // Vérification du status
    if (!response.ok) {
      const error = toApiError(response, data, fullUrl);
      // Émettre événement error
      eventBus.emit('api:request', {
        id: requestId,
        ts: startTime,
        phase: 'error',
        method,
        url,
        fullUrl,
        status: error.status,
        requestId: error.requestId ?? responseRequestId,
        durationMs,
        headers: headersForObservability,
      });
      throw error;
    }

    // Émettre événement end (succès)
    eventBus.emit('api:request', {
      id: requestId,
      ts: startTime,
      phase: 'end',
      method,
      url,
      fullUrl,
      status: response.status,
      requestId: responseRequestId,
      durationMs,
      headers: headersForObservability,
    });

    return data;
  } catch (error) {
    const durationMs = Date.now() - startTime;

    // Extraire les headers finals pour l'observabilité (si disponibles)
    // Note: headersForObservability peut ne pas être défini si l'erreur survient avant buildHeaders
    let headersForError: Record<string, string> | undefined;
    try {
      const headers = buildHeaders(method, fullUrl, options, options.headers);
      const finalHeaders =
        headers instanceof Headers ? headers : new Headers(headers);
      headersForError = {};
      finalHeaders.forEach((value, key) => {
        if (
          key.toLowerCase() !== 'authorization' &&
          !key.toLowerCase().includes('secret') &&
          !key.toLowerCase().includes('password')
        ) {
          headersForError![key] = value;
        }
      });
    } catch {
      // Si buildHeaders échoue, on continue sans headers
      headersForError = undefined;
    }

    // Gestion des erreurs réseau
    if (error instanceof ApiError) {
      // Événement error déjà émis dans le bloc if (!response.ok)
      throw error;
    }

    if (
      (error as { name?: string })?.name === 'AbortError' ||
      (error as Error).message.includes('aborted')
    ) {
      const abortedSignal = options.signal?.aborted;
      // Si c'est le timeout controller qui a aborté, c'est un timeout
      const isTimeout = controller.signal.aborted && !abortedSignal;
      const networkError = new NetworkError(
        isTimeout ? 'timeout' : 'aborted',
        isTimeout ? 'Request timeout' : 'Request aborted'
      );
      // Émettre événement error pour NetworkError (status 0)
      eventBus.emit('api:request', {
        id: requestId,
        ts: startTime,
        phase: 'error',
        method,
        url,
        fullUrl,
        status: 0,
        durationMs,
        headers: headersForError,
      });
      throw networkError;
    }

    if (error instanceof TypeError) {
      const networkError = new NetworkError(
        'offline',
        'Network error: offline'
      );
      // Émettre événement error pour NetworkError (status 0)
      eventBus.emit('api:request', {
        id: requestId,
        ts: startTime,
        phase: 'error',
        method,
        url,
        fullUrl,
        status: 0,
        durationMs,
        headers: headersForError,
      });
      throw networkError;
    }

    // Émettre événement error pour erreur inconnue (status 0)
    eventBus.emit('api:request', {
      id: requestId,
      ts: startTime,
      phase: 'error',
      method,
      url,
      fullUrl,
      status: 0,
      durationMs,
      headers: headersForError,
    });

    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Client HTTP avec méthodes standard
 */
export const http = {
  /**
   * GET request
   */
  async get<T>(url: string, options?: RequestOptions): Promise<T> {
    return request<T>('GET', url, undefined, options);
  },

  /**
   * POST request
   */
  async post<T>(
    url: string,
    body?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return request<T>('POST', url, body, options);
  },

  /**
   * PUT request
   */
  async put<T>(
    url: string,
    body?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return request<T>('PUT', url, body, options);
  },

  /**
   * DELETE request
   */
  async del<T>(url: string, options?: RequestOptions): Promise<T> {
    return request<T>('DELETE', url, undefined, options);
  },
};

// Export de l'ancien ApiClient pour compatibilité (peut être supprimé plus tard)
export class ApiClient {
  constructor() {
    // baseURL est déjà configuré globalement via configureHttp
  }

  async get<T>(endpoint: string): Promise<T> {
    return http.get<T>(endpoint);
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return http.post<T>(endpoint, data);
  }
}

export const apiClient = new ApiClient();
