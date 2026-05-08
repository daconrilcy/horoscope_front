import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { AdminEntitlementsPage } from "../pages/admin/AdminEntitlementsPage"
import { AdminPermissionsProvider } from "../state/AdminPermissionsContext"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminPermissionsProvider overrides={{ canEdit: () => true }}>
        <AdminEntitlementsPage />
      </AdminPermissionsProvider>
    </QueryClientProvider>,
  )
}

describe("AdminEntitlementsPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("renders an empty entitlement matrix from the API owner", async () => {
    setAccessToken("token")
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json({
          plans: [],
          features: [],
          cells: {},
        }),
      ),
    )

    renderPage()

    expect(screen.getByText("Chargement de la matrice des droits...")).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText("Matrice des Droits (Entitlements)")).toBeInTheDocument()
    })
  })

  it("renders the existing error state when the matrix request fails", async () => {
    setAccessToken("token")
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ error: "boom" }, { status: 500 })))

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Erreur lors de la récupération des données.")).toBeInTheDocument()
    })
  })
})
