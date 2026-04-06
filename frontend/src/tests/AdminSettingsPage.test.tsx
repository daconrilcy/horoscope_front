import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminSettingsPage } from "../pages/admin/AdminSettingsPage"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <AdminSettingsPage />
    </QueryClientProvider>,
  )
}

describe("AdminSettingsPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("revokes blob urls after export download", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const createObjectUrlMock = vi.fn(() => "blob:users-export")
    const revokeObjectUrlMock = vi.fn()
    Object.defineProperty(window.URL, "createObjectURL", {
      value: createObjectUrlMock,
      configurable: true,
    })
    Object.defineProperty(window.URL, "revokeObjectURL", {
      value: revokeObjectUrlMock,
      configurable: true,
    })

    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        return new Response("id,email\n1,test@example.com\n", {
          status: 200,
          headers: {
            "Content-Type": "text/csv",
          },
        })
      }),
    )

    renderPage()

    await userEvent.click(screen.getAllByRole("button", { name: "Exporter (CSV)" })[0])
    await waitFor(() => {
      expect(screen.getByText(/AVERTISSEMENT SÉCURITÉ/)).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Confirmer l'export" }))

    await waitFor(() => {
      expect(createObjectUrlMock).toHaveBeenCalled()
    })

    expect(revokeObjectUrlMock).toHaveBeenCalledWith("blob:users-export")
  })
})
