import { afterEach, describe, expect, it, vi } from "vitest"

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
  afterEach(() => {
    vi.unstubAllGlobals()
  })

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

  it("ne soumet pas de job Astral avec un token local inutilisable", async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal("fetch", fetchMock)

    await expect(
      astralApi.submitAstralJob("not-a-jwt", {
        product: "natal_simplified",
        plan: "free",
        client_request_id: "natal-request-1",
      }),
    ).rejects.toMatchObject({ code: "unauthorized", status: 401 })

    expect(fetchMock).not.toHaveBeenCalled()
  })

  it("annote les submits Astral avec la version client et la source courante", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          data: { run_id: "run-1", status: "queued" },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    )
    vi.stubGlobal("fetch", fetchMock)
    const token = [
      btoa(JSON.stringify({ alg: "HS256", typ: "JWT" })),
      btoa(JSON.stringify({ sub: "1", exp: Math.floor(Date.now() / 1000) + 3600 })),
      "sig",
    ].join(".")

    await astralApi.submitAstralJob(token, {
      product: "natal_simplified",
      plan: "free",
      client_request_id: "natal-request-1",
    })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/v1/astral/jobs"),
      expect.objectContaining({
        headers: expect.objectContaining({
          "X-Astral-Client-Version": astralApi.ASTRAL_CLIENT_VERSION,
          "X-Client-Request-Id": "natal-request-1",
        }),
      }),
    )
  })
})
