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
    const forbiddenClassifications = new Set(["migration-only", ["compat", "ibility"].join("")])
    const staleVocabularyPattern = new RegExp(
      ["legacy", "alias", "shim", "fallback", ["compat", "ibility"].join(""), "migration-only"].join("|"),
      "i",
    )
    const staleDefaultShadowNamespace = "--default_" + "dropshadow"

    const targetedViolations = entries
      .filter((entry) => targetedNamespaces.has(entry.namespace))
      .filter(
        (entry) =>
          forbiddenClassifications.has(entry.status) ||
          staleVocabularyPattern.test(`${entry.owner} ${entry.canonicalTarget} ${entry.exitCondition}`),
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

  it("bloque le retour des literals composants UI migres par CS-079", () => {
    const migratedFiles = [
      "components/ui/Badge/Badge.css",
      "components/ui/Badge/Badge.tsx",
      "components/ui/Button/Button.css",
      "components/ui/Card/Card.css",
      "components/ui/EmptyState/EmptyState.css",
      "components/ui/ErrorState/ErrorState.css",
      "components/ui/Field/Field.css",
      "components/ui/LockedSection/LockedSection.css",
      "components/ui/Modal/Modal.css",
      "components/ui/Select/Select.css",
      "components/ui/Skeleton/Skeleton.css",
      "components/ui/Skeleton/Skeleton.tsx",
      "components/ui/UpgradeCTA/UpgradeCTA.css",
      "components/ui/UserAvatar/UserAvatar.css",
      "components/ui/UserMenu/UserMenu.css",
    ]
    const forbiddenLiterals = [
      /var\(--(?:primary|text-[12]|glass(?:-2|-border|-blur)?|error)\)/,
      /var\(\s*--space-2\s*,\s*0\.5rem\s*\)/,
      /#(?:fff|ffffff)\b/i,
      /rgba\(239,\s*68,\s*68,\s*0\.1\)/,
      /rgba\(255,\s*255,\s*255,\s*0\.05\)/,
      /rgba\(0,\s*0,\s*0,\s*0\.5\)/,
      /box-shadow:\s*(?:none|0\s+10px\s+20px\s+rgba\(134,\s*108,\s*208,\s*0\.3\))/,
      /border-radius:\s*(?:50%|16px);/,
      /font-size:\s*(?:0\.75rem|0\.875rem|1\.25rem);/,
      /font-weight:\s*600;/,
      /line-height:\s*(?:1|1\.6);/,
      /letter-spacing:\s*(?:0\.04em|0\.05em);/,
    ]

    for (const file of migratedFiles) {
      const source = readFrontendFile(file)

      for (const literal of forbiddenLiterals) {
        expect(source).not.toMatch(literal)
      }
    }
  })

  it("bloque le retour des surfaces runtime E-009 fermees par CS-080", () => {
    const removedOverallSummary = ["overall", "_", "summary"].join("")
    const removedAstrologerId = ["astrologer", "Id"].join("")
    const removedAspectParser = ["aspect", "Legacy"].join("")
    const forbiddenTerms = [
      ["Deprecated", ":"].join(""),
      ["backwards", " ", "compat", "ibility"].join(""),
      ["backward", " ", "compat", "ibility"].join(""),
      ["legacy", " ", "fallback"].join(""),
      ["Legacy", " ", "codes"].join(""),
      ["aspect", "Legacy"].join(""),
      ["compat", "ibility"].join(""),
    ]
    const files = [".ts", ".tsx", ".md", ".json"].flatMap((extension) => listFiles("", extension))
    const vocabularyViolations = files.flatMap((file) => {
      const source = readFrontendFile(file)
      return forbiddenTerms
        .filter((term) => source.includes(term))
        .map((term) => ({ file, term }))
    })
    const targetedViolations = [
      { file: "pages/ChatPage.tsx", terms: [removedAstrologerId] },
      { file: "utils/dailySummaryHelper.ts", terms: [removedOverallSummary] },
      { file: "components/prediction/DayPredictionCard.tsx", terms: [removedOverallSummary] },
      { file: "types/dailyPrediction.ts", terms: [removedOverallSummary] },
      {
        file: "components/NatalInterpretation.tsx",
        terms: [removedAspectParser, "CONJUNCTION_", "SEXTILE_", "SQUARE_", "TRINE_", "OPPOSITION_"],
      },
    ].flatMap(({ file, terms }) => {
      const source = readFrontendFile(file)
      return terms.filter((term) => source.includes(term)).map((term) => ({ file, term }))
    })
    const predictionRuntimeSource = readFrontendFile("utils/predictionI18n.ts")
    const predictionKeySource = readFrontendFile("i18n/predictions.ts")
    const predictionKeyViolations = [
      "amour",
      "travail",
      "carriere",
      "energie",
      "vitalite",
      "humeur",
      "sante",
      "argent",
      "finances",
      "sexe_intimite",
      "famille_foyer",
      "social_reseau",
      "tendu",
      "neutre",
      "porteur",
      "exact",
      "ingress",
      "station",
      "enter_orb",
      "exit_orb",
      "generic_event",
    ]
      .filter((key) => predictionKeySource.match(new RegExp(`^\\s*${key}:`, "m")))
      .map((term) => ({ file: "i18n/predictions.ts", term }))
    const predictionRuntimeViolations = [
      /eventType\s*===\s*["']exact["']/,
      /^\s*exact:/m,
      /^\s*enter_orb:/m,
      /^\s*exit_orb:/m,
      /^\s*generic_event:/m,
    ]
      .filter((pattern) => pattern.test(predictionRuntimeSource))
      .map((pattern) => ({ file: "utils/predictionI18n.ts", term: String(pattern) }))
    const dailyInsightsSource = readFrontendFile("components/DailyInsightsSection.tsx")

    expect(vocabularyViolations).toEqual([])
    expect(targetedViolations).toEqual([])
    expect(predictionKeyViolations).toEqual([])
    expect(predictionRuntimeViolations).toEqual([])
    expect(dailyInsightsSource).not.toMatch(/^export\s+default/m)
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
