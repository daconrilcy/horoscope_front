import { describe, expect, it } from "vitest"

import { formatCurrencyCents } from "../utils/formatPrice"

describe("formatCurrencyCents", () => {
  it("formats cents with the requested currency and locale", () => {
    expect(formatCurrencyCents(900, "EUR", "fr-FR", { maximumFractionDigits: 0 })).toContain("9")
    expect(formatCurrencyCents(2900, "EUR", "en-US", { maximumFractionDigits: 0 })).toContain("29")
  })

  it("preserves decimal cents when the caller requests them", () => {
    const result = formatCurrencyCents(1299, "EUR", "fr-FR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })

    expect(result).toMatch(/12/)
    expect(result).toMatch(/99/)
  })
})
