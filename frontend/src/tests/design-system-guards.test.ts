// Gardes statiques du design-system et des primitives CSS actives.
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
  readAppCssSurface,
  APP_CSS_MODULE_FILES,
  toStableJson,
} from "./design-system-policy"
import {
  APP_CSS_ACCEPTED_PREFIXES,
  APP_CSS_SPECIFICITY_EXCEPTIONS,
  CSS_FALLBACK_EXCEPTIONS,
  INLINE_STYLE_EXCEPTIONS,
} from "./design-system-allowlist"
import { INLINE_STYLE_DYNAMIC_ALLOWLIST } from "./inline-style-allowlist"

function normalizeCssValue(value: string): string {
  return value.replace(/\s+/g, " ").trim()
}

function removeCssRange(css: string, start: number, end: number): string {
  return `${css.slice(0, start)}${" ".repeat(end - start)}${css.slice(end)}`
}

function findFlatCssBlock(css: string, selector: string): { body: string; start: number; end: number } {
  const match = new RegExp(`(^|\\n)${selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")} \\{`).exec(css)
  const start = match === null ? -1 : match.index + match[1].length
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

function extractMigratedHelpSubscriptionsValues(ownerBody: string): string[] {
  const declarations = [...ownerBody.matchAll(/--help-subscriptions-[a-zA-Z0-9_-]+\s*:\s*([\s\S]*?);/g)].map(
    (match) => normalizeCssValue(match[1]),
  )
  const atomicLiterals = declarations.flatMap((value) => [
    ...value.matchAll(/#[a-fA-F0-9]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)/g),
  ])

  return [
    ...new Set(
      [
        ...atomicLiterals.map((match) => normalizeCssValue(match[0])),
        ...declarations.filter((value) =>
          /rgba?\(|hsla?\(|#[a-fA-F0-9]{3,8}\b|gradient\(|clamp\(|^\d+(?:\.\d+)?(?:rem|em)$/.test(value),
        ),
      ],
    ),
  ]
}

function extractMigratedChatValues(ownerBody: string): string[] {
  const declarations = [...ownerBody.matchAll(/--chat-[a-zA-Z0-9_-]+\s*:\s*([\s\S]*?);/g)].map((match) =>
    normalizeCssValue(match[1]),
  )

  return [
    ...new Set(
      declarations.filter((value) => /rgba?\(|#[a-fA-F0-9]{3,8}\b|gradient\(/.test(value)),
    ),
  ]
}

function extractSelectedAppValues(ownerBody: string): string[] {
  const guardedVariables = new Set([
    "--app-button-shadow",
    "--app-button-hover-shadow",
    "--app-button-bg",
    "--app-summary-panel-bg",
    "--app-summary-panel-shadow",
    "--app-summary-panel-pill-bg",
    "--app-summary-panel-pill-shadow",
    "--app-summary-panel-glow",
    "--app-summary-panel-line",
    "--app-summary-panel-action-bg",
    "--app-summary-panel-action-shadow",
  ])
  const declarations = [...ownerBody.matchAll(/(--app-[a-zA-Z0-9_-]+)\s*:\s*([\s\S]*?);/g)]
    .filter((match) => guardedVariables.has(match[1]))
    .map((match) => normalizeCssValue(match[2]))

  return [...new Set(declarations)]
}

type CssDeclaration = {
  selector: string
  property: string
  value: string
}

type CssSyntaxIssue = {
  file: string
  selector: string
  property: string
  value: string
  issue: string
}

type LayoutWidthViolation = {
  file: string
  selector: string
  property: string
  value: string
}

type PageBackgroundViolation = {
  file: string
  selector: string
  property: string
  value: string
}

type LandingOwnerRoute = {
  owner: string
  declarations: Array<{
    file: string
    selectors: readonly string[]
  }>
}

type LandingVisualComplexityException = {
  file: string
  selector: string
  property: "animation" | "filter" | "backdrop-filter" | "-webkit-backdrop-filter"
  value: string
  reason: string
  exitCondition: string
}

const PAGE_BACKGROUND_SELECTORS = [
  ".landing-layout",
  ".people-page",
  ".premium-page-layout",
  ".daily-layout::before",
  ".daily-layout::after",
  ".daily-layout__bg-halo-3",
  ".daily-layout__noise",
  ".profile-bg-halo",
  ".profile-noise",
  ".result-bg-halo",
  ".result-noise",
  ".chat-page-container__bg-halo",
  ".chat-page-container__noise",
  ".natal-page-container__bg-halo",
  ".natal-page-container__noise",
  ".settings-bg-halo",
  ".settings-noise",
  ".help-bg-halo",
  ".help-noise",
] as const

const PAGE_BACKGROUND_CUSTOM_PROPERTIES = new Set([
  "--landing-page-atmosphere",
  "--app-premium-page-layout-background",
  "--app-astro-catalog-page-bg",
  "--app-astro-catalog-atmosphere",
  "--premium-daily-page-bg",
  "--premium-daily-bg-atmosphere",
  "--premium-daily-bg-depth",
  "--settings-page-bg",
  "--help-bg-halo",
  "--chat-bg-halo",
])

const CANONICAL_PAGE_BACKGROUND_VALUES = new Set([
  "var(--premium-app-bg)",
  "var(--premium-app-bg-atmosphere)",
  "var(--premium-noise-image)",
  "var(--app-premium-page-layout-background)",
  "var(--app-astro-catalog-page-bg)",
  "var(--app-astro-catalog-atmosphere)",
  "transparent",
  "none",
])

const LANDING_OWNER_GROUPS = new Map<string, LandingOwnerRoute>([
  ["accent", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout", ".dark .landing-layout"] }],
  }],
  ["contract", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout", ".dark .landing-layout"] }],
  }],
  ["compact", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout"] }],
  }],
  ["cta", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout"] }],
  }],
  ["footer", {
    owner: "footer",
    declarations: [{ file: "pages/landing/sections/LandingFooter.css", selectors: [".landing-footer"] }],
  }],
  ["hero", {
    owner: "hero",
    declarations: [{ file: "pages/landing/LandingPage.css", selectors: [".landing-page", ".dark .landing-page"] }],
  }],
  ["icon", {
    owner: "sections",
    declarations: [{ file: "pages/landing/sections/ProblemSection.css", selectors: [".problem-section"] }],
  }],
  ["language", {
    owner: "navigation",
    declarations: [{ file: "pages/landing/sections/LandingNavbar.css", selectors: [".landing-navbar", ".dark .landing-navbar"] }],
  }],
  ["live", {
    owner: "hero",
    declarations: [{ file: "pages/landing/LandingPage.css", selectors: [".landing-page"] }],
  }],
  ["mobile", {
    owner: "navigation",
    declarations: [{ file: "pages/landing/sections/LandingNavbar.css", selectors: [".landing-navbar", ".dark .landing-navbar"] }],
  }],
  ["navbar", {
    owner: "navigation",
    declarations: [{ file: "pages/landing/sections/LandingNavbar.css", selectors: [".landing-navbar", ".dark .landing-navbar"] }],
  }],
  ["overlay", {
    owner: "navigation",
    declarations: [{ file: "pages/landing/sections/LandingNavbar.css", selectors: [".landing-navbar"] }],
  }],
  ["page", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout", ".dark .landing-layout"] }],
  }],
  ["problem", {
    owner: "sections",
    declarations: [{ file: "pages/landing/sections/ProblemSection.css", selectors: [".problem-section"] }],
  }],
  ["radius", {
    owner: "layout",
    declarations: [
      { file: "layouts/LandingLayout.css", selectors: [".landing-layout"] },
      { file: "pages/landing/sections/LandingNavbar.css", selectors: [".landing-navbar"] },
    ],
  }],
  ["rating", {
    owner: "sections",
    declarations: [{ file: "pages/landing/sections/TestimonialsSection.css", selectors: [".testimonials-section"] }],
  }],
  ["shadow", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout"] }],
  }],
  ["soft", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout"] }],
  }],
  ["surface", {
    owner: "layout",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout", ".dark .landing-layout"] }],
  }],
  ["text", {
    owner: "footer",
    declarations: [{ file: "pages/landing/sections/LandingFooter.css", selectors: [".landing-footer"] }],
  }],
  ["type", {
    owner: "typography",
    declarations: [{ file: "layouts/LandingLayout.css", selectors: [".landing-layout"] }],
  }],
])

const FORBIDDEN_LANDING_OWNER_GROUPS = new Set(["misc", "common", "temp", "shared", "base", "general", "global"])

