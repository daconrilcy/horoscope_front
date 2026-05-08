// Teste les garde-fous d'architecture des pages React avec des exceptions exactes.
import {
  Children,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from "react"
import path from "node:path"
import { describe, expect, it } from "vitest"
import type { RouteObject } from "react-router-dom"

import { routes } from "../app/routes"
import { LandingRedirect } from "../app/guards/LandingRedirect"
import { AppLayout } from "../layouts/AppLayout"
import { AuthLayout } from "../layouts/AuthLayout"
import { LandingLayout } from "../layouts/LandingLayout"
import { RootLayout } from "../layouts/RootLayout"
import {
  frontendRoot,
  listFiles,
  readFrontendFile,
} from "./design-system-policy"
import {
  DIRECT_API_PAGE_EXCEPTIONS,
  FORBIDDEN_ADMIN_BARREL_EXPORTS,
  FORBIDDEN_PUBLIC_ROUTE_ALIASES,
  PAGE_LAYOUT_OWNER_CLASSIFICATIONS,
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

function routeElementType(route: RouteObject) {
  return isValidElement(route.element) ? route.element.type : undefined
}

function routeHasElementType(
  route: RouteObject,
  elementType: ReactElement["type"],
): boolean {
  if (!isValidElement(route.element)) {
    return false
  }

  if (route.element.type === elementType) {
    return true
  }

  return reactNodeHasElementType(route.element.props.children, elementType)
}

function reactNodeHasElementType(
  node: ReactNode,
  elementType: ReactElement["type"],
): boolean {
  return Children.toArray(node).some((child) => {
    if (!isValidElement(child)) {
      return false
    }

    return (
      child.type === elementType ||
      reactNodeHasElementType(child.props.children, elementType)
    )
  })
}

function rootRoute(): RouteObject {
  const route = routes.find(
    (candidate) =>
      candidate.path === "/" && routeElementType(candidate) === RootLayout,
  )
  expect(route).toBeDefined()
  return route as RouteObject
}

function rootChildren(): RouteObject[] {
  return rootRoute().children ?? []
}

function normalizeRoutePath(path: string): string {
  if (path === "*") {
    return "*"
  }
  return `/${path}`.replace(/\/+/g, "/").replace(/\/$/, "") || "/"
}

function joinRoutePath(parentPath: string, childPath: string): string {
  if (childPath === "*") {
    return "*"
  }
  return normalizeRoutePath(`${parentPath}/${childPath}`)
}

function collectRoutePaths(
  routeList: RouteObject[],
  parentPath = "",
): Set<string> {
  return new Set(
    routeList.flatMap((route) => {
      const routePath = route.index
        ? normalizeRoutePath(parentPath)
        : joinRoutePath(parentPath, route.path ?? "")
      return [routePath, ...collectRoutePaths(route.children ?? [], routePath)]
    }),
  )
}

function forbiddenUnknownClassification(): string {
  return ["unk", "nown"].join("")
}

function anonymousDecisionTokens(): string[] {
  return ["A definir", "Aucun owner runtime actif"]
}

function pageSymbol(file: string): string {
  return file.split("/").at(-1)?.replace(/\.tsx$/, "") ?? ""
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function pageModulePath(file: string): string {
  return file.replace(/\.tsx$/, "")
}

function normalizeFrontendPath(value: string): string {
  return value.replace(/\\/g, "/").replace(/\.tsx?$/, "")
}

function extractModuleSpecifiers(source: string): string[] {
  return [
    ...source.matchAll(
      /\b(?:import\s*\(|import\s+[^'";]+?\s+from\s+|export\s+[^'";]+?\s+from\s*)['"]([^'"]+)['"]/g,
    ),
  ].map((match) => match[1])
}

function resolveModuleSpecifier(
  importerFile: string,
  specifier: string,
): string {
  if (specifier.startsWith("@pages/")) {
    return normalizeFrontendPath(specifier.replace(/^@pages\//, "pages/"))
  }

  if (specifier === "@pages") {
    return "pages/index"
  }

  if (!specifier.startsWith(".")) {
    return normalizeFrontendPath(specifier)
  }

  const importerDirectory = path.dirname(path.join(frontendRoot, importerFile))
  const resolved = path.resolve(importerDirectory, specifier)
  return normalizeFrontendPath(path.relative(frontendRoot, resolved))
}

function moduleSpecifierTargetsPage(
  importerFile: string,
  specifier: string,
  candidateFile: string,
): boolean {
  return resolveModuleSpecifier(importerFile, specifier) === pageModulePath(candidateFile)
}

function sourceReattachesPage(
  source: string,
  importerFile: string,
  symbol: string,
  file: string,
): boolean {
  const escapedSymbol = escapeRegExp(symbol)
  const importsCandidate = extractModuleSpecifiers(source).some((specifier) =>
    moduleSpecifierTargetsPage(importerFile, specifier, file),
  )
  const jsxPattern = new RegExp(`<${escapedSymbol}\\b`)

  return importsCandidate || jsxPattern.test(source)
}

function runtimeSourceFiles(): string[] {
  return [...listFiles("", ".tsx"), ...listFiles("", ".ts")].filter(
    (file) => !file.startsWith("tests/") && !file.startsWith("test/"),
  )
}

function isStructuredStoryKey(value: string): boolean {
  return /^CS-\d{3}-[a-z0-9-]+$/.test(value)
}

function isIsoDate(value: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(value)
}

describe("page-architecture", () => {
  it("bloque les pages @ts-nocheck non declarees", () => {
    const allowed = exactFiles(TS_NOCHECK_PAGE_EXCEPTIONS)
    const offenders = pageFiles().filter(
      (file) =>
        readFrontendFile(file).includes("@ts-nocheck") && !allowed.has(file),
    )

    expect(offenders).toEqual([])
  })

  it("impose que les exceptions @ts-nocheck restent exactes", () => {
    const staleEntries = TS_NOCHECK_PAGE_EXCEPTIONS.filter(
      (entry) =>
        !pageFiles().includes(entry.file) ||
        !readFrontendFile(entry.file).includes("@ts-nocheck"),
    ).map((entry) => entry.file)

    expect(staleEntries).toEqual([])
  })

  it("bloque les appels apiFetch directs non declares dans les pages", () => {
    const allowed = exactFiles(DIRECT_API_PAGE_EXCEPTIONS)
    const offenders = pageFiles().filter(
      (file) =>
        readFrontendFile(file).includes("apiFetch(") && !allowed.has(file),
    )

    expect(offenders).toEqual([])
  })

  it("impose que les exceptions apiFetch direct restent exactes", () => {
    const staleEntries = DIRECT_API_PAGE_EXCEPTIONS.filter(
      (entry) =>
        !pageFiles().includes(entry.file) ||
        !readFrontendFile(entry.file).includes("apiFetch("),
    ).map((entry) => entry.file)

    expect(staleEntries).toEqual([])
  })

  it("bloque les alias publics retires dans la table de routes", () => {
    const routesSource = readFrontendFile("app/routes.tsx")
    const offenders = FORBIDDEN_PUBLIC_ROUTE_ALIASES.filter((routePath) =>
      hasRoutePath(routesSource, routePath),
    )

    expect(offenders).toEqual([])
  })

  it("bloque les exports admin retires du barrel de pages", () => {
    const adminBarrel = readFrontendFile("pages/admin/index.ts")
    const offenders = FORBIDDEN_ADMIN_BARREL_EXPORTS.filter((symbol) =>
      adminBarrel.includes(symbol),
    )

    expect(offenders).toEqual([])
  })

  it("impose un owner et un seuil exact aux pages volumineuses", () => {
    const allowedByFile = new Map(
      PAGE_SIZE_EXCEPTIONS.map((entry) => [entry.file, entry]),
    )
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

  it("monte RootLayout comme ancetre maitre de la route racine", () => {
    expect(routeElementType(rootRoute())).toBe(RootLayout)
    expect(rootChildren().length).toBeGreaterThan(0)
  })

  it("conserve AppLayout comme shell secondaire sous RootLayout sans reprendre le fond maitre", () => {
    const protectedBranch = rootChildren().find((route) =>
      routeHasElementType(route, AppLayout),
    )
    const appLayoutSource = readFrontendFile("layouts/AppLayout.tsx")

    expect(protectedBranch).toBeDefined()
    expect(appLayoutSource).not.toContain("StarfieldBackground")
    expect(appLayoutSource).not.toContain("app-shell app-bg")
    expect(appLayoutSource).not.toContain("app-bg-container")
  })

  it("monte la landing sous LandingLayout et bloque le bypass local", () => {
    const landingBranch = rootChildren().find(
      (route) => routeElementType(route) === LandingLayout,
    )
    const landingIndex = landingBranch?.children?.find(
      (route) => route.index === true,
    )
    const landingRedirectSource = readFrontendFile(
      "app/guards/LandingRedirect.tsx",
    )
    const landingWrapperOwners = listFiles("", ".tsx").filter(
      (file) =>
        readFrontendFile(file).includes('className="landing-layout"') &&
        file !== "layouts/LandingLayout.tsx",
    )

    expect(landingBranch).toBeDefined()
    expect(routeElementType(landingIndex as RouteObject)).toBe(LandingRedirect)
    expect(landingRedirectSource).not.toContain("LandingLayout.css")
    expect(landingRedirectSource).not.toContain("ScopedLandingPage")
    expect(landingWrapperOwners).toEqual([])
  })

  it("monte les routes auth sous AuthLayout sans routes directes au niveau maitre", () => {
    const authBranch = rootChildren().find(
      (route) => routeElementType(route) === AuthLayout,
    )
    const authPaths = new Set(
      (authBranch?.children ?? []).map((route) => route.path),
    )
    const directAuthRoutes = rootChildren().filter(
      (route) => route.path === "login" || route.path === "register",
    )

    expect(authBranch).toBeDefined()
    expect(authPaths).toEqual(new Set(["login", "register"]))
    expect(directAuthRoutes).toEqual([])
  })

  it("classe chaque fichier page avec un owner exact", () => {
    const classified = new Map(
      PAGE_LAYOUT_OWNER_CLASSIFICATIONS.map((entry) => [entry.file, entry]),
    )
    const missing = pageFiles().filter((file) => !classified.has(file))
    const stale = [...classified.keys()].filter(
      (file) => !pageFiles().includes(file),
    )
    const invalid = PAGE_LAYOUT_OWNER_CLASSIFICATIONS.filter(
      (entry) =>
        !entry.owner ||
        !entry.reason ||
        !entry.exit ||
        entry.classification.includes(forbiddenUnknownClassification()) ||
        entry.file.includes("**") ||
        entry.file.endsWith("/"),
    ).map((entry) => entry.file)

    expect(missing).toEqual([])
    expect(stale).toEqual([])
    expect(invalid).toEqual([])
  })

  it("bloque le routage des pages qui attendent une decision produit", () => {
    const blockedFiles = PAGE_LAYOUT_OWNER_CLASSIFICATIONS.filter(
      (entry) => entry.classification === "needs-user-decision",
    )
    const routesSource = readFrontendFile("app/routes.tsx")
    const routedBlockedFiles = blockedFiles
      .filter((entry) => routesSource.includes(pageSymbol(entry.file)))
      .map((entry) => entry.file)

    expect(blockedFiles.length).toBeGreaterThan(0)
    expect(routedBlockedFiles).toEqual([])
  })

  it("bloque le routage et le rattachement runtime des pages candidates mortes", () => {
    const deadCandidates = PAGE_LAYOUT_OWNER_CLASSIFICATIONS.filter(
      (entry) => entry.classification === "dead/unmounted-page-candidate",
    )
    const runtimeFiles = runtimeSourceFiles()
    const reattachedCandidates = deadCandidates.flatMap((entry) => {
      const symbol = pageSymbol(entry.file)
      const importingFiles = runtimeFiles.filter((file) => {
        if (file === entry.file) {
          return false
        }
        return sourceReattachesPage(
          readFrontendFile(file),
          file,
          symbol,
          entry.file,
        )
      })

      return importingFiles.map((file) => `${entry.file}:${file}`)
    })

    expect(deadCandidates.length).toBeGreaterThan(0)
    expect(reattachedCandidates).toEqual([])
  })

  it("detecte les imports relatifs imbriques des pages candidates mortes", () => {
    expect(
      sourceReattachesPage(
        'const Testimonials = lazy(() => import("./sections/TestimonialsSection"))',
        "pages/landing/LandingPage.tsx",
        "TestimonialsSection",
        "pages/landing/sections/TestimonialsSection.tsx",
      ),
    ).toBe(true)
    expect(
      sourceReattachesPage(
        "export { HomePage as LegacyHome } from './HomePage'",
        "pages/index.ts",
        "HomePage",
        "pages/HomePage.tsx",
      ),
    ).toBe(true)
    expect(
      sourceReattachesPage(
        'const LegacyHome = lazy(() => import("@pages/HomePage"))',
        "app/routes.tsx",
        "HomePage",
        "pages/HomePage.tsx",
      ),
    ).toBe(true)
  })

  it("exige une decision sourcee pour les pages bloquees ou candidates mortes", () => {
    const decisionEntries = PAGE_LAYOUT_OWNER_CLASSIFICATIONS.filter(
      (entry) =>
        entry.classification === "needs-user-decision" ||
        entry.classification === "dead/unmounted-page-candidate",
    )
    const anonymousTokens = anonymousDecisionTokens()
    const invalidDecisionEntries = decisionEntries
      .filter((entry) => {
        const decisionText = `${entry.owner} ${entry.reason} ${entry.exit}`
        const hasAnonymousToken = anonymousTokens.some((token) =>
          decisionText.includes(token),
        )
        const hasSource = Boolean(
          entry.decisionSource &&
            isStructuredStoryKey(entry.decisionSource.story) &&
            isIsoDate(entry.decisionSource.decidedOn) &&
            entry.decisionSource.owner === entry.owner &&
            entry.decisionSource.evidence.includes(
              entry.decisionSource.story,
            ) &&
            entry.decisionSource.evidence.endsWith(".md"),
        )
        const hasExit =
          entry.classification === "needs-user-decision"
            ? Boolean(entry.expiresOn && isIsoDate(entry.expiresOn))
            : Boolean(entry.removalStory)

        return hasAnonymousToken || !hasSource || !hasExit
      })
      .map((entry) => entry.file)

    expect(invalidDecisionEntries).toEqual([])
  })

  it("verifie que les routes classees comme routees sont presentes dans l'arbre", () => {
    const routePaths = collectRoutePaths(rootChildren())
    const absentRoutes = PAGE_LAYOUT_OWNER_CLASSIFICATIONS.filter(
      (entry) =>
        (entry.classification === "routed-page" ||
          entry.classification === "nested-routed-page") &&
        entry.route &&
        entry.route !== "*" &&
        !entry.route.includes(" et "),
    )
      .filter((entry) => !routePaths.has(entry.route ?? ""))
      .map((entry) => `${entry.file}:${entry.route}`)

    expect(absentRoutes).toEqual([])
  })
})
