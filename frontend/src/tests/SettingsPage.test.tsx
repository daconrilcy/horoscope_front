import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { createMemoryRouter, RouterProvider } from "react-router-dom"

import { setAccessToken } from "../utils/authToken"
import { routes } from "../app/routes"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

const AUTH_ME_USER = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      id: 42,
      role: "user",
      email: "test@example.com",
      created_at: "2025-01-15T10:30:00Z",
    },
  }),
}

const BILLING_SUBSCRIPTION = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      status: "active",
      plan: {
        code: "basic-entry",
        display_name: "Basic",
        monthly_price_cents: 500,
        currency: "EUR",
        daily_message_limit: 5,
        is_active: true,
      },
      failure_reason: null,
      updated_at: "2026-01-01T00:00:00Z",
    },
  }),
}

const BILLING_QUOTA = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      quota_date: "2026-02-23",
      limit: 5,
      consumed: 2,
      remaining: 3,
      reset_at: "2026-02-24T00:00:00Z",
      blocked: false,
    },
  }),
}

const EXPORT_STATUS_NONE = {
  ok: true,
  status: 200,
  json: async () => ({ data: null }),
}

const DELETE_STATUS_NONE = {
  ok: true,
  status: 200,
  json: async () => ({ data: null }),
}

const DELETE_SUCCESS = {
  ok: true,
  status: 200,
  json: async () => ({ data: { status: "completed" } }),
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

function makeFetchMock(overrides: Record<string, object> = {}) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.endsWith("/v1/auth/me")) return overrides.authMe ?? AUTH_ME_USER
    if (url.endsWith("/v1/billing/subscription")) return overrides.subscription ?? BILLING_SUBSCRIPTION
    if (url.endsWith("/v1/billing/quota")) return overrides.quota ?? BILLING_QUOTA
    if (url.endsWith("/v1/privacy/export")) return overrides.exportStatus ?? EXPORT_STATUS_NONE
    if (url.endsWith("/v1/privacy/delete")) {
      if (overrides.deleteAction) return overrides.deleteAction
      return overrides.deleteStatus ?? DELETE_STATUS_NONE
    }
    return NOT_FOUND
  })
}

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

function renderWithRouter(initialEntries: string[] = ["/settings"]) {
  const router = createMemoryRouter(routes, {
    initialEntries,
    future: { v7_relativeSplatPath: true },
  })
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  })

  return {
    router,
    ...render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} future={{ v7_startTransition: true }} />
      </QueryClientProvider>
    ),
  }
}

