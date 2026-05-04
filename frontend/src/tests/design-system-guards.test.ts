import { describe, expect, it } from "vitest"
import {
  collectCssFallbacks,
  collectInlineStyles,
  extractCssVariableDeclarations,
  hasRegistryMatch,
  listFiles,
  parseRegistryPatterns,
  readFrontendFile,
  toStableJson,
} from "./design-system-policy"
import { CSS_FALLBACK_EXCEPTIONS, INLINE_STYLE_EXCEPTIONS } from "./design-system-allowlist"
import { INLINE_STYLE_DYNAMIC_ALLOWLIST } from "./inline-style-allowlist"

// Suite anti-drift qui raccorde les registres design-system aux fichiers reels.
describe("design-system guards", () => {
  it("couvre les namespaces de tokens CSS par le registre CS-026", () => {
    const patterns = parseRegistryPatterns(readFrontendFile("styles/token-namespace-registry.md"))
    const variables = new Set(
      listFiles("", ".css").flatMap((file) => extractCssVariableDeclarations(readFrontendFile(file))),
    )
    const unclassified = [...variables].filter((variable) => !hasRegistryMatch(patterns, variable))

    expect(unclassified).toEqual([])
  })

  it("expose les roles typographiques requis par CS-028", () => {
    const registry = readFrontendFile("styles/typography-roles.md")
    const utilities = readFrontendFile("styles/utilities.css")

    for (const role of ["page-title", "section-title", "card-title", "body", "body-muted", "metadata", "label", "eyebrow", "cta", "numeric"]) {
      expect(registry).toContain(role)
      expect(utilities).toContain(`.type-${role}`)
    }
    expect(readFrontendFile("pages/settings/Settings.css")).toContain("font-size: var(--type-page-title-size)")
  })

  it("execute la garde des literals hardcodes migres par CS-027", () => {
    const migratedFiles = [
      "App.css",
      "pages/admin/AdminPromptsPage.css",
      "pages/HelpPage.css",
      "pages/settings/Settings.css",
      "pages/AstrologerProfilePage.css",
    ]

    for (const file of migratedFiles) {
      const css = readFrontendFile(file)
      expect(css).not.toMatch(/border-radius:\s*999px;/)
      expect(css).not.toMatch(/gap:\s*8px;/)
      expect(css).not.toMatch(/gap:\s*12px;/)
    }
  })

  it("execute les allowlists exactes inline-style et css-fallback", () => {
    const allowedInline = new Set(INLINE_STYLE_EXCEPTIONS.map(toStableJson))
    const allowedFallbacks = new Set(CSS_FALLBACK_EXCEPTIONS.map(toStableJson))

    expect(collectInlineStyles().filter((entry) => !allowedInline.has(toStableJson(entry)))).toEqual([])
    expect(collectCssFallbacks().filter((entry) => !allowedFallbacks.has(toStableJson(entry)))).toEqual([])
  })

  it("centralise les exceptions exactes anti-drift", () => {
    expect(INLINE_STYLE_DYNAMIC_ALLOWLIST.length).toBeGreaterThan(0)
    expect(INLINE_STYLE_EXCEPTIONS.length).toBeGreaterThan(0)
    expect(CSS_FALLBACK_EXCEPTIONS.length).toBeGreaterThan(0)
    expect(readFrontendFile("styles/css-fallback-allowlist.md")).toContain("Exit condition")
    expect(readFrontendFile("styles/legacy-style-surface-registry.md")).toContain("Canonical target")
  })
})
