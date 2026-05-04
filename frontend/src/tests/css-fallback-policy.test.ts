import { describe, expect, it } from "vitest"
import {
  collectCssFallbacks,
  extractCssFallbacks,
  listFiles,
  readFrontendFile,
  toStableJson,
} from "./design-system-policy"
import { CSS_FALLBACK_EXCEPTIONS } from "./design-system-allowlist"

// Garde les fallbacks CSS comme exceptions classees plutot que tokens caches.
describe("css-fallback policy", () => {
  it("declare un registre exact des fallbacks autorises", () => {
    const registry = readFrontendFile("styles/css-fallback-allowlist.md")

    expect(registry).toContain("| File | Token | Literal | Status | Reason | Exit condition |")
    expect(registry).toContain("`--sidebar-width`")
    expect(registry).toContain("`--usage-progress`")
  })

  it("retire les fallbacks des valeurs migrees du lot CS-027", () => {
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

  it("valide chaque fallback CSS restant contre l'allowlist centrale", () => {
    const fallbacks = collectCssFallbacks()
    const allowed = new Set(CSS_FALLBACK_EXCEPTIONS.map(toStableJson))
    const unclassified = fallbacks.filter((entry) => !allowed.has(toStableJson(entry)))

    expect(fallbacks.length).toBeGreaterThan(0)
    expect(unclassified).toEqual([])
  })
})
