// Client HTTP central pour les appels backend et la normalisation minimale des erreurs API.
import { clearAccessToken, markAuthorizationBearerRejected } from "../utils/authToken"

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001"
const DEFAULT_TIMEOUT_MS = 20000
const configuredTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? DEFAULT_TIMEOUT_MS)
export const API_TIMEOUT_MS = Number.isFinite(configuredTimeout) && configuredTimeout > 0
  ? configuredTimeout
  : DEFAULT_TIMEOUT_MS

export type ApiFetchInit = RequestInit & {
  timeoutMs?: number
}

export type ApiErrorEnvelope<TDetails = Record<string, unknown>> = {
  error?: {
    code?: string
    message?: string
    details?: TDetails
    request_id?: string | null
  }
}

export type ApiResponseEnvelope<TData> = {
  data: TData
}

const AUTH_SESSION_ERROR_CODES = new Set([
  "missing_access_token",
  "invalid_token",
  "invalid_token_type",
  "token_expired",
])

type FastApiValidationDetail = {
  msg?: string
}

export type ParsedApiError<TDetails> = {
  code: string
  message: string
  details: TDetails
  requestId: string | null
}

function resolveApiInput(input: RequestInfo | URL): RequestInfo | URL {
  if (typeof input === "string") {
    if (input.startsWith("http://") || input.startsWith("https://")) {
      return input
    }
    if (input.startsWith("/")) {
      return `${API_BASE_URL}${input}`
    }
    return input
  }

  if (input instanceof URL) {
    if (input.protocol === "http:" || input.protocol === "https:") {
      return input
    }
  }

  return input
}

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly requestId?: string;

  constructor(code: string, message: string, status: number, requestId?: string) {
    super(message);
    this.code = code;
    this.status = status;
    this.requestId = requestId;
  }
}

function linkAbortSignal(controller: AbortController, signal: AbortSignal | null | undefined): () => void {
  if (!signal) {
    return () => undefined
  }
  if (signal.aborted) {
    controller.abort()
    return () => undefined
  }
  const abortHandler = () => controller.abort()
  signal.addEventListener("abort", abortHandler, { once: true })
  return () => signal.removeEventListener("abort", abortHandler)
}

function readAuthorizationHeader(headers: HeadersInit | undefined): string | null {
  if (!headers) {
    return null
  }
  if (headers instanceof Headers) {
    return headers.get("Authorization")
  }
  if (Array.isArray(headers)) {
    const authorization = headers.find(([key]) => key.toLowerCase() === "authorization")
    return authorization?.[1] ?? null
  }
  const record = headers as Record<string, string>
  return record.Authorization ?? record.authorization ?? null
}

/** Execute une requete backend avec URL canonique, timeout et propagation auth. */
export async function apiFetch(input: RequestInfo | URL, init: ApiFetchInit = {}): Promise<Response> {
  const controller = new AbortController()
  const { timeoutMs = API_TIMEOUT_MS, signal, ...requestInit } = init
  const unlinkAbortSignal = linkAbortSignal(controller, signal)
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(resolveApiInput(input), {
      ...requestInit,
      signal: controller.signal,
    })
    if (response.status === 401) {
      markAuthorizationBearerRejected(readAuthorizationHeader(requestInit.headers))
      try {
        const payload = (await response.clone().json()) as {
          error?: { code?: string }
        }
        if (payload?.error?.code && AUTH_SESSION_ERROR_CODES.has(payload.error.code)) {
          clearAccessToken()
        }
      } catch {
        // ignore non-json 401 responses
      }
    }
    return response
  } finally {
    window.clearTimeout(timeoutId)
    unlinkAbortSignal()
  }
}

/** Lit une enveloppe d'erreur JSON sans masquer une reponse non JSON. */
export async function readApiErrorEnvelope<TDetails = Record<string, unknown>>(
  response: Response,
): Promise<ApiErrorEnvelope<TDetails> | null> {
  try {
    return (await response.json()) as ApiErrorEnvelope<TDetails>
  } catch {
    return null
  }
}

/** Convertit l'enveloppe d'erreur backend en champs stables pour les wrappers publics. */
export async function parseApiErrorDetails<TDetails>(
  response: Response,
  fallbackDetails: TDetails,
): Promise<ParsedApiError<TDetails>> {
  const payload = await readApiErrorEnvelope<TDetails>(response)
  if (!payload?.error) {
    const raw = payload as Record<string, unknown> | null
    if (Array.isArray(raw?.detail)) {
      const firstDetail = raw.detail[0] as FastApiValidationDetail | undefined
      return {
        code: "unprocessable_entity",
        message: firstDetail?.msg || "Données invalides",
        details: fallbackDetails,
        requestId: null,
      }
    }
  }
  return {
    code: payload?.error?.code ?? "unknown_error",
    message: payload?.error?.message ?? `Request failed with status ${response.status}`,
    details: payload?.error?.details ?? fallbackDetails,
    requestId: payload?.error?.request_id ?? null,
  }
}
