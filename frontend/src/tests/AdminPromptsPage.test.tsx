import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminPromptsPage } from "../pages/admin/AdminPromptsPage"
import { toUtcIsoFromDateTimeInput } from "../api/adminPrompts"
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
  const view = render(
    <QueryClientProvider client={queryClient}>
      <AdminPromptsPage />
    </QueryClientProvider>,
  )
  return { ...view, queryClient }
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
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: "assembly_preview",
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
      expect(screen.getByRole("heading", { name: "Assembly prompt résolue" })).toBeInTheDocument()
    })
    expect(screen.getByText("Prompts")).toBeInTheDocument()
    expect(screen.getByText("Données d'exemple")).toBeInTheDocument()
    expect(screen.getByText("Retour LLM")).toBeInTheDocument()
    expect(screen.getByLabelText("Mode d'inspection du détail")).toBeInTheDocument()
    expect(screen.getByText(/Mode: Assembly/)).toBeInTheDocument()
    expect(screen.getByText(/Prévisualisation statique/)).toBeInTheDocument()
    expect(screen.getAllByText("Execution profile").length).toBeGreaterThan(0)
    expect(screen.getByText("Affichable")).toBeInTheDocument()
    expect(screen.getByText("Contexte runtime")).toBeInTheDocument()
    expect(screen.getByText("assembled prompt")).toBeInTheDocument()
    expect(screen.getByText("post injectors prompt")).toBeInTheDocument()
    expect(screen.getByText("rendered prompt")).toBeInTheDocument()
    expect(screen.getByText("system hard policy")).toBeInTheDocument()
    expect(screen.getByText("developer content")).toBeInTheDocument()
    expect(screen.getAllByText("persona block").length).toBeGreaterThan(0)
    expect(screen.getByText(/Sortie d'exécution live/)).toBeInTheDocument()
    expect(screen.getByText(/Vide pour l'instant/)).toBeInTheDocument()
    expect(screen.getByText("Construction logique")).toBeInTheDocument()
    expect(screen.getByText("manifest_entry_id")).toBeInTheDocument()
    expect(screen.getByText("composition_sources")).toBeInTheDocument()
    expect(screen.getByText("transformation_pipeline")).toBeInTheDocument()
    expect(screen.getByText("provider_messages")).toBeInTheDocument()
    expect(screen.getByText("runtime inputs")).toBeInTheDocument()
    expect(screen.getByText("feature template")).toBeInTheDocument()
    expect(screen.getByText("subfeature template")).toBeInTheDocument()
    expect(screen.getByText("plan rules")).toBeInTheDocument()
    expect(screen.getAllByText("persona block").length).toBeGreaterThan(0)
    expect(screen.getByText("hard policy")).toBeInTheDocument()
    expect(screen.getByText("sample payloads")).toBeInTheDocument()
    expect(screen.getByText(/message system/)).toBeInTheDocument()
    expect(screen.getByText(/message persona/)).toBeInTheDocument()
  })

  it("passe le sample payload sélectionné dans la runtime preview", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    const fetchSpy = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/sample-payloads")) {
        return makeJsonResponse({
          data: {
            items: [
              {
                id: "sample-1",
                name: "sample natal",
                feature: "chat",
                locale: "fr-FR",
                description: null,
                is_default: true,
                is_active: true,
                created_at: "2026-04-10T10:00:00Z",
                updated_at: "2026-04-10T10:00:00Z",
              },
            ],
            recommended_default_id: "sample-1",
          },
        })
      }
      if (url.includes("/v1/admin/llm/catalog")) {
        if (url.includes("/resolved")) {
          return makeJsonResponse({
            data: {
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              feature: "chat",
              subfeature: "chat_default",
              plan: "premium",
              locale: "fr-FR",
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: url.includes("inspection_mode=runtime_preview") ? "runtime_preview" : "assembly_preview",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: null,
                plan_rules: null,
                persona_block: null,
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
                  persona_block: "",
                  execution_parameters: { max_output_tokens: 1200 },
                },
                placeholders: url.includes("inspection_mode=runtime_preview")
                  ? [
                      {
                        name: "last_user_msg",
                        status: "blocking_missing",
                        classification: "required",
                        resolution_source: "missing_required",
                        reason: "required_placeholder_missing",
                        safe_to_display: false,
                        value_preview: null,
                      },
                    ]
                  : [],
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
            facets: {},
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({ data: [] })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderPage()
    await waitFor(() => {
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await userEvent.selectOptions(screen.getByLabelText("Mode d'inspection du détail"), "runtime_preview")
    await waitFor(() => {
      expect(screen.getByLabelText("Sélecteur sample payload runtime")).toBeInTheDocument()
    })
    await userEvent.selectOptions(screen.getByLabelText("Sélecteur sample payload runtime"), "sample-1")
    await waitFor(() => {
      const calls = fetchSpy.mock.calls.map(([input]) => String(input))
      expect(
        calls.some(
          (callUrl) =>
            callUrl.includes("/resolved?") &&
            callUrl.includes("inspection_mode=runtime_preview") &&
            callUrl.includes("sample_payload_id=sample-1"),
        ),
      ).toBe(true)
    })
    expect(screen.getByText("Bloquant (manquant)")).toBeInTheDocument()
  })

  it("réaligne le sample payload runtime si la sélection n’est plus dans la liste (P2)", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    const item = (id: string, name: string, isDefault: boolean) => ({
      id,
      name,
      feature: "chat",
      locale: "fr-FR",
      description: null,
      is_default: isDefault,
      is_active: true,
      created_at: "2026-04-10T10:00:00Z",
      updated_at: "2026-04-10T10:00:00Z",
    })
    let listPayload = {
      items: [item("sample-1", "défaut", true), item("sample-2", "second", false)],
      recommended_default_id: "sample-1",
    }
    const fetchSpy = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/sample-payloads") && !url.match(/sample-payloads\/[^/?]+$/)) {
        return makeJsonResponse({ data: listPayload })
      }
      if (url.includes("/v1/admin/llm/catalog")) {
        if (url.includes("/resolved")) {
          return makeJsonResponse({
            data: {
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              feature: "chat",
              subfeature: "chat_default",
              plan: "premium",
              locale: "fr-FR",
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: url.includes("inspection_mode=runtime_preview") ? "runtime_preview" : "assembly_preview",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: null,
                plan_rules: null,
                persona_block: null,
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
                  persona_block: "",
                  execution_parameters: { max_output_tokens: 1200 },
                },
                placeholders: [],
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
            facets: {},
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({ data: [] })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    const { queryClient } = renderPage()
    await waitFor(() => {
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await userEvent.selectOptions(screen.getByLabelText("Mode d'inspection du détail"), "runtime_preview")
    await waitFor(() => {
      expect(screen.getByLabelText("Sélecteur sample payload runtime")).toBeInTheDocument()
    })
    await userEvent.selectOptions(screen.getByLabelText("Sélecteur sample payload runtime"), "sample-2")
    await waitFor(() => {
      const calls = fetchSpy.mock.calls.map(([input]) => String(input))
      expect(calls.some((u) => u.includes("sample_payload_id=sample-2"))).toBe(true)
    })

    listPayload = {
      items: [item("sample-1", "défaut", true)],
      recommended_default_id: "sample-1",
    }
    await queryClient.invalidateQueries({ queryKey: ["admin-llm-sample-payloads"] })

    await waitFor(() => {
      const select = screen.getByLabelText("Sélecteur sample payload runtime") as HTMLSelectElement
      expect(select.value).toBe("sample-1")
    })
    await waitFor(() => {
      const calls = fetchSpy.mock.calls.map(([input]) => String(input))
      const resolvedWithDefault = calls.filter(
        (u) => u.includes("/resolved?") && u.includes("sample_payload_id=sample-1"),
      )
      expect(resolvedWithDefault.length).toBeGreaterThan(0)
    })
  })

  it("affiche un libellé FR et le message serveur en repli quand la runtime preview échoue", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/sample-payloads")) {
        return makeJsonResponse({
          data: {
            items: [
              {
                id: "sample-1",
                name: "sample natal",
                feature: "chat",
                locale: "fr-FR",
                description: null,
                is_default: true,
                is_active: true,
                created_at: "2026-04-10T10:00:00Z",
                updated_at: "2026-04-10T10:00:00Z",
              },
            ],
            recommended_default_id: "sample-1",
          },
        })
      }
      if (url.includes("/v1/admin/llm/catalog")) {
        if (url.includes("/resolved")) {
          if (url.includes("inspection_mode=runtime_preview") && url.includes("sample_payload_id=sample-1")) {
            return makeJsonResponse({
              error: {
                code: "sample_payload_inactive",
                message: "sample payload is inactive and cannot be used for runtime preview",
                details: { sample_payload_id: "sample-1" },
              },
            }, 422)
          }
          return makeJsonResponse({
            data: {
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              feature: "chat",
              subfeature: "chat_default",
              plan: "premium",
              locale: "fr-FR",
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: url.includes("inspection_mode=runtime_preview") ? "runtime_preview" : "assembly_preview",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: null,
                plan_rules: null,
                persona_block: null,
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
                  persona_block: "",
                  execution_parameters: { max_output_tokens: 1200 },
                },
                placeholders: [],
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
            facets: {},
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
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await userEvent.selectOptions(screen.getByLabelText("Mode d'inspection du détail"), "runtime_preview")
    await waitFor(() => {
      expect(screen.getByLabelText("Sélecteur sample payload runtime")).toBeInTheDocument()
    })
    await userEvent.selectOptions(screen.getByLabelText("Sélecteur sample payload runtime"), "sample-1")
    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument()
    })
    expect(
      screen.getByText(
        "Ce sample payload est inactif. Choisissez un autre payload ou réactivez-le dans le catalogue.",
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText("sample payload is inactive and cannot be used for runtime preview"),
    ).toBeInTheDocument()
  })

  it("bascule en fallback texte quand le graphe devient trop dense", async () => {
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
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: "assembly_preview",
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
                placeholders: Array.from({ length: 16 }).map((_, index) => ({
                  name: `placeholder_${index}`,
                  status: index % 2 === 0 ? "expected_missing_in_preview" : "fallback_used",
                  classification: "required",
                  resolution_source: index % 2 === 0 ? "static_preview_gap" : "fallback",
                  reason: "from_context",
                  safe_to_display: true,
                  value_preview: `value_${index}`,
                })),
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
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await waitFor(() => {
      expect(screen.getByText(/Graphe simplifié en vue texte/)).toBeInTheDocument()
    })
    expect(screen.getByText(/runtime=8, fallback=8, sample=0/)).toBeInTheDocument()
  })

  it("classe les sources selon le contrat backend (runtime/fallback/sample)", async () => {
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
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: "assembly_preview",
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
                    name: "preview_gap",
                    status: "expected_missing_in_preview",
                    classification: "required",
                    resolution_source: "static_preview_gap",
                    reason: "needs_runtime_values",
                    safe_to_display: false,
                    value_preview: null,
                  },
                  {
                    name: "missing_required_runtime",
                    status: "blocking_missing",
                    classification: "required",
                    resolution_source: "missing_required",
                    reason: "missing_runtime",
                    safe_to_display: false,
                    value_preview: null,
                  },
                  {
                    name: "fallback_optional",
                    status: "fallback_used",
                    classification: "optional",
                    resolution_source: "fallback",
                    reason: "from_context",
                    safe_to_display: true,
                    value_preview: "value",
                  },
                  {
                    name: "missing_optional_only",
                    status: "optional_missing",
                    classification: "optional",
                    resolution_source: "missing_optional",
                    reason: "optional_placeholder_missing",
                    safe_to_display: false,
                    value_preview: null,
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
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await waitFor(() => {
      expect(screen.getByText("runtime:2 · fallback:1 · sample:0")).toBeInTheDocument()
    })
    expect(screen.getByText("Manquant optionnel")).toBeInTheDocument()
  })

  it("affiche des messages de premier rang pour preview partielle, erreur et données d'exemple vides", async () => {
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
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: "runtime_preview",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: null,
                plan_rules: null,
                persona_block: null,
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
                  persona_block: "",
                  execution_parameters: { max_output_tokens: 1200 },
                  render_error_kind: "static_preview_incomplete",
                  render_error: "missing runtime placeholder",
                },
                placeholders: [],
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
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await waitFor(() => {
      expect(screen.getByText(/Prévisualisation partielle :/)).toBeInTheDocument()
    })
    expect(screen.getByText(/Aucune donnée d'exemple disponible/)).toBeInTheDocument()
    expect(screen.getByText(/Sortie d'exécution live/)).toBeInTheDocument()
    expect(screen.getAllByRole("status").length).toBeGreaterThan(0)
  })

  it("annonce les états critiques avec des rôles ARIA adaptés", async () => {
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
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: "live_execution",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: null,
                plan_rules: null,
                persona_block: null,
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
                  persona_block: "",
                  execution_parameters: { max_output_tokens: 1200 },
                  render_error_kind: "execution_failure",
                  render_error: "provider timeout",
                },
                placeholders: [],
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
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    const alertMessage = await screen.findByRole("alert")
    expect(alertMessage).toHaveTextContent("Erreur détectée pendant l'inspection live")
    expect(screen.getAllByRole("status").length).toBeGreaterThan(0)
  })

  it("affiche une valeur vide quand elle est autorisée sans la marquer redacted", async () => {
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
              use_case_key: "chat_uc",
              context_quality: "full",
              assembly_id: "assembly-1",
              inspection_mode: "runtime_preview",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-1",
              active_snapshot_version: "v1",
              composition_sources: {
                feature_template: { id: "tpl-1", content: "feature prompt" },
                subfeature_template: null,
                plan_rules: null,
                persona_block: null,
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
                  persona_block: "",
                  execution_parameters: { max_output_tokens: 1200 },
                  render_error_kind: null,
                  render_error: null,
                },
                placeholders: [
                  {
                    name: "empty_but_visible",
                    status: "resolved",
                    classification: "string",
                    resolution_source: "runtime_context",
                    reason: "from_context",
                    safe_to_display: true,
                    value_preview: "",
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
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le detail" }))
    await waitFor(() => {
      expect(screen.getByText("empty_but_visible")).toBeInTheDocument()
    })
    expect(screen.getByText("Affichable")).toBeInTheDocument()
    expect(screen.getByText("Contexte runtime")).toBeInTheDocument()
    expect(screen.queryByText("redacted")).not.toBeInTheDocument()
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

  it("affiche l'historique release snapshot et le diff", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
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
              proof_summaries: [
                { proof_type: "qualification", status: "present", verdict: "go", generated_at: "2026-04-15T07:55:00Z", manifest_entry_id: "chat:chat_default:premium:fr-FR", correlated: true },
                { proof_type: "golden", status: "present", verdict: "pass", generated_at: "2026-04-15T07:56:00Z", manifest_entry_id: "chat:chat_default:premium:fr-FR", correlated: true },
                { proof_type: "smoke", status: "present", verdict: "pass", generated_at: "2026-04-15T07:57:00Z", manifest_entry_id: "chat:chat_default:premium:fr-FR", correlated: true },
                { proof_type: "readiness", status: "present", verdict: "valid", generated_at: "2026-04-15T07:57:00Z", manifest_entry_id: "chat:chat_default:premium:fr-FR", correlated: true },
              ],
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
                manifest_entry_id: "chat:chat_default:premium:fr-FR",
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
      if (url.includes("/v1/admin/llm/catalog/chat%3Achat_default%3Apremium%3Afr-FR/resolved")) {
        return makeJsonResponse({ data: {} })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()
    await userEvent.click(screen.getByRole("tab", { name: "Historique release" }))

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Timeline snapshots" })).toBeInTheDocument()
    })
    expect(screen.getByText(/qualification: go/)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Diff snapshot" })).toBeInTheDocument()
    })
    expect(screen.getByText("chat:chat_default:premium:fr-FR")).toBeInTheDocument()
  })

  it("affiche l'onglet consommation avec granularité, pagination serveur et axe canonique", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({ data: [] })
      }
      if (url.includes("/v1/admin/llm/consumption/canonical/drilldown")) {
        return makeJsonResponse({
          data: [
            {
              request_id: "req-1",
              timestamp: "2026-04-20T10:00:00Z",
              feature: "chat",
              subfeature: "chat_default",
              provider: "openai",
              active_snapshot_version: "release-1",
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              validation_status: "valid",
            },
          ],
          meta: { count: 1, limit: 50, order: "timestamp_desc" },
        })
      }
      if (url.includes("/v1/admin/llm/consumption/canonical")) {
        return makeJsonResponse({
          data: [
            {
              period_start_utc: "2026-04-20T00:00:00Z",
              granularity: "day",
              user_id: null,
              user_email: null,
              subscription_plan: null,
              feature: "chat",
              subfeature: "chat_default",
              request_count: 12,
              input_tokens: 1200,
              output_tokens: 600,
              total_tokens: 1800,
              estimated_cost: 1.23,
              avg_latency_ms: 240,
              error_rate: 0.05,
            },
          ],
          meta: {
            view: "feature",
            granularity: "day",
            count: 3,
            page: 1,
            page_size: 20,
            sort_by: "period_start_utc",
            sort_order: "desc",
            timezone: "UTC",
            default_granularity_behavior: "aggregated_by_selected_period",
          },
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()
    await userEvent.click(screen.getByRole("tab", { name: "Consommation" }))
    await userEvent.selectOptions(screen.getAllByRole("combobox")[0], "feature")
    await waitFor(() => {
      expect(screen.getByText(/Granularité par défaut: agrégé par période sélectionnée/)).toBeInTheDocument()
    })
    expect(screen.getByText("chat / chat_default")).toBeInTheDocument()
    expect(screen.queryByText("use_case")).not.toBeInTheDocument()
    expect(screen.getByText("Page 1")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Voir logs récents" }))
    await waitFor(() => {
      expect(screen.getByText("Drill-down appels récents (50 max)")).toBeInTheDocument()
    })
    expect(screen.getByText("req-1")).toBeInTheDocument()
  })

  it("convertit explicitement les bornes datetime-local en ISO UTC", () => {
    expect(toUtcIsoFromDateTimeInput("2026-04-22T10:30")).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:30:00\.000Z$/)
    expect(toUtcIsoFromDateTimeInput("2026-04-22T10:30")).not.toBe("2026-04-22T10:30")
    expect(toUtcIsoFromDateTimeInput("2026-04-22T10:30:00Z")).toBe("2026-04-22T10:30:00.000Z")
  })

  it("envoie les filtres temporels de consommation au format UTC dans la requete API", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchSpy = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({ data: [] })
      }
      if (url.includes("/v1/admin/llm/consumption/canonical")) {
        return makeJsonResponse({
          data: [],
          meta: {
            view: "user",
            granularity: "day",
            count: 0,
            page: 1,
            page_size: 20,
            sort_by: "period_start_utc",
            sort_order: "desc",
            timezone: "UTC",
            default_granularity_behavior: "aggregated_by_selected_period",
          },
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderPage()
    await userEvent.click(screen.getByRole("tab", { name: "Consommation" }))

    const dateInputs = Array.from(document.querySelectorAll("input[type='datetime-local']"))
    const fromInput = dateInputs[0]
    expect(fromInput).toBeDefined()
    await userEvent.type(fromInput as HTMLInputElement, "2026-04-22T10:30")

    const latestConsumptionCall = fetchSpy.mock.calls
      .map(([input]) => String(input))
      .filter((url) => url.includes("/v1/admin/llm/consumption/canonical"))
      .at(-1)

    expect(latestConsumptionCall).toBeTruthy()
    const parsedUrl = new URL(latestConsumptionCall as string)
    const fromUtc = parsedUrl.searchParams.get("from_utc")
    expect(fromUtc).toBeTruthy()
    expect(fromUtc).toMatch(/Z$/)
    expect(fromUtc).not.toBe("2026-04-22T10:30")
  })
})
