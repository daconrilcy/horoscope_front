// Inventaire statique exact des composants sans consommateur runtime direct.
import { describe, expect, it } from "vitest"

import { listFiles, readFrontendFile } from "./design-system-policy"
import { COMPONENT_USAGE_EXCEPTIONS, type ComponentUsageClassification } from "./component-usage-allowlist"

const ALLOWED_CLASSIFICATIONS: ComponentUsageClassification[] = [
  "runtime-used",
  "public-library-export",
  "test-only",
  "remove",
  "needs-user-decision",
]

function componentFiles(): string[] {
  return listFiles("components", ".tsx").filter((file) => !file.endsWith(".test.tsx"))
}

const allSourceFiles = [".ts", ".tsx"].flatMap((extension) => listFiles("", extension))
  .filter((file) => !file.startsWith("tests/"))
  .filter((file) => !file.endsWith(".test.tsx"))
  .filter((file) => !file.endsWith(".test.ts"))

const sourceFileSet = new Set(allSourceFiles)

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
    expect(parsedImports('import type { MiniInsightCardType } from "../components/MiniInsightCard"')[0]).toMatchObject({
      typeOnly: true,
      modulePath: "../components/MiniInsightCard",
    })
    expect(runtimeReachableFiles.has("components/MiniInsightCard.tsx")).toBe(false)
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
})
