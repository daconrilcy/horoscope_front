import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { RouterProvider } from "react-router-dom"
import { createTestMemoryRouter } from "../app/router"
import { setAccessToken, clearAccessToken } from "../utils/authToken"
import { ThemeProvider } from "../state/ThemeProvider"
import { resolvePromptsTabFromPath } from "../pages/admin/AdminPromptsPage"

beforeEach(() => {
  localStorage.setItem("lang", "fr")

  class ResizeObserverMock {
    observe = vi.fn()
    unobserve = vi.fn()
    disconnect = vi.fn()
  }
  vi.stubGlobal("ResizeObserver", ResizeObserverMock)

  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  )
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
  clearAccessToken()
})

const EMPTY_CATALOG = {
  data: [],
  meta: {
    page: 1,
    total: 0,
    page_size: 25,
    freshness_window_minutes: 5,
    facets: {
      feature: [],
      subfeature: [],
      plan: [],
      locale: [],
      provider: [],
      source_of_truth_status: [],
      assembly_status: [],
      release_health_status: [],
      catalog_visibility_status: [],
    },
  },
}

function fetchInputToUrlString(input: RequestInfo | URL): string {
  if (typeof input === "string") {
    return input
  }
  if (input instanceof Request) {
    return input.url
  }
  if (input instanceof URL) {
    return input.href
  }
  return String(input)
}

function makeAdminPromptsFetchMock() {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = fetchInputToUrlString(input)
    if (url.endsWith("/v1/auth/me")) {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            id: 99,
            role: "admin",
            email: "admin@example.com",
            created_at: "2025-01-01T00:00:00Z",
          },
        }),
      }
    }
    if (url.includes("/v1/billing/subscription")) {
      return { ok: true, status: 200, json: async () => ({ data: null }) }
    }
    if (url.includes("/v1/entitlements/me")) {
      return { ok: true, status: 200, json: async () => ({ data: { features: [] } }) }
    }
    if (
      url.includes("/v1/admin/llm/catalog?") &&
      !url.includes("/resolved") &&
      !url.includes("/execute-sample")
    ) {
      return {
        ok: true,
        status: 200,
        json: async () => EMPTY_CATALOG,
      }
    }
    if (/\/v1\/admin\/llm\/personas\/?(?:\?|$)/.test(url)) {
      return { ok: true, status: 200, json: async () => ({ data: [] }) }
    }
    if (url.includes("/v1/admin/llm/use-cases/") && url.includes("/prompts")) {
      return { ok: true, status: 200, json: async () => ({ data: [] }) }
    }
    if (url.includes("/v1/admin/llm/use-cases") && !url.includes("/prompts")) {
      return { ok: true, status: 200, json: async () => ({ data: [] }) }
    }
    return { ok: false, status: 404, json: async () => ({ error: { code: "not_found", message: "not found" } }) }
  })
}

function renderApp(initialEntries: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })
  const router = createTestMemoryRouter(initialEntries)
  const result = render(
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </QueryClientProvider>
    </ThemeProvider>,
  )
  return { ...result, router }
}

function setupToken() {
  const payload = btoa(JSON.stringify({ sub: "99", role: "admin" }))
  setAccessToken(`x.${payload}.y`)
}

describe("resolvePromptsTabFromPath", () => {
  it("mappe les segments URL vers l’univers prompts", () => {
    expect(resolvePromptsTabFromPath("/admin/prompts")).toBe("catalog")
    expect(resolvePromptsTabFromPath("/admin/prompts/catalog")).toBe("catalog")
    expect(resolvePromptsTabFromPath("/admin/prompts/legacy")).toBe("legacy")
    expect(resolvePromptsTabFromPath("/admin/prompts/sample-payloads")).toBe("samplePayloads")
  })
})

describe("Admin prompts — routage dédié (story 70.1)", () => {
  it("redirige /admin/prompts vers le catalogue canonique", async () => {
    vi.stubGlobal("fetch", makeAdminPromptsFetchMock())
    setupToken()

    const { router } = renderApp(["/admin/prompts"])

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/admin/prompts/catalog")
    })
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeInTheDocument()
    })
  })

  it("redirige /admin/personas vers la route personas du domaine prompts", async () => {
    vi.stubGlobal("fetch", makeAdminPromptsFetchMock())
    setupToken()

    const { router: personasRouter } = renderApp(["/admin/personas"])

    await waitFor(() => {
      expect(personasRouter.state.location.pathname).toBe("/admin/prompts/personas")
    })
    await waitFor(() => {
      expect(screen.getByTestId("personas-admin-title")).toHaveTextContent("Personas astrologues")
    })
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Personas LLM" })).toBeInTheDocument()
    })
  })

  it("affiche un titre de page distinct sur /admin/prompts/legacy", async () => {
    vi.stubGlobal("fetch", makeAdminPromptsFetchMock())
    setupToken()

    renderApp(["/admin/prompts/legacy"])

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Historique LLM hors catalogue" })).toBeInTheDocument()
    })
  })
})
