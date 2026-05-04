import { describe, expect, it } from "vitest"
import {
  extractLegacySelectors,
  hasRegistryMatch,
  listFiles,
  parseRegistryPatterns,
  readFrontendFile,
} from "./design-system-policy"

// Garde les selecteurs et aliases legacy classes par owner.
describe("legacy-style policy", () => {
  it("classe chaque famille de selecteurs legacy detectee", () => {
    const patterns = parseRegistryPatterns(readFrontendFile("styles/legacy-style-surface-registry.md"))
    const legacySelectors = new Set(
      listFiles("", ".css").flatMap((file) => extractLegacySelectors(readFrontendFile(file))),
    )

    for (const selector of legacySelectors) {
      expect(hasRegistryMatch(patterns, `${selector}*`) || hasRegistryMatch(patterns, selector)).toBe(true)
    }
  })

  it("classe les aliases de tokens historiques critiques", () => {
    const registry = readFrontendFile("styles/legacy-style-surface-registry.md")

    expect(registry).toContain("`--text-*`")
    expect(registry).toContain("`--glass*`")
    expect(registry).toContain("`--primary*`")
  })
})
