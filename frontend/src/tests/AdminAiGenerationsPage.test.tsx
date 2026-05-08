import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { AdminAiGenerationsPage } from "../pages/admin/AdminAiGenerationsPage"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminAiGenerationsPage />
    </QueryClientProvider>,
  )
}

describe("AdminAiGenerationsPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("renders loading and empty metrics through the admin API owner", async () => {
    setAccessToken("token")
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json({
          data: [],
        }),
      ),
    )

    renderPage()

    expect(screen.getByText("Chargement des métriques...")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByRole("table")).toBeInTheDocument()
    })
  })
})
