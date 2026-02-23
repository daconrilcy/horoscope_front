import { describe, it, expect } from "vitest"
import { formatDate, formatDateTime } from "../utils/formatDate"

describe("formatDate", () => {
  it("formats valid ISO date string", () => {
    const result = formatDate("2024-06-15T10:30:00Z", "en")
    expect(result).toMatch(/6\/15\/2024|15\/06\/2024/)
  })

  it("formats valid date with different language", () => {
    const resultFr = formatDate("2024-06-15T10:30:00Z", "fr")
    expect(resultFr).toMatch(/15\/06\/2024/)
  })

  it("returns fallback for invalid date string", () => {
    const result = formatDate("not-a-date", "fr")
    expect(result).toBe("—")
  })

  it("returns fallback for empty string", () => {
    const result = formatDate("", "fr")
    expect(result).toBe("—")
  })

  it("uses custom fallback when provided", () => {
    const result = formatDate("invalid", "fr", "N/A")
    expect(result).toBe("N/A")
  })

  it("defaults to French locale", () => {
    const result = formatDate("2024-12-25T00:00:00Z")
    expect(result).toMatch(/25\/12\/2024/)
  })

  it("handles dates with only date part", () => {
    const result = formatDate("2024-01-01", "en")
    expect(result).toBeTruthy()
    expect(result).not.toBe("—")
  })

  it("returns fallback for NaN date (Invalid Date object)", () => {
    const result = formatDate("NaN", "fr")
    expect(result).toBe("—")
  })
})

describe("formatDateTime", () => {
  it("formats valid ISO datetime string with date and time", () => {
    const result = formatDateTime("2024-02-22T10:00:00Z")
    expect(result).toBeTruthy()
    expect(result).not.toBe("—")
    // Should contain both date and time components
    expect(result).toMatch(/\d/)
  })

  it("returns fallback for invalid date string", () => {
    const result = formatDateTime("not-a-date")
    expect(result).toBe("—")
  })

  it("returns fallback for empty string", () => {
    const result = formatDateTime("")
    expect(result).toBe("—")
  })

  it("uses custom fallback when provided", () => {
    const result = formatDateTime("invalid", "N/A")
    expect(result).toBe("N/A")
  })

  it("handles ISO date without time component", () => {
    const result = formatDateTime("2024-06-15")
    expect(result).toBeTruthy()
    expect(result).not.toBe("—")
  })

  it("returns fallback for malformed date like 'undefined'", () => {
    const result = formatDateTime("undefined")
    expect(result).toBe("—")
  })
})
