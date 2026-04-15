import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminPromptsPage } from "../pages/admin/AdminPromptsPage"
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

  it("affiche le catalogue canonique et les badges de source", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        if (url.includes("/resolved")) {
          return makeJsonResponse({
            data: {
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              feature: "chat",
              subfeature: "chat_default",
              plan: "premium",
              locale: "fr-FR",
              assembly_id: "assembly-1",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: { id: "tpl-2", content: "subfeature prompt" },
                plan_rules: { ref: "premium_depth", content: "plan rules prompt" },
                persona_block: { id: "persona-1", name: "Luna", content: "persona prompt" },
                hard_policy: { safety_profile: "astrology", content: "hard policy prompt" },
                execution_profile: {
                  id: "profile-1",
                  name: "default",
                  provider: "openai",
                  model: "gpt-5",
                  reasoning: "medium",
                  verbosity: "balanced",
                  provider_params: { max_output_tokens: 1200 },
                },
              },
              transformation_pipeline: {
                assembled_prompt: "assembled",
                post_injectors_prompt: "post",
                rendered_prompt: "rendered",
              },
              resolved_result: {
                provider_messages: {
                  system_hard_policy: "hard policy prompt",
                  developer_content_rendered: "rendered",
                  persona_block: "persona prompt",
                  execution_parameters: { max_output_tokens: 1200 },
                },
                placeholders: [
                  {
                    name: "locale",
                    status: "resolved",
                    classification: "required",
                    resolution_source: "runtime_context",
                    reason: "from_context",
                    safe_to_display: true,
                    value_preview: "fr-FR",
                  },
                ],
                context_quality_handled_by_template: false,
                context_quality_instruction_injected: false,
                context_compensation_status: "not_needed",
                source_of_truth_status: "active_snapshot",
                active_snapshot_id: "snapshot-1",
                active_snapshot_version: "v1",
                manifest_entry_id: "chat:chat_default:premium:fr-FR",
              },
            },
          })
        }
        return makeJsonResponse({
          data: [
            {
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              feature: "chat",
              subfeature: "chat_default",
              plan: "premium",
              locale: "fr-FR",
              assembly_id: "assembly-1",
              assembly_status: "published",
              execution_profile_id: "profile-1",
              execution_profile_ref: "profile-1",
              output_contract_ref: "contract-1",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              provider: "openai",
              model: "gpt-5",
              source_of_truth_status: "active_snapshot",
              release_health_status: "monitoring",
              catalog_visibility_status: "visible",
              runtime_signal_status: "fresh",
              execution_path_kind: "nominal",
              context_compensation_status: "none",
              max_output_tokens_source: "execution_profile",
            },
          ],
          meta: {
            total: 1,
            page: 1,
            page_size: 25,
            sort_by: "feature",
            sort_order: "asc",
            freshness_window_minutes: 120,
            facets: {
              feature: ["chat"],
              subfeature: ["chat_default"],
              plan: ["premium"],
              locale: ["fr-FR"],
              provider: ["openai"],
              source_of_truth_status: ["active_snapshot"],
              assembly_status: ["published"],
              release_health_status: ["monitoring"],
              catalog_visibility_status: ["visible"],
            },
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({ data: [] })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeInTheDocument()
    })

    expect(screen.getByRole("tab", { name: "Catalogue canonique" })).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    expect(screen.getAllByText("active_snapshot").length).toBeGreaterThan(0)
    expect(screen.getAllByText(/monitoring/).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/fresh/).length).toBeGreaterThan(0)
    expect(screen.getByLabelText("Tri catalogue")).toBeInTheDocument()
    expect(screen.getByLabelText("Ordre tri catalogue")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Resolved Prompt Assembly" })).toBeInTheDocument()
    })
    expect(screen.getByText("Pipeline de transformation")).toBeInTheDocument()
    expect(screen.getByText("Resultat resolu")).toBeInTheDocument()
    expect(screen.getAllByText("Execution profile").length).toBeGreaterThan(0)
    expect(screen.getByText("safe_to_display")).toBeInTheDocument()
    expect(screen.getByText("runtime_context")).toBeInTheDocument()
  })

  it("affiche l'onglet historique legacy avec rollback", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
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
            facets: {},
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat",
              description: "Conversation astrologique",
              persona_strategy: "required",
              safety_profile: "astrology",
              allowed_persona_ids: [],
              active_prompt_version_id: "prompt-2",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts")) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-2",
              use_case_key: "chat",
              status: "published",
              developer_prompt: "x",
              model: "gpt-5",
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
              developer_prompt: "line one old\nline two",
              model: "gpt-5",
              temperature: 0.3,
              max_output_tokens: 900,
              fallback_use_case_key: null,
              created_by: "98",
              created_at: "2026-04-04T08:00:00Z",
              published_at: "2026-04-04T09:00:00Z",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/rollback")) {
        expect(init?.method).toBe("POST")
        return makeJsonResponse({
          data: {
            id: "prompt-2",
            use_case_key: "chat",
            status: "published",
            developer_prompt: "x",
            model: "gpt-5",
            temperature: 0.3,
            max_output_tokens: 900,
            fallback_use_case_key: null,
            created_by: "99",
            created_at: "2026-04-05T08:00:00Z",
            published_at: "2026-04-05T09:00:00Z",
          },
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()
    await userEvent.click(screen.getByRole("tab", { name: "Historique legacy" }))

    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Rollback" }).length).toBeGreaterThan(0)
    })
    expect(screen.getByRole("table", { name: "Diff prompt legacy" })).toBeInTheDocument()

    await userEvent.click(screen.getAllByRole("button", { name: "Rollback" })[0])
    const dialog = await screen.findByRole("dialog", { name: "Confirmer le rollback legacy" })
    await userEvent.click(within(dialog).getByRole("button", { name: /^Rollback$/ }))
    await waitFor(() => {
      expect(screen.getByText(/Rollback effectue vers/)).toBeInTheDocument()
    })
  })
})