const LANDING_VISUAL_COMPLEXITY_EXCEPTIONS: LandingVisualComplexityException[] = [
  {
    file: "pages/landing/sections/LandingNavbar.css",
    selector: ".landing-navbar__shell",
    property: "backdrop-filter",
    value: "blur(14px)",
    reason: "Conserve la separation glass du header sticky au-dessus du contenu.",
    exitCondition: "A retirer si le header adopte une surface opaque sans effet glass.",
  },
  {
    file: "pages/landing/sections/LandingNavbar.css",
    selector: ".landing-navbar__mobile-menu",
    property: "backdrop-filter",
    value: "blur(6px)",
    reason: "Conserve une separation legere du menu mobile apres reduction du glow dominant.",
    exitCondition: "A retirer si le panneau mobile devient pleine page opaque.",
  },
]

function findSelectorBeforeBrace(css: string, braceIndex: number): string {
  let cursor = braceIndex - 1
  while (cursor >= 0 && /\s/.test(css[cursor])) {
    cursor -= 1
  }

  const end = cursor + 1
  while (cursor >= 0 && css[cursor] !== "}" && css[cursor] !== "{") {
    cursor -= 1
  }

  return css.slice(cursor + 1, end).trim()
}

function collectCssDeclarations(css: string): CssDeclaration[] {
  const declarations: CssDeclaration[] = []
  const selectorStack: string[] = []
  let cursor = 0

  while (cursor < css.length) {
    const current = css[cursor]
    if (current === "/" && css[cursor + 1] === "*") {
      const commentEnd = css.indexOf("*/", cursor + 2)
      cursor = commentEnd === -1 ? css.length : commentEnd + 2
      continue
    }

    if (current === "{") {
      selectorStack.push(findSelectorBeforeBrace(css, cursor))
      cursor += 1
      continue
    }

    if (current === "}") {
      selectorStack.pop()
      cursor += 1
      continue
    }

    if (current === ":" && selectorStack.length > 0) {
      let propertyStart = cursor - 1
      while (propertyStart >= 0 && /[a-zA-Z0-9_-]/.test(css[propertyStart])) {
        propertyStart -= 1
      }

      const property = css.slice(propertyStart + 1, cursor)
      let valueEnd = cursor + 1
      let depth = 0
      let quote: string | null = null

      while (valueEnd < css.length) {
        const char = css[valueEnd]
        if (quote !== null) {
          if (char === "\\") {
            valueEnd += 2
            continue
          }
          if (char === quote) {
            quote = null
          }
          valueEnd += 1
          continue
        }

        if (char === "\"" || char === "'") {
          quote = char
          valueEnd += 1
          continue
        }
        if (char === "(") {
          depth += 1
        } else if (char === ")") {
          depth = Math.max(0, depth - 1)
        } else if ((char === ";" || char === "}") && depth === 0) {
          break
        }
        valueEnd += 1
      }

      if (css[valueEnd] === ";") {
        declarations.push({
          selector: selectorStack[selectorStack.length - 1],
          property: property.trim(),
          value: normalizeCssValue(css.slice(cursor + 1, valueEnd)),
        })
        cursor = valueEnd + 1
        continue
      }
    }

    cursor += 1
  }

  return declarations
}

function extractLandingGroup(property: string): string | null {
  const match = /^--landing-([a-zA-Z0-9]+)(?:-[a-zA-Z0-9_-]+)?$/.exec(property)

  return match?.[1] ?? null
}

