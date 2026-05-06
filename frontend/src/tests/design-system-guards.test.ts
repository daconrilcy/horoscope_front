import { describe, expect, it } from "vitest"
import {
  collectCssFallbacks,
  extractCssVariableUsages,
  collectInlineStyles,
  extractCssVariableDeclarations,
  hasRegistryMatch,
  listFiles,
  parseRegistryPatterns,
  parseTokenNamespaceRegistry,
  patternMatches,
  readFrontendFile,
  toStableJson,
} from "./design-system-policy"
import { CSS_FALLBACK_EXCEPTIONS, INLINE_STYLE_EXCEPTIONS } from "./design-system-allowlist"
import { INLINE_STYLE_DYNAMIC_ALLOWLIST } from "./inline-style-allowlist"

function normalizeCssValue(value: string): string {
  return value.replace(/\s+/g, " ").trim()
}

function removeCssRange(css: string, start: number, end: number): string {
  return `${css.slice(0, start)}${" ".repeat(end - start)}${css.slice(end)}`
}

function findFlatCssBlock(css: string, selector: string): { body: string; start: number; end: number } {
  const start = css.indexOf(`${selector} {`)
  expect(start).toBeGreaterThanOrEqual(0)

  const bodyStart = css.indexOf("{", start) + 1
  const end = css.indexOf("\n}", bodyStart)
  expect(end).toBeGreaterThan(bodyStart)

  return {
    body: css.slice(bodyStart, end),
    start,
    end: end + "\n}".length,
  }
}

function extractMigratedHelpPageValues(ownerBody: string): string[] {
  const declarations = [...ownerBody.matchAll(/--help-[a-zA-Z0-9_-]+\s*:\s*([\s\S]*?);/g)].map((match) =>
    normalizeCssValue(match[1]),
  )

  return [...new Set(declarations.filter((value) => /rgba?\(|#[a-fA-F0-9]{3,8}\b|gradient\(|^2\.35rem$/.test(value)))]
}

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

  it("bloque la consommation des namespaces page-scoped hors owner", () => {
    const pageScopedNamespaces = parseTokenNamespaceRegistry(readFrontendFile("styles/token-namespace-registry.md"))
      .filter(
        (entry) =>
          entry.owner.startsWith("frontend/src/pages/") &&
          (entry.canonicalTarget.includes("page tokens") || entry.canonicalTarget.includes("page visual roles")),
      )
      .map((entry) => ({
        namespace: entry.namespace,
        owner: entry.owner.replace(/^frontend\/src\//, ""),
      }))

    const violations = listFiles("", ".css").flatMap((file) =>
      extractCssVariableUsages(readFrontendFile(file))
        .filter((usage) =>
          pageScopedNamespaces.some((entry) => file !== entry.owner && patternMatches(entry.namespace, usage)),
        )
        .map((usage) => ({ file, usage })),
    )

    expect(violations).toEqual([])
  })

  it("bloque le retour des namespaces migration-only converges par CS-075", () => {
    const registry = readFrontendFile("styles/token-namespace-registry.md")
    const entries = parseTokenNamespaceRegistry(registry)
    const targetedNamespaces = new Set(["--settings-*", "--profile-*", "--astro-*"])
    const forbiddenClassifications = new Set(["migration-only", "compatibility"])
    const staleDefaultShadowNamespace = "--default_" + "dropshadow"

    const targetedViolations = entries
      .filter((entry) => targetedNamespaces.has(entry.namespace))
      .filter(
        (entry) =>
          forbiddenClassifications.has(entry.status) ||
          /legacy|alias|shim|fallback|compatibility|migration-only/i.test(
            `${entry.owner} ${entry.canonicalTarget} ${entry.exitCondition}`,
          ),
      )

    expect(entries.map((entry) => entry.namespace)).not.toContain(staleDefaultShadowNamespace)
    expect(targetedViolations).toEqual([])
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

  it("bloque le retour des literals prediction premium migres par CS-078", () => {
    const migratedFiles = [
      "pages/DailyHoroscopePage.css",
      "components/prediction/DailyAdviceCard.css",
      "components/prediction/DailyPageHeader.css",
      "components/prediction/DayStateBadge.css",
    ]
    const forbiddenLiterals = [
      /border-radius:\s*50%;/,
      /font-size:\s*(?:11|12|15|18|20|32|40)px;/,
      /font-weight:\s*(?:600|650|700);/,
      /letter-spacing:\s*-0\.0[12]em;/,
      /letter-spacing:\s*0\.06em;/,
      /box-shadow:\s*0\s+(?:8|10)px\s+(?:22|24)px\s+rgba\(76,\s*52,\s*122,\s*0\.08\)/,
      /--(?:glass|text|shadow)-[a-z-]+:\s*(?:#[0-9A-Fa-f]{3,8}|rgba?\()/,
    ]

    for (const file of migratedFiles) {
      const css = readFrontendFile(file)

      for (const literal of forbiddenLiterals) {
        expect(css).not.toMatch(literal)
      }
    }
  })

  it("execute les allowlists exactes inline-style et css-fallback", () => {
    const allowedInline = new Set(INLINE_STYLE_EXCEPTIONS.map(toStableJson))
    const allowedFallbacks = new Set(CSS_FALLBACK_EXCEPTIONS.map(toStableJson))

    expect(collectInlineStyles().filter((entry) => !allowedInline.has(toStableJson(entry)))).toEqual([])
    expect(collectCssFallbacks().filter((entry) => !allowedFallbacks.has(toStableJson(entry)))).toEqual([])
  })

  it("bloque la reintroduction locale des literals HelpPage migres par CS-073", () => {
    const css = readFrontendFile("pages/HelpPage.css")
    const ownerBlock = findFlatCssBlock(css, ":where(.help-page, .help-bg-halo)")
    const subscriptionsStart = css.indexOf("/* --- Help Subscriptions Page")
    expect(subscriptionsStart).toBeGreaterThan(ownerBlock.end)

    const migratedValues = extractMigratedHelpPageValues(ownerBlock.body)
    let guardedCss = removeCssRange(css, ownerBlock.start, ownerBlock.end)
    guardedCss = guardedCss.slice(0, subscriptionsStart)
    const normalizedGuardedCss = normalizeCssValue(guardedCss)

    for (const value of migratedValues) {
      expect(normalizedGuardedCss).not.toContain(value)
    }
    expect(css).toContain("font-size: var(--help-section-heading-size)")
    expect(css).toContain("font-size: clamp(1.7rem, 7vw, var(--help-section-heading-size))")
  })

  it("centralise les exceptions exactes anti-drift", () => {
    expect(INLINE_STYLE_DYNAMIC_ALLOWLIST.length).toBeGreaterThan(0)
    expect(INLINE_STYLE_EXCEPTIONS.length).toBeGreaterThan(0)
    expect(CSS_FALLBACK_EXCEPTIONS.length).toBeGreaterThan(0)
    expect(readFrontendFile("styles/css-fallback-allowlist.md")).toContain("Exit condition")
    expect(readFrontendFile("styles/legacy-style-surface-registry.md")).toContain("Canonical target")
  })
})
