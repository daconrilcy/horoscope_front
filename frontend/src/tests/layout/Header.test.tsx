import { describe, it, expect, vi, afterEach } from "vitest"
import { render, cleanup, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Header } from "../../components/layout/Header"

// Mock dependencies
vi.mock("../../utils/authToken", () => ({
  useAccessTokenSnapshot: () => "mock-token",
  clearAccessToken: vi.fn(),
}))

vi.mock("../../api/authMe", () => ({
  useAuthMe: () => ({
    data: { role: "user" },
  }),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe("Header", () => {
  describe("AC1: Masquage du header sur /dashboard mobile", () => {
    it("affiche le header sur d'autres routes (ex: /natal)", () => {
      render(
        <MemoryRouter initialEntries={["/natal"]}>
          <Header />
        </MemoryRouter>
      )
      const header = document.querySelector("header.app-header")
      expect(header).toBeInTheDocument()
      expect(header).not.toHaveClass("app-header--dashboard")
      expect(screen.getByText("Horoscope")).toBeInTheDocument()
    })

    it("ajoute la classe app-header--dashboard sur /dashboard", () => {
      render(
        <MemoryRouter initialEntries={["/dashboard"]}>
          <Header />
        </MemoryRouter>
      )
      const header = document.querySelector("header.app-header")
      expect(header).toHaveClass("app-header--dashboard")
      // Le titre "Horoscope" est caché via condition React sur /dashboard
      expect(screen.queryByText("Horoscope")).not.toBeInTheDocument()
    })

    it("ajoute la classe app-header--dashboard sur /dashboard/ (slash final)", () => {
      render(
        <MemoryRouter initialEntries={["/dashboard/"]}>
          <Header />
        </MemoryRouter>
      )
      const header = document.querySelector("header.app-header")
      expect(header).toHaveClass("app-header--dashboard")
    })

    it("ajoute la classe app-header--dashboard sur /dashboard// (multiples slashes)", () => {
      render(
        <MemoryRouter initialEntries={["/dashboard//"]}>
          <Header />
        </MemoryRouter>
      )
      const header = document.querySelector("header.app-header")
      expect(header).toHaveClass("app-header--dashboard")
    })

    it("n'ajoute pas la classe app-header--dashboard sur /", () => {
      render(
        <MemoryRouter initialEntries={["/"]}>
          <Header />
        </MemoryRouter>
      )
      const header = document.querySelector("header.app-header")
      expect(header).not.toHaveClass("app-header--dashboard")
    })

    it("affiche les actions utilisateur par défaut", () => {
      render(
        <MemoryRouter initialEntries={["/natal"]}>
          <Header />
        </MemoryRouter>
      )
      expect(screen.getByText("Se déconnecter")).toBeInTheDocument()
      expect(screen.getByText("Utilisateur")).toBeInTheDocument()
    })
  })
})
