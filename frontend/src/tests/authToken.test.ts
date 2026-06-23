import { afterEach, describe, expect, it } from "vitest"

import {
  AUTH_TOKEN_KEY,
  getAccessTokenSnapshot,
  hasUsableAccessToken,
  isAccessTokenExpired,
  markAuthorizationBearerRejected,
  setAccessToken,
} from "../utils/authToken"

function toBase64Url(value: string): string {
  return btoa(value).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "")
}

function buildJwt(payload: Record<string, unknown>): string {
  const header = toBase64Url(JSON.stringify({ alg: "HS256", typ: "JWT" }))
  const body = toBase64Url(JSON.stringify(payload))
  return `${header}.${body}.sig`
}

afterEach(() => {
  localStorage.clear()
})

describe("isAccessTokenExpired", () => {
  it("stores new sessions under a versioned key and removes the legacy key", () => {
    const token = buildJwt({ sub: "user-1", exp: Math.floor(Date.now() / 1000) + 3600 })
    localStorage.setItem("access_token", "legacy-token")

    setAccessToken(token)

    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBe(token)
    expect(localStorage.getItem("access_token")).toBeNull()
  })

  it("ignores and purges the legacy access token key", () => {
    localStorage.setItem("access_token", "legacy-token")

    expect(getAccessTokenSnapshot()).toBeNull()
    expect(localStorage.getItem("access_token")).toBeNull()
  })

  it("returns true when exp is in the past", () => {
    const token = buildJwt({ exp: Math.floor(Date.now() / 1000) - 60 })
    expect(isAccessTokenExpired(token)).toBe(true)
  })

  it("returns false when exp is in the future", () => {
    const token = buildJwt({ exp: Math.floor(Date.now() / 1000) + 3600 })
    expect(isAccessTokenExpired(token)).toBe(false)
  })

  it("returns true when token has no exp", () => {
    const token = buildJwt({ sub: "user-1" })
    expect(isAccessTokenExpired(token)).toBe(true)
  })

  it("rejects malformed or incomplete tokens as unusable", () => {
    expect(hasUsableAccessToken("not-a-jwt")).toBe(false)
    expect(hasUsableAccessToken(buildJwt({ sub: "user-1" }))).toBe(false)
    expect(hasUsableAccessToken(buildJwt({ exp: Math.floor(Date.now() / 1000) + 3600 }))).toBe(false)
  })

  it("accepts a decodable unexpired subject token", () => {
    const token = buildJwt({ sub: "user-1", exp: Math.floor(Date.now() / 1000) + 3600 })
    setAccessToken(token)
    expect(hasUsableAccessToken(token)).toBe(true)
  })

  it("marks a backend-rejected bearer as unusable and clears the stored session", () => {
    const token = buildJwt({ sub: "user-1", exp: Math.floor(Date.now() / 1000) + 3600 })
    setAccessToken(token)

    markAuthorizationBearerRejected(`Bearer ${token}`)

    expect(hasUsableAccessToken(token)).toBe(false)
    expect(localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull()
  })
})
