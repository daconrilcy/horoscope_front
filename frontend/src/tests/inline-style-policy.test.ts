// Tests de politique frontend limitant les styles inline aux exceptions exactes.
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
  function toDynamicAllowlistEntry(entry: { file: string; style: string }): string {
    if (entry.style.includes("--period-accent")) return `frontend/src/${entry.file}::--period-accent`
    if (entry.style.includes("--skeleton-gap") || entry.style.includes("groupStyle")) {
      return `frontend/src/${entry.file}::--skeleton-gap`
    }
    if (entry.style.includes("style={style}")) return `frontend/src/${entry.file}::style-prop`
    if (entry.file === "components/TurningPointCard.tsx") return `frontend/src/${entry.file}::badge-color`
    if (entry.style.includes("backgroundColor:")) return `frontend/src/${entry.file}::backgroundColor`
    if (entry.style.includes("background:")) return `frontend/src/${entry.file}::background`
    if (entry.style.includes("width:")) return `frontend/src/${entry.file}::width`
    if (entry.style.includes("left:")) return `frontend/src/${entry.file}::left`
    if (entry.style.includes("color:")) return `frontend/src/${entry.file}::color`

    throw new Error(`Inline style exception without dynamic allowlist mapping: ${entry.file} ${entry.style}`)
  }

  it("documente les exceptions dynamiques avec fichier et cle exacte", () => {
    expect(INLINE_STYLE_DYNAMIC_ALLOWLIST.length).toBeGreaterThan(0)
    for (const entry of INLINE_STYLE_DYNAMIC_ALLOWLIST) {
      expect(entry).toMatch(/^frontend\/src\/.+\.tsx::(?:[a-zA-Z0-9_-]+|--[a-zA-Z0-9_-]+|badge-color|style-prop)$/)
    }
  })

  it("synchronise l'allowlist dynamique avec les exceptions inline exactes", () => {
    const expected = new Set(INLINE_STYLE_EXCEPTIONS.map(toDynamicAllowlistEntry))
    const actual = new Set(INLINE_STYLE_DYNAMIC_ALLOWLIST)

    expect(actual).toEqual(expected)
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