function normalizeLandingDeclarationSelector(selector: string): string {
  return normalizeCssValue(selector.replace(/\/\*[\s\S]*?\*\//g, ""))
}

function isLandingDeclarationAllowed(route: LandingOwnerRoute, file: string, selector: string): boolean {
  const normalizedSelector = normalizeLandingDeclarationSelector(selector)

  return route.declarations.some((declarationOwner) =>
    declarationOwner.file === file && declarationOwner.selectors.includes(normalizedSelector),
  )
}

function collectLandingConsumerGroups(files: string[]): string[] {
  const declarationPattern = /--landing-[a-zA-Z0-9_-]+\s*:/g

  return [
    ...new Set(
      files.flatMap((file) => {
        const sourceWithoutDeclarations = readFrontendFile(file).replace(declarationPattern, "")

        return [...sourceWithoutDeclarations.matchAll(/var\(\s*--landing-([a-zA-Z0-9]+)(?:-[a-zA-Z0-9_-]+)?/g)]
          .map((match) => match[1])
      }),
    ),
  ].sort()
}

function collectLandingVisualComplexityDeclarations(): Array<CssDeclaration & { file: string }> {
  const files = [
    "layouts/LandingLayout.css",
    ...listFiles("pages/landing", ".css"),
  ]

  return files.flatMap((file) =>
    collectCssDeclarations(readFrontendFile(file))
      .filter((declaration) =>
        declaration.property === "animation" ||
        declaration.property === "filter" ||
        declaration.property === "backdrop-filter" ||
        declaration.property === "-webkit-backdrop-filter",
      )
      .filter((declaration) => declaration.value !== "none !important")
      .map((declaration) => ({ ...declaration, file })),
  )
}

function collectLandingVisualComplexityViolations(): Array<CssDeclaration & { file: string }> {
  const allowed = new Set(
    LANDING_VISUAL_COMPLEXITY_EXCEPTIONS.map((entry) =>
      toStableJson({
        file: entry.file,
        selector: entry.selector,
        property: entry.property,
        value: entry.value,
      }),
    ),
  )

  return collectLandingVisualComplexityDeclarations().filter((declaration) =>
    !allowed.has(toStableJson({
      file: declaration.file,
      selector: normalizeLandingDeclarationSelector(declaration.selector),
      property: declaration.property,
      value: declaration.value,
    })),
  )
}

function selectorMatchesExactPageBackground(selector: string, pageBackgroundSelector: string): boolean {
  return selector.split(",").some((part) => {
    const normalizedSelector = normalizeCssValue(part)

    return normalizedSelector === pageBackgroundSelector || normalizedSelector.endsWith(` ${pageBackgroundSelector}`)
  })
}

function validateCssValueDelimiters(value: string): string | null {
  const stack: string[] = []
  const pairs: Record<string, string> = {
    "(": ")",
    "[": "]",
  }
  let quote: string | null = null

  for (let index = 0; index < value.length; index += 1) {
    const char = value[index]
    if (quote !== null) {
      if (char === "\\") {
        index += 1
        continue
      }
      if (char === quote) {
        quote = null
      }
      continue
    }

    if (char === "\"" || char === "'") {
      quote = char
      continue
    }
    if (char in pairs) {
      stack.push(pairs[char])
      continue
    }
    if (char === ")" || char === "]") {
      const expected = stack.pop()
      if (expected !== char) {
        return `unexpected ${char}`
      }
    }
  }

  if (quote !== null) {
    return "unterminated string"
  }

  const expected = stack.pop()
  return expected === undefined ? null : `missing ${expected}`
}

function collectCssSyntaxIssues(files: string[]): CssSyntaxIssue[] {
  return files.flatMap((file) =>
    collectCssDeclarations(readFrontendFile(file)).flatMap((declaration) => {
      const issue = validateCssValueDelimiters(declaration.value)

      return issue === null
        ? []
        : [{
            file,
            selector: declaration.selector,
            property: declaration.property,
            value: declaration.value,
            issue,
          }]
    }),
  )
}

function collectNonAdminPageLevelWidthViolations(): LayoutWidthViolation[] {
  const excludedPrefixes = ["pages/admin/", "pages/landing/"]
  const scannedFiles = Array.from(new Set([
    "styles/design-tokens.css",
    "styles/backgrounds.css",
    ...APP_CSS_MODULE_FILES,
    "layouts/PageLayout.css",
    ...listFiles("pages", ".css").filter((file) =>
      !excludedPrefixes.some((prefix) => file.startsWith(prefix)),
    ),
  ]))

  return scannedFiles.flatMap((file) =>
    collectCssDeclarations(readFrontendFile(file)).flatMap((declaration) => {
      const property = declaration.property
      const value = declaration.value
      const selector = declaration.selector
      const isCanonicalOwner = [
        "styles/design-tokens.css",
        "styles/backgrounds.css",
        "styles/app/layout.css",
        "layouts/PageLayout.css",
      ].includes(file)
      const redefinesLayoutToken =
        property === "--layout-max-width" ||
        (property === "--layout-page-max-width" && file !== "styles/design-tokens.css")
      const bypassesCanonicalContainer =
        selector.includes(".app-bg-container:has") ||
        /max-width:\s*none\s*!important/.test(`${property}: ${value}`)
      const hidesHorizontalOverflow = property === "overflow-x" && value === "hidden"
      const usesLocalPageCap =
        property === "max-width" &&
        (/^(?:900px|1100px|1200px)$/.test(value) ||
          (selector.includes(".page-layout") && file !== "layouts/PageLayout.css") ||
          value.includes("--layout-max-width") ||
          (value.includes("--layout-page-max-width") && !isCanonicalOwner))

      return redefinesLayoutToken || bypassesCanonicalContainer || hidesHorizontalOverflow || usesLocalPageCap
        ? [{ file, selector, property, value }]
        : []
    }),
  )
}

function collectPageBackgroundViolations(): PageBackgroundViolation[] {
  const scannedFiles = Array.from(new Set([
    "styles/premium-theme.css",
    "styles/backgrounds.css",
    "styles/app/tokens.css",
    "styles/app/cards.css",
    "layouts/LandingLayout.css",
    ...listFiles("pages", ".css"),
  ]))

  return scannedFiles.flatMap((file) =>
    collectCssDeclarations(readFrontendFile(file)).flatMap((declaration) => {
      const selectorOwnsPageBackground = PAGE_BACKGROUND_SELECTORS.some((selector) =>
        selectorMatchesExactPageBackground(declaration.selector, selector),
      )
      const isPageBackgroundProperty =
        selectorOwnsPageBackground &&
        (declaration.property === "background" || declaration.property === "background-image")
      const isPageBackgroundToken = PAGE_BACKGROUND_CUSTOM_PROPERTIES.has(declaration.property)

      if (!isPageBackgroundProperty && !isPageBackgroundToken) {
        return []
      }

      return CANONICAL_PAGE_BACKGROUND_VALUES.has(declaration.value)
        ? []
        : [{ file, selector: declaration.selector, property: declaration.property, value: declaration.value }]
    }),
  )
}

function isForbiddenAppLiteralDeclaration(declaration: CssDeclaration): boolean {
  const property = declaration.property.toLowerCase()
  if (declaration.selector === "#root" || property.startsWith("--")) {
    return false
  }

  const value = declaration.value
  if (declaration.selector === ".usage-progress-fill" && property === "width") {
    return value !== "calc(var(--usage-progress, 0) * 1%)"
  }
  if (["font-size", "font-weight", "line-height", "letter-spacing"].includes(property)) {
    return !value.startsWith("var(")
  }
  if (["border-radius", "box-shadow", "text-shadow"].includes(property)) {
    return !/^(?:var\(|none(?:\s*!important)?|inherit)/.test(value)
  }

  return /#[0-9A-Fa-f]{3,8}\b|rgba?\(|hsla?\(|(?:linear|radial)-gradient\(|color-mix\(|var\(\s*--[a-zA-Z0-9_-]+\s*,/.test(value)
}

function isPremiumSharedVisualLiteralOrFallback(value: string): boolean {
  if (/var\(\s*--[a-zA-Z0-9_-]+\s*,/.test(value)) {
    return true
  }
  if (/#[0-9A-Fa-f]{3,8}\b|rgba?\(|hsla?\(|(?:linear|radial)-gradient\(/.test(value)) {
    return true
  }

  return false
}

function isForbiddenPremiumSharedDeclaration(file: string, declaration: CssDeclaration): boolean {
  const property = declaration.property
  const value = declaration.value

  if (property.startsWith("--")) {
    if (property.startsWith("--glass-")) {
      return file !== "styles/glass.css"
    }

    return isPremiumSharedVisualLiteralOrFallback(value)
  }

  if (isPremiumSharedVisualLiteralOrFallback(value)) {
    return true
  }
  if (["box-shadow", "text-shadow", "border-radius", "filter", "backdrop-filter", "-webkit-backdrop-filter"].includes(property)) {
    return !/^(?:var\(|none|inherit)/.test(value)
  }

  return false
}

function hasRepeatedNameSegment(name: string): boolean {
  const segments = name.replace(/^--app-/, "").split("-")

  for (let size = 2; size <= 4; size += 1) {
    const seen = new Set<string>()
    for (let index = 0; index <= segments.length - size; index += 1) {
      const segment = segments.slice(index, index + size).join("-")
      if (seen.has(segment)) {
        return true
      }
      seen.add(segment)
    }
  }

  return false
}

function isMechanicalAppCustomPropertyName(name: string): boolean {
  return name.includes("__") || hasRepeatedNameSegment(name)
}

function isAppSpecificName(name: string): boolean {
  return /(?:astrolog|consult|dashboard|settings|wizard|expert|session|preferences|overview)/i.test(name)
}

function collectAppClassSelectors(css: string): string[] {
  return [
    ...new Set(
      [...css.matchAll(/\.([_a-zA-Z][a-zA-Z0-9_-]*)/g)]
        .map((match) => match[1])
        .filter((name) => isAppSpecificName(name) && !name.startsWith("app-")),
    ),
  ].sort()
}

function collectAppSpecificCustomProperties(ownerBody: string): string[] {
  return [
    ...new Set(
      [...ownerBody.matchAll(/(--app-[a-zA-Z0-9_-]+)\s*:/g)]
        .map((match) => match[1])
        .filter(isAppSpecificName),
    ),
  ].sort()
}

function collectAppCustomPropertyPrefixes(css: string): string[] {
  return [
    ...new Set(
      [...css.matchAll(/--app-([a-zA-Z0-9]+)(?:-[a-zA-Z0-9_-]*)?\s*:/g)]
        .map((match) => match[1]),
    ),
  ].sort()
}

function collectPrecisionEvidenceAppCssHits(appCss: string): string[] {
  return [...appCss.matchAll(/(?:--app-(?:precision|evidence)-[a-zA-Z0-9_-]+|\.(?:precision-badge|evidence-tags|evidence-pill)[a-zA-Z0-9_-]*)/g)]
    .map((match) => match[0])
}

function collectLegacyPrecisionEvidenceCssHits(): Array<{ file: string; selector: string }> {
  const forbiddenSelectorPattern =
    /\.(?:precision-badge(?:--[a-zA-Z0-9_-]+)?|evidence-tags(?:__[a-zA-Z0-9_-]+)?|evidence-pill(?:__[a-zA-Z0-9_-]+|--[a-zA-Z0-9_-]+)?)(?![a-zA-Z0-9_-])/g

  return listFiles("", ".css").flatMap((file) =>
    [...readFrontendFile(file).matchAll(forbiddenSelectorPattern)]
      .map((match) => ({ file, selector: match[0] })),
  )
}

function extractMigratedSettingsValues(ownerBody: string): string[] {
  const declarations = [...ownerBody.matchAll(/--settings-[a-zA-Z0-9_-]+\s*:\s*([\s\S]*?);/g)].map((match) =>
    normalizeCssValue(match[1]),
  )

  return [
    ...new Set(
      declarations.filter((value) =>
        /rgba?\(|#[a-fA-F0-9]{3,8}\b|gradient\(|clamp\(/.test(value),
      ),
    ),
  ]
}

function extractMigratedLandingValues(ownerBody: string): string[] {
  const declarations = [...ownerBody.matchAll(/--landing-[a-zA-Z0-9_-]+\s*:\s*([\s\S]*?);/g)].map((match) =>
    normalizeCssValue(match[1]),
  )

  return [
    ...new Set(
      declarations.filter((value) =>
        /rgba?\(|#[a-fA-F0-9]{3,8}\b|gradient\(|clamp\(/.test(value),
      ),
    ),
  ]
}

function collectAdminCssCluster(): Array<{ file: string; source: string }> {
  return [
    "layouts/AdminLayout.css",
    ...listFiles("pages/admin", ".css"),
  ].map((file) => ({
    file,
    source: readFrontendFile(file),
  }))
}

function collectResidualCssTokenCluster(): Array<{ file: string; source: string }> {
  return [
    "app/guards/AdminGuard.css",
    "components/astro/AstroMoodBackground.css",
    "components/AstroDailyEvents.css",
    "components/AstroFoundationSection.css",
    "components/BestWindowCard.css",
    "components/DayClimateHero.css",
    "components/DomainRankingCard.css",
    "components/ErrorBoundary/ErrorBoundary.css",
    "layouts/components/Header.css",
    "layouts/components/Sidebar.css",
    "features/natal-chart/NatalInterpretation.css",
    "components/prediction/DayTimelineSectionV4.css",
    "components/prediction/KeyPointCard.css",
    "pages/settings/components/DeleteAccountModal.css",
    "components/ShortcutCard.css",
    "features/auth/SignUpForm.css",
    "components/TurningPointCard.css",
    "index.css",
    "layouts/AdminLayout.css",
    "layouts/PageLayout.css",
    "layouts/WizardLayout.css",
    ...listFiles("pages/admin", ".css"),
    "pages/AstrologerProfilePage.css",
    "pages/billing/billing-return.css",
    "pages/BirthProfilePage.css",
    "pages/ConsultationResultPage.css",
    "pages/NatalChartPage.css",
    "pages/PrivacyPolicyPage.css",
  ].map((file) => ({
    file,
    source: readFrontendFile(file),
  }))
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

  it("garde le top menu en couche glass au-dessus du contenu scrolle", () => {
    const headerCss = readFrontendFile("layouts/components/Header.css")
    const headerBlock = findFlatCssBlock(headerCss, ".app-header")
    const veilBlock = findFlatCssBlock(headerCss, ".app-header::before")

    expect(headerBlock.body).toContain("position: sticky")
    expect(headerBlock.body).toContain("width: 100%")
    expect(headerBlock.body).toContain("max-width: 100%")
    expect(headerBlock.body).not.toContain("width: 100vw")
    expect(headerBlock.body).not.toContain("50vw")
    expect(headerBlock.body).toContain("z-index: 220")
    expect(headerBlock.body).toContain("background: color-mix(in srgb, var(--color-bg-top) 8%, var(--color-nav-glass) 11%)")
    expect(headerBlock.body).toContain("backdrop-filter: blur(calc(var(--surface-glass-blur))) saturate(170%)")
    expect(headerBlock.body).toContain("-webkit-backdrop-filter: blur(calc(var(--surface-glass-blur))) saturate(170%)")
    expect(headerBlock.body).toContain("isolation: isolate")
    expect(veilBlock.body).toContain("background: linear-gradient(")
    expect(veilBlock.body).toContain("pointer-events: none")
  })

  it("execute la garde des literals hardcodes migres par CS-027", () => {
    const migratedFiles = [
      "App.css",
      ...APP_CSS_MODULE_FILES,
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

  it("bloque le retour des literals premium partages migres par CS-089", () => {
    const guardedFiles = [
      "styles/backgrounds.css",
      "styles/glass.css",
      "pages/DailyHoroscopePage.css",
      "components/prediction/DailyAdviceCard.css",
    ]
    const registry = readFrontendFile("styles/token-namespace-registry.md")
    const premiumTheme = readFrontendFile("styles/premium-theme.css")
    const glassCss = readFrontendFile("styles/glass.css")

    const violations = guardedFiles.flatMap((file) =>
      collectCssDeclarations(readFrontendFile(file))
        .filter((declaration) => isForbiddenPremiumSharedDeclaration(file, declaration))
        .map((declaration) => ({ file, declaration })),
    )

    expect(registry).toContain("| `--premium-*` | semantic-extension |")
    expect(registry).toContain("| `--glass-card-*` | semantic-extension |")
    expect(premiumTheme).toContain("--premium-app-bg:")
    expect(premiumTheme).toContain("--premium-daily-advice-icon-bg:")
    expect(glassCss).toContain("--glass-card-premium-bg:")
    expect(readFrontendFile("styles/backgrounds.css")).not.toMatch(/--(?:glass|premium)-[a-zA-Z0-9_-]*\s*:/)
    expect(readFrontendFile("pages/DailyHoroscopePage.css")).not.toMatch(/--glass-[a-zA-Z0-9_-]*\s*:/)
    expect(readFrontendFile("components/prediction/DailyAdviceCard.css")).not.toMatch(/--(?:glass|premium)-[a-zA-Z0-9_-]*\s*:/)
    expect(violations).toEqual([])
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

  it("bloque le retour des literals chat migres par CS-081", () => {
    const migratedFiles = [
      "pages/ChatPage.css",
      "features/chat/components/ChatComposer.css",
      "features/chat/components/ChatPageHeader.css",
      "features/chat/components/ChatQuotaBanner.css",
      "features/chat/components/ChatWindow.css",
      "features/chat/components/ConversationItem.css",
      "features/chat/components/ConversationList.css",
    ]
    const chatPageCss = readFrontendFile("pages/ChatPage.css")
    const ownerBlock = findFlatCssBlock(chatPageCss, ".chat-page-container")
    const migratedValues = extractMigratedChatValues(ownerBlock.body)
    const forbiddenPropertyLiterals =
      /(?:#[a-fA-F0-9]{3,8}\b|rgba?\(|hsl(?:a)?\(|border-radius:\s*(?:50%|999px|28px|24px|22px|20px|16px|14px|12px|10px|6px|4px)\b|font-size:\s*(?:11|12|13|14|15|20|22|28|38)px\b|font-weight:\s*(?:500|600|650|700|750)\b|line-height:\s*(?:1\.1|1\.15|1\.4|1\.5|1\.55|1\.65)\b|letter-spacing:\s*-?0\.\d+em\b|box-shadow:\s*(?!\s*var\())/

    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--chat-*` | semantic-extension |")
    expect(migratedValues.length).toBeGreaterThan(0)

    for (const file of migratedFiles) {
      const source = file === "pages/ChatPage.css" ? removeCssRange(chatPageCss, ownerBlock.start, ownerBlock.end) : readFrontendFile(file)
      const normalizedSource = normalizeCssValue(source)

      expect(source).toContain("var(--chat-")
      expect(source).not.toMatch(forbiddenPropertyLiterals)
      for (const value of migratedValues) {
        expect(normalizedSource).not.toContain(value)
      }
    }
  })

  it("bloque le retour des literals App migres par CS-082", () => {
    const appCss = readAppCssSurface()
    const ownerBlock = findFlatCssBlock(appCss, "#root")
    const guardedCss = removeCssRange(appCss, ownerBlock.start, ownerBlock.end)
    const normalizedGuardedCss = normalizeCssValue(guardedCss)
    const migratedValues = extractSelectedAppValues(ownerBlock.body)
    const bottomNavBlock = findFlatCssBlock(appCss, ".bottom-nav")
    const buttonBlock = findFlatCssBlock(appCss, "button")
    const buttonHoverBlock = findFlatCssBlock(appCss, "button:hover:not(:disabled)")
    const stateLoadingBlock = findFlatCssBlock(appCss, ".app-state--loading")
    const stateEmptyBlock = findFlatCssBlock(appCss, ".app-state--empty")
    const stateSuccessBlock = findFlatCssBlock(appCss, ".app-state--success")
    const catalogueBlock = findFlatCssBlock(appCss, ".people-page")
    const summaryBlock = findFlatCssBlock(appCss, ".summary-panel-card-wrapper")

    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--app-button-*` | semantic-extension |")
    expect(migratedValues.length).toBeGreaterThan(0)
    expect(guardedCss).toContain("var(--app-")
    expect(guardedCss).not.toMatch(/var\(\s*--app-[a-zA-Z0-9_-]+\s*,/)
    for (const value of migratedValues) {
      expect(normalizedGuardedCss).not.toContain(value)
    }

    expect(bottomNavBlock.body).toContain("border-radius: var(--app-mobile-nav-radius)")
    expect(buttonBlock.body).toContain("background: var(--app-button-bg)")
    expect(buttonBlock.body).toContain("box-shadow: var(--app-button-shadow)")
    expect(buttonHoverBlock.body).toContain("box-shadow: var(--app-button-hover-shadow)")
    expect(stateLoadingBlock.body).toContain("var(--app-state-loading-")
    expect(stateEmptyBlock.body).toContain("var(--app-state-empty-")
    expect(stateSuccessBlock.body).toContain("var(--app-state-success-")
    expect(catalogueBlock.body).toContain("background: var(--app-astro-catalog-page-bg)")
    expect(summaryBlock.body).toContain("background: var(--app-summary-panel-bg)")
    expect(summaryBlock.body).toContain("box-shadow: var(--app-summary-panel-shadow)")
  })

  it("garde le relief compact et le contrat catalogue CS-148 de la liste astrologues", () => {
    const appCss = readAppCssSurface()
    const appCssEntry = readFrontendFile("App.css")
    const gridBlock = findFlatCssBlock(appCss, ".people-page .person-grid")
    const compactCardBlock = findFlatCssBlock(appCss, ".people-page .person-card")
    const iconBlock = findFlatCssBlock(appCss, ".people-page .person-card-icon")
    const iconRingBlock = findFlatCssBlock(appCss, ".people-page .person-card-icon::before")
    const avatarBlock = findFlatCssBlock(appCss, ".people-page .person-card-avatar")
    const styleBlock = findFlatCssBlock(appCss, ".people-page .person-card-style")
    const chipBlock = findFlatCssBlock(appCss, ".people-page .person-card-tag")
    const badgeBlock = findFlatCssBlock(appCss, ".people-page .person-card-provider-badge,\n.people-page .person-card-featured-badge,\n.people-page .person-default-badge")
    const ctaBlock = findFlatCssBlock(appCss, ".people-page .person-card-cta")
    const legacyFeaturedClass = ["person-card", "featured"].join("--")
    const typoBlendModeProperty = ["mix", "alend", "mode"].join("-")

    expect(appCssEntry).not.toMatch(/person-card|people-page|astrologer/)
    expect(gridBlock.body).toContain("repeat(auto-fit, minmax(min(100%, 280px), 1fr))")
    expect(compactCardBlock.body).toContain("background: var(--app-person-card-compact-background)")
    expect(compactCardBlock.body).toContain("border: var(--app-person-card-compact-border)")
    expect(compactCardBlock.body).toContain("var(--app-person-card-compact-radius)")
    expect(compactCardBlock.body).toContain("box-shadow: var(--app-person-card-compact-box-shadow)")
    expect(appCss).not.toContain(`.people-page .${legacyFeaturedClass}`)
    expect(appCss).not.toContain(typoBlendModeProperty)
    expect(iconBlock.body).toContain("position: absolute")
    expect(iconBlock.body).toContain("z-index: 5")
    expect(iconBlock.body).toContain("background: var(--app-person-card-compact-icon-background)")
    expect(iconBlock.body).toContain("border: var(--app-person-card-compact-icon-border)")
    expect(iconBlock.body).toContain("box-shadow: var(--app-person-card-compact-icon-box-shadow)")
    expect(iconRingBlock.body).toContain("background: var(--app-person-card-compact-icon-ring-background)")
    expect(avatarBlock.body).toContain("background: var(--app-person-card-compact-avatar-background)")
    expect(avatarBlock.body).toContain("border: var(--app-person-card-compact-avatar-border)")
    expect(avatarBlock.body).toContain("box-shadow: var(--app-person-card-compact-avatar-box-shadow)")
    expect(styleBlock.body).toContain("color: var(--app-person-card-compact-style-color)")
    expect(chipBlock.body).toContain("background: var(--app-person-card-compact-tag-background)")
    expect(chipBlock.body).toContain("border: var(--app-person-card-compact-tag-border)")
    expect(chipBlock.body).toContain("box-shadow: var(--app-person-card-compact-tag-box-shadow)")
    expect(badgeBlock.body).toContain("display: inline-flex")
    expect(ctaBlock.body).toContain("margin-top: auto")
    expect(ctaBlock.body).toContain("text-decoration: underline")
    expect(appCss).not.toMatch(/\.astrologer-(?:card|grid|card-avatar|card-specialties)/)
  })

  it("bloque les noms App specifiques non classes par CS-124", () => {
    const appCss = readAppCssSurface()
    const ownerBlock = findFlatCssBlock(appCss, "#root")
    const allowed = new Set(
      APP_CSS_SPECIFICITY_EXCEPTIONS.map((entry) => `${entry.kind}:${entry.name}`),
    )
    const activeEntries = [
      ...collectAppSpecificCustomProperties(ownerBlock.body).map((name) => ({
        kind: "custom-property" as const,
        name,
      })),
      ...collectAppClassSelectors(appCss).map((name) => ({
        kind: "selector" as const,
        name,
      })),
    ]
    const activeKeys = new Set(activeEntries.map((entry) => `${entry.kind}:${entry.name}`))
    const violations = activeEntries.filter((entry) => !allowed.has(`${entry.kind}:${entry.name}`))
    const staleExceptions = APP_CSS_SPECIFICITY_EXCEPTIONS.filter(
      (entry) => !activeKeys.has(`${entry.kind}:${entry.name}`),
    )
    const expiredExceptions = APP_CSS_SPECIFICITY_EXCEPTIONS.filter(
      (entry) => entry.expiresAfter <= "2026-05-09",
    )

    expect(violations).toEqual([])
    expect(staleExceptions).toEqual([])
    expect(expiredExceptions).toEqual([])
  })

  it("bloque les prefixes App non classes par CS-125", () => {
    const appCss = readAppCssSurface()
    const registry = readFrontendFile("styles/token-namespace-registry.md")
    const activePrefixes = collectAppCustomPropertyPrefixes(appCss)
    const acceptedPrefixes = APP_CSS_ACCEPTED_PREFIXES.map((entry) => entry.prefix).sort()
    const acceptedPrefixSet = new Set(acceptedPrefixes)
    const unclassifiedPrefixes = activePrefixes.filter((prefix) => !acceptedPrefixSet.has(prefix))
    const staleAcceptedPrefixes = acceptedPrefixes.filter((prefix) => !activePrefixes.includes(prefix))
    const duplicatedAcceptedPrefixes = acceptedPrefixes.filter((prefix, index) => acceptedPrefixes.indexOf(prefix) !== index)
    const registryViolations = APP_CSS_ACCEPTED_PREFIXES.filter(
      (entry) =>
        !registry.includes(`| \`--app-${entry.prefix}-*\` | semantic-extension | \`${entry.owner}\` |`) ||
        entry.classification !== "canonical-active" ||
        entry.decision !== "retain-app-owned-prefix" ||
        entry.proof.trim().length === 0,
    )

    expect(registry).not.toContain("| `--app-*` |")
    expect(activePrefixes).toEqual(acceptedPrefixes)
    expect(unclassifiedPrefixes).toEqual([])
    expect(staleAcceptedPrefixes).toEqual([])
    expect(duplicatedAcceptedPrefixes).toEqual([])
    expect(registryViolations).toEqual([])
    expect(acceptedPrefixSet.has("precision")).toBe(false)
    expect(acceptedPrefixSet.has("evidence")).toBe(false)
  })

  it("bloque les familles precision et evidence non routees dans App.css par CS-126", () => {
    const appCss = readAppCssSurface()

    expect(collectPrecisionEvidenceAppCssHits(appCss)).toEqual([])
    expect(collectLegacyPrecisionEvidenceCssHits()).toEqual([])
  })

  it("bloque les declarations visuelles et typographiques App non routees par CS-087", () => {
    const appCss = readAppCssSurface()
    const ownerBlock = findFlatCssBlock(appCss, "#root")
    const declarations = collectCssDeclarations(appCss)
    const activeViolations = declarations.filter(isForbiddenAppLiteralDeclaration)
    const appOwnerNames = [...ownerBlock.body.matchAll(/(--app-[a-zA-Z0-9_-]+)\s*:/g)].map((match) => match[1])
    const mechanicalOwnerNames = appOwnerNames.filter(isMechanicalAppCustomPropertyName)

    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--app-state-*` | semantic-extension |")
    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--astro-*` | semantic-extension |")
    expect(activeViolations).toEqual([])
    expect(mechanicalOwnerNames).toEqual([])
    expect(appCss).toContain("width: calc(var(--usage-progress, 0) * 1%)")
    expect(appCss.match(/var\(\s*--[a-zA-Z0-9_-]+\s*,/g)).toEqual(["var(--usage-progress,"])
  })

  it("blocks App CSS duplicate selectors and size regression", () => {
    const appCss = readFrontendFile("App.css")
    const importedModules = [...appCss.matchAll(/@import ['"]\.\/(styles\/app\/[^'"]+)['"];/g)].map((match) => match[1])
    const appSurface = readAppCssSurface()
    const countSelector = (selector: string) =>
      [...appSurface.matchAll(new RegExp(`(^|\\n)${selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")} \\{`, "g"))].length
    const mechanicalTokens = [...appSurface.matchAll(/--app-[a-zA-Z0-9_-]+-(?:font-size|border-radius|background|color)-[0-9]+/g)]
      .map((match) => match[0])

    expect(appCss.split(/\r?\n/).length).toBeLessThan(2600)
    expect(importedModules).toEqual([...APP_CSS_MODULE_FILES])
    expect(appCss.replace(/@import[^;]+;/g, "")).not.toMatch(/^\s*[.#][a-zA-Z0-9_-]+\s*\{/m)
    expect(countSelector(".skeleton-line")).toBe(1)
    expect(countSelector(".people-page-header h1")).toBe(1)
    expect(countSelector(".people-page-header p")).toBe(1)
    expect(mechanicalTokens).toEqual([])
  })

  it("garde le profil astrologue sans overflow masque ni styles hors owner", () => {
    const appCss = readFrontendFile("App.css")
    const profileCss = readFrontendFile("pages/AstrologerProfilePage.css")
    const profileRoute = readFrontendFile("pages/AstrologerProfilePage.tsx")
    const profileSections = readFrontendFile("features/astrologers/components/AstrologerProfileSections.tsx")

    expect(appCss).not.toMatch(/AstrologerProfile|profile-/)
    expect(`${profileRoute}\n${profileSections}`).not.toMatch(/\sstyle=/)
    expect(profileCss).not.toMatch(/overflow-x:\s*hidden/)
    expect(profileCss).toContain("grid-template-columns: repeat(2, minmax(0, 1fr))")
    expect(profileCss).toContain("--profile-hero-avatar-size: min(210px, calc(100vw - 72px))")
    expect(profileCss).toContain(".profile-hero-actions")
    expect(profileCss).toContain(".profile-reviews-summary--empty")
  })

  it("garde la largeur centrale non-admin sous ownership layout CS-130", () => {
    const tokensCss = readFrontendFile("styles/design-tokens.css")
    const backgroundsCss = readFrontendFile("styles/backgrounds.css")
    const pageLayoutCss = readFrontendFile("layouts/PageLayout.css")

    expect(tokensCss).toContain("--layout-page-max-width: min(1440px, calc(100vw - 2 * var(--space-6)))")
    expect(backgroundsCss).toContain("max-width: var(--layout-page-max-width)")
    expect(pageLayoutCss).toContain("max-width: var(--layout-page-max-width)")
    expect(collectNonAdminPageLevelWidthViolations()).toEqual([])
  })

  it("garde un fond de page canonique unique par theme", () => {
    const premiumThemeCss = readFrontendFile("styles/premium-theme.css")
    const backgroundsCss = readFrontendFile("styles/backgrounds.css")
    const rootThemeBlock = findFlatCssBlock(premiumThemeCss, ":root")
    const darkThemeBlock = findFlatCssBlock(premiumThemeCss, ".dark")

    expect(rootThemeBlock.body).toContain("--premium-app-bg:")
    expect(rootThemeBlock.body).toContain("var(--color-token-rgb-171-211-255)")
    expect(rootThemeBlock.body).toContain("var(--color-token-fcfdff)")
    expect(rootThemeBlock.body).toContain("--premium-app-bg-atmosphere: transparent")
    expect(darkThemeBlock.body).toContain("--premium-app-bg:")
    expect(darkThemeBlock.body).toContain("rgba(255, 190, 82, 0.52)")
    expect(darkThemeBlock.body).toContain("linear-gradient(180deg, transparent 0%, transparent 92%")
    expect(darkThemeBlock.body).not.toContain("linear-gradient(90deg, transparent 0%, rgba(255, 158, 67")
    expect(darkThemeBlock.body).toContain("linear-gradient(124deg")
    expect(darkThemeBlock.body).toContain("--starfield-star-blue:")
    expect(darkThemeBlock.body).toContain("--starfield-star-dawn:")
    expect(darkThemeBlock.body).toContain("--starfield-milky-mid:")
    expect(backgroundsCss).toMatch(/\.app-bg\s*\{[^}]*background:\s*var\(--premium-app-bg\)/)
    expect(backgroundsCss).toMatch(/\.app-bg\s*\{[^}]*background-attachment:\s*fixed/)
    expect(backgroundsCss).toMatch(/\.dark\s+\.app-bg\s*\{[^}]*background-attachment:\s*fixed/)
    expect(backgroundsCss).toMatch(/\.app-bg::before\s*\{[^}]*background:\s*var\(--premium-app-bg-atmosphere\)/)
    expect(backgroundsCss).toContain(".app-bg--internal")
    expect(backgroundsCss).not.toContain("app-bg--landing")
    expect(backgroundsCss).toContain("@media (prefers-reduced-motion: reduce)")
    expect(backgroundsCss).toContain(".starfield-bg__milky-way--smoke")
    expect(backgroundsCss).toContain("astral-milky-smoke-drift")
    expect(backgroundsCss).toContain("astral-milky-haze-drift")
    expect(backgroundsCss).toContain("astral-milky-veil-drift")
    expect(backgroundsCss).toContain("astral-dawn-breath")
    expect(collectPageBackgroundViolations()).toEqual([])
  })

  it("bloque le retour d'une variante de fond dediee a la landing", () => {
    const forbiddenClassName = ["app-bg", "landing"].join("--")
    const scannedFiles = [
      "layouts/RootLayout.tsx",
      "styles/backgrounds.css",
      ...listFiles("layouts", ".tsx"),
      ...listFiles("styles", ".css"),
      ...listFiles("pages", ".tsx"),
    ]
    const violations = [...new Set(scannedFiles)]
      .filter((file) => readFrontendFile(file).includes(forbiddenClassName))

    expect(violations).toEqual([])
  })

  it("blocks non-type App CSS module filenames", () => {
    const approved = APP_CSS_MODULE_FILES.map((file) => file.replace("styles/app/", "")).sort()
    const actual = listFiles("styles/app", ".css").map((file) => file.replace("styles/app/", "")).sort()

    expect(actual).toEqual(approved)
  })

  it("blocks stale TSX consumers from App CSS mapping", () => {
    const mapping = readFrontendFile("../../_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-type-primitive-mapping.md")
    const deletedSelectors = [...mapping.matchAll(/\|\s*`\.([a-zA-Z0-9_-]+)`\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*deleted\s*\|/g)]
      .map((match) => match[1])
    const tsxSurface = listFiles("", ".tsx").map((file) => readFrontendFile(file)).join("\n")
    const staleConsumers = deletedSelectors.filter((selector) =>
      new RegExp(`\\b${selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`).test(tsxSurface),
    )

    expect(staleConsumers).toEqual([])
  })

  it("blocks single-use App custom properties without retained decision", () => {
    const usageArtifact = readFrontendFile("../../_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-variable-usage.md")
    const appSurface = readAppCssSurface()
    const variables = [...new Set([...appSurface.matchAll(/--app-[a-zA-Z0-9_-]+/g)].map((match) => match[0]))]
    const undocumentedSingleUse = variables.filter((variable) => {
      const variablePattern = variable.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
      const usages = [...appSurface.matchAll(new RegExp(`var\\(\\s*${variablePattern}\\s*\\)`, "g"))].length
      return usages < 2 && !usageArtifact.includes(`| \`${variable}\` |`)
    })

    expect(undocumentedSingleUse).toEqual([])
  })

  it("CS-127 expose et consomme les primitives globales typees", () => {
    const appCss = readAppCssSurface()
    const tsxSurface = listFiles("", ".tsx").map((file) => readFrontendFile(file)).join("\n")

    for (const primitive of [".notice", ".select-card", ".form-control", ".state-centered", ".stack", ".cluster"]) {
      expect(appCss).toContain(`${primitive} {`)
      expect(tsxSurface).toContain(primitive.slice(1))
    }
  })

  it("bloque le retour des literals Settings migres par CS-084", () => {
    const settingsCss = readFrontendFile("pages/settings/Settings.css")
    const ownerBlock = findFlatCssBlock(settingsCss, ".is-settings-page")
    const guardedCss = removeCssRange(settingsCss, ownerBlock.start, ownerBlock.end)
    const normalizedGuardedCss = normalizeCssValue(guardedCss)
    const migratedValues = extractMigratedSettingsValues(ownerBlock.body)
    const forbiddenPropertyLiterals =
      /(?:#[a-fA-F0-9]{3,8}\b|rgba?\(|hsl(?:a)?\(|background:\s*(?:linear|radial)-gradient\(|box-shadow:\s*(?!\s*var\()|border-radius:\s*(?:50%|\d)|font-size:\s*(?:clamp\(|\d)|font-weight:\s*\d|line-height:\s*\d|letter-spacing:\s*-?0\.|(?:^|[;{\n]\s*)(?:margin|padding|gap|inset|top|right|bottom|left|outline-offset):\s*-?\d+(?:\.\d+)?(?:px|rem|em|ch|%))/

    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--settings-*` | semantic-extension |")
    expect(migratedValues.length).toBeGreaterThan(0)
    expect(ownerBlock.body).toContain("--settings-page-bg:")
    expect(ownerBlock.body).toContain("--settings-page-bg: var(--premium-app-bg)")
    expect(ownerBlock.body).toContain("--settings-page-padding:")
    expect(ownerBlock.body).toContain("--settings-save-feedback-offset:")
    expect(guardedCss).toContain("var(--settings-")
    expect(guardedCss).toContain("var(--usage-progress, 0)")
    expect(findFlatCssBlock(settingsCss, ".settings-bg-halo").body).toContain("background: none")
    expect(guardedCss).not.toMatch(forbiddenPropertyLiterals)
    for (const value of migratedValues) {
      expect(normalizedGuardedCss).not.toContain(value)
    }
  })

  it("bloque le retour des literals landing migres par CS-085", () => {
    const landingOwnerBlocks = [
      { file: "layouts/LandingLayout.css", selector: ".landing-layout" },
      { file: "pages/landing/LandingPage.css", selector: ".landing-page" },
      { file: "pages/landing/sections/LandingFooter.css", selector: ".landing-footer" },
      { file: "pages/landing/sections/LandingNavbar.css", selector: ".landing-navbar" },
      { file: "pages/landing/sections/ProblemSection.css", selector: ".problem-section" },
      { file: "pages/landing/sections/TestimonialsSection.css", selector: ".testimonials-section" },
    ]
    const ownerBlocksByFile = new Map(
      landingOwnerBlocks.map(({ file, selector }) => {
        const source = readFrontendFile(file)
        return [file, { source, block: findFlatCssBlock(source, selector) }]
      }),
    )
    const landingFiles = [
      "layouts/LandingLayout.css",
      "pages/landing/LandingPage.css",
      "pages/landing/sections/FaqSection.css",
      "pages/landing/sections/LandingFooter.css",
      "pages/landing/sections/LandingNavbar.css",
      "pages/landing/sections/PricingSection.css",
      "pages/landing/sections/ProblemSection.css",
      "pages/landing/sections/SocialProofSection.css",
      "pages/landing/sections/SolutionSection.css",
      "pages/landing/sections/TestimonialsSection.css",
    ]
    const guardedCss = landingFiles
      .map((file) => {
        const owner = ownerBlocksByFile.get(file)

        return owner === undefined
          ? readFrontendFile(file)
          : removeCssRange(owner.source, owner.block.start, owner.block.end)
      })
      .join("\n")
    const normalizedGuardedCss = normalizeCssValue(guardedCss)
    const migratedValues = [...new Set(
      [...ownerBlocksByFile.values()].flatMap(({ block }) => extractMigratedLandingValues(block.body)),
    )]
    const forbiddenPropertyLiterals =
      /(?:#[a-fA-F0-9]{3,8}\b|rgba?\(|hsl(?:a)?\(|box-shadow:\s*(?!\s*(?:var\(|none))|border-radius:\s*(?:50%|\d)|font-size:\s*(?:clamp\(|\d)|font-weight:\s*\d|line-height:\s*\d|letter-spacing:\s*-?0\.|var\(\s*--[a-zA-Z0-9_-]+\s*,)/
    const forbiddenPageScopedNamespaceUsage = /--(?:settings|help|chat|app)-[a-zA-Z0-9_-]+/

    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--landing-*` | semantic-extension |")
    expect(readFrontendFile("styles/typography-roles.md")).toContain("landing-marketing")
    expect(migratedValues.length).toBeGreaterThan(100)
    expect(ownerBlocksByFile.get("pages/landing/LandingPage.css")?.block.body).toContain("--landing-hero-")
    expect(ownerBlocksByFile.get("pages/landing/sections/LandingNavbar.css")?.block.body).toContain("--landing-navbar-")
    expect(ownerBlocksByFile.get("pages/landing/sections/LandingFooter.css")?.block.body).toContain("--landing-footer-")
    expect(guardedCss).toContain("var(--landing-")
    expect(guardedCss).not.toMatch(forbiddenPropertyLiterals)
    expect(guardedCss).not.toMatch(forbiddenPageScopedNamespaceUsage)
    for (const value of migratedValues) {
      expect(normalizedGuardedCss).not.toContain(value)
    }
  })

  it("garde une carte finie des groupes owners landing", () => {
    const landingCssFiles = [
      "layouts/LandingLayout.css",
      ...listFiles("pages/landing", ".css"),
    ]
    const landingSurfaceFiles = [
      ...landingCssFiles,
      ...listFiles("pages/landing", ".tsx"),
    ]
    const landingDeclarations = landingCssFiles.flatMap((file) =>
      collectCssDeclarations(readFrontendFile(file))
        .map((declaration) => ({
          ...declaration,
          file,
          group: extractLandingGroup(declaration.property),
        }))
        .filter((declaration): declaration is CssDeclaration & { file: string; group: string } =>
          declaration.group !== null,
        ),
    )
    const variables = [...new Set(landingDeclarations.map((declaration) => declaration.group))].sort()
    const unclassified = variables.filter((group) => !LANDING_OWNER_GROUPS.has(group))
    const forbidden = variables.filter((group) => FORBIDDEN_LANDING_OWNER_GROUPS.has(group))
    const declarationRouteViolations = landingDeclarations.flatMap((declaration) => {
      const route = LANDING_OWNER_GROUPS.get(declaration.group)

      if (route === undefined || isLandingDeclarationAllowed(route, declaration.file, declaration.selector)) {
        return []
      }

      return [{
        file: declaration.file,
        selector: declaration.selector,
        property: declaration.property,
        owner: route.owner,
        allowed: route.declarations,
      }]
    })
    const consumerGroups = collectLandingConsumerGroups(landingSurfaceFiles)
    const groupsWithoutConsumer = variables.filter((group) => !consumerGroups.includes(group))

    expect(variables).toEqual([...LANDING_OWNER_GROUPS.keys()].sort())
    expect(unclassified).toEqual([])
    expect(forbidden).toEqual([])
    expect(declarationRouteViolations).toEqual([])
    expect(groupsWithoutConsumer).toEqual([])
  })

  it("borne la complexite visuelle motion et filters landing par exceptions exactes", () => {
    const landingCss = [
      "layouts/LandingLayout.css",
      ...listFiles("pages/landing", ".css"),
    ].map((file) => readFrontendFile(file)).join("\n")
    const exceptionKeys = LANDING_VISUAL_COMPLEXITY_EXCEPTIONS.map((entry) =>
      toStableJson({
        file: entry.file,
        selector: entry.selector,
        property: entry.property,
        value: entry.value,
      }),
    )
    const actualDeclarationKeys = new Set(
      collectLandingVisualComplexityDeclarations().map((declaration) =>
        toStableJson({
          file: declaration.file,
          selector: normalizeLandingDeclarationSelector(declaration.selector),
          property: declaration.property,
          value: declaration.value,
        }),
      ),
    )
    const wildcardExceptions = LANDING_VISUAL_COMPLEXITY_EXCEPTIONS.filter((entry) =>
      entry.file.includes("*") ||
      entry.selector.includes("*") ||
      entry.value.includes("*") ||
      entry.reason.trim().length === 0 ||
      entry.exitCondition.trim().length === 0,
    )
    const staleExceptions = exceptionKeys.filter((key) => !actualDeclarationKeys.has(key))

    expect(landingCss).not.toMatch(/@keyframes\s+/)
    expect(collectLandingVisualComplexityViolations()).toEqual([])
    expect(wildcardExceptions).toEqual([])
    expect(staleExceptions).toEqual([])
    expect(new Set(exceptionKeys).size).toBe(exceptionKeys.length)
  })

  it("bloque le retour des literals admin migres par CS-086", () => {
    const forbiddenVisualOrTypeLiterals =
      /(?:#[a-fA-F0-9]{3,8}\b|rgba?\(|hsl(?:a)?\(|box-shadow:\s*(?!\s*var\()|border-radius:\s*(?:50%|\d)|font-size:\s*(?:clamp\(|\d)|font-weight:\s*\d|line-height:\s*\d|letter-spacing:\s*-?0\.|var\(\s*--[a-zA-Z0-9_-]+\s*,)/
    const forbiddenMigratedSpacingLiterals =
      /(?:padding:\s*(?:4px 12px|0\.75rem 1rem)|gap:\s*2px|margin:\s*0 0 4px|margin-bottom:\s*0\.25rem|padding-left:\s*1\.5rem|margin-top:\s*0\.5rem)/
    const forbiddenPageScopedNamespaceUsage = /--(?:settings|help|chat|app|landing)-[a-zA-Z0-9_-]+/
    const adminCluster = collectAdminCssCluster()

    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--radius-admin-*` | canonical |")
    expect(readFrontendFile("styles/token-namespace-registry.md")).toContain("| `--shadow-admin-*` | canonical |")
    expect(readFrontendFile("styles/typography-roles.md")).toContain("admin-compact")

    for (const { source } of adminCluster) {
      expect(source).not.toMatch(forbiddenVisualOrTypeLiterals)
      expect(source).not.toMatch(forbiddenMigratedSpacingLiterals)
      expect(source).not.toMatch(forbiddenPageScopedNamespaceUsage)
    }
  })

  it("bloque le retour des literals du cluster residuel frontend design-system", () => {
    const forbiddenVisualOrTypeLiterals = new RegExp(
      [
        "#[a-fA-F0-9]{3,8}\\b",
        "rgba?\\(",
        "hsl(?:a)?\\(",
        "box-shadow:\\s*(?!\\s*(?:var\\(|none))",
        "text-shadow:\\s*(?!\\s*(?:var\\(|none))",
        "border-radius:\\s*(?!\\s*(?:var\\(|inherit))[\\d.]+(?:px|rem|%)",
        "font-size:\\s*(?!\\s*var\\()[^;]*(?:clamp\\(|[\\d.]+(?:px|rem))",
        "font-weight:\\s*(?!\\s*var\\()\\d",
        "line-height:\\s*(?!\\s*(?:var\\(|inherit))[\\d.]+",
        "letter-spacing:\\s*(?!\\s*var\\()-?[\\d.]+(?:px|em)",
        "font-family:\\s*(?!\\s*(?:var\\(|inherit))",
        "var\\(\\s*--[a-zA-Z0-9_-]+\\s*,",
      ].join("|"),
    )

    for (const { source } of collectResidualCssTokenCluster()) {
      expect(source).not.toMatch(forbiddenVisualOrTypeLiterals)
    }
    expect(readFrontendFile("styles/typography-roles.md")).toContain("residual-css-token-cluster")
    expect(readFrontendFile("styles/typography-roles.md")).not.toContain("profile editorial sizes")
  })

  it("garde les corrections dark mode CS-137 dans les owners CSS attendus", () => {
    const appCssEntry = readFrontendFile("App.css")
    const darkModeOwners = [
      "styles/app/tokens.css",
      "styles/app/cards.css",
      "layouts/LandingLayout.css",
      "pages/PrivacyPolicyPage.css",
      "components/ui/UserAvatar/UserAvatar.css",
      "components/ShortcutCard.css",
      "pages/AstrologerProfilePage.css",
      "pages/HelpPage.css",
      "pages/settings/Settings.css",
      "pages/NatalChartPage.css",
      "features/natal-chart/NatalInterpretation.css",
      "pages/ChatPage.css",
      "pages/ConsultationResultPage.css",
    ]
    const ownerSurface = darkModeOwners.map((file) => readFrontendFile(file)).join("\n")

    expect(appCssEntry).not.toMatch(/(?:^|\n)\s*(?:html\.)?\.dark\b/)
    expect(ownerSurface).toContain(".dark #root")
    expect(ownerSurface).toContain("--app-premium-page-layout-background: var(--premium-app-bg)")
    expect(ownerSurface).toContain("--app-premium-hero-title-color: var(--premium-text-strong)")
    expect(ownerSurface).toContain("--app-summary-panel-cta-color: var(--premium-text-strong)")
    expect(ownerSurface).toContain(".summary-title")
    expect(ownerSurface).toContain(".summary-section-title")
    expect(ownerSurface).toContain(".dark .landing-layout")
    expect(ownerSurface).toContain(".dark :where(.help-page, .help-bg-halo)")
    expect(ownerSurface).toContain(".dark .is-settings-page")
    expect(ownerSurface).toContain(".dark .astrologer-profile-container")
    expect(ownerSurface).toContain("--app-astro-catalog-page-bg: transparent")
    expect(ownerSurface).toContain("--app-astro-catalog-atmosphere: transparent")
    expect(ownerSurface).toContain("--settings-page-bg: var(--premium-app-bg)")
    expect(ownerSurface).toContain("--help-bg-halo: var(--premium-app-bg)")
    expect(ownerSurface).toContain(".dark .chat-page-container")
    expect(ownerSurface).toContain(".dark .user-avatar")
    expect(ownerSurface).toContain("background: var(--color-glass-shortcut)")
    expect(ownerSurface).toContain(".dark :where(.shortcut-card__title)")
    expect(ownerSurface).toContain(".dark :where(.shortcut-card__subtitle)")
    expect(ownerSurface).toContain("background: var(--premium-glass-surface-1)")
    expect(ownerSurface).toContain(".dark .profile-metrics-bar")
    expect(ownerSurface).toContain("color: var(--premium-text-strong)")
    expect(ownerSurface).toContain(".dark .privacy-policy-page a")
    expect(ownerSurface).toContain(".dark .privacy-policy-page a:focus-visible")
    expect(ownerSurface).not.toMatch(/#0000ee|rgb\(\s*0\s*,\s*0\s*,\s*238\s*\)|color:\s*blue\b/)
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
      { file: "types/dailyPrediction.ts", terms: [removedOverallSummary] },
      {
        file: "features/natal-chart/NatalInterpretation.tsx",
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

    expect(vocabularyViolations).toEqual([])
    expect(targetedViolations).toEqual([])
    expect(predictionKeyViolations).toEqual([])
    expect(predictionRuntimeViolations).toEqual([])
  })

  it("execute les allowlists exactes inline-style et css-fallback", () => {
    const allowedInline = new Set(INLINE_STYLE_EXCEPTIONS.map(toStableJson))
    const allowedFallbacks = new Set(CSS_FALLBACK_EXCEPTIONS.map(toStableJson))

    expect(collectInlineStyles().filter((entry) => !allowedInline.has(toStableJson(entry)))).toEqual([])
    expect(collectCssFallbacks().filter((entry) => !allowedFallbacks.has(toStableJson(entry)))).toEqual([])
  })

  it("valide la syntaxe des declarations CSS actives des layouts", () => {
    const layoutCssFiles = listFiles("layouts", ".css")
    const syntaxIssues = collectCssSyntaxIssues(layoutCssFiles)

    expect(syntaxIssues).toEqual([])
    expect(layoutCssFiles).toContain("layouts/PageLayout.css")
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

  it("bloque la reintroduction locale des literals subscriptions Help migres par CS-088", () => {
    const css = readFrontendFile("pages/HelpPage.css")
    const ownerBlock = findFlatCssBlock(css, ":where(.help-page, .help-bg-halo)")
    const subscriptionsStart = css.indexOf("/* --- Help Subscriptions Page")
    expect(subscriptionsStart).toBeGreaterThan(ownerBlock.end)

    const migratedValues = extractMigratedHelpSubscriptionsValues(ownerBlock.body)
    const guardedCss = css.slice(subscriptionsStart)
    const guardedDeclarations = collectCssDeclarations(guardedCss).filter(
      (declaration) => !declaration.property.startsWith("--"),
    )
    const guardedDeclarationValues = guardedDeclarations.map((declaration) => declaration.value)
    const forbiddenTypographyLiterals = [
      "font-size: 0.78rem",
      "font-size: 0.76rem",
      "font-size: 0.7rem",
      "font-size: 2.15rem",
      "font-size: clamp(2.8rem, 6vw, 3.55rem)",
      "font-size: clamp(3.35rem, 6vw, 4.22rem)",
      "line-height: 0.96",
      "line-height: 1.72",
      "letter-spacing: 0.12em",
      "letter-spacing: 0.14em",
    ]

    expect(migratedValues.length).toBeGreaterThan(40)
    expect(extractMigratedHelpSubscriptionsValues("--help-subscriptions-proof: hsl(10 20% 30%);")).toContain(
      "hsl(10 20% 30%)",
    )
    expect(extractMigratedHelpSubscriptionsValues("--help-subscriptions-proof: hsla(10, 20%, 30%, 0.4);")).toContain(
      "hsla(10, 20%, 30%, 0.4)",
    )
    for (const value of migratedValues) {
      expect(guardedDeclarationValues.filter((declarationValue) => declarationValue.includes(value))).toEqual([])
    }
    for (const literal of forbiddenTypographyLiterals) {
      expect(normalizeCssValue(guardedCss)).not.toContain(literal)
    }
    expect(guardedCss).not.toMatch(/var\(\s*--(?:settings|app|chat|landing|admin)-/)
    expect(guardedCss).not.toMatch(/var\(\s*--[a-zA-Z0-9_-]+\s*,/)
  })

  it("centralise les exceptions exactes anti-drift", () => {
    expect(INLINE_STYLE_DYNAMIC_ALLOWLIST.length).toBeGreaterThan(0)
    expect(INLINE_STYLE_EXCEPTIONS.length).toBeGreaterThan(0)
    expect(CSS_FALLBACK_EXCEPTIONS.length).toBeGreaterThan(0)
    expect(readFrontendFile("styles/css-fallback-allowlist.md")).toContain("Exit condition")
    expect(readFrontendFile("styles/legacy-style-surface-registry.md")).toContain("Canonical target")
  })
})
