import { readFileSync } from "node:fs"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Navigate, Route, Routes } from "react-router-dom"

const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

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

function AdminPromptsRoutesFixture() {
  return (
    <Routes>
      <Route path="/admin/prompts" element={<AdminPromptsPage />}>
        <Route index element={<Navigate to="catalog" replace />} />
        <Route path="catalog" element={null} />
        <Route path="legacy" element={null} />
        <Route path="release" element={null} />
        <Route path="consumption" element={null} />
        <Route path="personas" element={null} />
        <Route path="sample-payloads" element={null} />
        <Route path="*" element={<Navigate to="catalog" replace />} />
      </Route>
    </Routes>
  )
}

function renderPage(initialEntry = "/admin/prompts/catalog") {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  const view = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={[initialEntry]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <AdminPromptsRoutesFixture />
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return { ...view, queryClient }
}

describe("AdminPromptsPage", () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    vi.stubGlobal(
      "ResizeObserver",
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    )
  })

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

    const { container } = renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeInTheDocument()
    })

    expect(container.querySelector(".admin-prompts-catalog-master-detail")).not.toBeNull()
    expect(screen.getByRole("link", { name: "Catalogue canonique" })).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    const catalogTable = screen.getByRole("table")
    expect(within(catalogTable).getAllByRole("columnheader")).toHaveLength(5)
    expect(screen.getByLabelText("Détail catalogue entrée")).toBeInTheDocument()
    expect(
      screen.getByText(/Sélectionnez une ligne du catalogue pour afficher le détail résolu/),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Réinitialiser les filtres" })).toBeInTheDocument()
    expect(screen.getByText("Snapshot actif (catalogue)")).toBeInTheDocument()
    expect(screen.getByText(/Surveillance · signal À jour · Visible/)).toBeInTheDocument()
    expect(screen.getByRole("navigation", { name: "Sections administration des prompts" })).toBeInTheDocument()
    expect(document.querySelector(".admin-prompts-catalog__health-cell")).not.toBeNull()
    expect(screen.getByLabelText("Tri catalogue")).toBeInTheDocument()
    expect(screen.getByLabelText("Ordre tri catalogue")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Mode d'inspection" })).toBeInTheDocument()
    })
    expect(screen.getByLabelText("Résumé")).toBeInTheDocument()
    expect(screen.getByLabelText("Actions")).toBeInTheDocument()
    expect(screen.getByText("Prompts")).toBeInTheDocument()
    expect(screen.getByText("Placeholders")).toBeInTheDocument()
    expect(screen.getByText("Retour LLM")).toBeInTheDocument()
    expect(screen.getByLabelText("Mode d'inspection du détail")).toBeInTheDocument()
    expect(screen.getByText(/Mode : Préassemblage/)).toBeInTheDocument()
    expect(screen.getByText(/Prévisualisation statique/)).toBeInTheDocument()
    expect(screen.getAllByText("Profil d'exécution").length).toBeGreaterThan(0)
    expect(screen.getByText("Affichable")).toBeInTheDocument()
    expect(screen.getByText("Contexte runtime")).toBeInTheDocument()
    expect(screen.getByText("Prompt assemblé")).toBeInTheDocument()
    expect(screen.getByText("Après injecteurs")).toBeInTheDocument()
    expect(screen.getByText("Prompt rendu")).toBeInTheDocument()
    expect(screen.getByText("Politique système stricte")).toBeInTheDocument()
    expect(screen.getByText("Contenu développeur rendu")).toBeInTheDocument()
    expect(screen.getAllByText("Bloc persona").length).toBeGreaterThan(0)
    expect(screen.getByText(/Sortie d'exécution live/)).toBeInTheDocument()
    expect(
      screen.getByText(/Passez en prévisualisation runtime pour exécuter le fournisseur/),
    ).toBeInTheDocument()
    expect(screen.getByText("Graphe logique")).toBeInTheDocument()
    expect(screen.getByTestId("admin-prompts-logic-graph-visual")).toBeInTheDocument()
    expect(screen.getByText("manifest_entry_id")).toBeInTheDocument()
    expect(screen.getByText("résultat opérateur")).toBeInTheDocument()
    expect(screen.getByText("composition_sources")).toBeInTheDocument()
    expect(screen.getByText("transformation_pipeline")).toBeInTheDocument()
    expect(screen.getByText("provider_messages")).toBeInTheDocument()
    expect(screen.getByText("runtime inputs")).toBeInTheDocument()
    expect(screen.getByText("feature template")).toBeInTheDocument()
    expect(screen.getByText("subfeature template")).toBeInTheDocument()
    expect(screen.getByText("plan rules")).toBeInTheDocument()
    expect(screen.getAllByText("Bloc persona").length).toBeGreaterThan(0)
    expect(screen.getByText("hard policy")).toBeInTheDocument()
    expect(screen.getByText("sample payloads")).toBeInTheDocument()
    expect(screen.getByText(/message system/)).toBeInTheDocument()
    expect(screen.getByText(/message persona/)).toBeInTheDocument()
  })

  it("ouvre une ligne du catalogue au clavier et garde un contrat responsive explicite", async () => {
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
                assembled_prompt: "assembled prompt",
                post_injectors_prompt: "post injectors prompt",
                rendered_prompt: "rendered prompt",
              },
              resolved_result: {
                provider_messages: {
                  system_hard_policy: "system hard policy",
                  developer_content_rendered: "developer content",
                  persona_block: "persona block",
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

    const catalogTable = screen.getByRole("table")
    const dataRow = within(catalogTable).getAllByRole("row")[1]
    dataRow.focus()
    expect(dataRow).toHaveFocus()

    await userEvent.keyboard("{Enter}")

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Mode d'inspection" })).toBeInTheDocument()
    })

    const css = readFileSync("src/pages/admin/AdminPromptsPage.css", "utf8")
    expect(css).toContain("@media (max-width: 1024px)")
    expect(css).toContain(".admin-prompts-catalog-master-detail")
    expect(css).toContain("grid-template-columns: 1fr;")
    expect(css).toContain(".admin-prompts-catalog__detail-panel")
    expect(css).toContain("position: static;")
    expect(css).toContain(".admin-prompts-catalog__health-cell")
    expect(css).toContain("word-break: break-word;")
  })

  it("structure le détail catalogue : ordre des sections, zone Actions et prompts repliables", async () => {
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
              catalog_visibility_status: "visible",
            },
          ],
          meta: { page: 1, page_size: 50, total: 1 },
        })
      }
      return makeJsonResponse({}, 404)
    }))
    renderPage()
    await userEvent.click(await screen.findByRole("button", { name: "Ouvrir le détail" }))
    await waitFor(() => {
      expect(screen.getByLabelText("Résumé")).toBeInTheDocument()
    })
    const detailPanel = screen.getByLabelText("Détail catalogue entrée")
    const sections = within(detailPanel).getAllByRole("region")
    const regionLabels = sections.map((el) => el.getAttribute("aria-label"))
    const idx = (name: string) => regionLabels.indexOf(name)
    expect(idx("Résumé")).toBeGreaterThanOrEqual(0)
    expect(idx("Résumé")).toBeLessThan(idx("Mode d'inspection"))
    expect(idx("Mode d'inspection")).toBeLessThan(idx("État d'exécution"))
    expect(idx("État d'exécution")).toBeLessThan(idx("Actions"))
    expect(idx("Actions")).toBeLessThan(idx("Prompts"))
    expect(idx("Prompts")).toBeLessThan(idx("Placeholders"))
    expect(idx("Placeholders")).toBeLessThan(idx("Retour LLM"))
    expect(idx("Retour LLM")).toBeLessThan(idx("Graphe logique"))
    expect(screen.getByText(/Risque : exécution fournisseur réelle/)).toBeInTheDocument()
    const promptsRegion = screen.getByLabelText("Prompts")
    const assembledSummary = within(promptsRegion).getByText("Prompt assemblé", { selector: "summary" })
    expect(assembledSummary).toBeInTheDocument()
    const assembledDetails = assembledSummary.closest("details")
    expect(assembledDetails).not.toBeNull()
    await userEvent.click(assembledSummary)
    expect(assembledDetails).toHaveAttribute("open")
  })

  it("réinitialise les filtres catalogue via le bouton dédié", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        if (url.includes("/resolved")) {
          return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
        }
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
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))
    renderPage()
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeInTheDocument()
    })
    const searchInput = screen.getByLabelText("Recherche")
    await userEvent.type(searchInput, "filtre-test")
    expect(searchInput).toHaveValue("filtre-test")
    await userEvent.click(screen.getByRole("button", { name: "Réinitialiser les filtres" }))
    expect(searchInput).toHaveValue("")
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
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

  it("conserve les sample payloads runtime quand la ligne sélectionnée sort de la page catalogue", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    const rowA = {
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
    }
    const rowB = {
      ...rowA,
      manifest_entry_id: "other:other_default:free:en-US",
      feature: "other",
      subfeature: "other_default",
      plan: "free",
      locale: "en-US",
    }
    const resolvedBody = (inspectionMode: string) => ({
      manifest_entry_id: "chat:chat_default:premium:fr-FR",
      feature: "chat",
      subfeature: "chat_default",
      plan: "premium",
      locale: "fr-FR",
      use_case_key: "chat_uc",
      context_quality: "full",
      assembly_id: "assembly-1",
      inspection_mode: inspectionMode.includes("runtime_preview") ? "runtime_preview" : "assembly_preview",
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
    })
    const fetchSpy = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/sample-payloads") && !url.match(/sample-payloads\/[^/?]+$/)) {
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
            data: resolvedBody(url),
          })
        }
        if (url.includes("page=2")) {
          return makeJsonResponse({
            data: [rowB],
            meta: {
              total: 50,
              page: 2,
              page_size: 25,
              sort_by: "feature",
              sort_order: "asc",
              freshness_window_minutes: 120,
              facets: {},
            },
          })
        }
        return makeJsonResponse({
          data: [rowA],
          meta: {
            total: 50,
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
    await userEvent.selectOptions(screen.getByLabelText("Mode d'inspection du détail"), "runtime_preview")
    await waitFor(() => {
      expect(screen.getByLabelText("Sélecteur sample payload runtime")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Suivant" }))
    await waitFor(() => {
      expect(screen.getByText("other/other_default/free/en-US")).toBeInTheDocument()
    })
    const select = screen.getByLabelText("Sélecteur sample payload runtime") as HTMLSelectElement
    expect(select.querySelectorAll("option:not([value=''])").length).toBeGreaterThan(0)
    await waitFor(() => {
      const calls = fetchSpy.mock.calls.map(([u]) => String(u))
      expect(calls.some((c) => c.includes("/sample-payloads?") && c.includes("feature=chat") && c.includes("locale=fr-FR"))).toBe(
        true,
      )
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
    await waitFor(() => {
      expect(screen.getByText(/Graphe simplifié en vue texte/)).toBeInTheDocument()
    })
    expect(screen.queryByTestId("admin-prompts-logic-graph-visual")).toBeNull()
    expect(screen.getByText(/runtime=8, fallback=8, sample=0/)).toBeInTheDocument()
    expect(screen.getByText("Détail des nœuds (données opérateur)")).toBeInTheDocument()
    expect(screen.getByLabelText("Nœuds du graphe logique (mode dense)")).toBeInTheDocument()
    expect(screen.getByText(/openai\/gpt-5/)).toBeInTheDocument()
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
    await waitFor(() => {
      expect(screen.getByText(/Prévisualisation partielle :/)).toBeInTheDocument()
    })
    expect(screen.getByText(/Aucun placeholder disponible pour cette cible/)).toBeInTheDocument()
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
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
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
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
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Historique LLM hors catalogue" })).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByText("Hors catalogue canonique")).toBeInTheDocument()
    })
    expect(screen.getByRole("region", { name: "Investigation historique LLM hors catalogue" })).toBeInTheDocument()
    expect(screen.getByLabelText("Cas d'usage historique")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Restaurer cette version" })).toBeInTheDocument()
    })
    expect(screen.getByRole("group", { name: "Diff prompt développeur legacy" })).toBeInTheDocument()
    expect(screen.getAllByText("Statut").length).toBeGreaterThan(0)

    await userEvent.click(screen.getByRole("button", { name: "Restaurer cette version" }))
    const dialog = await screen.findByRole("dialog", { name: "Confirmer la restauration de version" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Confirmer la restauration" }))
    await waitFor(() => {
      expect(screen.getByText(/Restauration effectuée vers/)).toBeInTheDocument()
    })
  })

  it("legacy: sans id actif API, pas de badge « en production » et diff en colonne peer", async () => {
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
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat",
              description: "Conversation astrologique",
              persona_strategy: "required",
              safety_profile: "astrology",
              allowed_persona_ids: [],
              active_prompt_version_id: null,
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
              developer_prompt: "right column",
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
              developer_prompt: "left column",
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
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))

    await waitFor(() => {
      expect(screen.getByRole("region", { name: "Investigation historique LLM hors catalogue" })).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(
        screen.getByText(/Aucune version « active » résolue par l'API pour ce cas d'usage/),
      ).toBeInTheDocument()
    })
    expect(screen.queryByText("En production", { exact: true })).not.toBeInTheDocument()
    expect(
      screen.getByRole("heading", { name: "Colonne droite — autre version (actif non résolu)" }),
    ).toBeInTheDocument()
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
    await userEvent.click(screen.getByRole("link", { name: "Historique release" }))

    expect(
      screen.getByRole("region", { name: "Investigation des snapshots release" }),
    ).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Timeline et comparaison de snapshots" })).toBeInTheDocument()
    })
    expect(screen.getByText(/Qualification: Go/)).toBeInTheDocument()
    expect(screen.getByText(/Événement : Surveillance/)).toBeInTheDocument()
    expect(screen.getByText(/État courant : Actif/)).toBeInTheDocument()
    expect(screen.getByText(/Jeu golden: Succès/)).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Chronologie des événements" })).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Synthèse de comparaison" })).toBeInTheDocument()
    })
    expect(screen.getByText("Référence (source)")).toBeInTheDocument()
    expect(screen.getByText("Comparée (cible)")).toBeInTheDocument()
    expect(screen.getByText("chat:chat_default:premium:fr-FR")).toBeInTheDocument()
    expect(screen.getByText("Écart sur cette fiche")).toBeInTheDocument()
    expect(screen.queryByText(/Ouvrir 66\.46/)).not.toBeInTheDocument()
    const catalogOpenButton = screen.getByRole("button", {
      name: "Ouvrir l'entrée canonique chat:chat_default:premium:fr-FR dans le catalogue",
    })
    expect(catalogOpenButton).toBeInTheDocument()
    expect(screen.getByText("chat · chat_default · premium · fr-FR")).toBeInTheDocument()
    await userEvent.click(catalogOpenButton)
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/admin/prompts/catalog")
    })
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
    await userEvent.click(screen.getByRole("link", { name: "Consommation" }))
    expect(screen.getByRole("region", { name: /Pilotage de la consommation LLM/i })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Agrégats par période" })).toBeInTheDocument()
    await userEvent.selectOptions(screen.getByRole("combobox", { name: /Vue d'agrégation/i }), "feature")
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

  it("affiche les cartes de consommation en viewport étroit avec accès aux logs récents", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal(
      "matchMedia",
      vi.fn((query: string) => ({
        matches: query.includes("max-width: 960px"),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    )

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
              request_id: "req-narrow-1",
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
              request_count: 3,
              input_tokens: 100,
              output_tokens: 50,
              total_tokens: 150,
              estimated_cost: 0.12,
              avg_latency_ms: 200,
              error_rate: 0,
            },
          ],
          meta: {
            view: "feature",
            granularity: "day",
            count: 1,
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
    await userEvent.click(screen.getByRole("link", { name: "Consommation" }))
    await waitFor(() => {
      expect(screen.getByRole("list")).toBeInTheDocument()
    })
    expect(screen.queryByRole("columnheader", { name: "Période" })).not.toBeInTheDocument()
    const logsButtons = screen.getAllByRole("button", { name: "Voir logs récents" })
    expect(logsButtons.length).toBe(1)
    await userEvent.click(logsButtons[0])
    await waitFor(() => {
      expect(screen.getByText("req-narrow-1")).toBeInTheDocument()
    })
  })

  it("affiche un état vide explicite lorsque la consommation canonique ne retourne aucune ligne", async () => {
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
    }))

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Consommation" }))
    await waitFor(() => {
      expect(screen.getByText(/Aucune ligne d'agrégat/)).toBeInTheDocument()
    })
    expect(screen.queryByRole("columnheader", { name: "Période" })).not.toBeInTheDocument()
  })

  it("réinitialise le drill-down quand la granularité redéfinit le périmètre d'agrégats", async () => {
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
              request_id: "req-reset-1",
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
        const granularity = new URL(url).searchParams.get("granularity") ?? "day"
        return makeJsonResponse({
          data: [
            {
              period_start_utc: "2026-04-20T00:00:00Z",
              granularity,
              user_id: null,
              user_email: null,
              subscription_plan: null,
              feature: "chat",
              subfeature: "chat_default",
              request_count: granularity === "day" ? 3 : 12,
              input_tokens: 100,
              output_tokens: 50,
              total_tokens: 150,
              estimated_cost: 0.12,
              avg_latency_ms: 200,
              error_rate: 0,
            },
          ],
          meta: {
            view: "feature",
            granularity,
            count: 1,
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
    await userEvent.click(screen.getByRole("link", { name: "Consommation" }))
    await userEvent.selectOptions(screen.getByRole("combobox", { name: /Vue d'agrégation/i }), "feature")
    await userEvent.click(await screen.findByRole("button", { name: "Voir logs récents" }))

    await waitFor(() => {
      expect(screen.getByText("Drill-down appels récents (50 max)")).toBeInTheDocument()
    })
    expect(screen.getByText("req-reset-1")).toBeInTheDocument()

    await userEvent.selectOptions(screen.getByRole("combobox", { name: /Pas de temps des agrégats/i }), "month")

    await waitFor(() => {
      expect(screen.queryByText("Drill-down appels récents (50 max)")).not.toBeInTheDocument()
    })
    expect(screen.queryByText("req-reset-1")).not.toBeInTheDocument()
  })

  it("legacy: préremplit le formulaire de nouvelle version et crée un draft visible dans l'historique", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    let historyCallCount = 0
    const fetchSpy = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat guidance",
              description: "Prompt chat",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: "prompt-published",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && !init?.method) {
        historyCallCount += 1
        return makeJsonResponse({
          data:
            historyCallCount >= 2
              ? [
                  {
                    id: "prompt-draft-3",
                    use_case_key: "chat",
                    status: "draft",
                    developer_prompt: "Prompt draft enrichi",
                    model: "gpt-5.1",
                    temperature: 0.9,
                    max_output_tokens: 1600,
                    fallback_use_case_key: null,
                    created_by: "admin@example.com",
                    created_at: "2026-04-18T10:30:00Z",
                    published_at: null,
                  },
                  {
                    id: "prompt-published",
                    use_case_key: "chat",
                    status: "published",
                    developer_prompt: "Prompt historique",
                    model: "gpt-5",
                    temperature: 0.7,
                    max_output_tokens: 1200,
                    fallback_use_case_key: null,
                    created_by: "admin@example.com",
                    created_at: "2026-04-17T09:00:00Z",
                    published_at: "2026-04-17T09:05:00Z",
                  },
                ]
              : [
                  {
                    id: "prompt-published",
                    use_case_key: "chat",
                    status: "published",
                    developer_prompt: "Prompt historique",
                    model: "gpt-5",
                    temperature: 0.7,
                    max_output_tokens: 1200,
                    fallback_use_case_key: null,
                    created_by: "admin@example.com",
                    created_at: "2026-04-17T09:00:00Z",
                    published_at: "2026-04-17T09:05:00Z",
                  },
                  {
                    id: "prompt-older",
                    use_case_key: "chat",
                    status: "archived",
                    developer_prompt: "Prompt archive",
                    model: "gpt-4.1",
                    temperature: 0.5,
                    max_output_tokens: 900,
                    fallback_use_case_key: "natal",
                    created_by: "ops@example.com",
                    created_at: "2026-04-15T09:00:00Z",
                    published_at: null,
                  },
                ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && init?.method === "POST") {
        expect(JSON.parse(String(init.body))).toEqual({
          developer_prompt: "Prompt draft enrichi",
          model: "gpt-5.1",
          temperature: 0.9,
          max_output_tokens: 1600,
          fallback_use_case_key: null,
        })
        return makeJsonResponse({
          data: {
            id: "prompt-draft-3",
            use_case_key: "chat",
            status: "draft",
            developer_prompt: "Prompt draft enrichi",
            model: "gpt-5.1",
            temperature: 0.9,
            max_output_tokens: 1600,
            fallback_use_case_key: null,
            created_by: "admin@example.com",
            created_at: "2026-04-18T10:30:00Z",
            published_at: null,
          },
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))

    expect(await screen.findByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()
    expect(screen.getByLabelText("Prompt développeur")).toHaveValue("Prompt historique")
    expect(screen.getByLabelText("Modèle")).toHaveValue("gpt-5")
    expect(screen.getByLabelText("Température")).toHaveValue(0.7)
    expect(screen.getByLabelText("Budget de sortie")).toHaveValue(1200)
    expect(screen.getByText("Statut courant")).toBeInTheDocument()
    expect(screen.getAllByText("Publié").length).toBeGreaterThan(0)

    await userEvent.clear(screen.getByLabelText("Prompt développeur"))
    await userEvent.type(screen.getByLabelText("Prompt développeur"), "Prompt draft enrichi")
    await userEvent.clear(screen.getByLabelText("Modèle"))
    await userEvent.type(screen.getByLabelText("Modèle"), "gpt-5.1")
    await userEvent.clear(screen.getByLabelText("Température"))
    await userEvent.type(screen.getByLabelText("Température"), "0.9")
    await userEvent.clear(screen.getByLabelText("Budget de sortie"))
    await userEvent.type(screen.getByLabelText("Budget de sortie"), "1600")

    await userEvent.click(screen.getByRole("button", { name: "Créer une nouvelle version" }))

    await waitFor(() => {
      expect(fetchSpy.mock.calls.some(([url, init]) => String(url).endsWith("/v1/admin/llm/use-cases/chat/prompts") && init?.method === "POST")).toBe(true)
    })
    await waitFor(() => {
      expect(screen.getByText(/Nouvelle version non publiée créée/)).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getAllByText("prompt-draft-3").length).toBeGreaterThan(0)
    })
    await waitFor(() => {
      expect(
        screen.getByLabelText("Version de référence pour la comparaison legacy"),
      ).toHaveValue("prompt-draft-3")
    })
  })

  it("legacy: bloque la sauvegarde si la validation locale échoue", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchSpy = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat guidance",
              description: "Prompt chat",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: "prompt-published",
            },
            {
              key: "natal",
              display_name: "Natal",
              description: "Prompt natal",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: null,
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-published",
              use_case_key: "chat",
              status: "published",
              developer_prompt: "Prompt historique",
              model: "gpt-5",
              temperature: 0.7,
              max_output_tokens: 1200,
              fallback_use_case_key: null,
              created_by: "admin@example.com",
              created_at: "2026-04-17T09:00:00Z",
              published_at: "2026-04-17T09:05:00Z",
            },
          ],
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))
    expect(await screen.findByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()

    await userEvent.clear(screen.getByLabelText("Prompt développeur"))
    await userEvent.clear(screen.getByLabelText("Température"))
    await userEvent.type(screen.getByLabelText("Température"), "3")
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Créer une nouvelle version" })).toBeEnabled()
    })
    await userEvent.click(screen.getByRole("button", { name: "Créer une nouvelle version" }))

    expect(await screen.findAllByRole("alert")).toHaveLength(2)
    expect(screen.getByText("Le prompt développeur est requis.")).toBeInTheDocument()
    expect(screen.getByText("La température doit rester comprise entre 0 et 2.")).toBeInTheDocument()
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).endsWith("/v1/admin/llm/use-cases/chat/prompts") && init?.method === "POST")).toBe(false)
  })

  it("legacy: rejette une température vide au lieu de la convertir silencieusement à 0", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchSpy = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat guidance",
              description: "Prompt chat",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: "prompt-published",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-published",
              use_case_key: "chat",
              status: "published",
              developer_prompt: "Prompt historique",
              model: "gpt-5",
              temperature: 0.7,
              max_output_tokens: 1200,
              fallback_use_case_key: null,
              created_by: "admin@example.com",
              created_at: "2026-04-17T09:00:00Z",
              published_at: "2026-04-17T09:05:00Z",
            },
          ],
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))
    expect(await screen.findByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()

    await userEvent.clear(screen.getByLabelText("Température"))
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Créer une nouvelle version" })).toBeEnabled()
    })
    await userEvent.click(screen.getByRole("button", { name: "Créer une nouvelle version" }))

    expect(await screen.findByText("La température doit être un nombre valide.")).toBeInTheDocument()
    expect(fetchSpy.mock.calls.some(([url, init]) => String(url).endsWith("/v1/admin/llm/use-cases/chat/prompts") && init?.method === "POST")).toBe(false)
  })

  it("legacy: affiche le statut inactive quand le backend renvoie cette valeur", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat guidance",
              description: "Prompt chat",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: null,
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-inactive",
              use_case_key: "chat",
              status: "inactive",
              developer_prompt: "Prompt inactif",
              model: "gpt-5",
              temperature: 0.6,
              max_output_tokens: 1000,
              fallback_use_case_key: null,
              created_by: "admin@example.com",
              created_at: "2026-04-17T09:00:00Z",
              published_at: null,
            },
          ],
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))

    expect(await screen.findByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()
    expect(screen.getByText("Statut courant")).toBeInTheDocument()
    expect(screen.getAllByText("Inactive").length).toBeGreaterThan(0)
  })

  it("legacy: relaie les erreurs backend de sauvegarde sans exposer de JSON brut", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [],
          meta: { total: 0, page: 1, page_size: 25, sort_by: "feature", sort_order: "asc", freshness_window_minutes: 120, facets: {} },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat",
              display_name: "Chat guidance",
              description: "Prompt chat",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: "prompt-published",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-published",
              use_case_key: "chat",
              status: "published",
              developer_prompt: "Prompt historique",
              model: "gpt-5",
              temperature: 0.7,
              max_output_tokens: 1200,
              fallback_use_case_key: null,
              created_by: "admin@example.com",
              created_at: "2026-04-17T09:00:00Z",
              published_at: "2026-04-17T09:05:00Z",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/chat/prompts") && init?.method === "POST") {
        return makeJsonResponse(
          {
            error: {
              code: "validation_error",
              message: "fallback use case inconnu",
              details: {
                fallback_use_case_key: "missing use case",
              },
            },
          },
          422,
        )
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Historique legacy" }))
    expect(await screen.findByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()

    await userEvent.clear(screen.getByLabelText("Modèle"))
    await userEvent.type(screen.getByLabelText("Modèle"), "gpt-5.1")
    await userEvent.click(screen.getByRole("button", { name: "Créer une nouvelle version" }))

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Le backend a refusé la sauvegarde: fallback use case inconnu (fallback_use_case_key: missing use case)",
      )
    })
    expect(screen.queryByText(/^\{/)).not.toBeInTheDocument()
  })

  it("diffère la révocation du blob lors de l'export CSV", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const createObjectURL = vi.fn(() => "blob:test-consumption")
    const revokeObjectURL = vi.fn()
    const anchorClick = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {})
    const setTimeoutSpy = vi.spyOn(window, "setTimeout")

    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL,
      revokeObjectURL,
    })

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
      if (url.includes("/v1/admin/llm/consumption/canonical/export")) {
        return new Response("period,requests\n2026-04-20,3\n", {
          status: 200,
          headers: { "Content-Type": "text/csv" },
        })
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
    }))

    renderPage()
    await userEvent.click(screen.getByRole("link", { name: "Consommation" }))
    await userEvent.click(screen.getByRole("button", { name: "Exporter CSV" }))

    await waitFor(() => {
      expect(createObjectURL).toHaveBeenCalledTimes(1)
    })
    expect(anchorClick).toHaveBeenCalledTimes(1)
    expect(revokeObjectURL).not.toHaveBeenCalled()
    const revokeTimeoutCall = setTimeoutSpy.mock.calls.find(([, delay]) => delay === 30_000)
    expect(revokeTimeoutCall).toBeDefined()

    const revokeLater = revokeTimeoutCall?.[0]
    expect(typeof revokeLater).toBe("function")
    ;(revokeLater as () => void)()
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:test-consumption")

    setTimeoutSpy.mockRestore()
    anchorClick.mockRestore()
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
    await userEvent.click(screen.getByRole("link", { name: "Consommation" }))

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

  it("affiche le bandeau de mode, ouvre une confirmation avant execute-sample puis envoie le POST", async () => {
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
        if (url.includes("/execute-sample")) {
          return makeJsonResponse({
            data: {
              manifest_entry_id: "chat:chat_default:premium:fr-FR",
              sample_payload_id: "sample-1",
              use_case_key: "chat_uc",
              provider: "openai",
              model: "gpt-5",
              request_id: "req-exec",
              trace_id: "tr-exec",
              gateway_request_id: "gw-exec",
              prompt_sent: "prompt",
              resolved_runtime_parameters: {},
              raw_output: "sortie mock",
              structured_output: null,
              structured_output_parseable: false,
              validation_status: "valid",
              execution_path: "nominal",
              meta_validation_errors: null,
              latency_ms: 5,
              admin_manual_execution: true,
              usage_input_tokens: 1,
              usage_output_tokens: 2,
            },
            meta: { request_id: "req-exec" },
          })
        }
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

    renderPage()
    await waitFor(() => {
      expect(screen.getByText("chat/chat_default/premium/fr-FR")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByRole("button", { name: "Ouvrir le détail" }))
    expect(screen.getByLabelText("Mode d'inspection actif pour ce détail")).toHaveTextContent(/Préassemblage/)

    await userEvent.selectOptions(screen.getByLabelText("Mode d'inspection du détail"), "runtime_preview")
    await waitFor(() => {
      expect(screen.getByLabelText("Mode d'inspection actif pour ce détail")).toHaveTextContent("Prévisualisation runtime")
    })

    await userEvent.click(screen.getByRole("button", { name: "Exécuter avec le LLM" }))
    expect(await screen.findByRole("dialog", { name: "Confirmer l'exécution LLM réelle" })).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Confirmer l'exécution" }))

    await waitFor(() => {
      const posts = fetchSpy.mock.calls.filter(([u]) => String(u).includes("/execute-sample"))
      expect(posts.length).toBeGreaterThan(0)
    })
  })
})
