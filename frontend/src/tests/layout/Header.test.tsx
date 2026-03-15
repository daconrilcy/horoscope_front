import { describe, it, expect, vi, afterEach } from "vitest"
import { fireEvent, render, cleanup, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Header } from "../../components/layout/Header"
import { SidebarProvider } from "../../state/SidebarContext"

const toggleThemeMock = vi.fn()

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

// Mock dependencies
vi.mock("../../utils/authToken", () => ({
  useAccessTokenSnapshot: () => "mock-token",
}))

vi.mock("../../api/authMe", () => ({
  useAuthMe: () => ({
    data: { role: "user", email: "test@example.com" },
  }),
}))

vi.mock("../../state/ThemeProvider", () => ({
  useThemeSafe: () => ({
    theme: "light",
    toggleTheme: toggleThemeMock,
  }),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe("Header", () => {
  it("affiche le branding central avec logo et nom d'application", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/natal"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    expect(screen.getByAltText("Astrorizon")).toBeInTheDocument()
    expect(screen.getByText("Astrorizon")).toBeInTheDocument()
  })

  it("expose les boutons hamburger, thème et menu utilisateur avec leurs labels", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    expect(screen.getByRole("button", { name: "Ouvrir le menu" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Changer le thème" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Menu utilisateur" })).toBeInTheDocument()
  })

  it("bascule le thème via le bouton dédié", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/natal"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Changer le thème" }))
    expect(toggleThemeMock).toHaveBeenCalledOnce()
  })

  it("ouvre et ferme le menu utilisateur via l'avatar", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/natal"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    const avatarButton = screen.getByRole("button", { name: "Menu utilisateur" })
    fireEvent.click(avatarButton)

    expect(screen.getByRole("menu")).toBeInTheDocument()
    expect(screen.getByText("Modifier mon compte")).toBeInTheDocument()

    fireEvent.click(avatarButton)
    expect(screen.queryByRole("menu")).not.toBeInTheDocument()
  })

  it("bascule l'état du hamburger et met à jour son aria-label", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    const menuButton = screen.getByRole("button", { name: "Ouvrir le menu" })
    fireEvent.click(menuButton)
    expect(screen.getByRole("button", { name: "Fermer le menu" })).toBeInTheDocument()
  })
})
