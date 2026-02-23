import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"
import { generateUniqueId } from "../utils/generateUniqueId"

describe("generateUniqueId", () => {
  it("generates unique IDs", () => {
    const id1 = generateUniqueId()
    const id2 = generateUniqueId()
    expect(id1).not.toBe(id2)
  })

  it("uses default 'consultation' prefix", () => {
    const id = generateUniqueId()
    expect(id.startsWith("consultation-")).toBe(true)
  })

  it("uses custom prefix when provided", () => {
    const id = generateUniqueId("custom")
    expect(id.startsWith("custom-")).toBe(true)
  })

  it("generates ID with UUID format when crypto.randomUUID is available", () => {
    const id = generateUniqueId()
    expect(id.length).toBeGreaterThan(20)
  })

  describe("fallback when crypto.randomUUID is unavailable", () => {
    const originalRandomUUID = crypto.randomUUID

    beforeEach(() => {
      vi.stubGlobal("crypto", { ...crypto, randomUUID: undefined })
    })

    afterEach(() => {
      vi.stubGlobal("crypto", { ...crypto, randomUUID: originalRandomUUID })
    })

    it("generates valid fallback format without crypto.randomUUID", () => {
      const fallbackPattern = /^consultation-\d+-[a-z0-9]+$/
      const id = generateUniqueId()
      expect(fallbackPattern.test(id)).toBe(true)
    })

    it("generates unique fallback IDs", () => {
      const id1 = generateUniqueId()
      const id2 = generateUniqueId()
      expect(id1).not.toBe(id2)
    })

    it("uses custom prefix in fallback mode", () => {
      const id = generateUniqueId("test")
      expect(id.startsWith("test-")).toBe(true)
    })
  })
})
