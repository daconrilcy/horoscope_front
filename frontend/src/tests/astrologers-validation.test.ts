import { describe, expect, it } from "vitest"
import { isValidAstrologerId } from "../api/astrologers"

describe("isValidAstrologerId", () => {
  it("rejects empty string", () => {
    expect(isValidAstrologerId("")).toBe(false)
  })

  it("rejects IDs with special characters", () => {
    expect(isValidAstrologerId("id&param=test")).toBe(false)
    expect(isValidAstrologerId("id<script>")).toBe(false)
    expect(isValidAstrologerId("id with spaces")).toBe(false)
    expect(isValidAstrologerId("id/path")).toBe(false)
  })

  it("rejects IDs longer than 64 characters", () => {
    const longId = "a".repeat(65)
    expect(isValidAstrologerId(longId)).toBe(false)
  })

  it("accepts valid IDs with alphanumeric, underscore, and hyphen", () => {
    expect(isValidAstrologerId("astro-42")).toBe(true)
    expect(isValidAstrologerId("astro_expert_42")).toBe(true)
    expect(isValidAstrologerId("1")).toBe(true)
    expect(isValidAstrologerId("a".repeat(64))).toBe(true)
  })
})
