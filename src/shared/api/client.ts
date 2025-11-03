import { v4 as uuidv4 } from 'uuid';
import { useAuthStore } from '@/stores/authStore';
import { eventBus } from './eventBus';
import { ApiError, NetworkError, extractRequestId } from './errors';
import type { PaywallPayload } from './types';

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
  if (options.idempotency === true) {
    // Warning en dev si utilisé sur GET
    if (method === 'GET' && import.meta.env.DEV) {
      console.warn('Idempotency-Key on GET: avoid unless you know why.');
    }
    // Injecter uniquement sur mutations
    if (shouldAddIdempotencyKey(method, options.idempotency)) {
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
    return (await response.blob()) as T;
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

  const message =
    (body as { message?: string })?.message ??
    response.statusText ??
    'Unknown error';
  let code: string | undefined;
  let details: unknown;

  // Extraction des détails pour 400/422
  if (status === 400 || status === 422) {
    details =
      (body as { errors?: unknown; details?: unknown })?.errors ||
      (body as { errors?: unknown; details?: unknown })?.details ||
      body;
  }

  // Création de l'erreur
  const error = new ApiError(message, status, code, requestId, details);

  // Mapping des événements selon le status
  if (status === 401) {
    eventBus.emit('unauthorized');
    // Ne pas rediriger si déjà sur /login (éviter les boucles)
    if (onUnauthorized && !url.includes('/login')) {
      onUnauthorized();
    }
  } else if (status === 402) {
    const payload: PaywallPayload = {
      reason: 'plan',
      upgradeUrl: (body as { upgrade_url?: string })?.upgrade_url,
    };
    eventBus.emit('paywall', payload);
  } else if (status === 429) {
    const payload: PaywallPayload = {
      reason: 'rate',
      upgradeUrl: (body as { upgrade_url?: string })?.upgrade_url,
    };
    eventBus.emit('quota', payload);
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

    const requestInit: RequestInit = {
      method,
      headers,
      signal,
    };

    if (body !== undefined && method !== 'GET' && method !== 'HEAD') {
      requestInit.body = JSON.stringify(body);
    }

    const response = await fetch(fullUrl, requestInit);

    // Parsing de la réponse
    const data = await parseResponse<T>(response, options.parseAs);

    // Vérification du status
    if (!response.ok) {
      throw toApiError(response, data, fullUrl);
    }

    return data;
  } catch (error) {
    // Gestion des erreurs réseau
    if (error instanceof ApiError) {
      throw error;
    }

    if (
      (error as { name?: string })?.name === 'AbortError' ||
      (error as Error).message.includes('aborted')
    ) {
      const abortedSignal = options.signal?.aborted;
      // Si c'est le timeout controller qui a aborté, c'est un timeout
      const isTimeout = controller.signal.aborted && !abortedSignal;
      throw new NetworkError(
        isTimeout ? 'timeout' : 'aborted',
        isTimeout ? 'Request timeout' : 'Request aborted'
      );
    }

    if (error instanceof TypeError) {
      throw new NetworkError('offline', 'Network error: offline');
    }

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
