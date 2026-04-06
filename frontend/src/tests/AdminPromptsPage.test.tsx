import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminPromptsPage } from "../pages/admin/AdminPromptsPage"
import { setAccessToken, clearAccessToken } from "../utils/authToken"

vi.mock("../pages/admin/PersonasAdmin", () => ({
  PersonasAdmin: () => <div data-testid="personas-admin-mock">Personas tab</div>,
}))

function makeJsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <AdminPromptsPage />
    </QueryClientProvider>,
  )
}

describe("AdminPromptsPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("renders use cases, diff and targeted rollback", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat",
              description: "Conversation astrologique",
              persona_strategy: "required",
              safety_profile: "astrology",
              allowed_persona_ids: ["persona-1"],
              active_prompt_version_id: "prompt-2",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/llm/personas")) {
        return makeJsonResponse({
          data: [{ id: "persona-1", name: "Guide astral", enabled: true }],
        })
      }

      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts")) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-2",
              use_case_key: "chat",
              status: "published",
              developer_prompt: "Line one updated\nLine two",
              model: "gpt-5-mini",
              temperature: 0.3,
              max_output_tokens: 900,
              fallback_use_case_key: null,
              created_by: "99",
              created_at: "2026-04-05T08:00:00Z",
              published_at: "2026-04-05T09:00:00Z",
            },
            {
              id: "prompt-1",
              use_case_key: "chat",
              status: "archived",
              developer_prompt: "Line one original\nLine two",
              model: "gpt-5-mini",
              temperature: 0.4,
              max_output_tokens: 900,
              fallback_use_case_key: null,
              created_by: "42",
              created_at: "2026-04-04T08:00:00Z",
              published_at: "2026-04-04T09:00:00Z",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/llm/use-cases/chat/rollback")) {
        expect(init?.method).toBe("POST")
        expect(init?.body).toBe(JSON.stringify({ target_version_id: "prompt-1" }))
        return makeJsonResponse({
          data: {
            id: "prompt-1",
            use_case_key: "chat",
            status: "published",
            developer_prompt: "Line one original\nLine two",
            model: "gpt-5-mini",
            temperature: 0.4,
            max_output_tokens: 900,
            fallback_use_case_key: null,
            created_by: "42",
            created_at: "2026-04-04T08:00:00Z",
            published_at: "2026-04-06T08:00:00Z",
          },
        })
      }

      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })

    vi.stubGlobal("fetch", fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Prompts & Personas" })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getAllByText("Chat")).toHaveLength(2)
    })

    expect(screen.getAllByText(/Guide astral/)).toHaveLength(2)
    expect(screen.getAllByText(/Line one updated/)).toHaveLength(2)
    expect(screen.getByLabelText("Comparer avec une version")).toBeInTheDocument()
    expect(screen.getByRole("table", { name: "Diff prompt" })).toBeInTheDocument()
    expect(screen.getByText("Line one original")).toBeInTheDocument()

    const rollbackButton = screen.getByRole("button", { name: "Rollback" })
    await userEvent.click(rollbackButton)

    await waitFor(() => {
      expect(screen.getByRole("dialog", { name: "Confirmer le rollback" })).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("button", { name: "Rollback vers cette version" }))

    await waitFor(() => {
      expect(screen.getByText(/Rollback effectue vers/)).toBeInTheDocument()
    })
  })

  it("switches to personas tab", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({ data: [] })
      }
      if (url.endsWith("/v1/admin/llm/personas")) {
        return makeJsonResponse({ data: [] })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()

    await userEvent.click(screen.getByRole("tab", { name: "Personas" }))

    expect(screen.getByTestId("personas-admin-mock")).toBeInTheDocument()
  })
})
