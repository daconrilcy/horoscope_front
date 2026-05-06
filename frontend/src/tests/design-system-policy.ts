// Helpers de tests statiques pour garder la discipline design-system frontend.
import fs from "fs"
import path from "path"

export const frontendRoot = path.resolve(__dirname, "..")

export function readFrontendFile(relativePath: string): string {
  return fs.readFileSync(path.join(frontendRoot, relativePath), "utf-8")
}

export function listFiles(dir: string, extension: string): string[] {
  const base = path.join(frontendRoot, dir)
  const results: string[] = []

  for (const entry of fs.readdirSync(base, { withFileTypes: true })) {
    const fullPath = path.join(base, entry.name)
    const relativePath = path.relative(frontendRoot, fullPath).replace(/\\/g, "/")
    if (entry.isDirectory()) {
      results.push(...listFiles(relativePath, extension))
    } else if (entry.isFile() && entry.name.endsWith(extension)) {
      results.push(relativePath)
    }
  }

  return results
}

export function extractCssVariableDeclarations(css: string): string[] {
  return [...css.matchAll(/(?:^|[;{]\s*)(--[a-zA-Z0-9_-]+)\s*:/gm)].map((match) => match[1])
}

export function extractLegacySelectors(css: string): string[] {
  return [...css.matchAll(/\.([a-zA-Z0-9_-]*legacy[a-zA-Z0-9_-]*)/g)].map((match) => `.${match[1]}`)
}

export function extractLegacyOrAliasSelectors(css: string): string[] {
  return [...css.matchAll(/\.([a-zA-Z0-9_-]*(?:legacy|alias)[a-zA-Z0-9_-]*)/g)].map((match) => `.${match[1]}`)
}

export function extractCssFallbacks(css: string): Array<{ token: string; literal: string }> {
  return [...css.matchAll(/var\(\s*(--[a-zA-Z0-9_-]+)\s*,\s*([^)]+)\)/g)].map((match) => ({
    token: match[1],
    literal: match[2].trim(),
  }))
}

export function extractCssComments(css: string): string[] {
  return [...css.matchAll(/\/\*[\s\S]*?\*\//g)].map((match) => match[0])
}

/** Extrait les variables CSS consommees via var() pour les gardes d'ownership. */
export function extractCssVariableUsages(css: string): string[] {
  return [...css.matchAll(/var\(\s*(--[a-zA-Z0-9_-]+)/g)].map((match) => match[1])
}

export function collectCssFallbacks(): Array<{ file: string; token: string; literal: string }> {
  return listFiles("", ".css").flatMap((file) =>
    extractCssFallbacks(readFrontendFile(file)).map((fallback) => ({ file, ...fallback })),
  )
}

export function parseCssFallbackRegistry(
  markdown: string,
): Array<{ file: string; token: string; literal: string; status: string; reason: string; exitCondition: string }> {
  return markdown
    .split(/\r?\n/)
    .filter((line) => line.startsWith("| `frontend/src/"))
    .map((line) => {
      const cells = line.split("|").slice(1, -1).map((cell) => cell.trim())
      const [file, token, literal, status, reason, exitCondition] = cells.map((cell) =>
        cell.replace(/^`|`$/g, ""),
      )

      return {
        file: file.replace(/^frontend\/src\//, ""),
        token,
        literal,
        status,
        reason,
        exitCondition,
      }
    })
}

export function parseRegistryPatterns(markdown: string): string[] {
  return [...markdown.matchAll(/\|\s*`([^`]+)`\s*\|/g)].map((match) => match[1])
}

/** Ligne normalisee du registre des namespaces de tokens CSS. */
export type TokenNamespaceRegistryEntry = {
  namespace: string
  status: string
  owner: string
  canonicalTarget: string
  exitCondition: string
}

/** Parse le registre markdown afin que les tests statiques suivent la source canonique. */
export function parseTokenNamespaceRegistry(markdown: string): TokenNamespaceRegistryEntry[] {
  return markdown
    .split(/\r?\n/)
    .filter((line) => line.startsWith("| `--"))
    .map((line) => {
      const [namespace, status, owner, canonicalTarget, exitCondition] = line
        .split("|")
        .slice(1, -1)
        .map((cell) => cell.trim().replace(/^`|`$/g, ""))

      return {
        namespace,
        status,
        owner,
        canonicalTarget,
        exitCondition,
      }
    })
}

export function patternMatches(pattern: string, value: string): boolean {
  if (pattern.endsWith("*")) {
    return value.startsWith(pattern.slice(0, -1))
  }
  return value === pattern
}

export function hasRegistryMatch(patterns: string[], value: string): boolean {
  return patterns.some((pattern) => patternMatches(pattern, value))
}

export function extractStyleAttributes(tsx: string): string[] {
  return [...tsx.matchAll(/style=\{([^}\n]*(?:\{[^]*?\})?[^}]*)\}/g)].map((match) =>
    match[0].replace(/\s+/g, " ").trim(),
  )
}

export function collectInlineStyles(): Array<{ file: string; style: string }> {
  return listFiles("", ".tsx").flatMap((file) =>
    extractStyleAttributes(readFrontendFile(file)).map((style) => ({ file, style })),
  )
}

export function toStableJson(value: unknown): string {
  return JSON.stringify(value)
}
