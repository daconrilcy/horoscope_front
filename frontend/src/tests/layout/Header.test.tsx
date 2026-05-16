import { describe, it, expect, vi, afterEach } from "vitest"
import { fireEvent, render, cleanup, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Header } from "../../layouts/components/Header"
import { SidebarProvider } from "../../state/SidebarContext"

const toggleThemeMock = vi.fn()
const updateSettingsMock = vi.fn()

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

vi.mock("../../api/languages", () => ({
  useLanguages: () => ({
    data: [
      { code: "fr", name: "french" },
      { code: "en", name: "english" },
      { code: "es", name: "spanish" },
    ],
  }),
}))

vi.mock("../../api/userSettings", () => ({
  useUserSettings: () => ({
    data: {
      astrologer_profile: "standard",
      default_astrologer_id: null,
      default_language_code: null,
      detected_locale: "fr-FR",
      detected_country_code: "FR",
      detected_timezone: "Europe/Paris",
    },
  }),
  useUpdateUserSettings: () => ({
    mutate: updateSettingsMock,
    isPending: false,
  }),
}))

vi.mock("../../state/ThemeProvider", () => ({
  useTheme: () => ({
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
    expect(screen.getByRole("button", { name: "Choisir la langue" })).toBeInTheDocument()
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

  it("ouvre le choix de langue et persiste la langue sélectionnée", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Choisir la langue" }))
    fireEvent.click(screen.getByRole("menuitemradio", { name: "English" }))

    expect(updateSettingsMock).toHaveBeenCalledWith(
      expect.objectContaining({ default_language_code: "en" }),
    )
  })
})
