import { describe, it, expect, vi, afterEach } from "vitest"
import { fireEvent, render, cleanup, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Header } from "../../layouts/components/Header"
import { SidebarProvider } from "../../state/SidebarContext"

const toggleThemeMock = vi.fn()
const updateSettingsMock = vi.fn()
let languagesMock = [
  { code: "fr", name: "Français API" },
  { code: "en", name: "English API" },
  { code: "es", name: "Español API" },
]
let defaultLanguageCodeMock: string | null = null

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
    data: languagesMock,
  }),
}))

vi.mock("../../api/userSettings", () => ({
  useUserSettings: () => ({
    data: {
      astrologer_profile: "standard",
      default_astrologer_id: null,
      default_language_code: defaultLanguageCodeMock,
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
  vi.unstubAllGlobals()
  localStorage.clear()
  languagesMock = [
    { code: "fr", name: "Français API" },
    { code: "en", name: "English API" },
    { code: "es", name: "Español API" },
  ]
  defaultLanguageCodeMock = null
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
    fireEvent.click(screen.getByRole("menuitemradio", { name: "English API" }))

    expect(updateSettingsMock).toHaveBeenCalledWith(
      expect.objectContaining({ default_language_code: "en" }),
      expect.objectContaining({
        onError: expect.any(Function),
        onSuccess: expect.any(Function),
      }),
    )
  })

  it("ne laisse pas une préférence compte stale annuler une sélection explicite", async () => {
    defaultLanguageCodeMock = "fr"

    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Choisir la langue" }))
    fireEvent.click(screen.getByRole("menuitemradio", { name: "English API" }))

    await waitFor(() => {
      expect(localStorage.getItem("lang")).toBe("en")
    })
  })

  it("affiche les libellés de langues fournis par l'API", () => {
    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Choisir la langue" }))

    expect(screen.getByRole("menuitemradio", { name: "Français API" })).toBeInTheDocument()
    expect(screen.getByRole("menuitemradio", { name: "English API" })).toBeInTheDocument()
  })

  it("applique la préférence compte quand la langue existe dans les options API", async () => {
    defaultLanguageCodeMock = "es"

    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    await waitFor(() => {
      expect(localStorage.getItem("lang")).toBe("es")
    })
  })

  it("ignore la préférence compte si la langue manque des options API", () => {
    defaultLanguageCodeMock = "en"
    languagesMock = [
      { code: "fr", name: "Français API" },
      { code: "es", name: "Español API" },
    ]

    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Choisir la langue" }))

    expect(screen.queryByRole("menuitemradio", { name: "English API" })).not.toBeInTheDocument()
    expect(localStorage.getItem("lang")).not.toBe("en")
  })

  it("persiste le pays detecte depuis une locale BCP47 avec script", async () => {
    vi.stubGlobal("navigator", { language: "zh-Hant-TW" })

    render(
      <SidebarProvider>
        <MemoryRouter initialEntries={["/dashboard"]} future={routerFutureFlags}>
          <Header />
        </MemoryRouter>
      </SidebarProvider>,
    )

    await waitFor(() => {
      expect(updateSettingsMock).toHaveBeenCalledWith(
        expect.objectContaining({
          detected_locale: "zh-Hant-TW",
          detected_country_code: "TW",
        }),
        expect.objectContaining({
          onError: expect.any(Function),
        }),
      )
    })
  })
})
