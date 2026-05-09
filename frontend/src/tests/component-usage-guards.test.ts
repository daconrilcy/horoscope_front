// Inventaire statique exact des composants sans consommateur runtime direct.
import { describe, expect, it } from "vitest"

import { listFiles, readFrontendFile } from "./design-system-policy"
import { COMPONENT_USAGE_EXCEPTIONS, type ComponentUsageClassification } from "./component-usage-allowlist"

const ALLOWED_CLASSIFICATIONS: ComponentUsageClassification[] = [
  "runtime-used",
  "public-library-export",
  "remove",
  "needs-user-decision",
]

function pascal(parts: string[]): string {
  return parts.join("")
}

function componentPath(parts: string[], folder = "components"): string {
  return `${folder}/${pascal(parts)}.tsx`
}

function cssPath(parts: string[], folder = "components"): string {
  return `${folder}/${pascal(parts)}.css`
}

function testPath(parts: string[], suffix = ".test.tsx"): string {
  return `tests/${pascal(parts)}${suffix}`
}

const FORBIDDEN_REMOVED_COMPONENT_FILES = [
  componentPath(["B2B", "Astrology", "Panel"]),
  componentPath(["B2B", "Billing", "Panel"]),
  componentPath(["B2B", "Editorial", "Panel"]),
  componentPath(["B2B", "Usage", "Panel"]),
  componentPath(["Ops", "Monitoring", "Panel"]),
  componentPath(["Ops", "Persona", "Panel"]),
  componentPath(["Privacy", "Panel"]),
  componentPath(["Daily", "Insights", "Section"]),
  componentPath(["Mini", "Insight", "Card"]),
  componentPath(["Constellation", "SVG"]),
  componentPath(["Hero", "Horoscope", "Card"]),
  componentPath(["Today", "Header"]),
  componentPath(["Day", "Prediction", "Card"], "components/prediction"),
  componentPath(["Turning", "Points", "List"], "components/prediction"),
]

const FORBIDDEN_REMOVED_COMPONENT_SYMBOLS = [
  pascal(["B2B", "Astrology", "Panel"]),
  pascal(["B2B", "Billing", "Panel"]),
  pascal(["B2B", "Editorial", "Panel"]),
  pascal(["B2B", "Usage", "Panel"]),
  pascal(["Ops", "Monitoring", "Panel"]),
  pascal(["Ops", "Persona", "Panel"]),
  pascal(["Privacy", "Panel"]),
  pascal(["Daily", "Insights", "Section"]),
  pascal(["Mini", "Insight", "Card"]),
  pascal(["Constellation", "SVG"]),
  pascal(["Hero", "Horoscope", "Card"]),
  pascal(["Today", "Header"]),
  pascal(["Day", "Prediction", "Card"]),
  pascal(["Turning", "Points", "List"]),
]

const FORBIDDEN_REMOVED_CSS_FILES = [
  cssPath(["Hero", "Horoscope", "Card"]),
  cssPath(["Mini", "Insight", "Card"]),
  cssPath(["Day", "Prediction", "Card"], "components/prediction"),
  cssPath(["Turning", "Points", "List"], "components/prediction"),
]

const FORBIDDEN_REMOVED_TEST_FILES = [
  testPath(["B2B", "Astrology", "Panel"]),
  testPath(["B2B", "Billing", "Panel"]),
  testPath(["B2B", "Editorial", "Panel"]),
  testPath(["B2B", "Usage", "Panel"]),
  testPath(["Ops", "Monitoring", "Panel"]),
  testPath(["Ops", "Persona", "Panel"]),
  testPath(["Privacy", "Panel"]),
  testPath(["Hero", "Horoscope", "Card"]),
  testPath(["Mini", "Insight", "Card"]),
  testPath(["Today", "Header"]),
  testPath(["Turning", "Points", "Enriched"]),
  testPath(["day", "-prediction", "-card", "-tone"], ".test.ts"),
]

