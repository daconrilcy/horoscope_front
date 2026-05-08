import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

import { AdminSupportPage } from "../pages/admin/AdminSupportPage"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <AdminSupportPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe("AdminSupportPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("renders empty ticket and flagged-content states through API owners", async () => {
    setAccessToken("token")
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input)
        if (url.includes("flagged-content")) {
          return Response.json({ data: [] })
        }
        return Response.json({ data: [] })
      }),
    )

    renderPage()

    expect(screen.getByText("Chargement des tickets...")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText("Aucun ticket trouvé.")).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("button", { name: "Contenus Signalés" }))
    await waitFor(() => {
      expect(screen.getByText("Aucun contenu à modérer.")).toBeInTheDocument()
    })
  })
})
