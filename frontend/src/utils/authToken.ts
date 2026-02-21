import { useSyncExternalStore } from "react"

const AUTH_TOKEN_KEY = "access_token"
const AUTH_TOKEN_EVENT = "auth-token-changed"

function emitAuthTokenChanged() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_TOKEN_EVENT))
  }
}

export function setAccessToken(token: string) {
  if (typeof window === "undefined") {
    return
  }
  window.localStorage.setItem(AUTH_TOKEN_KEY, token)
  emitAuthTokenChanged()
}

export function clearAccessToken() {
  if (typeof window === "undefined") {
    return
  }
  window.localStorage.removeItem(AUTH_TOKEN_KEY)
  emitAuthTokenChanged()
}

export function getAccessTokenSnapshot(): string | null {
  if (typeof window === "undefined") {
    return null
  }
  return window.localStorage.getItem(AUTH_TOKEN_KEY)
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

export function getAccessTokenAuthHeader(): Record<string, string> {
  const token = getAccessTokenSnapshot()
  return token ? { Authorization: `Bearer ${token}` } : {}
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
