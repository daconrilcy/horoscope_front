import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react"
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

function makeResolvedPayload(overrides?: Record<string, unknown>) {
  return {
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
    activation: {
      manifest_entry_id: "natal:interpretation:free:fr-FR",
      feature: "natal",
      subfeature: "interpretation",
      plan: "free",
      locale: "fr-FR",
      active_snapshot_id: "snapshot-natal",
      active_snapshot_version: "v1",
      execution_profile: "profile-natal",
      provider_target: "openai / gpt-5",
      policy_family: "astrology",
      output_schema: "AstroResponse_v1",
      injector_set: ["context_quality_injector", "length_budget_inactive", "verbosity_instruction"],
      persona_policy: "none",
    },
    selected_components: [
      {
        key: "domain_instructions",
        component_type: "domain_instructions",
        title: "Instructions métier",
        content: "Interprète strictement le thème natal fourni.",
        summary: "Bloc source principal résolu depuis le feature template.",
        ref: "tpl-natal",
        source_label: "feature_template",
        version_label: null,
        merge_mode: null,
        impact_status: "active",
        editable_use_case_key: null,
        meta: { feature: "natal" },
      },
      {
        key: "use_case_overlay",
        component_type: "use_case_overlay",
        title: "Use case overlay",
        content: "Version free: interprétation synthétique, sans approfondissement premium.",
        summary: "Surcharge éditoriale spécifique au use case runtime actif.",
        ref: "prompt-free",
        source_label: "natal_long_free",
        version_label: "2026-04-19T20:00:00Z",
        merge_mode: null,
        impact_status: "active",
        editable_use_case_key: "natal_long_free",
        meta: { use_case_key: "natal_long_free" },
      },
      {
        key: "output_contract",
        component_type: "output_contract",
        title: "Output contract",
        content: null,
        summary: "Contrat de sortie résolu pour ce contexte.",
        ref: "AstroResponse_v1",
        source_label: "output_schema",
        version_label: null,
        merge_mode: null,
        impact_status: "reference_only",
        editable_use_case_key: null,
        meta: {},
      },
      {
        key: "hard_policy",
        component_type: "hard_policy",
        title: "Hard policy",
        content: "Respecte les garde-fous astrologie.",
        summary: "Politique stricte envoyée au provider en message system.",
        ref: "astrology",
        source_label: "system_prompt",
        version_label: null,
        merge_mode: "system_message",
        impact_status: "active",
        editable_use_case_key: null,
        meta: { safety_profile: "astrology" },
      },
    ],
    runtime_artifacts: [
      {
        key: "developer_prompt_assembled",
        artifact_type: "developer_prompt_assembled",
        title: "Developer prompt assembled",
        content: "assembled prompt",
        summary: "Premier artefact textuel après assemblage.",
        change_status: "changed",
        delta_note: "Compose les instructions métier et la surcharge éditoriale active.",
        injection_point: "developer",
        meta: {},
      },
      {
        key: "developer_prompt_after_injectors",
        artifact_type: "developer_prompt_after_injectors",
        title: "Developer prompt after injectors",
        content: "assembled prompt\n\n[CONSIGNE DE VERBOSITÉ] balanced",
        summary: "État developer après injecteurs.",
        change_status: "changed",
        delta_note: "Les injecteurs runtime modifient le message developer principal.",
        injection_point: "developer",
        meta: {},
      },
      {
        key: "system_prompt",
        artifact_type: "system_prompt",
        title: "System prompt(s)",
        content: "Respecte les garde-fous astrologie.",
        summary: "Message system réellement préparé pour le provider.",
        change_status: "changed",
        delta_note: "La hard policy est envoyée séparément du developer prompt.",
        injection_point: "system",
        meta: {},
      },
      {
        key: "final_provider_payload",
        artifact_type: "final_provider_payload",
        title: "Final provider payload",
        content: "{\n  \"messages\": []\n}",
        summary: "Payload inspectable réellement prêt pour l'appel provider.",
        change_status: "changed",
        delta_note: "Agrège system message, messages developer et paramètres provider traduits.",
        injection_point: "provider",
        meta: {},
      },
    ],
    composition_sources: {
      feature_template: { id: "tpl-natal", content: "feature prompt" },
      subfeature_template: null,
      plan_rules: null,
      persona_block: null,
      hard_policy: { safety_profile: "astrology", content: "Respecte les garde-fous astrologie." },
      execution_profile: {
        id: "profile-natal",
        name: "profile-natal",
        provider: "openai",
        model: "gpt-5",
        reasoning: null,
        verbosity: "balanced",
        provider_params: { max_output_tokens: 1000 },
      },
    },
    transformation_pipeline: {
      assembled_prompt: "assembled prompt",
      post_injectors_prompt: "assembled prompt\n\n[CONSIGNE DE VERBOSITÉ] balanced",
      rendered_prompt: "rendered natal prompt",
    },
    resolved_result: {
      provider_messages: {
        system_hard_policy: "Respecte les garde-fous astrologie.",
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
    ...overrides,
  }
}

function installCatalogFetchStub(resolvedPayload: Record<string, unknown>) {
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.includes("/v1/admin/llm/catalog") && url.includes("/resolved")) {
      return makeJsonResponse({ data: resolvedPayload })
    }
    if (url.includes("/v1/admin/llm/catalog")) {
      const manifestEntryId = String(resolvedPayload.manifest_entry_id)
      const feature = String(resolvedPayload.feature)
      const subfeature = resolvedPayload.subfeature ? String(resolvedPayload.subfeature) : null
      const plan = resolvedPayload.plan ? String(resolvedPayload.plan) : null
      const locale = resolvedPayload.locale ? String(resolvedPayload.locale) : null
      return makeJsonResponse({
        data: [
          {
            manifest_entry_id: manifestEntryId,
            feature,
            subfeature,
            plan,
            locale,
            assembly_id: "assembly-natal",
            assembly_status: "published",
            execution_profile_id: "profile-natal",
            execution_profile_ref: "profile-natal",
            output_contract_ref: "AstroResponse_v1",
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
            feature: [feature],
            plan: plan ? [plan] : [],
            locale: locale ? [locale] : [],
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
            active_prompt_version_id: "prompt-free",
          },
          {
            key: "natal_premium",
            display_name: "Natal Premium",
            description: "Prompt natal premium",
            persona_strategy: "premium",
            safety_profile: "astro",
            allowed_persona_ids: ["persona-1"],
            active_prompt_version_id: "prompt-premium",
          },
        ],
      })
    }
    if (url.endsWith("/v1/admin/llm/use-cases/natal_long_free/prompts") && !init?.method) {
      return makeJsonResponse({
        data: [
          {
            id: "prompt-free",
            use_case_key: "natal_long_free",
            status: "published",
            developer_prompt: "Version free: interprétation synthétique, sans approfondissement premium.",
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
    if (url.endsWith("/v1/admin/llm/use-cases/natal_premium/prompts") && !init?.method) {
      return makeJsonResponse({
        data: [
          {
            id: "prompt-premium",
            use_case_key: "natal_premium",
            status: "published",
            developer_prompt: "Version premium détaillée.",
            model: "gpt-5",
            temperature: 0.7,
            max_output_tokens: 1500,
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

  async function selectCatalogFlowContext(plan: "free" | "premium") {
    const selector = await screen.findByRole("region", { name: "Sélection du contexte catalogue" })
    await within(selector).findByRole("option", { name: "natal" })
    await userEvent.selectOptions(within(selector).getByLabelText("Fonctionnalité"), "natal")
    await userEvent.selectOptions(within(selector).getByLabelText("Formule"), plan)
    await userEvent.selectOptions(within(selector).getByLabelText("Locale"), "fr-FR")
    await userEvent.click(within(selector).getByRole("button", { name: "Afficher le schéma" }))
  }

  it("affiche la lecture en activation composants et artefacts runtime", async () => {
    installCatalogFetchStub(makeResolvedPayload())
    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeInTheDocument()
    })

    await selectCatalogFlowContext("free")

    expect(await screen.findByText("Activation")).toBeInTheDocument()
    expect(screen.getByText("Composants sélectionnés")).toBeInTheDocument()
    expect(screen.getByText("Artefacts runtime")).toBeInTheDocument()
    expect(screen.getAllByText("Use case overlay").length).toBeGreaterThan(0)
    expect(screen.queryByText("Prompt use case")).not.toBeInTheDocument()
    expect(screen.getAllByText("Final provider payload").length).toBeGreaterThan(0)
  })

  it("ouvre l édition sur le nœud use case overlay et expose la couche free", async () => {
    installCatalogFetchStub(makeResolvedPayload())
    renderPage()

    await selectCatalogFlowContext("free")

    const graphs = await screen.findAllByTestId("admin-prompts-logic-graph-visual")
    const graph = await waitFor(() => {
      const matchingGraph = graphs.find((candidate) => within(candidate).queryByText("Use case overlay"))
      expect(matchingGraph).toBeTruthy()
      return matchingGraph as HTMLElement
    })
    const useCaseOverlayNode = await within(graph).findByText("Use case overlay")
    expect(useCaseOverlayNode).toBeTruthy()
    fireEvent.click(useCaseOverlayNode)

    expect((await screen.findAllByRole("heading", { name: "Use case overlay" })).length).toBeGreaterThan(0)
    expect(screen.getByText("Edition directe")).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Préparer une nouvelle version" })).toBeInTheDocument()
  })

  it("rend la persona et le delta before/after persona pour une cible premium", async () => {
    installCatalogFetchStub(
      makeResolvedPayload({
        manifest_entry_id: "natal:interpretation:premium:fr-FR",
        plan: "premium",
        use_case_key: "natal_premium",
        runtime_use_case_key: "natal_premium",
        activation: {
          manifest_entry_id: "natal:interpretation:premium:fr-FR",
          feature: "natal",
          subfeature: "interpretation",
          plan: "premium",
          locale: "fr-FR",
          active_snapshot_id: "snapshot-premium",
          active_snapshot_version: "v2",
          execution_profile: "profile-premium",
          provider_target: "openai / gpt-5",
          policy_family: "astrology",
          output_schema: "AstroResponse_v3",
          injector_set: ["context_quality_injector", "length_budget_inactive", "verbosity_instruction"],
          persona_policy: "enabled",
        },
        selected_components: [
          makeResolvedPayload().selected_components[0],
          {
            key: "use_case_overlay",
            component_type: "use_case_overlay",
            title: "Use case overlay",
            content: "Version premium détaillée.",
            summary: "Surcharge éditoriale spécifique au use case runtime actif.",
            ref: "prompt-premium",
            source_label: "natal_premium",
            version_label: "2026-04-19T20:00:00Z",
            merge_mode: null,
            impact_status: "active",
            editable_use_case_key: "natal_premium",
            meta: { use_case_key: "natal_premium" },
          },
          {
            key: "persona_overlay",
            component_type: "persona_overlay",
            title: "Persona overlay",
            content: "Voix premium empathique et approfondie.",
            summary: "Persona résolue, injectée comme message developer séparé.",
            ref: "persona-1",
            source_label: "Luna Premium",
            version_label: "2026-04-19T21:00:00Z",
            merge_mode: "separate_developer_message",
            impact_status: "active",
            editable_use_case_key: null,
            meta: { persona_name: "Luna Premium" },
          },
          makeResolvedPayload().selected_components[2],
          makeResolvedPayload().selected_components[3],
        ],
        runtime_artifacts: [
          makeResolvedPayload().runtime_artifacts[0],
          {
            key: "developer_prompt_after_persona",
            artifact_type: "developer_prompt_after_persona",
            title: "Developer prompt after persona",
            content:
              "[DEVELOPER MESSAGE 1 / main]\nassembled prompt\n\n[DEVELOPER MESSAGE 2 / persona overlay]\nVoix premium empathique et approfondie.",
            summary: "Vue opératoire des messages developer après ajout de la persona.",
            change_status: "changed",
            delta_note: "La persona n'est pas fusionnée dans le texte principal; elle part comme second message developer.",
            injection_point: "developer",
            meta: {},
          },
          makeResolvedPayload().runtime_artifacts[1],
          makeResolvedPayload().runtime_artifacts[2],
          makeResolvedPayload().runtime_artifacts[3],
        ],
      }),
    )

    renderPage()

    await selectCatalogFlowContext("premium")

    expect(await screen.findByText("Persona overlay")).toBeInTheDocument()
    expect(screen.getAllByText("Developer prompt after persona").length).toBeGreaterThan(0)
    expect(screen.getByText(/second message developer/i)).toBeInTheDocument()
  })
})
