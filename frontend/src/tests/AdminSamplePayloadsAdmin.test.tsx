import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminSamplePayloadsAdmin } from "../pages/admin/AdminSamplePayloadsAdmin"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function makeJsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

function renderAdmin() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminSamplePayloadsAdmin seedFeature={null} seedLocale={null} />
    </QueryClientProvider>,
  )
}

describe("AdminSamplePayloadsAdmin", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("liste les sample payloads et appelle include_inactive quand la case est cochée", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    const fetchSpy = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: {
            total: 0,
            page: 1,
            page_size: 25,
            sort_by: "feature",
            sort_order: "asc",
            freshness_window_minutes: 120,
            facets: {
              feature: ["natal"],
              locale: ["fr-FR"],
            },
          },
        })
      }
      if (url.includes("/v1/admin/llm/sample-payloads")) {
        return makeJsonResponse({
          data: {
            items: [
              {
                id: "sp-1",
                name: "démo",
                feature: "natal",
                locale: "fr-FR",
                description: null,
                is_default: true,
                is_active: true,
                created_at: "2026-04-10T10:00:00Z",
                updated_at: "2026-04-10T10:00:00Z",
              },
            ],
            recommended_default_id: "sp-1",
          },
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderAdmin()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Échantillons runtime (sample payloads)" })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText("démo")).toBeInTheDocument()
    })

    const includeCalls = () =>
      fetchSpy.mock.calls.filter((call) => {
        const u = String(call[0])
        return u.includes("/v1/admin/llm/sample-payloads") && !u.includes("/sp-1")
      })

    expect(includeCalls().some((call) => String(call[0]).includes("include_inactive=true"))).toBe(true)

    const checkbox = screen.getByRole("checkbox", { name: "Afficher les sample payloads inactifs" })
    await userEvent.click(checkbox)
    await userEvent.click(checkbox)

    expect(
      includeCalls().some((call) => String(call[0]).includes("include_inactive=true")),
    ).toBe(true)
  })

  it("préremplit le payload JSON hors natal avec l’exemple suggéré et le bouton d’insertion", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    const fetchSpy = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: {
            total: 0,
            page: 1,
            page_size: 25,
            sort_by: "feature",
            sort_order: "asc",
            freshness_window_minutes: 120,
            facets: {
              feature: ["chat"],
              locale: ["fr-FR"],
            },
          },
        })
      }
      if (url.includes("/v1/admin/llm/sample-payloads")) {
        return makeJsonResponse({
          data: {
            items: [],
            recommended_default_id: null,
          },
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderAdmin()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Échantillons runtime (sample payloads)" })).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("button", { name: "Nouveau sample payload" }))

    const payloadField = (await screen.findByLabelText(/payload_json \(objet JSON, non vide\)/i)) as HTMLTextAreaElement
    expect(payloadField.value).toContain("chat_test")

    await userEvent.clear(payloadField)
    fireEvent.change(payloadField, { target: { value: "{}" } })

    await userEvent.click(screen.getByRole("button", { name: /Insérer l'exemple suggéré \(chat\)/i }))

    expect(payloadField.value).toContain("last_user_msg")
  })
})
