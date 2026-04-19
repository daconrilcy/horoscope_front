import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Navigate, Route, Routes } from "react-router-dom"

import { AdminPromptsPage } from "../pages/admin/AdminPromptsPage"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

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
      </Route>
    </Routes>
  )
}

function renderPage(initialEntry = "/admin/prompts/catalog") {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={[initialEntry]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <AdminPromptsRoutesFixture />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("Admin prompts catalog flow", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "ResizeObserver",
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    )
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
  })

  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("affiche le graphe apres selection feature / abonnement / locale", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog") && url.includes("/resolved")) {
        return makeJsonResponse({
          data: {
            manifest_entry_id: "chat:chat_default:premium:fr-FR",
            feature: "chat",
            subfeature: "chat_default",
            plan: "premium",
            locale: "fr-FR",
            use_case_key: "chat_uc",
            runtime_use_case_key: "chat_uc",
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
              rendered_prompt: "rendered final prompt",
            },
            resolved_result: {
              provider_messages: {
                system_hard_policy: "hard policy prompt",
                developer_content_rendered: "rendered",
                persona_block: "persona prompt",
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
      if (url.includes("/v1/admin/llm/catalog")) {
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
            page_size: 1,
            sort_by: "feature",
            sort_order: "asc",
            freshness_window_minutes: 120,
            facets: {
              feature: ["chat"],
              plan: ["premium"],
              locale: ["fr-FR"],
            },
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat_uc",
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
      if (url.endsWith("/v1/admin/llm/use-cases/chat_uc/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-published",
              use_case_key: "chat_uc",
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
    }))

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeInTheDocument()
    })

    await screen.findByRole("option", { name: "chat" })
    await userEvent.selectOptions(screen.getByLabelText("Fonctionnalité"), "chat")
    await userEvent.selectOptions(screen.getByLabelText("Formule"), "premium")
    await userEvent.selectOptions(screen.getByLabelText("Locale"), "fr-FR")
    await userEvent.click(screen.getByRole("button", { name: "Afficher le schéma" }))

    expect(await screen.findByText("Prompt rendu final")).toBeInTheDocument()
    expect(screen.getAllByText("rendered final prompt").length).toBeGreaterThan(0)
    expect(screen.getByTestId("admin-prompts-logic-graph-visual")).toBeInTheDocument()
  })

  it("ouvre la modale d edition sur clic du noeud use case", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog") && url.includes("/resolved")) {
        return makeJsonResponse({
          data: {
            manifest_entry_id: "chat:chat_default:premium:fr-FR",
            feature: "chat",
            subfeature: "chat_default",
            plan: "premium",
            locale: "fr-FR",
            use_case_key: "chat_uc",
            runtime_use_case_key: "chat_uc",
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
              rendered_prompt: "rendered final prompt",
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
      if (url.includes("/v1/admin/llm/catalog")) {
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
            page_size: 1,
            sort_by: "feature",
            sort_order: "asc",
            freshness_window_minutes: 120,
            facets: {
              feature: ["chat"],
              plan: ["premium"],
              locale: ["fr-FR"],
            },
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "chat_uc",
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
      if (url.endsWith("/v1/admin/llm/use-cases/chat_uc/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-published",
              use_case_key: "chat_uc",
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
    }))

    renderPage()

    await screen.findByRole("option", { name: "chat" })
    await userEvent.selectOptions(screen.getByLabelText("Fonctionnalité"), "chat")
    await userEvent.selectOptions(screen.getByLabelText("Formule"), "premium")
    await userEvent.selectOptions(screen.getByLabelText("Locale"), "fr-FR")
    await userEvent.click(screen.getByRole("button", { name: "Afficher le schéma" }))

    const useCaseNode = await screen.findByText(/Prompt use case/)
    fireEvent.click(useCaseNode)

    expect(await screen.findByRole("dialog", { name: "Prompt use case" })).toBeInTheDocument()
    expect(screen.getByText("Edition directe")).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()
  })

  it("aligne le graphe sur le use case effectivement utilise pour natal free", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/admin/llm/catalog") && url.includes("/resolved")) {
        return makeJsonResponse({
          data: {
            manifest_entry_id: "natal:interpretation:free:fr-FR",
            feature: "natal",
            subfeature: "interpretation",
            plan: "free",
            locale: "fr-FR",
            use_case_key: "natal_long_free",
            runtime_use_case_key: "natal_long_free",
            context_quality: "full",
            assembly_id: "assembly-natal",
            inspection_mode: "assembly_preview",
            source_of_truth_status: "active_snapshot",
            active_snapshot_id: "snapshot-natal",
            active_snapshot_version: "v1",
            composition_sources: {
              feature_template: { id: "tpl-natal", content: "feature prompt" },
              subfeature_template: null,
              plan_rules: null,
              persona_block: null,
              hard_policy: { safety_profile: "astrology", content: "hard policy prompt" },
              execution_profile: {
                id: "profile-natal",
                name: "default",
                provider: "openai",
                model: "gpt-5",
                reasoning: null,
                verbosity: "balanced",
                provider_params: { max_output_tokens: 1000 },
              },
            },
            transformation_pipeline: {
              assembled_prompt: "assembled natal",
              post_injectors_prompt: "post natal",
              rendered_prompt: "rendered natal prompt",
            },
            resolved_result: {
              provider_messages: {
                system_hard_policy: "hard policy prompt",
                developer_content_rendered: "rendered natal prompt",
                persona_block: "",
                execution_parameters: { max_output_tokens: 1000 },
              },
              placeholders: [],
              context_quality_handled_by_template: false,
              context_quality_instruction_injected: false,
              context_compensation_status: "not_needed",
              source_of_truth_status: "active_snapshot",
              active_snapshot_id: "snapshot-natal",
              active_snapshot_version: "v1",
              manifest_entry_id: "natal:interpretation:free:fr-FR",
            },
          },
        })
      }
      if (url.includes("/v1/admin/llm/catalog")) {
        return makeJsonResponse({
          data: [
            {
              manifest_entry_id: "natal:interpretation:free:fr-FR",
              feature: "natal",
              subfeature: "interpretation",
              plan: "free",
              locale: "fr-FR",
              assembly_id: "assembly-natal",
              assembly_status: "published",
              execution_profile_id: "profile-natal",
              execution_profile_ref: "profile-natal",
              output_contract_ref: "contract-natal",
              active_snapshot_id: "snapshot-natal",
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
            page_size: 1,
            sort_by: "feature",
            sort_order: "asc",
            freshness_window_minutes: 120,
            facets: {
              feature: ["natal"],
              plan: ["free"],
              locale: ["fr-FR"],
            },
          },
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases")) {
        return makeJsonResponse({
          data: [
            {
              key: "natal_long_free",
              display_name: "Natal Long Free",
              description: "Prompt natal free actif",
              persona_strategy: "default",
              safety_profile: "astro",
              allowed_persona_ids: [],
              active_prompt_version_id: "prompt-natal",
            },
          ],
        })
      }
      if (url.endsWith("/v1/admin/llm/use-cases/natal_long_free/prompts") && !init?.method) {
        return makeJsonResponse({
          data: [
            {
              id: "prompt-natal",
              use_case_key: "natal_long_free",
              status: "published",
              developer_prompt: "Prompt canonique natal",
              model: "gpt-5",
              temperature: 0.7,
              max_output_tokens: 1000,
              fallback_use_case_key: null,
              created_by: "admin@example.com",
              created_at: "2026-04-17T09:00:00Z",
              published_at: "2026-04-17T09:05:00Z",
            },
          ],
        })
      }
      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    }))

    renderPage()

    await screen.findByRole("option", { name: "natal" })
    await userEvent.selectOptions(screen.getByLabelText("Fonctionnalité"), "natal")
    await userEvent.selectOptions(screen.getByLabelText("Formule"), "free")
    await userEvent.selectOptions(screen.getByLabelText("Locale"), "fr-FR")
    await userEvent.click(screen.getByRole("button", { name: "Afficher le schéma" }))

    expect(screen.queryByText("Runtime different")).not.toBeInTheDocument()

    const useCaseNode = await screen.findByText("Prompt use case")
    fireEvent.click(useCaseNode)

    expect(await screen.findByText("Use case canonique")).toBeInTheDocument()
    expect(screen.getByText("natal_long_free")).toBeInTheDocument()
    expect(screen.queryByText("Use case runtime")).not.toBeInTheDocument()
  })
})
