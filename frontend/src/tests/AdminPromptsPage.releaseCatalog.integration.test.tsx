import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { RouterProvider } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { createTestMemoryRouter } from "../app/router"
import { ThemeProvider } from "../state/ThemeProvider"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

vi.mock("../pages/admin/PersonasAdmin", () => ({
  PersonasAdmin: () => <div data-testid="personas-admin-mock">Personas tab</div>,
}))

function makeJsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

const MANIFEST_ENTRY_ID = "chat:chat_default:premium:fr-FR"

/** Fetch minimal pour AdminGuard + onglet release + passage catalogue (catalogue vide, resolved 404). */
function makeReleaseToCatalogFetchMock() {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) {
      return makeJsonResponse({
        data: {
          id: 99,
          role: "admin",
          email: "admin@example.com",
          created_at: "2025-01-01T00:00:00Z",
        },
      })
    }
    if (url.includes("/v1/billing/subscription")) {
      return makeJsonResponse({ data: null })
    }
    if (url.includes("/v1/entitlements/me")) {
      return makeJsonResponse({ data: { features: [] } })
    }
    if (url.includes("/v1/admin/llm/catalog") && !url.includes("/resolved") && !url.includes("/execute-sample")) {
      return makeJsonResponse({
        data: [],
        meta: {
          total: 0,
          page: 1,
          page_size: 25,
          sort_by: "feature",
          sort_order: "asc",
          freshness_window_minutes: 120,
          facets: {},
        },
      })
    }
    if (url.endsWith("/v1/admin/llm/use-cases")) {
      return makeJsonResponse({ data: [] })
    }
    if (url.includes("/v1/admin/llm/release-snapshots/timeline")) {
      return makeJsonResponse({
        data: [
          {
            event_type: "monitoring",
            snapshot_id: "11111111-1111-1111-1111-111111111111",
            snapshot_version: "v2",
            occurred_at: "2026-04-15T08:00:00Z",
            current_status: "active",
            release_health_status: "monitoring",
            status_history: [{ status: "monitoring" }],
            reason: "Monitoring healthy.",
            from_snapshot_id: null,
            to_snapshot_id: "11111111-1111-1111-1111-111111111111",
            manifest_entry_count: 2,
            proof_summaries: [],
          },
          {
            event_type: "rolled_back",
            snapshot_id: "22222222-2222-2222-2222-222222222222",
            snapshot_version: "v1",
            occurred_at: "2026-04-14T08:00:00Z",
            current_status: "archived",
            release_health_status: "rolled_back",
            status_history: [{ status: "rolled_back" }],
            reason: "Rollback executed.",
            from_snapshot_id: "11111111-1111-1111-1111-111111111111",
            to_snapshot_id: "22222222-2222-2222-2222-222222222222",
            manifest_entry_count: 1,
            proof_summaries: [],
          },
        ],
      })
    }
    if (url.includes("/v1/admin/llm/release-snapshots/diff")) {
      return makeJsonResponse({
        data: {
          from_snapshot_id: "22222222-2222-2222-2222-222222222222",
          to_snapshot_id: "11111111-1111-1111-1111-111111111111",
          entries: [
            {
              manifest_entry_id: MANIFEST_ENTRY_ID,
              category: "changed",
              assembly_changed: true,
              execution_profile_changed: false,
              output_contract_changed: false,
              from_snapshot_id: "22222222-2222-2222-2222-222222222222",
              to_snapshot_id: "11111111-1111-1111-1111-111111111111",
            },
          ],
        },
      })
    }
    if (url.includes("/v1/admin/llm/catalog/") && url.includes("/resolved")) {
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }
    return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
  })
}

function renderPromptsApp(initialEntries: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  const router = createTestMemoryRouter(initialEntries)
  const view = render(
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </QueryClientProvider>
    </ThemeProvider>,
  )
  return { ...view, router }
}

describe("AdminPromptsPage — navigation release → catalogue (intégration route)", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "ResizeObserver",
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    )
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
    localStorage.setItem("lang", "fr")
  })

  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
    localStorage.removeItem("lang")
  })

  it("après clic « Ouvrir dans le catalogue », bascule vers /admin/prompts/catalog et conserve l'entrée manifeste sélectionnée", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    vi.stubGlobal("fetch", makeReleaseToCatalogFetchMock())

    const { router } = renderPromptsApp(["/admin/prompts/release"])

    await waitFor(() => {
      expect(screen.getByRole("region", { name: "Investigation release snapshots" })).toBeInTheDocument()
    })

    const catalogBtn = await screen.findByRole("button", {
      name: `Ouvrir l'entrée canonique ${MANIFEST_ENTRY_ID} dans le catalogue`,
    })
    await userEvent.click(catalogBtn)

    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/admin/prompts/catalog")
    })

    await waitFor(() => {
      expect(screen.getByRole("link", { name: "Catalogue canonique" })).toHaveAttribute("aria-current", "page")
    })

    const detail = screen.getByRole("complementary", { name: "Détail catalogue entrée" })
    const summary = within(detail).getByRole("region", { name: "Résumé" })
    await waitFor(() => {
      expect(within(summary).getByText(/Entrée hors page courante/)).toBeInTheDocument()
    })
    expect(within(summary).getByRole("code")).toHaveTextContent(MANIFEST_ENTRY_ID)
  })
})
