import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminContentPage } from "../pages/admin/AdminContentPage"
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
      <AdminContentPage />
    </QueryClientProvider>,
  )
}

describe("AdminContentPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("renders sections and updates content, feature flags and rules", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.includes("/v1/admin/content/texts?category=paywall")) {
        return makeJsonResponse({
          data: [
            {
              key: "paywall.daily.locked_section",
              value: "Texte verrouillé",
              category: "paywall",
              updated_at: "2026-04-06T09:00:00Z",
              updated_by_user_id: 1,
            },
          ],
        })
      }

      if (url.includes("/v1/admin/content/texts?category=transactional")) {
        return makeJsonResponse({
          data: [
            {
              key: "transactional.billing.success",
              value: "Paiement confirmé",
              category: "transactional",
              updated_at: "2026-04-06T09:00:00Z",
              updated_by_user_id: 1,
            },
          ],
        })
      }

      if (url.includes("/v1/admin/content/texts?category=marketing")) {
        return makeJsonResponse({
          data: [
            {
              key: "marketing.in_app.welcome",
              value: "Bienvenue premium",
              category: "marketing",
              updated_at: "2026-04-06T09:00:00Z",
              updated_by_user_id: 1,
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/content/feature-flags")) {
        return makeJsonResponse({
          data: [
            {
              key: "paywall_experiment_copy",
              description: "Expérimentation wording",
              enabled: false,
              target_roles: [],
              target_user_ids: [],
              updated_by_user_id: 1,
              updated_at: "2026-04-06T09:00:00Z",
              scope: "Tous plans",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/content/editorial-templates")) {
        return makeJsonResponse({
          data: [
            {
              template_code: "daily_overview",
              title: "Daily overview",
              active_version_id: "version-1",
              active_version_number: 1,
              published_at: "2026-04-06T09:00:00Z",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/content/editorial-templates/daily_overview")) {
        return makeJsonResponse({
          data: {
            template_code: "daily_overview",
            active_version_id: "version-1",
            versions: [
              {
                id: "version-1",
                template_code: "daily_overview",
                version_number: 1,
                title: "Daily overview",
                content: "<intro>\n<advice>",
                expected_tags: ["intro", "advice"],
                example_render: "Exemple",
                status: "published",
                created_at: "2026-04-06T09:00:00Z",
                published_at: "2026-04-06T09:00:00Z",
                created_by_user_id: 1,
              },
              {
                id: "version-0",
                template_code: "daily_overview",
                version_number: 0,
                title: "Daily overview old",
                content: "<intro>",
                expected_tags: ["intro"],
                example_render: "Ancien",
                status: "archived",
                created_at: "2026-04-05T09:00:00Z",
                published_at: "2026-04-05T09:00:00Z",
                created_by_user_id: 1,
              },
            ],
          },
        })
      }

      if (url.endsWith("/v1/admin/content/calibration-rules")) {
        return makeJsonResponse({
          data: [
            {
              rule_code: "scores.flat_day_threshold",
              value: "0.45",
              data_type: "float",
              description: "Seuil journée plate",
              ruleset_version: "2026.04",
            },
          ],
        })
      }

      if (url.endsWith("/v1/admin/content/texts/paywall.daily.locked_section") && init?.method === "PATCH") {
        return makeJsonResponse({
          data: {
            key: "paywall.daily.locked_section",
            value: "Texte mis à jour",
            category: "paywall",
            updated_at: "2026-04-06T10:00:00Z",
            updated_by_user_id: 1,
          },
        })
      }

      if (url.endsWith("/v1/admin/content/feature-flags/paywall_experiment_copy") && init?.method === "PATCH") {
        return makeJsonResponse({
          data: {
            key: "paywall_experiment_copy",
            description: "Expérimentation wording",
            enabled: true,
            target_roles: [],
            target_user_ids: [],
            updated_by_user_id: 1,
            updated_at: "2026-04-06T10:00:00Z",
            scope: "Tous plans",
          },
        })
      }

      if (url.endsWith("/v1/admin/content/editorial-templates/daily_overview/versions") && init?.method === "POST") {
        return makeJsonResponse({
          data: {
            template_code: "daily_overview",
            active_version_id: "version-2",
            versions: [],
          },
        })
      }

      if (url.endsWith("/v1/admin/content/editorial-templates/daily_overview/rollback") && init?.method === "POST") {
        return makeJsonResponse({
          data: {
            template_code: "daily_overview",
            active_version_id: "version-0",
            versions: [],
          },
        })
      }

      if (url.endsWith("/v1/admin/content/calibration-rules/scores.flat_day_threshold") && init?.method === "PATCH") {
        return makeJsonResponse({
          data: {
            rule_code: "scores.flat_day_threshold",
            value: "0.55",
            data_type: "float",
            description: "Seuil journée plate",
            ruleset_version: "2026.04",
          },
        })
      }

      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })

    vi.stubGlobal("fetch", fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Contenus & Paywalls" })).toBeInTheDocument()
    })

    expect(screen.getByRole("tab", { name: "Textes paywalls" })).toBeInTheDocument()
    expect(screen.getByRole("tab", { name: "Messages transactionnels" })).toBeInTheDocument()
    expect(screen.getByRole("tab", { name: "Feature flags" })).toBeInTheDocument()

    const paywallInput = await screen.findByLabelText("Texte paywall.daily.locked_section")
    await userEvent.clear(paywallInput)
    await userEvent.type(paywallInput, "Texte mis à jour")
    await userEvent.click(screen.getByRole("button", { name: "Sauvegarder" }))

    await waitFor(() => {
      expect(screen.getByText("Texte paywall.daily.locked_section mis à jour.")).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("tab", { name: "Feature flags" }))
    await userEvent.click(screen.getByRole("button", { name: "Activer" }))

    await waitFor(() => {
      expect(screen.getByRole("dialog", { name: "Confirmer le changement du feature flag" })).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("button", { name: "Confirmer" }))

    await userEvent.click(screen.getByRole("tab", { name: "Règles métier" }))

    await waitFor(() => {
      expect(screen.getByText("Templates éditoriaux")).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("button", { name: "Rollback" }))

    await userEvent.clear(screen.getByLabelText("Valeur scores.flat_day_threshold"))
    await userEvent.type(screen.getByLabelText("Valeur scores.flat_day_threshold"), "0.55")
    await userEvent.click(screen.getByRole("button", { name: "Sauvegarder" }))

    await waitFor(() => {
      expect(screen.getByRole("dialog", { name: "Confirmer la mise à jour de la règle" })).toBeInTheDocument()
    })
  })
})