const FORBIDDEN_REMOVED_CSS_SELECTOR_PREFIXES = [
  "today-header",
  "mini-cards-grid",
  "mini-card",
  "hero-card",
  "day-prediction-card",
  "turning-points-list",
]

const ALLOWED_ACTIVE_CSS_SELECTOR_OWNERS = new Map<string, Set<string>>([
  [
    "hero-card",
    new Set([
      "pages/landing/LandingPage.css",
      "pages/landing/sections/HeroSection.tsx",
    ]),
  ],
])

function componentFiles(): string[] {
  return listFiles("components", ".tsx").filter((file) => !file.endsWith(".test.tsx"))
}

const allSourceFiles = [".ts", ".tsx"].flatMap((extension) => listFiles("", extension))
  .filter((file) => !file.startsWith("tests/"))
  .filter((file) => !file.endsWith(".test.tsx"))
  .filter((file) => !file.endsWith(".test.ts"))

const sourceFileSet = new Set(allSourceFiles)
const activeSourceFiles = [
  ...allSourceFiles,
  ...listFiles("", ".css").filter((file) => !file.startsWith("tests/")),
]

function unique(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean)))
}

function extractExportedSymbols(source: string): string[] {
  const symbols = [
    ...source.matchAll(/export\s+(?:function|const|class)\s+([A-Z][A-Za-z0-9_]*)/g),
    ...source.matchAll(/export\s+const\s+([A-Z][A-Za-z0-9_]*):\s*React\.FC/g),
    ...source.matchAll(/export\s*\{([^}]+)\}/g),
  ].map((match) => match[1])

  const expandedSymbols = symbols.flatMap((symbol) =>
    symbol.split(",").map((part) => part.trim().split(/\s+as\s+/).at(-1)?.trim() ?? ""),
  )

  return unique(expandedSymbols)
}

function normalizedModulePath(modulePath: string): string {
  return modulePath.replace(/\\/g, "/").replace(/\.(tsx?|jsx?)$/, "")
}

function normalizeSegments(path: string): string {
  const segments = path.split("/")
  const normalized: string[] = []

  for (const segment of segments) {
    if (!segment || segment === ".") {
      continue
    }
    if (segment === "..") {
      normalized.pop()
      continue
    }
    normalized.push(segment)
  }

  return normalized.join("/")
}

function dirname(file: string): string {
  return file.split("/").slice(0, -1).join("/")
}

