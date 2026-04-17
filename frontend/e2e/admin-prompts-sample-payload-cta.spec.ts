import { expect, test } from "@playwright/test"

/** Même encodage que les tests Vitest (JWT factice admin). */
const ADMIN_ACCESS_TOKEN = "x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y"

const AUTH_ME_BODY = JSON.stringify({
  data: {
    id: 1,
    role: "admin",
    email: "playwright-admin@example.com",
    created_at: "2026-04-17T00:00:00Z",
  },
})

const CATALOG_LIST_BODY = JSON.stringify({
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

const RESOLVED_ASSEMBLY_BODY = JSON.stringify({
  data: {
    manifest_entry_id: "chat:chat_default:premium:fr-FR",
    feature: "chat",
    subfeature: "chat_default",
    plan: "premium",
    locale: "fr-FR",
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
  meta: { request_id: "e2e-resolved" },
})

const SAMPLE_PAYLOADS_EMPTY_BODY = JSON.stringify({
  data: {
    items: [],
    recommended_default_id: null,
  },
  meta: { request_id: "e2e-samples" },
})

const USE_CASES_EMPTY_BODY = JSON.stringify({ data: [] })

async function setupAdminPromptsApiMocks(page: import("@playwright/test").Page) {
  await page.route("**/v1/auth/me**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: AUTH_ME_BODY,
    })
  })

  await page.route("**/v1/admin/llm/use-cases**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: USE_CASES_EMPTY_BODY,
    })
  })

  await page.route("**/v1/admin/llm/catalog**", async (route) => {
    const url = route.request().url()
    if (url.includes("/resolved")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: RESOLVED_ASSEMBLY_BODY,
      })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: CATALOG_LIST_BODY,
    })
  })

  await page.route("**/v1/admin/llm/sample-payloads**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: SAMPLE_PAYLOADS_EMPTY_BODY,
    })
  })
}

test.describe("Admin prompts — sample payloads", () => {
  test("depuis Données d'exemple, le lien ouvre l'onglet Échantillons runtime avec la cible présélectionnée", async ({
    page,
  }) => {
    const pageErrors: string[] = []
    page.on("pageerror", (err) => pageErrors.push(err.message))

    await setupAdminPromptsApiMocks(page)

    await page.addInitScript((token: string) => {
      window.localStorage.setItem("access_token", token)
      window.localStorage.setItem("lang", "fr")
    }, ADMIN_ACCESS_TOKEN)

    await page.goto("/admin/prompts")
    await expect(page.getByRole("heading", { name: "Catalogue prompts LLM" })).toBeVisible()

    await page.getByRole("button", { name: "Ouvrir le detail" }).click()
    await expect(page.getByRole("heading", { name: "Assembly prompt résolue" })).toBeVisible()

    const cta = page.getByRole("button", { name: /Gérer les sample payloads \(chat \/ fr-FR\)/ })
    await expect(cta).toBeVisible()
    await cta.click()

    const samplesTab = page.getByRole("tab", { name: "Échantillons runtime" })
    await expect(samplesTab).toHaveAttribute("aria-selected", "true")

    await expect(page.getByRole("region", { name: "Gestion des sample payloads" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "Échantillons runtime (sample payloads)" })).toBeVisible()

    await expect(page.getByLabel("Feature pour les sample payloads")).toHaveValue("chat")
    await expect(page.getByLabel("Locale pour les sample payloads")).toHaveValue("fr-FR")

    expect(pageErrors).toEqual([])
  })
})
