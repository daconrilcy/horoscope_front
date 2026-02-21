import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen } from "@testing-library/react"

import App from "../App"
import { AppProviders } from "../state/providers"
import { setAccessToken } from "../utils/authToken"

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe("App", () => {
  it("reacts to access token changes in runtime", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.endsWith("/v1/auth/me")) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ data: { id: 42, role: "user" } }),
        }
      }
      return {
        ok: false,
        status: 404,
        json: async () => ({ error: { code: "natal_chart_not_found", message: "not found" } }),
      }
    })
    vi.stubGlobal(
      "fetch",
      fetchMock,
    )

    localStorage.removeItem("access_token")
    const { rerender } = render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    expect(screen.getByText("Aucun token detecte. Connectez-vous pour acceder aux fonctionnalités protegees.")).toBeInTheDocument()

    const payload = btoa(JSON.stringify({ sub: "42", role: "user" }))
    setAccessToken(`x.${payload}.y`)
    rerender(
      <AppProviders>
        <App />
      </AppProviders>,
    )
    expect(
      screen.queryByText("Aucun token detecte. Connectez-vous pour acceder aux fonctionnalités protegees."),
    ).not.toBeInTheDocument()
    expect(await screen.findByRole("button", { name: "Chat" })).toBeInTheDocument()
  })

  it("renders natal chart page shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ error: { code: "natal_chart_not_found", message: "not found" } }),
      }),
    )

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )

    expect(await screen.findByRole("heading", { name: "Theme natal" })).toBeInTheDocument()
  })
})
