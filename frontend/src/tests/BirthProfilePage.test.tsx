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
    expect(screen.getByText(/req-gen-123/i)).toBeInTheDocument()
  })

  it("shows specific error message when natal engine is unavailable", async () => {
    setupToken()
    const UNAVAILABLE_ERROR_RESPONSE = {
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "natal_engine_unavailable", message: "service unavailable", request_id: "req-gen-456" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(UNAVAILABLE_ERROR_RESPONSE),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/Le service de génération est temporairement indisponible/i)).toBeInTheDocument()
    expect(screen.getByText(/req-gen-456/i)).toBeInTheDocument()
  })

  it("shows specific error message when generation returns 422 (invalid birth data)", async () => {
    setupToken()
    const UNPROCESSABLE_RESPONSE = {
      ok: false,
      status: 422,
      json: async () => ({ error: { code: "unprocessable_entity", message: "Données invalides" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(UNPROCESSABLE_RESPONSE),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(
      await screen.findByText(/Vos données de naissance sont invalides ou incomplètes/i),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).not.toBeDisabled()
  })

  it("shows generic error message on network failure during generation", async () => {
    setupToken()
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockRejectedValue(new Error("Network error")),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/Une erreur est survenue\. Veuillez réessayer/i)).toBeInTheDocument()
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

    expect(await screen.findByText(/Impossible de charger votre profil natal/i, {}, { timeout: 3000 })).toBeInTheDocument()
    expect(screen.getByText(/req-load-456/i)).toBeInTheDocument()
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
    expect(screen.getByText(/req-save-789/i)).toBeInTheDocument()
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
    expect(body).toMatchObject(UPDATED_PROFILE)
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

    // UX refinement test: field errors PERSIST when a DIFFERENT field is modified
    fireEvent.input(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris, France" } })
    
    // The error on birth_time should STILL BE THERE (better UX than clearing everything)
    expect(screen.queryByText(/Format HH:MM\(:SS\) requis \(ex: 10:30\)/i)).toBeInTheDocument()
    
    // Now verify that if we actually modify the field in error, it should eventually clear
    // (React Hook Form handles this with reValidateMode: 'onChange' once it has been submitted)
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: "11:00" } })
    await waitFor(() => {
      expect(screen.queryByText(/Format HH:MM\(:SS\) requis \(ex: 10:30\)/i)).not.toBeInTheDocument()
    })
  })

  // H1 — AC4 : invalid_timezone manquant dans la suite de tests initiale
  it("shows inline error on birth_timezone field when API returns invalid_timezone", async () => {
    setupToken()
    const invalidTimezoneResponse = {
      ok: false,
      status: 422,
      json: async () => ({ error: { code: "invalid_timezone", message: "Fuseau horaire invalide (ex: Europe/Paris)." } }),
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(NOT_FOUND_RESPONSE).mockResolvedValue(invalidTimezoneResponse),
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

    expect(await screen.findByText(/Fuseau horaire invalide \(ex: Europe\/Paris\)/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Fuseau horaire/i)).toHaveAttribute("aria-invalid", "true")
  })

  // M1 — Régression : UTC sans slash doit passer la validation client
  it("accepts UTC as valid timezone (no slash required)", async () => {
    setupToken()
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(NOT_FOUND_RESPONSE).mockResolvedValue(SUCCESS_PUT_RESPONSE),
    )
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/Date de naissance/i), { target: { value: "1990-01-15" } })
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: "10:30" } })
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Fuseau horaire/i), { target: { value: "UTC" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    // UTC should pass client validation → API call made → success message
    expect(await screen.findByText(/Profil natal sauvegardé/i)).toBeInTheDocument()
    expect(screen.queryByText(/Format IANA requis/i)).not.toBeInTheDocument()
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

    expect(await screen.findByText(/La date de naissance est indispensable/i)).toBeInTheDocument()
    expect(screen.getByText(/Le lieu de naissance est requis/i)).toBeInTheDocument()
    expect(screen.getByText(/Le fuseau horaire est requis/i)).toBeInTheDocument()

    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveAttribute("aria-invalid", "true")
    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveAttribute(
      "aria-describedby",
      "birth-place-error",
    )
  })

  it("case 'Heure inconnue' cochée → champ désactivé + birth_time null dans payload PUT", async () => {
    setupToken()
    const putCalls: Array<{ url: string; init: RequestInit }> = []
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/birth-data") && init?.method === "PUT") {
        putCalls.push({ url, init })
        return SUCCESS_PUT_RESPONSE
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    fireEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
    expect(screen.getByLabelText(/Heure de naissance/i)).toBeDisabled()

    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(putCalls.length).toBeGreaterThan(0)
      const body = JSON.parse(putCalls[0].init.body as string)
      expect(body.birth_time).toBeNull()
    })
  })

  it("décocher 'Heure inconnue' → champ réactivé", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    renderWithProviders()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    fireEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
    expect(screen.getByLabelText(/Heure de naissance/i)).toBeDisabled()

    fireEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
    expect(screen.getByLabelText(/Heure de naissance/i)).not.toBeDisabled()
  })

  it("reset depuis API avec birth_time null → checkbox auto-cochée, champ vide", async () => {
    setupToken()
    const NULL_TIME_RESPONSE = {
      ok: true,
      status: 200,
      json: async () => ({ data: { ...VALID_PROFILE, birth_time: null }, meta: { request_id: "r1" } }),
    }
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NULL_TIME_RESPONSE))
    renderWithProviders()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    expect(screen.getByRole("checkbox", { name: /Heure inconnue/i })).toBeChecked()
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveValue("")
  })

  it("soumission sans birth_date → blocage + message indispensable (AC4)", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderWithProviders()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: "10:30" } })
    fireEvent.change(screen.getByLabelText(/Lieu de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Fuseau horaire/i), { target: { value: "Europe/Paris" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(
      await screen.findByText(/La date de naissance est indispensable pour calculer votre thème natal/i),
    ).toBeInTheDocument()
    expect(screen.getByLabelText(/Date de naissance/i)).toHaveAttribute("aria-invalid", "true")
    // Aucune requête API envoyée
    const fetchCalls = (global.fetch as ReturnType<typeof vi.fn>).mock.calls
    expect(fetchCalls.every((call) => !(call[1] as RequestInit | undefined)?.method)).toBe(true)
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

  it("disables geocoding button when city or country is empty, enables when both filled", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    const geocodeButton = screen.getByRole("button", { name: /Valider les coordonnées/i })

    // Initially both empty → disabled
    expect(geocodeButton).toBeDisabled()

    // City filled, country still empty → still disabled
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    expect(geocodeButton).toBeDisabled()

    // Both filled → enabled
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    expect(geocodeButton).not.toBeDisabled()

    // City cleared → disabled again
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "" } })
    expect(geocodeButton).toBeDisabled()
  })

  it("shows resolved geocoding label after successful Nominatim search", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("nominatim")) {
        return {
          ok: true,
          json: async () => [{ lat: "48.8566", lon: "2.3522", display_name: "Paris, Île-de-France, France" }],
        }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Valider les coordonnées/i }))

    expect(await screen.findByText(/Paris, Île-de-France, France/i)).toBeInTheDocument()
    expect(screen.getByText(/lat:/i)).toBeInTheDocument()
    
    // Check that birth_place was automatically updated (H2 Fix)
    expect(screen.getByLabelText(/Lieu de naissance/i)).toHaveValue("Paris, Île-de-France, France")
  })

  it("shows not-found error message when Nominatim returns empty array", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("nominatim")) {
        return { ok: true, json: async () => [] }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "XyzUnknown" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "ZZ" } })
    fireEvent.click(screen.getByRole("button", { name: /Valider les coordonnées/i }))

    expect(
      await screen.findByText(/Lieu introuvable/i),
    ).toBeInTheDocument()
  })

  it("shows service-unavailable error message and keeps save button active when Nominatim fails", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("nominatim")) {
        throw new Error("Network error")
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Valider les coordonnées/i }))

    expect(await screen.findByText(/Service de géocodage indisponible/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Sauvegarder/i })).not.toBeDisabled()
  })

  it("does not include birth_lat or birth_lon in save payload when geocoding was not performed (AC4)", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    // Save directly without geocoding
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    await screen.findByText(/Profil natal sauvegardé/i)

    const putCall = fetchMock.mock.calls.find((call) => {
      const [, init] = call as [RequestInfo | URL, RequestInit]
      return init?.method === "PUT"
    })
    expect(putCall).toBeDefined()
    const body = JSON.parse((putCall![1] as RequestInit).body as string)
    expect(body.birth_lat).toBeUndefined()
    expect(body.birth_lon).toBeUndefined()
  })

  it("resets geocoding state and clears resolved label when city field changes after successful geocoding (L4)", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("nominatim")) {
        return {
          ok: true,
          json: async () => [{ lat: "48.8566", lon: "2.3522", display_name: "Paris, Île-de-France, France" }],
        }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    // Successful geocode
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Valider les coordonnées/i }))
    await screen.findByText(/Paris, Île-de-France, France/i)

    // Changing city should reset geocoding state
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Lyon" } })
    await waitFor(() => {
      expect(screen.queryByText(/Paris, Île-de-France, France/i)).not.toBeInTheDocument()
    })
    expect(screen.queryByText(/lat:/i)).not.toBeInTheDocument()
  })

  it("includes birth_lat and birth_lon in save payload when geocoding succeeded", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const urlStr = String(input)
      if (urlStr.includes("nominatim")) {
        return {
          ok: true,
          json: async () => [{ lat: "48.8566", lon: "2.3522", display_name: "Paris, France" }],
        }
      }
      if (urlStr.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    // Geocode first
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Valider les coordonnées/i }))
    await screen.findByText(/Paris, France/i)

    // Then save
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    await screen.findByText(/Profil natal sauvegardé/i)

    const putCall = fetchMock.mock.calls.find((call) => {
      const [, init] = call as [string, RequestInit]
      return init?.method === "PUT"
    })
    expect(putCall).toBeDefined()
    const body = JSON.parse((putCall![1] as RequestInit).body as string)
    expect(body.birth_lat).toBeCloseTo(48.8566)
    expect(body.birth_lon).toBeCloseTo(2.3522)
  })

  it("flux complet mode dégradé: checkbox cochée → sauvegarde → génération avec birth_time null", async () => {
    setupToken()
    const onNavigate = vi.fn()
    const CHART_WITH_DEGRADED = {
      chart_id: "c1",
      metadata: { reference_version: "1.0", ruleset_version: "1.0", degraded_mode: "no_time" },
      created_at: "2026-02-22T10:00:00Z",
      result: {
        reference_version: "1.0",
        ruleset_version: "1.0",
        prepared_input: {
          birth_datetime_local: "1990-01-15T12:00:00",
          birth_datetime_utc: "1990-01-15T12:00:00Z",
          timestamp_utc: 632491200,
          julian_day: 2447907.0,
          birth_timezone: "UTC",
        },
        planet_positions: [],
        houses: [],
        aspects: [],
      },
    }
    const putCalls: Array<{ url: string; body: string }> = []
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/birth-data")) {
        if (init?.method === "PUT") {
          putCalls.push({ url, body: init.body as string })
          return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
        }
        return SUCCESS_GET_RESPONSE
      }
      if (url.includes("/natal-chart") && init?.method === "POST") {
        return { ok: true, status: 200, json: async () => ({ data: CHART_WITH_DEGRADED, meta: { request_id: "r3" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders(onNavigate)

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    // Step 1: Check "Heure inconnue"
    fireEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
    expect(screen.getByLabelText(/Heure de naissance/i)).toBeDisabled()

    // Step 2: Save profile
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    await screen.findByText(/Profil natal sauvegardé/i)

    // Verify birth_time is null in PUT payload
    expect(putCalls.length).toBeGreaterThan(0)
    const savedBody = JSON.parse(putCalls[0].body)
    expect(savedBody.birth_time).toBeNull()

    // Step 3: Generate natal chart
    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    // Step 4: Verify navigation to natal view
    await waitFor(() => {
      expect(onNavigate).toHaveBeenCalledWith("natal")
    })
  })

  it("flux complet mode dégradé no_location: géocodage échoué → sauvegarde sans coords → génération", async () => {
    setupToken()
    const onNavigate = vi.fn()
    const CHART_NO_LOCATION = {
      chart_id: "c2",
      metadata: { reference_version: "1.0", ruleset_version: "1.0", degraded_mode: "no_location" },
      created_at: "2026-02-22T10:00:00Z",
      result: {
        reference_version: "1.0",
        ruleset_version: "1.0",
        prepared_input: {
          birth_datetime_local: "1990-01-15T10:30:00",
          birth_datetime_utc: "1990-01-15T09:30:00Z",
          timestamp_utc: 632400600,
          julian_day: 2447907.896,
          birth_timezone: "Europe/Paris",
        },
        planet_positions: [],
        houses: [],
        aspects: [],
      },
    }
    const putCalls: Array<{ url: string; body: string }> = []
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("nominatim")) {
        return { ok: true, json: async () => [] }
      }
      if (url.includes("/birth-data")) {
        if (init?.method === "PUT") {
          putCalls.push({ url, body: init.body as string })
          return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
        }
        return SUCCESS_GET_RESPONSE
      }
      if (url.includes("/natal-chart") && init?.method === "POST") {
        return { ok: true, status: 200, json: async () => ({ data: CHART_NO_LOCATION, meta: { request_id: "r3" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderWithProviders(onNavigate)

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    // Step 1: Try geocoding with unknown location
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "UnknownCity" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "ZZ" } })
    fireEvent.click(screen.getByRole("button", { name: /Valider les coordonnées/i }))
    await screen.findByText(/Lieu introuvable/i)

    // Step 2: Save profile without coords (degraded mode)
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    await screen.findByText(/Profil natal sauvegardé/i)

    // Verify no birth_lat/birth_lon in PUT payload
    expect(putCalls.length).toBeGreaterThan(0)
    const savedBody = JSON.parse(putCalls[0].body)
    expect(savedBody.birth_lat).toBeUndefined()
    expect(savedBody.birth_lon).toBeUndefined()

    // Step 3: Generate natal chart
    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    // Step 4: Verify navigation to natal view
    await waitFor(() => {
      expect(onNavigate).toHaveBeenCalledWith("natal")
    })
  })
})
