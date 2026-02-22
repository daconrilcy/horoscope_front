import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"

import App from "../App"
import { AppProviders } from "../state/providers"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

const AUTH_ME_SUCCESS = {
  ok: true,
  status: 200,
  json: async () => ({ data: { id: 42, role: "user" } }),
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  json: async () => ({ error: { code: "not_found", message: "not found" } }),
}

function makeFetchMock(withAuthMe = true) {
  return vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (withAuthMe && url.endsWith("/v1/auth/me")) return AUTH_ME_SUCCESS
    return NOT_FOUND
  })
}

describe("App", () => {
  it("reacts to access token changes in runtime", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    localStorage.removeItem("access_token")
    const { rerender } = render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    expect(screen.getByRole("button", { name: "Se connecter" })).toBeInTheDocument()

    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)
    rerender(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    expect(screen.queryByRole("button", { name: "Se connecter" })).not.toBeInTheDocument()
    expect(await screen.findByRole("button", { name: "Chat" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Mon profil natal" })).toBeInTheDocument()
  })

  it("renders birth profile page when Mon profil natal is clicked", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )

    const profileButton = await screen.findByRole("button", { name: "Mon profil natal" })
    fireEvent.click(profileButton)

    expect(await screen.findByRole("heading", { name: "Mon profil natal" })).toBeInTheDocument()
  })

  it("renders natal chart page shell", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeInTheDocument()
  })

  // H2 — Flux auth : nouveaux tests pour machine d'état home/signin/register
  it("shows HomePage with Se connecter and Créer un compte buttons when unauthenticated", () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    expect(screen.getByRole("heading", { name: "Bienvenue" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Se connecter" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Créer un compte" })).toBeInTheDocument()
  })

  it("navigates from HomePage to SignInForm when Se connecter is clicked", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))

    await waitFor(() => {
      expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
      expect(screen.getByLabelText("Mot de passe")).toBeInTheDocument()
    })
    expect(screen.queryByRole("heading", { name: "Bienvenue" })).not.toBeInTheDocument()
  })

  it("navigates from HomePage to SignUpForm when Créer un compte is clicked", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    fireEvent.click(screen.getByRole("button", { name: "Créer un compte" }))

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Créer un compte" })).toBeInTheDocument()
    })
    expect(screen.queryByRole("heading", { name: "Bienvenue" })).not.toBeInTheDocument()
  })

  it("returns to HomePage after signing out", async () => {
    vi.stubGlobal("fetch", makeFetchMock())
    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )

    expect(await screen.findByRole("button", { name: "Se déconnecter" })).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Se déconnecter" }))

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Bienvenue" })).toBeInTheDocument()
    })
    expect(screen.queryByRole("button", { name: "Se déconnecter" })).not.toBeInTheDocument()
  })

  it("clears authView back to home when token is removed externally", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(NOT_FOUND))
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    // Navigate to signin
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }))
    await waitFor(() => {
      expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
    })
    // Token cleared externally (simulates another tab logout)
    clearAccessToken()
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Bienvenue" })).toBeInTheDocument()
    })
  })
})
