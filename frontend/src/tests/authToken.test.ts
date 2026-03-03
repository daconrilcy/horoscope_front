import { describe, expect, it } from "vitest"

import { isAccessTokenExpired } from "../utils/authToken"

function toBase64Url(value: string): string {
  return btoa(value).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "")
}

function buildJwt(payload: Record<string, unknown>): string {
  const header = toBase64Url(JSON.stringify({ alg: "HS256", typ: "JWT" }))
  const body = toBase64Url(JSON.stringify(payload))
  return `${header}.${body}.sig`
}

describe("isAccessTokenExpired", () => {
  it("returns true when exp is in the past", () => {
    const token = buildJwt({ exp: Math.floor(Date.now() / 1000) - 60 })
    expect(isAccessTokenExpired(token)).toBe(true)
  })

  it("returns false when exp is in the future", () => {
    const token = buildJwt({ exp: Math.floor(Date.now() / 1000) + 3600 })
    expect(isAccessTokenExpired(token)).toBe(false)
  })

  it("returns false when token has no exp", () => {
    const token = buildJwt({ sub: "user-1" })
    expect(isAccessTokenExpired(token)).toBe(false)
  })
})
