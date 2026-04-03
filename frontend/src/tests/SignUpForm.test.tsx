import { afterEach, describe, expect, it, vi, beforeEach } from "vitest"
import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react"

import { SignUpForm } from "../components/SignUpForm"
import { renderWithRouter } from "./test-utils"

const ACCESS_TOKEN = "tok.eyJzdWIiOiI0MiIsInJvbGUiOiJ1c2VyIn0.sig"

const SUCCESS_RESPONSE = {
  ok: true,
  status: 200,
  json: async () => ({
    data: {
      tokens: { access_token: ACCESS_TOKEN },
      user: { id: 42, role: "user" },
    },
    meta: { request_id: "r1" },
  }),
}

const EMAIL_TAKEN_RESPONSE = {
  ok: false,
  status: 409,
  json: async () => ({
    error: { code: "email_already_registered", message: "Email already in use" },
  }),
}

const GENERIC_ERROR_RESPONSE = {
  ok: false,
  status: 500,
  json: async () => ({
    error: { code: "internal_error", message: "Internal error" },
  }),
}

const onSignInMock = vi.fn()

// Mock analytics
const trackMock = vi.fn()
vi.mock("../hooks/useAnalytics", () => ({
  useAnalytics: () => ({
    track: trackMock
  }),
  getUtmParams: () => ({ utm_source: 'test' })
}))

beforeEach(() => {
  trackMock.mockClear()
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
  sessionStorage.clear()
  onSignInMock.mockClear()
})

describe("SignUpForm", () => {
  it("renders inputs, submit button, and back-to-signin link", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    expect(screen.getByLabelText(/Adresse e-mail/i, { selector: 'input' })).toBeInTheDocument()
    expect(screen.getByLabelText(/Mot de passe/i, { selector: 'input' })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Créer mon compte/i })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Se connecter/i })).toBeInTheDocument()
  })

  it("stores intended plan in sessionStorage and displays badge", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />, { initialEntries: ["/register?plan=premium"] })

    await waitFor(() => {
      expect(sessionStorage.getItem("intended_plan")).toBe("premium")
      expect(screen.getByText(/Plan sélectionné : Premium/i)).toBeInTheDocument()
    })
  })

  it("tracks register_view on mount", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />, { initialEntries: ["/register?plan=basic"] })

    await waitFor(() => {
      expect(trackMock).toHaveBeenCalledWith('register_view', expect.objectContaining({ from_plan: 'basic' }))
    })
  })

  it("tracks register_success on successful submission", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />, { initialEntries: ["/register?plan=free"] })

    fireEvent.change(screen.getByLabelText(/Adresse e-mail/i, { selector: 'input' }), { target: { value: "new@example.com" } })
    fireEvent.change(screen.getByLabelText(/Mot de passe/i, { selector: 'input' }), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: /Créer mon compte/i }))

    await waitFor(() => {
      expect(trackMock).toHaveBeenCalledWith('register_success', { method: 'email', plan: 'free' })
    })
  })

  it("submit button has type=submit for Enter key activation", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    expect(screen.getByRole("button", { name: /Créer mon compte/i })).toHaveAttribute("type", "submit")
  })

  it("shows validation error when email is invalid", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "not-an-email" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(screen.getByText("Adresse e-mail invalide.")).toBeInTheDocument()
    })
  })

  it("shows validation error when password is too short (< 8 characters)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "short" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(screen.getByText("Le mot de passe doit contenir au moins 8 caractères.")).toBeInTheDocument()
    })
  })

  it("sets aria-invalid and aria-describedby on email field after validation error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    const emailInput = screen.getByLabelText("Adresse e-mail")
    expect(emailInput).not.toHaveAttribute("aria-invalid")

    fireEvent.change(emailInput, { target: { value: "bad" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(emailInput).toHaveAttribute("aria-invalid", "true")
      expect(emailInput).toHaveAttribute("aria-describedby", "signup-email-error")
    })
  })

  it("calls setAccessToken with access_token on successful registration", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "new@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(localStorage.getItem("access_token")).toBe(ACCESS_TOKEN)
    })
  })

  it("shows specific error message when email is already registered", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(EMAIL_TAKEN_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "taken@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(screen.getByText("Cette adresse e-mail est déjà utilisée.")).toBeInTheDocument()
    })
  })

  it("shows generic error message on other API errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(GENERIC_ERROR_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(screen.getByText("Inscription impossible. Veuillez réessayer.")).toBeInTheDocument()
    })
  })

  it("shows generic error message when network request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network error")))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "password123" } })
    fireEvent.click(screen.getByRole("button", { name: "Créer mon compte" }))

    await waitFor(() => {
      expect(screen.getByText("Une erreur est survenue. Veuillez réessayer.")).toBeInTheDocument()
    })
  })

  it("calls onSignIn callback when 'Se connecter' button is clicked", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignUpForm onSignIn={onSignInMock} />)

    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    expect(onSignInMock).toHaveBeenCalledOnce()
  })
})