function resolveModulePath(importerFile: string, modulePath: string): string {
  const normalized = normalizedModulePath(modulePath)

  if (normalized === "@components") {
    return "components"
  }
  if (normalized.startsWith("@components/")) {
    return normalized.replace(/^@components/, "components")
  }
  if (normalized === "@ui") {
    return "components/ui"
  }
  if (normalized.startsWith("@ui/")) {
    return normalized.replace(/^@ui/, "components/ui")
  }
  if (normalized.startsWith(".")) {
    return normalizeSegments(`${dirname(importerFile)}/${normalized}`)
  }

  return normalized.replace(/^src\//, "")
}

function resolveSourceFile(importerFile: string, modulePath: string): string | null {
  const resolvedModule = resolveModulePath(importerFile, modulePath)
  const candidates = [
    resolvedModule,
    `${resolvedModule}.ts`,
    `${resolvedModule}.tsx`,
    `${resolvedModule}/index.ts`,
    `${resolvedModule}/index.tsx`,
  ]

  return candidates.find((candidate) => sourceFileSet.has(candidate)) ?? null
}

function parsedImports(source: string): Array<{ typeOnly: boolean; modulePath: string }> {
  return [...source.matchAll(/import\s+(type\s+)?([\s\S]*?)\s+from\s+["']([^"']+)["']/g)].map(
    (match) => ({
      typeOnly: Boolean(match[1]),
      modulePath: match[3],
    }),
  )
}

function parsedDynamicImports(source: string): string[] {
  return [...source.matchAll(/import\(\s*["']([^"']+)["']\s*\)/g)].map((match) => match[1])
}

function parsedRuntimeReExports(source: string): string[] {
  return [...source.matchAll(/export\s+(type\s+)?(?:\*|\{[\s\S]*?\})\s+from\s+["']([^"']+)["']/g)]
    .filter((match) => !match[1])
    .map((match) => match[2])
}

function parsedModuleSpecifiers(source: string): string[] {
  return unique([
    ...parsedImports(source).map((entry) => entry.modulePath),
    ...parsedDynamicImports(source),
    ...[...source.matchAll(/export\s+(?:type\s+)?(?:\*|\{[\s\S]*?\})\s+from\s+["']([^"']+)["']/g)]
      .map((match) => match[1]),
  ])
}

function stripSourceExtension(file: string): string {
  return file.replace(/\.(tsx?|css)$/, "")
}

function forbiddenModulePaths(): Set<string> {
  return new Set([
    ...FORBIDDEN_REMOVED_COMPONENT_FILES,
    ...FORBIDDEN_REMOVED_CSS_FILES,
  ].map(stripSourceExtension))
}

function containsForbiddenSymbol(source: string, symbol: string): boolean {
  return new RegExp(`\\b[A-Za-z0-9_]*${symbol}[A-Za-z0-9_]*\\b`).test(source)
}

function extractCssSelectorClasses(css: string): string[] {
  return [...css.matchAll(/\.(-?[_a-zA-Z][-_a-zA-Z0-9]*)/g)].map((match) => match[1])
}

function extractStringLiteralClassTokens(source: string): string[] {
  return [...source.matchAll(/["'`]([^"'`]*?(?:today-header|mini-cards-grid|mini-card|hero-card|day-prediction-card|turning-points-list)[^"'`]*)["'`]/g)]
    .flatMap((match) => match[1].split(/\s+/))
    .map((token) => token.trim().replace(/[{}()[\],:;]+$/g, ""))
    .filter(Boolean)
}

function matchesForbiddenCssSelector(token: string, selectorPrefix: string): boolean {
  return token === selectorPrefix || token.startsWith(`${selectorPrefix}__`) || token.startsWith(`${selectorPrefix}--`)
}

function isAllowedActiveCssSelector(file: string, selectorPrefix: string): boolean {
  return ALLOWED_ACTIVE_CSS_SELECTOR_OWNERS.get(selectorPrefix)?.has(file) ?? false
}

function runtimeDependencies(file: string): string[] {
  const source = readFrontendFile(file)
  const staticImports = parsedImports(source)
    .filter((entry) => !entry.typeOnly)
    .map((entry) => entry.modulePath)
  const modulePaths = [...staticImports, ...parsedDynamicImports(source), ...parsedRuntimeReExports(source)]

  return unique(modulePaths.map((modulePath) => resolveSourceFile(file, modulePath) ?? ""))
}

function runtimeRootFiles(): string[] {
  const entrypoints = ["main.tsx"]

  for (const entrypoint of entrypoints) {
    expect(sourceFileSet.has(entrypoint)).toBe(true)
  }

  return entrypoints
}

function reachableRuntimeFiles(): Set<string> {
  const reachable = new Set<string>()
  const pending = [...runtimeRootFiles()]

  while (pending.length > 0) {
    const file = pending.pop()
    if (!file || reachable.has(file)) {
      continue
    }

    reachable.add(file)

    for (const dependency of runtimeDependencies(file)) {
      if (!reachable.has(dependency)) {
        pending.push(dependency)
      }
    }
  }

  return reachable
}

const runtimeReachableFiles = reachableRuntimeFiles()

describe("component-usage guards", () => {
  it("detecte les exports aliases et ignore les occurrences sans import runtime", () => {
    expect(extractExportedSymbols('export { AppLayout as AppShell } from "../layouts/AppLayout"')).toContain(
      "AppShell",
    )

    expect(
      parsedImports('const label = "AppShell";\n// AppShell\nimport { Other } from "@components"').some(
        (entry) => entry.modulePath.includes("AppShell"),
      ),
    ).toBe(false)
    expect(parsedImports('import type { DailyInsightCardType } from "../hooks/useDailyInsights"')[0]).toMatchObject({
      typeOnly: true,
      modulePath: "../hooks/useDailyInsights",
    })
  })

  it("classe exactement les composants conserves sans consommateur runtime direct", () => {
    for (const entry of COMPONENT_USAGE_EXCEPTIONS) {
      expect(entry.file).not.toContain("*")
      expect(ALLOWED_CLASSIFICATIONS).toContain(entry.classification)
      expect(entry.exports.length).toBeGreaterThan(0)
      expect(entry.owner.trim()).not.toBe("")
      expect(entry.evidence.trim()).not.toBe("")
      expect(entry.exitCondition.trim()).not.toBe("")
      expect(readFrontendFile(entry.file)).toContain(entry.exports[0])
    }

    const allowed = new Set(COMPONENT_USAGE_EXCEPTIONS.map((entry) => entry.file))
    const candidates = componentFiles().filter((file) => {
      const source = readFrontendFile(file)
      const symbols = extractExportedSymbols(source)
      return symbols.length > 0 && !runtimeReachableFiles.has(file)
    })

    expect(candidates.filter((file) => !allowed.has(file))).toEqual([])
  })

  it("bloque la reintroduction des composants test-only supprimes par CS-119", () => {
    const files = new Set(componentFiles())
    const cssFiles = new Set(listFiles("components", ".css"))
    const testFiles = new Set([
      ...listFiles("tests", ".ts"),
      ...listFiles("tests", ".tsx"),
    ])
    const allowlistEntries = new Set(COMPONENT_USAGE_EXCEPTIONS.map((entry) => entry.file))

    for (const file of FORBIDDEN_REMOVED_COMPONENT_FILES) {
      expect(files.has(file)).toBe(false)
      expect(allowlistEntries.has(file)).toBe(false)
    }
    for (const file of FORBIDDEN_REMOVED_CSS_FILES) {
      expect(cssFiles.has(file)).toBe(false)
    }
    for (const file of FORBIDDEN_REMOVED_TEST_FILES) {
      expect(testFiles.has(file)).toBe(false)
    }
  })

  it("scanne les sources actives contre les symboles, aliases et selecteurs CS-119", () => {
    const removedModulePaths = forbiddenModulePaths()
    const forbiddenReferences: string[] = []

    for (const file of activeSourceFiles) {
      const source = readFrontendFile(file)

      if (file.endsWith(".ts") || file.endsWith(".tsx")) {
        for (const symbol of FORBIDDEN_REMOVED_COMPONENT_SYMBOLS) {
          if (containsForbiddenSymbol(source, symbol)) {
            forbiddenReferences.push(`${file}:symbol:${symbol}`)
          }
        }

        for (const modulePath of parsedModuleSpecifiers(source)) {
          const resolved = resolveModulePath(file, modulePath)
          if (removedModulePaths.has(resolved) || removedModulePaths.has(stripSourceExtension(resolved))) {
            forbiddenReferences.push(`${file}:module:${modulePath}`)
          }
        }
      }

      const cssTokens = file.endsWith(".css")
        ? extractCssSelectorClasses(source)
        : extractStringLiteralClassTokens(source)

      for (const selectorPrefix of FORBIDDEN_REMOVED_CSS_SELECTOR_PREFIXES) {
        if (isAllowedActiveCssSelector(file, selectorPrefix)) {
          continue
        }

        const matchingToken = cssTokens.find((token) => matchesForbiddenCssSelector(token, selectorPrefix))
        if (matchingToken) {
          forbiddenReferences.push(`${file}:css-selector:${matchingToken}`)
        }
      }
    }

    expect(forbiddenReferences).toEqual([])
  })
})
