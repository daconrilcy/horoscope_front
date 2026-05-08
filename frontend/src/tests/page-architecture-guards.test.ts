// Teste les garde-fous d'architecture des pages React avec des exceptions exactes.
import { describe, expect, it } from "vitest"

import { listFiles, readFrontendFile } from "./design-system-policy"
import {
  DIRECT_API_PAGE_EXCEPTIONS,
  FORBIDDEN_ADMIN_BARREL_EXPORTS,
  FORBIDDEN_PUBLIC_ROUTE_ALIASES,
  PAGE_SIZE_EXCEPTIONS,
  TS_NOCHECK_PAGE_EXCEPTIONS,
} from "./page-architecture-allowlist"

function pageFiles(): string[] {
  return listFiles("pages", ".tsx")
}

function exactFiles(entries: Array<{ file: string }>): Set<string> {
  return new Set(entries.map((entry) => entry.file))
}

function hasRoutePath(source: string, routePath: string): boolean {
  const pathLiteral = routePath.slice(1).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  return new RegExp(`\\bpath\\s*:\\s*['"]${pathLiteral}['"]`).test(source)
}

describe("page-architecture", () => {
  it("bloque les pages @ts-nocheck non declarees", () => {
    const allowed = exactFiles(TS_NOCHECK_PAGE_EXCEPTIONS)
    const offenders = pageFiles().filter((file) => readFrontendFile(file).includes("@ts-nocheck") && !allowed.has(file))

    expect(offenders).toEqual([])
  })

  it("impose que les exceptions @ts-nocheck restent exactes", () => {
    const staleEntries = TS_NOCHECK_PAGE_EXCEPTIONS.filter(
      (entry) => !pageFiles().includes(entry.file) || !readFrontendFile(entry.file).includes("@ts-nocheck"),
    ).map((entry) => entry.file)

    expect(staleEntries).toEqual([])
  })

  it("bloque les appels apiFetch directs non declares dans les pages", () => {
    const allowed = exactFiles(DIRECT_API_PAGE_EXCEPTIONS)
    const offenders = pageFiles().filter((file) => readFrontendFile(file).includes("apiFetch(") && !allowed.has(file))

    expect(offenders).toEqual([])
  })

  it("impose que les exceptions apiFetch direct restent exactes", () => {
    const staleEntries = DIRECT_API_PAGE_EXCEPTIONS.filter(
      (entry) => !pageFiles().includes(entry.file) || !readFrontendFile(entry.file).includes("apiFetch("),
    ).map((entry) => entry.file)

    expect(staleEntries).toEqual([])
  })

  it("bloque les alias publics retires dans la table de routes", () => {
    const routesSource = readFrontendFile("app/routes.tsx")
    const offenders = FORBIDDEN_PUBLIC_ROUTE_ALIASES.filter((routePath) => hasRoutePath(routesSource, routePath))

    expect(offenders).toEqual([])
  })

  it("bloque les exports admin retires du barrel de pages", () => {
    const adminBarrel = readFrontendFile("pages/admin/index.ts")
    const offenders = FORBIDDEN_ADMIN_BARREL_EXPORTS.filter((symbol) => adminBarrel.includes(symbol))

    expect(offenders).toEqual([])
  })

  it("impose un owner et un seuil exact aux pages volumineuses", () => {
    const allowedByFile = new Map(PAGE_SIZE_EXCEPTIONS.map((entry) => [entry.file, entry]))
    const offenders = pageFiles().flatMap((file) => {
      const lineCount = readFrontendFile(file).split(/\r?\n/).length
      if (lineCount <= 700) {
        return []
      }
      const entry = allowedByFile.get(file)
      if (!entry || !entry.owner || !entry.exit || lineCount > entry.maxLines) {
        return [`${file}:${lineCount}`]
      }
      return []
    })

    expect(offenders).toEqual([])
  })

  it("impose que les exceptions de taille restent exactes", () => {
    const staleEntries = PAGE_SIZE_EXCEPTIONS.filter((entry) => {
      if (!pageFiles().includes(entry.file)) {
        return true
      }
      return readFrontendFile(entry.file).split(/\r?\n/).length <= 700
    }).map((entry) => entry.file)

    expect(staleEntries).toEqual([])
  })
})
