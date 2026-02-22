import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"

import { BirthProfilePage } from "../pages/BirthProfilePage"
import { AppProviders } from "../state/providers"
import { setAccessToken } from "../utils/authToken"

const VALID_PROFILE = {
  birth_date: "1990-01-15",
  birth_time: "10:30",
  birth_place: "Paris, France",
  birth_timezone: "Europe/Paris",
}

const SUCCESS_GET_RESPONSE = {
  ok: true,
  status: 200,
  json: async () => ({ data: VALID_PROFILE, meta: { request_id: "r1" } }),
}

const NOT_FOUND_RESPONSE = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "birth_profile_not_found", message: "not found" } }),
}

const SUCCESS_PUT_RESPONSE = {
  ok: true,
  status: 200,
  json: async () => ({ data: VALID_PROFILE, meta: { request_id: "r2" } }),
}

function renderWithProviders(onNavigate = vi.fn()) {
  return render(
    <AppProviders>
      <BirthProfilePage onNavigate={onNavigate} />
    </AppProviders>,
  )
}

function setupToken() {
  const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe("BirthProfilePage", () => {
  it("shows loading then pre-fills form with existing birth data", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    renderWithProviders()

    expect(screen.getByText(/Chargement de votre profil natal/i)).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveValue("10:30")
    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveValue("Paris, France")
    expect(screen.getByLabelText(/Fuseau horaire/i)).toHaveValue("Europe/Paris")
  })

  it("shows the generation button only if birth data exists", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    expect(screen.queryByRole("button", { name: /Générer mon thème astral/i })).not.toBeInTheDocument()

    // Mock successful get
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    cleanup()
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })
  })

  it("generates natal chart successfully and navigates to natal view", async () => {
    setupToken()
    const onNavigate = vi.fn()
    const SUCCESS_GENERATE_RESPONSE = {
      ok: true,
      status: 200,
      json: async () => ({ data: { chart_id: "c1" }, meta: { request_id: "r3" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(SUCCESS_GENERATE_RESPONSE),
    )
    renderWithProviders(onNavigate)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    await waitFor(() => {
      expect(onNavigate).toHaveBeenCalledWith("natal")
    })
  })

  it("shows specific error message and requestId on natal generation timeout", async () => {
    setupToken()
    const TIMEOUT_ERROR_RESPONSE = {
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "natal_generation_timeout", message: "timeout", request_id: "req-gen-123" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(TIMEOUT_ERROR_RESPONSE),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/La génération a pris trop de temps/i)).toBeInTheDocument()
    expect(screen.getByText(/ID de requête: req-gen-123/i)).toBeInTheDocument()
  })

  it("shows error message and requestId when initial data load fails", async () => {
    setupToken()
    const errorResponse = {
      ok: false,
      status: 500,
      json: async () => ({ error: { code: "internal_error", message: "server error", request_id: "req-load-456" } }),
    }
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(errorResponse))
    renderWithProviders()

    expect(await screen.findByText(/Impossible de charger votre profil natal/i)).toBeInTheDocument()
    expect(screen.getByText(/ID de requête: req-load-456/i)).toBeInTheDocument()
  })

  it("shows global error and requestId when saving birth data fails with a general error", async () => {
    setupToken()
    const errorResponse = {
      ok: false,
      status: 422,
      json: async () => ({ error: { code: "invalid_birth_input", message: "general error", request_id: "req-save-789" } }),
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(NOT_FOUND_RESPONSE).mockResolvedValue(errorResponse),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/Date de naissance/i), { target: { value: "1990-01-15" } })
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: "10:30" } })
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Fuseau horaire/i), { target: { value: "Europe/Paris" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Données invalides/i)).toBeInTheDocument()
    expect(screen.getByText(/ID de requête: req-save-789/i)).toBeInTheDocument()
  })

  it("shows empty form without error when birth profile is not found (404)", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })
    expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("")
    expect(screen.queryByRole("alert")).not.toBeInTheDocument()
  })

  it("shows success message after saving birth data and verifies payload with updated values", async () => {
    setupToken()
    const UPDATED_PROFILE = { ...VALID_PROFILE, birth_place: "Lyon, France" }
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/users/me/birth-data")) {
        if (init?.method === "PUT") {
          return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
        }
        return SUCCESS_GET_RESPONSE
      }
      return NOT_FOUND_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Lyon, France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Profil natal sauvegardé/i)).toBeInTheDocument()

    // Check payload after success
    const lastCall = fetchMock.mock.calls.find((call) => call[1]?.method === "PUT")
    expect(lastCall).toBeDefined()
    const body = JSON.parse(lastCall![1]!.body as string)
    expect(body).toEqual(UPDATED_PROFILE)
  })

  it("removes success message when user modifies a field after saving", async () => {
    setupToken()
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(SUCCESS_PUT_RESPONSE),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Profil natal sauvegardé/i)).toBeInTheDocument()

    // Simulate user typing which should trigger 'watch' and clear success message
    fireEvent.input(screen.getByLabelText(/Date de naissance/i), {
      target: { value: "1991-02-20" },
    })

    await waitFor(() => {
      expect(screen.queryByText(/Profil natal sauvegardé/i)).not.toBeInTheDocument()
    })
  })

  it("shows inline error on birth_time field when API returns invalid_birth_time", async () => {
    setupToken()
    const invalidTimeResponse = {
      ok: false,
      status: 422,
      json: async () => ({ error: { code: "invalid_birth_time", message: "Format HH:MM(:SS) requis (ex: 10:30)" } }),
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(NOT_FOUND_RESPONSE).mockResolvedValue(invalidTimeResponse),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    // Use values that PASS Zod but trigger the mocked API error
    fireEvent.change(screen.getByLabelText(/Date de naissance/i), {
      target: { value: "1990-01-15" },
    })
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), {
      target: { value: "10:30" },
    })
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Fuseau horaire/i), {
      target: { value: "Europe/Paris" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    // Now it should reach the API and get the "Format HH:MM(:SS) requis (ex: 10:30)" error
    expect(await screen.findByText(/Format HH:MM\(:SS\) requis \(ex: 10:30\)/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveAttribute("aria-invalid", "true")

    // UX refinement test: clearing errors
    fireEvent.input(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris, France" } })
    await waitFor(() => {
      expect(screen.queryByText(/Format HH:MM\(:SS\) requis \(ex: 10:30\)/i)).not.toBeInTheDocument()
    })
  })

  it("shows generic error message on network failure during save", async () => {
    setupToken()
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(NOT_FOUND_RESPONSE).mockRejectedValue(new Error("Network error")),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/Date de naissance/i), {
      target: { value: "1990-01-15" },
    })
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), {
      target: { value: "10:30" },
    })
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Fuseau horaire/i), {
      target: { value: "Europe/Paris" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Erreur lors de la sauvegarde. Veuillez réessayer/i)).toBeInTheDocument()
  })

  it("blocks client-side submission and shows inline errors for missing fields", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    // Submit empty form
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Format YYYY-MM-DD requis/i)).toBeInTheDocument()
    expect(screen.getByText(/Le lieu de naissance est requis/i)).toBeInTheDocument()
    expect(screen.getByText(/Le fuseau horaire est requis/i)).toBeInTheDocument()

    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveAttribute("aria-invalid", "true")
    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveAttribute(
      "aria-describedby",
      "birth-place-error",
    )
  })

  it("blocks client-side submission for a future date", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    const nextYear = new Date().getFullYear() + 1
    fireEvent.change(screen.getByLabelText(/Date de naissance/i), {
      target: { value: `${nextYear}-01-15` },
    })
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), {
      target: { value: "10:30" },
    })
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Fuseau horaire/i), {
      target: { value: "Europe/Paris" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/La date de naissance ne peut pas être dans le futur/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Date de naissance/i)).toHaveAttribute("aria-invalid", "true")
  })

  it("prevents background reset when form is dirty", async () => {
    setupToken()
    // Initial data: VALID_PROFILE
    const fetchMock = vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE)
    vi.stubGlobal("fetch", fetchMock)
    
    const { rerender } = renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    // User starts typing
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "New York" } })
    
    // Simulate background refetch with different data
    const NEW_DATA = { ...VALID_PROFILE, birth_place: "London" }
    fetchMock.mockResolvedValue({ ok: true, status: 200, json: async () => ({ data: NEW_DATA }) })
    
    rerender(<AppProviders><BirthProfilePage onNavigate={vi.fn()} /></AppProviders>)

    // Form should still have "New York", not "London"
    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveValue("New York")
  })
})
