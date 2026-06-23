import { useSyncExternalStore } from "react"

export const AUTH_TOKEN_KEY = "access_token_v2"
const LEGACY_AUTH_TOKEN_KEYS = ["access_token"]
const AUTH_TOKEN_EVENT = "auth-token-changed"
const rejectedAccessTokens = new Set<string>()

function emitAuthTokenChanged() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_TOKEN_EVENT))
  }
}

export function setAccessToken(token: string) {
  if (typeof window === "undefined") {
    return
  }
  rejectedAccessTokens.delete(token)
  removeLegacyAccessTokens()
  window.localStorage.setItem(AUTH_TOKEN_KEY, token)
  emitAuthTokenChanged()
}

export function clearAccessToken() {
  if (typeof window === "undefined") {
    return
  }
  window.localStorage.removeItem(AUTH_TOKEN_KEY)
  removeLegacyAccessTokens()
  emitAuthTokenChanged()
}

export function getAccessTokenSnapshot(): string | null {
  if (typeof window === "undefined") {
    return null
  }
  const token = window.localStorage.getItem(AUTH_TOKEN_KEY)
  if (token) {
    return token
  }
  removeLegacyAccessTokens()
  return null
}

function removeLegacyAccessTokens() {
  for (const key of LEGACY_AUTH_TOKEN_KEYS) {
    window.localStorage.removeItem(key)
  }
}

export function markAccessTokenRejected(token: string | null) {
  if (!token) {
    return
  }
  rejectedAccessTokens.add(token)
  if (getAccessTokenSnapshot() === token) {
    clearAccessToken()
  }
}

export function markAuthorizationBearerRejected(authorization: string | null | undefined) {
  if (!authorization?.startsWith("Bearer ")) {
    return
  }
  markAccessTokenRejected(authorization.slice("Bearer ".length).trim())
}

export function parseJwtPayload(token: string | null): Record<string, unknown> | null {
  if (!token) {
    return null
  }
  const parts = token.split(".")
  if (parts.length !== 3) {
    return null
  }
  try {
    const base64Url = parts[1].replace(/-/g, "+").replace(/_/g, "/")
    const padding = "=".repeat((4 - (base64Url.length % 4)) % 4)
    return JSON.parse(atob(`${base64Url}${padding}`)) as Record<string, unknown>
  } catch {
    return null
  }
}

export function getSubjectFromAccessToken(token: string | null): string | null {
  const payload = parseJwtPayload(token)
  return typeof payload?.sub === "string" ? payload.sub : null
}

export function isAccessTokenExpired(token: string | null, skewSeconds = 5): boolean {
  const payload = parseJwtPayload(token)
  if (!payload || typeof payload.exp !== "number") {
    return true
  }
  const nowSeconds = Math.floor(Date.now() / 1000)
  return payload.exp <= nowSeconds + skewSeconds
}

export function hasUsableAccessToken(token: string | null): token is string {
  const payload = parseJwtPayload(token)
  return Boolean(
    token &&
      !rejectedAccessTokens.has(token) &&
      payload &&
      typeof payload.sub === "string" &&
      !isAccessTokenExpired(token),
  )
}

export function getAccessTokenAuthHeader(): Record<string, string> {
  const token = getAccessTokenSnapshot()
  if (!hasUsableAccessToken(token)) {
    if (token) {
      clearAccessToken()
    }
    return {}
  }
  return { Authorization: `Bearer ${token}` }
}

export function useAccessTokenSnapshot(): string | null {
  return useSyncExternalStore(
    (onStoreChange) => {
      if (typeof window === "undefined") {
        return () => undefined
      }
      const notify = () => onStoreChange()
      window.addEventListener("storage", notify)
      window.addEventListener(AUTH_TOKEN_EVENT, notify)
      return () => {
        window.removeEventListener("storage", notify)
        window.removeEventListener(AUTH_TOKEN_EVENT, notify)
      }
    },
    getAccessTokenSnapshot,
    () => null,
  )
}
