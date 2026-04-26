import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminSettingsPage } from "../pages/admin/AdminSettingsPage"
import { AdminPermissionsProvider } from "../state/AdminPermissionsContext"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function renderPage(canExport = true) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <AdminPermissionsProvider overrides={{ canExport }}>
        <AdminSettingsPage />
      </AdminPermissionsProvider>
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

  it("hides export actions when canExport is false", () => {
    renderPage(false)

    expect(screen.queryByRole("button", { name: "Exporter (CSV)" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Exporter (CSV/JSON)" })).not.toBeInTheDocument()
    expect(screen.getAllByText("Export indisponible pour ce profil.")).toHaveLength(3)
  })

  it("does not show a deprecation notice after generations export success", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")
    const createObjectUrlMock = vi.fn(() => "blob:generations-export")
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
        return new Response('{"ok":true}', {
          status: 200,
          headers: {
            "Content-Type": "application/json",
          },
        })
      }),
    )

    renderPage()
    await userEvent.click(screen.getByRole("button", { name: "Exporter (CSV/JSON)" }))
    await waitFor(() => {
      expect(screen.getByText(/AVERTISSEMENT SÉCURITÉ/)).toBeInTheDocument()
    })

    await userEvent.click(screen.getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Confirmer l'export" }))

    await waitFor(() => {
      expect(createObjectUrlMock).toHaveBeenCalled()
    })
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
    expect(revokeObjectUrlMock).toHaveBeenCalledWith("blob:generations-export")
  })
})
