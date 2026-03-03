import { clearAccessToken } from "../utils/authToken"

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001"
const DEFAULT_TIMEOUT_MS = 20000
const configuredTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? DEFAULT_TIMEOUT_MS)
export const API_TIMEOUT_MS = Number.isFinite(configuredTimeout) && configuredTimeout > 0
  ? configuredTimeout
  : DEFAULT_TIMEOUT_MS

export async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS)
  try {
    const response = await fetch(input, {
      ...init,
      signal: controller.signal,
    })
    if (response.status === 401) {
      try {
        const payload = (await response.clone().json()) as {
          error?: { code?: string }
        }
        if (payload?.error?.code === "token_expired") {
          clearAccessToken()
        }
      } catch {
        // ignore non-json 401 responses
      }
    }
    return response
  } finally {
    window.clearTimeout(timeoutId)
  }
}
