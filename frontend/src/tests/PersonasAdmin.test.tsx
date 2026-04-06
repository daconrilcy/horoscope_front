import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { PersonasAdmin } from "../pages/admin/PersonasAdmin"
import { setAccessToken, clearAccessToken } from "../utils/authToken"

function makeJsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <PersonasAdmin />
    </QueryClientProvider>,
  )
}

describe("PersonasAdmin", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("renders persona list, detail and deactivation modal", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith("/v1/admin/llm/personas")) {
        return makeJsonResponse({
          data: [
            {
              id: "persona-1",
              name: "Guide astral",
              enabled: true,
              description: "Voix premium",
              tone: "warm",
              verbosity: "medium",
              style_markers: ["tutoiement"],
              boundaries: ["pas de fatalisme"],
              allowed_topics: [],
              disallowed_topics: [],
              formatting: { sections: true, bullets: false, emojis: false },
              created_at: "2026-04-05T09:00:00Z",
              updated_at: "2026-04-06T09:00:00Z",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/llm/personas/persona-1") && init?.method === "PATCH") {
        return makeJsonResponse({
          data: {
            id: "persona-1",
            name: "Guide astral",
            enabled: false,
            description: "Voix premium",
            tone: "warm",
            verbosity: "medium",
            style_markers: ["tutoiement"],
            boundaries: ["pas de fatalisme"],
            allowed_topics: [],
            disallowed_topics: [],
            formatting: { sections: true, bullets: false, emojis: false },
            created_at: "2026-04-05T09:00:00Z",
            updated_at: "2026-04-06T09:00:00Z",
          },
        })
      }

      if (url.endsWith("/v1/admin/llm/personas/persona-1")) {
        return makeJsonResponse({
          data: {
            persona: {
              id: "persona-1",
              name: "Guide astral",
              enabled: true,
              description: "Voix premium",
              tone: "warm",
              verbosity: "medium",
              style_markers: ["tutoiement"],
              boundaries: ["pas de fatalisme"],
              allowed_topics: [],
              disallowed_topics: [],
              formatting: { sections: true, bullets: false, emojis: false },
              created_at: "2026-04-05T09:00:00Z",
              updated_at: "2026-04-06T09:00:00Z",
            },
            use_cases: ["chat"],
            affected_users_count: 3,
          },
        })
      }

      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })

    vi.stubGlobal("fetch", fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Personas astrologues" })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getAllByText("Guide astral").length).toBeGreaterThan(0)
    })

    await waitFor(() => {
      expect(screen.getByText("chat")).toBeInTheDocument()
    })
    expect(screen.getByText("Utilisateurs impactés")).toBeInTheDocument()
    expect(screen.getByText("3")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Désactiver" }))

    await waitFor(() => {
      expect(screen.getByRole("dialog", { name: "Désactiver la persona" })).toBeInTheDocument()
    })

    expect(screen.getByText(/Cette persona est utilisée par 3 utilisateurs actifs/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Confirmer la désactivation" }))

    await waitFor(() => {
      expect(screen.getByText("Persona Guide astral désactivée.")).toBeInTheDocument()
    })
  })

  it("shows an error when persona update fails", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith("/v1/admin/llm/personas")) {
        return makeJsonResponse({
          data: [
            {
              id: "persona-1",
              name: "Guide astral",
              enabled: true,
              description: "Voix premium",
              tone: "warm",
              verbosity: "medium",
              style_markers: ["tutoiement"],
              boundaries: ["pas de fatalisme"],
              allowed_topics: [],
              disallowed_topics: [],
              formatting: { sections: true, bullets: false, emojis: false },
              created_at: "2026-04-05T09:00:00Z",
              updated_at: "2026-04-06T09:00:00Z",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/llm/personas/persona-1") && init?.method === "PATCH") {
        return makeJsonResponse(
          {
            error: {
              code: "persona_update_failed",
              message: "Le backend a refusé la mise à jour.",
            },
          },
          409,
        )
      }

      if (url.endsWith("/v1/admin/llm/personas/persona-1")) {
        return makeJsonResponse({
          data: {
            persona: {
              id: "persona-1",
              name: "Guide astral",
              enabled: true,
              description: "Voix premium",
              tone: "warm",
              verbosity: "medium",
              style_markers: ["tutoiement"],
              boundaries: ["pas de fatalisme"],
              allowed_topics: [],
              disallowed_topics: [],
              formatting: { sections: true, bullets: false, emojis: false },
              created_at: "2026-04-05T09:00:00Z",
              updated_at: "2026-04-06T09:00:00Z",
            },
            use_cases: ["chat"],
            affected_users_count: 1,
          },
        })
      }

      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })

    vi.stubGlobal("fetch", fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Désactiver" })).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("button", { name: "Désactiver" }))
    await userEvent.click(screen.getByRole("button", { name: "Confirmer la désactivation" }))

    await waitFor(() => {
      expect(screen.getByText(/Impossible de mettre à jour la persona/)).toBeInTheDocument()
    })

    expect(screen.getByRole("dialog", { name: "Désactiver la persona" })).toBeInTheDocument()
  })
})
