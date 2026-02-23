import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, screen, waitFor } from "@testing-library/react"

import { SignInForm } from "../components/SignInForm"
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

const ERROR_RESPONSE = {
  ok: false,
  status: 401,
  json: async () => ({
    error: { code: "invalid_credentials", message: "Identifiants invalides" },
  }),
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe("SignInForm", () => {
  it("renders email input, password input, and submit button", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
    expect(screen.getByLabelText("Mot de passe")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Se connecter" })).toBeInTheDocument()
  })

  it("shows validation error when email is invalid", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "not-an-email" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByText("Adresse e-mail invalide.")).toBeInTheDocument()
    })
    expect(screen.queryByText("Le mot de passe est requis.")).not.toBeInTheDocument()
  })

  it("shows validation error when password is empty", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByText("Le mot de passe est requis.")).toBeInTheDocument()
    })
  })

  it("disables button and shows loading text during submission", async () => {
    let resolveLogin!: (v: typeof SUCCESS_RESPONSE) => void
    const loginPromise = new Promise<typeof SUCCESS_RESPONSE>((resolve) => {
      resolveLogin = resolve
    })
    vi.stubGlobal("fetch", vi.fn().mockReturnValue(loginPromise))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByText("Connexion en cours...")).toBeInTheDocument()
    })
    expect(screen.getByRole("button")).toBeDisabled()

    resolveLogin(SUCCESS_RESPONSE)
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Se connecter" })).not.toBeDisabled()
    })
  })

  it("calls setAccessToken with access_token on successful login", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(localStorage.getItem("access_token")).toBe(ACCESS_TOKEN)
    })
  })

  it("shows non-technical error message on API authentication failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ERROR_RESPONSE))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "wrongpassword" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByText("Identifiants incorrects. Veuillez réessayer.")).toBeInTheDocument()
    })
  })

  // M4 — Erreur réseau : fetch qui rejette
  it("shows generic error message when network request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network error")))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByText("Une erreur est survenue. Veuillez réessayer.")).toBeInTheDocument()
    })
  })

  // M1 — Réponse d'erreur non-JSON (502 gateway, etc.)
  it("shows generic error message when server returns non-JSON error response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => { throw new SyntaxError("Unexpected token < in JSON") },
    }))
    renderWithRouter(<SignInForm />)

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByText("Une erreur est survenue. Veuillez réessayer.")).toBeInTheDocument()
    })
  })

  // H1 — Navigation clavier : attributs WCAG (aria-invalid, aria-describedby, type=submit)
  it("submit button has type=submit for Enter key activation", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    expect(screen.getByRole("button", { name: "Se connecter" })).toHaveAttribute("type", "submit")
  })

  it("sets aria-invalid and aria-describedby on email field after validation error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    const emailInput = screen.getByLabelText("Adresse e-mail")
    expect(emailInput).toHaveAttribute("aria-invalid", "false")

    fireEvent.change(emailInput, { target: { value: "not-an-email" } })
    fireEvent.change(screen.getByLabelText("Mot de passe"), { target: { value: "secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(emailInput).toHaveAttribute("aria-invalid", "true")
      expect(emailInput).toHaveAttribute("aria-describedby", "signin-email-error")
    })
  })

  it("sets aria-invalid and aria-describedby on password field after validation error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    const passwordInput = screen.getByLabelText("Mot de passe")
    expect(passwordInput).toHaveAttribute("aria-invalid", "false")

    fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "test@example.com" } })
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(passwordInput).toHaveAttribute("aria-invalid", "true")
      expect(passwordInput).toHaveAttribute("aria-describedby", "signin-password-error")
    })
  })

  // M2 — prop onRegister : visibilité conditionnelle et invocation du callback
  it("shows 'Créer un compte' button when onRegister prop is provided", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    const onRegister = vi.fn()
    renderWithRouter(<SignInForm onRegister={onRegister} />)

    expect(screen.getByRole("button", { name: "Créer un compte" })).toBeInTheDocument()
  })

  it("does not show 'Créer un compte' button when onRegister prop is omitted", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    renderWithRouter(<SignInForm />)

    expect(screen.queryByRole("button", { name: "Créer un compte" })).not.toBeInTheDocument()
  })

  it("calls onRegister callback when 'Créer un compte' button is clicked", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(SUCCESS_RESPONSE))
    const onRegister = vi.fn()
    renderWithRouter(<SignInForm onRegister={onRegister} />)

    fireEvent.click(screen.getByRole("button", { name: "Créer un compte" }))

    expect(onRegister).toHaveBeenCalledOnce()
  })
})