describe("SettingsPage", () => {
  describe("AC1: Navigation settings", () => {
    it("affiche les onglets Compte, Abonnement, Usage", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Paramètres" })).toBeInTheDocument()
      })

      const nav = screen.getByRole("navigation", { name: "Navigation des paramètres" })
      expect(within(nav).getByRole("link", { name: "Compte" })).toBeInTheDocument()
      expect(within(nav).getByRole("link", { name: "Abonnement" })).toBeInTheDocument()
      expect(within(nav).getByRole("link", { name: "Usage" })).toBeInTheDocument()
    })

    it("redirige vers /settings/account par défaut", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      const { router } = renderWithRouter(["/settings"])

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/account")
      })
    })

    it("navigue entre les onglets", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/settings"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Paramètres" })).toBeInTheDocument()
      })

      // Use IDs to avoid ambiguity with AppShell links
      const subscriptionTab = document.getElementById("settings-tab-subscription") as HTMLElement
      await user.click(subscriptionTab)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/subscription")
      })

      const usageTab = document.getElementById("settings-tab-usage") as HTMLElement
      await user.click(usageTab)

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/usage")
      })
    })

    it("navigue entre les onglets avec les touches flèches", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Paramètres" })).toBeInTheDocument()
      })

      const accountTab = document.getElementById("settings-tab-account") as HTMLElement
      accountTab.focus()

      await user.keyboard("{ArrowRight}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/subscription")
      })

      await user.keyboard("{ArrowRight}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/usage")
      })

      await user.keyboard("{ArrowRight}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/account")
      })

      await user.keyboard("{ArrowLeft}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/usage")
      })
    })

    it("navigue avec Home et End", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/settings/subscription"])

      await waitFor(() => {
        expect(screen.getByRole("heading", { name: "Paramètres" })).toBeInTheDocument()
      })

      const subscriptionTab = document.getElementById("settings-tab-subscription") as HTMLElement
      subscriptionTab.focus()

      await user.keyboard("{End}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/usage")
      })

      await user.keyboard("{Home}")

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/settings/account")
      })
    })
  })

  describe("AC2: Page compte", () => {
    it("affiche les informations du compte (email, date inscription, rôle)", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByText("Informations du compte")).toBeInTheDocument()
      })

      await waitFor(() => {
        expect(screen.getByText("Adresse e-mail")).toBeInTheDocument()
        expect(screen.getByText("test@example.com")).toBeInTheDocument()
      })

      expect(screen.getByText("Membre depuis")).toBeInTheDocument()
      expect(screen.getByText("Rôle")).toBeInTheDocument()
      expect(screen.getByText("user")).toBeInTheDocument()
    })

    it("affiche le bouton Supprimer mon compte", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })
    })

    it("affiche le lien vers les données de naissance (AC2 - Story 16.8)", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByText("Informations du compte")).toBeInTheDocument()
      })

      await waitFor(() => {
        const birthDataLink = screen.getByRole("link", { name: "Modifier mes données de naissance" })
        expect(birthDataLink).toBeInTheDocument()
        expect(birthDataLink).toHaveAttribute("href", "/profile")
      })
    })

    it("affiche un message d'erreur quand le chargement du compte échoue", async () => {
      const AUTH_ME_ERROR = {
        ok: false,
        status: 500,
        json: async () => ({ error: { code: "server_error", message: "Internal error" } }),
      }
      vi.stubGlobal("fetch", makeFetchMock({ authMe: AUTH_ME_ERROR }))
      setupToken()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByText("Impossible de charger vos informations")).toBeInTheDocument()
      })

      expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument()
    })
  })

  describe("AC3: Suppression compte", () => {
    it("ouvre la modal de confirmation", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
        expect(screen.getByText(/Êtes-vous sûr de vouloir supprimer votre compte/)).toBeInTheDocument()
      })
    })

    it("passe à l'étape de confirmation avec le mot SUPPRIMER", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
      })

      const confirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(confirmButtons[0])

      await waitFor(() => {
        expect(screen.getByText("SUPPRIMER")).toBeInTheDocument()
        expect(screen.getByRole("textbox")).toBeInTheDocument()
      })
    })

    it("refuse la suppression si le mot ne correspond pas", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
      })

      const confirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(confirmButtons[0])

      await waitFor(() => {
        expect(screen.getByRole("textbox")).toBeInTheDocument()
      })

      await user.type(screen.getByRole("textbox"), "WRONG")
      const finalConfirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(finalConfirmButtons[0])

      await waitFor(() => {
        expect(screen.getByText("Le mot ne correspond pas")).toBeInTheDocument()
      })
    })

    it("supprime le compte et redirige vers /login", async () => {
      vi.stubGlobal("fetch", makeFetchMock({ deleteAction: DELETE_SUCCESS }))
      setupToken()
      const user = userEvent.setup()

      const { router } = renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
      })

      const confirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(confirmButtons[0])

      await waitFor(() => {
        expect(screen.getByRole("textbox")).toBeInTheDocument()
      })

      await user.type(screen.getByRole("textbox"), "SUPPRIMER")
      const finalConfirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(finalConfirmButtons[0])

      await waitFor(() => {
        expect(router.state.location.pathname).toBe("/login")
      })
    })

    it("ferme la modal avec Annuler", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Annuler" }))

      await waitFor(() => {
        expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
      })
    })

    it("affiche un message d'erreur quand l'API de suppression échoue", async () => {
      const DELETE_ERROR = {
        ok: false,
        status: 500,
        json: async () => ({ error: { code: "server_error", message: "Internal error" } }),
      }
      vi.stubGlobal("fetch", makeFetchMock({ deleteAction: DELETE_ERROR }))
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
      })

      const confirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(confirmButtons[0])

      await waitFor(() => {
        expect(screen.getByRole("textbox")).toBeInTheDocument()
      })

      await user.type(screen.getByRole("textbox"), "SUPPRIMER")
      const finalConfirmButtons = screen.getAllByRole("button", { name: "Confirmer la suppression" })
      await user.click(finalConfirmButtons[0])

      await waitFor(() => {
        expect(screen.getByText("Une erreur est survenue. Veuillez réessayer.")).toBeInTheDocument()
      })

      expect(screen.getByRole("dialog")).toBeInTheDocument()
    })

    it("ferme la modal avec la touche Escape", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()
      const user = userEvent.setup()

      renderWithRouter(["/settings/account"])

      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Supprimer mon compte" })).toBeInTheDocument()
      })

      await user.click(screen.getByRole("button", { name: "Supprimer mon compte" }))

      await waitFor(() => {
        expect(screen.getByRole("dialog")).toBeInTheDocument()
      })

      await user.keyboard("{Escape}")

      await waitFor(() => {
        expect(screen.queryByRole("dialog")).not.toBeInTheDocument()
      })
    })
  })

  describe("AC4: Page abonnement", () => {
    it("affiche le BillingPanel avec le plan actuel", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/subscription"])

      await waitFor(() => {
        expect(screen.getByText("Mon abonnement")).toBeInTheDocument()
      })

      await waitFor(() => {
        expect(screen.getByText(/Statut: actif/)).toBeInTheDocument()
        expect(screen.getByText(/Plan: Basic/)).toBeInTheDocument()
      })
    })
  })

  describe("AC5: Page usage", () => {
    it("affiche les statistiques de consommation", async () => {
      vi.stubGlobal("fetch", makeFetchMock())
      setupToken()

      renderWithRouter(["/settings/usage"])

      await waitFor(() => {
        expect(screen.getByText("Statistiques d'usage")).toBeInTheDocument()
      })

      await waitFor(() => {
        expect(screen.getByText("Messages envoyés")).toBeInTheDocument()
        expect(screen.getByText("2")).toBeInTheDocument()
        expect(screen.getByText("Limite")).toBeInTheDocument()
        expect(screen.getByText("5")).toBeInTheDocument()
        expect(screen.getByText("Restants")).toBeInTheDocument()
        expect(screen.getByText("3")).toBeInTheDocument()
      })
    })

    it("affiche un message d'erreur quand le chargement des quotas échoue", async () => {
      const QUOTA_ERROR = {
        ok: false,
        status: 500,
        json: async () => ({ error: { code: "server_error", message: "Internal error" } }),
      }
      vi.stubGlobal("fetch", makeFetchMock({ quota: QUOTA_ERROR }))
      setupToken()

      renderWithRouter(["/settings/usage"])

      await waitFor(() => {
        expect(screen.getByText("Statistiques d'usage")).toBeInTheDocument()
      })

      await waitFor(() => {
        expect(screen.getByText(/Erreur de chargement/)).toBeInTheDocument()
        expect(screen.getByText(/Erreur serveur/)).toBeInTheDocument()
      })

      expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument()
    })
  })
})
