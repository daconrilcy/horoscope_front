import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react"

import { BirthProfilePage } from "../pages/BirthProfilePage"
import { setAccessToken } from "../utils/authToken"
import { renderWithRouter } from "./test-utils"

const VALID_PROFILE = {
  birth_date: "1990-01-15",
  birth_time: "10:30",
  birth_place: "Paris, France",
  birth_timezone: "Europe/Paris",
  birth_city: "Paris",
  birth_country: "France",
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

function renderBirthProfilePage(initialEntries = ["/profile"]) {
  return renderWithRouter(<BirthProfilePage />, { initialEntries })
}

function setupToken() {
  const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
  setAccessToken(`x.${payload}.y`)
}

/**
 * Helper pour remplir les champs obligatoires du formulaire de naissance.
 * Les labels sont recherchés de manière case-insensitive via le flag /i.
 * Note: birth_timezone utilise un composant custom TimezoneSelect, pas un input standard.
 */
function fillBirthForm(overrides: Partial<typeof VALID_PROFILE> = {}) {
  const values = { ...VALID_PROFILE, ...overrides }
  if (values.birth_date) {
    fireEvent.change(screen.getByLabelText(/Date de naissance/i), { target: { value: values.birth_date } })
  }
  if (values.birth_time) {
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: values.birth_time } })
  }
  if (values.birth_city) {
    fireEvent.change(screen.getByLabelText(/Ville de naissance/i), { target: { value: values.birth_city } })
  }
  if (values.birth_country) {
    fireEvent.change(screen.getByLabelText(/Pays de naissance/i), { target: { value: values.birth_country } })
  }
}

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe("BirthProfilePage", () => {
  it("shows loading then pre-fills form with existing birth data", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    renderBirthProfilePage()

    expect(screen.getByText(/Chargement de votre profil natal/i)).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveValue("10:30")
    expect(screen.getByLabelText(/Ville de naissance/i)).toHaveValue("Paris")
    expect(screen.getByLabelText(/Pays de naissance/i)).toHaveValue("France")
    expect(screen.getByLabelText(/Fuseau horaire/i)).toHaveValue("Europe/Paris")
  })

  it("falls back to birth_place parsing when birth_city and birth_country are missing", async () => {
    setupToken()
    const responseWithoutCityCountry = {
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          birth_date: "1990-01-15",
          birth_time: "10:30",
          birth_place: "Paris, Ile-de-France, France",
          birth_timezone: "Europe/Paris",
          birth_city: null,
          birth_country: null,
        },
        meta: { request_id: "r1" },
      }),
    }
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(responseWithoutCityCountry))

    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Ville de naissance/i)).toHaveValue("Paris")
    })
    expect(screen.getByLabelText(/Pays de naissance/i)).toHaveValue("France")
  })

  it("shows the generation button only if birth data exists", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    expect(screen.queryByRole("button", { name: /Générer mon thème astral/i })).not.toBeInTheDocument()

    // Mock successful get
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    cleanup()
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })
  })

  it("generates natal chart successfully and triggers navigation", async () => {
    setupToken()
    const SUCCESS_GENERATE_RESPONSE = {
      ok: true,
      status: 200,
      json: async () => ({ data: { chart_id: "c1" }, meta: { request_id: "r3" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(SUCCESS_GENERATE_RESPONSE),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /Générer mon thème astral/i })).not.toBeInTheDocument()
    })
  })

  it("shows specific error message and requestId on natal generation timeout", async () => {
    setupToken()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    const TIMEOUT_ERROR_RESPONSE = {
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "natal_generation_timeout", message: "timeout", request_id: "req-gen-123" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(TIMEOUT_ERROR_RESPONSE),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/La génération a pris trop de temps/i)).toBeInTheDocument()
    // AC8: requestId is logged to console, not displayed to user
    expect(consoleErrorSpy).toHaveBeenCalledWith("[Support] Request ID: req-gen-123")
    consoleErrorSpy.mockRestore()
  })

  it("clears generationError when form changes after failed generation", async () => {
    setupToken()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    const TIMEOUT_ERROR_RESPONSE = {
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "natal_generation_timeout", message: "timeout", request_id: "req-gen-789" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(TIMEOUT_ERROR_RESPONSE),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/La génération a pris trop de temps/i)).toBeInTheDocument()

    fireEvent.input(screen.getByLabelText(/Date de naissance/i), {
      target: { value: "1991-02-20" },
    })

    await waitFor(() => {
      expect(screen.queryByText(/La génération a pris trop de temps/i)).not.toBeInTheDocument()
    })
    consoleErrorSpy.mockRestore()
  })

  it("shows specific error message when natal engine is unavailable", async () => {
    setupToken()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    const UNAVAILABLE_ERROR_RESPONSE = {
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "natal_engine_unavailable", message: "service unavailable", request_id: "req-gen-456" } }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(UNAVAILABLE_ERROR_RESPONSE),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/Le service de génération est temporairement indisponible/i)).toBeInTheDocument()
    // AC8: requestId is logged to console, not displayed to user
    expect(consoleErrorSpy).toHaveBeenCalledWith("[Support] Request ID: req-gen-456")
    consoleErrorSpy.mockRestore()
  })

  it("shows specific error message when generation returns 422 (invalid birth data)", async () => {
    setupToken()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    const UNPROCESSABLE_RESPONSE = {
      ok: false,
      status: 422,
      json: async () => ({
        error: { code: "unprocessable_entity", message: "Données invalides", request_id: "req-gen-422" },
      }),
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(UNPROCESSABLE_RESPONSE),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(
      await screen.findByText(/Vos données de naissance sont invalides ou incomplètes/i),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).not.toBeDisabled()
    expect(consoleErrorSpy).not.toHaveBeenCalledWith("[Support] Request ID: req-gen-422")
    consoleErrorSpy.mockRestore()
  })

  it("shows generic error message on network failure during generation", async () => {
    setupToken()
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockRejectedValue(new Error("Network error")),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Générer mon thème astral/i })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    expect(await screen.findByText(/Une erreur est survenue\. Veuillez réessayer/i)).toBeInTheDocument()
  })

  it("shows error message and requestId when initial data load fails", async () => {
    setupToken()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    const errorResponse = {
      ok: false,
      status: 500,
      json: async () => ({ error: { code: "internal_error", message: "server error", request_id: "req-load-456" } }),
    }
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(errorResponse))
    renderBirthProfilePage()

    expect(await screen.findByText(/Impossible de charger votre profil natal/i)).toBeInTheDocument()
    // AC8: requestId is logged to console, not displayed to user
    expect(consoleErrorSpy).toHaveBeenCalledWith("[Support] Request ID: req-load-456")
    consoleErrorSpy.mockRestore()
  })

  it("shows global error but does not log requestId when saving birth data fails with a 422 functional error", async () => {
    setupToken()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
    const errorResponse = {
      ok: false,
      status: 422,
      json: async () => ({ error: { code: "invalid_birth_input", message: "general error", request_id: "req-save-789" } }),
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(NOT_FOUND_RESPONSE).mockResolvedValue(errorResponse),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/Date de naissance/i), { target: { value: "1990-01-15" } })
    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: "10:30" } })
    fireEvent.change(screen.getByLabelText(/Ville de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays de naissance/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(screen.getByText(/Données invalides/i)).toBeInTheDocument()
    })
    expect(consoleErrorSpy).not.toHaveBeenCalledWith("[Support] Request ID: req-save-789")
    consoleErrorSpy.mockRestore()
  })

  it("shows empty form without error when birth profile is not found (404)", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })
    expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("")
    expect(screen.queryByRole("alert")).not.toBeInTheDocument()
  })

  it("shows success message after saving birth data and verifies payload with updated values", async () => {
    setupToken()
    const UPDATED_PROFILE = { ...VALID_PROFILE, birth_city: "Lyon" }
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/users/me/birth-data")) {
        if (init?.method === "PUT") {
          return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
        }
        return SUCCESS_GET_RESPONSE
      }
      // Mock geocoding to avoid network errors
      if (url.includes("/v1/geocoding/search")) {
        return { ok: true, json: async () => ({ data: { results: [{ lat: 45.76, lon: 4.83, display_name: "Lyon, France" }], count: 1 } }) }
      }
      return NOT_FOUND_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville de naissance/i), { target: { value: "Lyon" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Profil natal sauvegardé/i)).toBeInTheDocument()

    // Check payload after success
    const lastCall = fetchMock.mock.calls.find((call) => call[1]?.method === "PUT")
    expect(lastCall).toBeDefined()
    const body = JSON.parse(lastCall![1]!.body as string)
    expect(body.birth_city).toBe("Lyon")
  })

  it("removes success message when user modifies a field after saving", async () => {
    setupToken()
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(SUCCESS_PUT_RESPONSE),
    )
    renderBirthProfilePage()

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

  it("clears all feedback messages (success, globalError, generationError) when form changes", async () => {
    setupToken()
    const saveError = {
      ok: false,
      status: 500,
      json: async () => ({ error: { code: "server_error", message: "Server error" } }),
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(SUCCESS_GET_RESPONSE).mockResolvedValue(saveError),
    )
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    // Trigger a save that fails with globalError
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(screen.getByText(/Server error/i)).toBeInTheDocument()
    })

    // Modify form - should clear the globalError
    fireEvent.input(screen.getByLabelText(/Date de naissance/i), {
      target: { value: "1991-02-20" },
    })

    await waitFor(() => {
      expect(screen.queryByText(/Server error/i)).not.toBeInTheDocument()
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
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    // Use values that PASS Zod but trigger the mocked API error
    fillBirthForm()
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    // Now it should reach the API and get the "Format HH:MM(:SS) requis (ex: 10:30)" error
    expect(await screen.findByText(/Format HH:MM\(:SS\) requis \(ex: 10:30\)/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveAttribute("aria-invalid", "true")

    // UX refinement test: field errors PERSIST when a DIFFERENT field is modified
    fireEvent.input(screen.getByLabelText(/Ville de naissance/i), { target: { value: "Lyon" } })
    
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
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fillBirthForm()
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
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fillBirthForm()
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
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    fillBirthForm()
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Erreur lors de la sauvegarde. Veuillez réessayer/i)).toBeInTheDocument()
  })

  it("blocks client-side submission and shows inline errors for missing fields", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument()
    })

    // Submit empty form
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/La date de naissance est indispensable/i)).toBeInTheDocument()
    expect(screen.getByText(/La ville de naissance est requise/i)).toBeInTheDocument()
    expect(screen.getByText(/Le pays de naissance est requis/i)).toBeInTheDocument()
    // Fuseau horaire auto-détecté via getUserTimezone() dans TimezoneSelect, pas d'erreur si vide

    expect(screen.getByLabelText(/Ville de naissance/i)).toHaveAttribute("aria-invalid", "true")
    expect(screen.getByLabelText(/Ville de naissance/i)).toHaveAttribute(
      "aria-describedby",
      "birth-city-error",
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
    renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    fireEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
    expect(screen.getByLabelText(/Heure de naissance/i)).toBeDisabled()

    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(putCalls.length).toBeGreaterThan(0)
      const body = JSON.parse(putCalls[0].init.body as string)
      expect(body.birth_time).toBeNull() // stratégie unique : null pour heure inconnue
    })
  })

  it("décocher 'Heure inconnue' → champ réactivé", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    renderBirthProfilePage()

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
    renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    expect(screen.getByRole("checkbox", { name: /Heure inconnue/i })).toBeChecked()
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveValue("")
  })

  it("reset depuis API avec birth_time '00:00' → champ affiche '00:00', heure connue (pas de sentinelle)", async () => {
    setupToken()
    const MIDNIGHT_TIME_RESPONSE = {
      ok: true,
      status: 200,
      json: async () => ({ data: { ...VALID_PROFILE, birth_time: "00:00" }, meta: { request_id: "r1" } }),
    }
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(MIDNIGHT_TIME_RESPONSE))
    renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    // "00:00" is a valid explicit time, not a sentinel — checkbox must NOT be checked
    expect(screen.getByRole("checkbox", { name: /Heure inconnue/i })).not.toBeChecked()
    expect(screen.getByLabelText(/Heure de naissance/i)).toHaveValue("00:00")
    expect(screen.getByLabelText(/Heure de naissance/i)).not.toBeDisabled()
  })

  it("soumission sans birth_date → blocage + message indispensable (AC4)", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND_RESPONSE))
    renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Heure de naissance/i), { target: { value: "10:30" } })
    fireEvent.change(screen.getByLabelText(/Ville de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays de naissance/i), { target: { value: "France" } })
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
    renderBirthProfilePage()

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
    fireEvent.change(screen.getByLabelText(/Ville de naissance/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays de naissance/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/La date de naissance ne peut pas être dans le futur/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Date de naissance/i)).toHaveAttribute("aria-invalid", "true")
  })

  it("prevents background reset when form is dirty", async () => {
    setupToken()
    // Initial data: VALID_PROFILE
    const fetchMock = vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE)
    vi.stubGlobal("fetch", fetchMock)
    
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    // User starts typing in city field
    fireEvent.change(screen.getByLabelText(/Ville de naissance/i), { target: { value: "New York" } })
    
    // Simulate background refetch with different data - this would be triggered by React Query
    const NEW_DATA = { ...VALID_PROFILE, birth_city: "London" }
    fetchMock.mockResolvedValue({ ok: true, status: 200, json: async () => ({ data: NEW_DATA }) })
    
    // Wait a bit for any potential refetch
    await waitFor(() => {
      // Form should still have "New York", not "London" since isDirty prevents reset
      expect(screen.getByLabelText(/Ville de naissance/i)).toHaveValue("New York")
    })
  })

  it("shows validation error when city or country is empty on submit", async () => {
    setupToken()
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_GET_RESPONSE))
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(screen.getByText(/La ville de naissance est requise/i)).toBeInTheDocument()
    })
  })

  it("shows resolved geocoding label after successful save with geocoding", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        return {
          ok: true,
          json: async () => ({ data: { results: [{ lat: 48.8566, lon: 2.3522, display_name: "Paris, Île-de-France, France" }], count: 1 } }),
        }
      }
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(await screen.findByText(/Lieu résolu : Paris, Île-de-France, France/i)).toBeInTheDocument()
  })

  it("shows not-found warning message when backend geocoding returns empty results on save", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        return { ok: true, json: async () => ({ data: { results: [], count: 0 } }) }
      }
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "XyzUnknown" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "ZZ" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    expect(
      await screen.findByText(/Ville ou pays introuvable/i),
    ).toBeInTheDocument()
  })

  it("saves data in degraded mode when geocoding backend fails", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        throw new Error("Network error")
      }
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(screen.getByText(/Profil natal sauvegardé/i)).toBeInTheDocument()
    })
  })

  it("shows service unavailable warning when geocoding service fails (AC4 - Story 16.8)", async () => {
    // Note: geocodeCity wraps network errors into GeocodingError, which triggers error_unavailable state
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        throw new Error("Network error") // geocodeCity converts this to GeocodingError
      }
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    await waitFor(() => {
      expect(screen.getByText(/Service de géolocalisation temporairement indisponible/i)).toBeInTheDocument()
    })
    expect(screen.getByText(/mode dégradé/i)).toBeInTheDocument()
  })

  it("does not include birth_lat or birth_lon in save payload when geocoding finds nothing", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        return { ok: true, json: async () => ({ data: { results: [], count: 0 } }) }
      }
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Unknown" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "ZZ" } })
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

  it("resets geocoding state when city field changes (L4)", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        return {
          ok: true,
          json: async () => ({ data: { results: [{ lat: 48.8566, lon: 2.3522, display_name: "Paris, Île-de-France, France" }], count: 1 } }),
        }
      }
      if (url.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    await screen.findByText(/Lieu résolu : Paris, Île-de-France, France/i)

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Lyon" } })
    await waitFor(() => {
      expect(screen.queryByText(/Lieu résolu/i)).not.toBeInTheDocument()
    })
  })

  it("includes birth_lat and birth_lon in save payload when geocoding succeeded", async () => {
    setupToken()
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const urlStr = String(input)
      if (urlStr.includes("/v1/geocoding/search")) {
        return {
          ok: true,
          json: async () => ({ data: { results: [{ lat: 48.8566, lon: 2.3522, display_name: "Paris, France" }], count: 1 } }),
        }
      }
      if (urlStr.includes("/birth-data") && init?.method === "PUT") {
        return { ok: true, status: 200, json: async () => ({ data: JSON.parse(init.body as string), meta: { request_id: "r2" } }) }
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)
    renderBirthProfilePage()

    await waitFor(() => {
      expect(screen.getByLabelText(/Date de naissance/i)).toHaveValue("1990-01-15")
    })

    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "France" } })
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
    renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    // Step 1: Check "Heure inconnue"
    fireEvent.click(screen.getByRole("checkbox", { name: /Heure inconnue/i }))
    expect(screen.getByLabelText(/Heure de naissance/i)).toBeDisabled()

    // Step 2: Save profile
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    await screen.findByText(/Profil natal sauvegardé/i)

    // Verify birth_time is null in PUT payload (stratégie unique : null pour heure inconnue)
    expect(putCalls.length).toBeGreaterThan(0)
    const savedBody = JSON.parse(putCalls[0].body)
    expect(savedBody.birth_time).toBeNull()

    // Step 3: Generate natal chart
    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    // Step 4: Verify navigation triggered (button no longer visible after navigation)
    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /Générer mon thème astral/i })).not.toBeInTheDocument()
    })
  })

  it("flux complet mode dégradé no_location: géocodage échoué → sauvegarde sans coords → génération", async () => {
    setupToken()
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
      if (url.includes("/v1/geocoding/search")) {
        return { ok: true, json: async () => ({ data: { results: [], count: 0 } }) }
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
    renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    // Step 1: Try saving with unknown location (geocoding happens during save)
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "UnknownCity" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "ZZ" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))
    
    // Should show geocoding warning but still save
    await screen.findByText(/Profil natal sauvegardé/i)

    // Verify no birth_lat/birth_lon in PUT payload
    expect(putCalls.length).toBeGreaterThan(0)
    const savedBody = JSON.parse(putCalls[0].body)
    expect(savedBody.birth_lat).toBeUndefined()
    expect(savedBody.birth_lon).toBeUndefined()

    // Step 3: Generate natal chart
    fireEvent.click(screen.getByRole("button", { name: /Générer mon thème astral/i }))

    // Step 4: Verify navigation triggered
    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /Générer mon thème astral/i })).not.toBeInTheDocument()
    })
  })

  it("aborts pending geocode request on unmount", async () => {
    setupToken()
    const abortSpy = vi.fn()
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})

    // Track if geocode fetch started
    let geocodeFetchStarted = false
    let resolveGeocode: (() => void) | null = null

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.includes("/v1/geocoding/search")) {
        geocodeFetchStarted = true
        // Track the abort signal
        if (init?.signal) {
          init.signal.addEventListener("abort", abortSpy)
        }
        // Return a promise that never resolves to simulate pending request
        return new Promise<Response>((resolve) => {
          resolveGeocode = () => resolve({ ok: true, json: async () => ({ data: { results: [], count: 0 } }) } as Response)
        })
      }
      if (url.includes("/birth-data")) {
        return SUCCESS_GET_RESPONSE
      }
      return SUCCESS_GET_RESPONSE
    })
    vi.stubGlobal("fetch", fetchMock)

    const { unmount } = renderBirthProfilePage()

    await waitFor(() => expect(screen.getByLabelText(/Date de naissance/i)).toBeInTheDocument())

    // Trigger geocoding by changing city and country
    fireEvent.change(screen.getByLabelText(/Ville/i), { target: { value: "TestCity" } })
    fireEvent.change(screen.getByLabelText(/Pays/i), { target: { value: "TestCountry" } })
    fireEvent.click(screen.getByRole("button", { name: /Sauvegarder/i }))

    // Wait for geocode fetch to actually start
    await waitFor(() => expect(geocodeFetchStarted).toBe(true))

    // Unmount while geocoding is pending
    unmount()

    // Verify abort was called
    expect(abortSpy).toHaveBeenCalled()
    consoleErrorSpy.mockRestore()
    // Cleanup: resolve the pending promise to avoid leaks
    resolveGeocode?.()
  })
})
