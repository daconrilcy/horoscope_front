import { describe, expect, it } from "vitest"

import * as astralApi from "../api/astral"
import { routes } from "../app/routes"
import { navItems } from "../ui/nav"

function collectPaths(routeList: typeof routes): string[] {
  return routeList.flatMap((route) => {
    const currentPath = route.path ? [route.path] : []
    const childPaths = route.children ? collectPaths(route.children as typeof routes) : []
    return [...currentPath, ...childPaths]
  })
}

describe("Astral externalization guardrails", () => {
  it("retire les routes produit non supportees pour le moment", () => {
    const paths = collectPaths(routes)

    expect(paths).not.toContain("chat")
    expect(paths).not.toContain("chat/:conversationId")
    expect(paths).not.toContain("consultations")
    expect(paths).not.toContain("ai-generations")
    expect(paths).not.toContain("prompts")
    expect(paths).toContain("natal")
    expect(paths).toContain("dashboard")
  })

  it("retire chat et consultations de la navigation", () => {
    const navKeys = navItems.map((item) => item.key)

    expect(navKeys).not.toContain("chat")
    expect(navKeys).not.toContain("consultations")
    expect(navKeys).toContain("today")
    expect(navKeys).toContain("natal")
  })

  it("expose une souscription SSE backend authentifiee", () => {
    expect(typeof astralApi.useAstralJobEvents).toBe("function")
  })
})
