// Teste les garde-fous d'architecture des pages React avec des exceptions exactes.
import {
  Children,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from "react"
import { describe, expect, it } from "vitest"
import type { RouteObject } from "react-router-dom"

import { routes } from "../app/routes"
import { LandingRedirect } from "../app/guards/LandingRedirect"
import { AppLayout } from "../layouts/AppLayout"
import { AuthLayout } from "../layouts/AuthLayout"
import { LandingLayout } from "../layouts/LandingLayout"
import { RootLayout } from "../layouts/RootLayout"
import { listFiles, readFrontendFile } from "./design-system-policy"
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
      .filter((entry) => {
        const symbol = entry.file
          .split("/")
          .at(-1)
          ?.replace(/\.tsx$/, "")
        return Boolean(symbol && routesSource.includes(symbol))
      })
      .map((entry) => entry.file)

    expect(blockedFiles.length).toBeGreaterThan(0)
    expect(routedBlockedFiles).toEqual([])
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
