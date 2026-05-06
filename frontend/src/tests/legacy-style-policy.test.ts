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

  it("bloque le retour des aliases de tokens historiques critiques retires par CS-067", () => {
    const registry = readFrontendFile("styles/legacy-style-surface-registry.md")
    const theme = readFrontendFile("styles/theme.css")
    const appCss = readFrontendFile("App.css")

    expect(registry).not.toContain("`--text-*`")
    expect(registry).not.toContain("`--glass*`")
    expect(registry).not.toContain("`--primary*`")
    expect(theme).not.toMatch(/--(?:text-[123]|text-headline|glass(?:-2|-border|-blur|-shortcut|-shortcut-border|-mini|-mini-border)?|primary(?:-strong|-rgb)?)\s*:/)
    expect(appCss).not.toMatch(/var\(--(?:text-[123]|text-headline|glass(?:-2|-border|-blur)?|primary(?:-strong|-rgb)?)\)/)
  })

  it("bloque le retour des selectors legacy admin prompts retires par CS-067", () => {
    const tsx = readFrontendFile("pages/admin/AdminPromptsPage.tsx")
    const css = readFrontendFile("pages/admin/AdminPromptsPage.css")
    const combined = `${tsx}\n${css}`

    expect(combined).not.toContain("admin-prompts-legacy")
    expect(combined).not.toContain("admin-prompts-modal--legacy-rollback")
    expect(tsx).toContain("admin-prompts-archive")
    expect(css).toContain(".admin-prompts-archive")
    expect(tsx).toContain("admin-prompts-modal--rollback")
    expect(css).toContain(".admin-prompts-modal--rollback")
  })
})
