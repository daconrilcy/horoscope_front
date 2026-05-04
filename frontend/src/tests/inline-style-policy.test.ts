import { describe, expect, it } from "vitest"
import {
  collectInlineStyles,
  extractStyleAttributes,
  readFrontendFile,
  toStableJson,
} from "./design-system-policy"
import { INLINE_STYLE_DYNAMIC_ALLOWLIST, INLINE_STYLE_EXCEPTIONS } from "./inline-style-allowlist"

// Garde les styles statiques dans les fichiers CSS et limite les exceptions dynamiques.
describe("inline-style policy", () => {
  it("documente les exceptions dynamiques avec fichier et cle exacte", () => {
    expect(INLINE_STYLE_DYNAMIC_ALLOWLIST.length).toBeGreaterThan(0)
    for (const entry of INLINE_STYLE_DYNAMIC_ALLOWLIST) {
      expect(entry).toMatch(/^frontend\/src\/.+\.tsx::(?:[a-zA-Z0-9_-]+|--[a-zA-Z0-9_-]+|badge-color|style-prop)$/)
    }
  })

  it("ne conserve plus les styles inline statiques audites dans le lot migre", () => {
    const auditedFiles = [
      "layouts/SettingsLayout.tsx",
      "features/astrologers/components/AstrologerCard.tsx",
      "components/settings/DeleteAccountModal.tsx",
    ]

    for (const file of auditedFiles) {
      expect(extractStyleAttributes(readFrontendFile(file))).toEqual([])
    }
  })

  it("valide chaque attribut style restant contre l'allowlist centrale", () => {
    const remaining = collectInlineStyles()
    const allowed = new Set(INLINE_STYLE_EXCEPTIONS.map(toStableJson))
    const unclassified = remaining.filter((entry) => !allowed.has(toStableJson(entry)))

    expect(remaining.length).toBeGreaterThan(0)
    expect(unclassified).toEqual([])
    expect(remaining.map((entry) => entry.style).join("\n")).not.toContain("fontSize: '2.4rem'")
    expect(remaining.map((entry) => entry.style).join("\n")).not.toContain("fontWeight: 'bold'")
  })
})
