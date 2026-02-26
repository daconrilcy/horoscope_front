import { describe, it, expect, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import { TodayHeader } from "../components/TodayHeader"
import { ThemeProvider } from "../state/ThemeProvider"

function renderWithTheme(ui: React.ReactElement) {
  return render(<ThemeProvider>{ui}</ThemeProvider>)
}

describe("TodayHeader", () => {
  afterEach(() => {
    cleanup()
    localStorage.clear()
    document.documentElement.classList.remove("dark")
  })

  describe("AC1: Toggle dark/light présent et accessible (AC-17-14)", () => {
    it("affiche exactement un bouton (le toggle dark/light)", () => {
      renderWithTheme(<TodayHeader />)
      expect(screen.queryAllByRole("button")).toHaveLength(1)
    })

    it("le bouton toggle a un aria-label accessible", () => {
      renderWithTheme(<TodayHeader />)
      const toggle = screen.getByRole("button")
      expect(toggle).toHaveAttribute("aria-label")
      const label = toggle.getAttribute("aria-label") ?? ""
      expect(label.length).toBeGreaterThan(0)
    })

    it("le bouton toggle a aria-pressed", () => {
      renderWithTheme(<TodayHeader />)
      const toggle = screen.getByRole("button")
      expect(toggle).toHaveAttribute("aria-pressed")
    })

    it("le bouton toggle a la classe today-header__toggle", () => {
      renderWithTheme(<TodayHeader />)
      const toggle = screen.getByRole("button")
      expect(toggle).toHaveClass("today-header__toggle")
    })

    it("appeler le toggle change le label aria (dark <-> light)", () => {
      renderWithTheme(<TodayHeader />)
      const toggle = screen.getByRole("button")
      const initialLabel = toggle.getAttribute("aria-label") ?? ""
      fireEvent.click(toggle)
      const newLabel = toggle.getAttribute("aria-label") ?? ""
      expect(newLabel).not.toBe(initialLabel)
    })

    it("le toggle persiste le thème dans localStorage", () => {
      renderWithTheme(<TodayHeader />)
      const toggle = screen.getByRole("button")
      fireEvent.click(toggle)
      expect(localStorage.getItem("theme")).toMatch(/light|dark/)
    })

    it("l'avatar est positionné top-right avec la classe today-header__avatar", () => {
      renderWithTheme(<TodayHeader />)
      const avatar = screen.getByRole("img")
      expect(avatar).toHaveClass("today-header__avatar")
    })
  })

  describe("AC1: Kicker rendu correctement", () => {
    it("renders kicker with text 'Aujourd'hui'", () => {
      renderWithTheme(<TodayHeader />)
      const kicker = screen.getByText("Aujourd'hui")
      expect(kicker).toBeInTheDocument()
    })

    it("renders kicker as a p element", () => {
      renderWithTheme(<TodayHeader />)
      const kicker = screen.getByText("Aujourd'hui")
      expect(kicker.tagName).toBe("P")
    })

    it("kicker has class today-header__kicker", () => {
      renderWithTheme(<TodayHeader />)
      const kicker = screen.getByText("Aujourd'hui")
      expect(kicker).toHaveClass("today-header__kicker")
    })
  })

  describe("AC1: H1 'Horoscope' rendu correctement", () => {
    it("renders H1 with text 'Horoscope'", () => {
      renderWithTheme(<TodayHeader />)
      const title = screen.getByRole("heading", { level: 1 })
      expect(title).toBeInTheDocument()
      expect(title.textContent).toBe("Horoscope")
    })

    it("H1 has class today-header__title", () => {
      renderWithTheme(<TodayHeader />)
      const title = screen.getByRole("heading", { level: 1 })
      expect(title).toHaveClass("today-header__title")
    })
  })

  describe("AC1: Structure sémantique et avatar (40×40 top-right)", () => {
    it("renders header element as container with content wrapper", () => {
      renderWithTheme(<TodayHeader />)
      const header = document.querySelector("header.today-header")
      const content = header?.querySelector(".today-header__content")
      expect(header).toBeInTheDocument()
      expect(content).toBeInTheDocument()
    })

    it("renders avatar div with class today-header__avatar and role img", () => {
      renderWithTheme(<TodayHeader />)
      const avatar = screen.getByRole("img", { name: /profil de/i })
      expect(avatar).toHaveClass("today-header__avatar")
    })

    it("shows img when avatarUrl is provided", () => {
      const { container } = renderWithTheme(<TodayHeader avatarUrl="https://example.com/avatar.png" userName="Alice" />)
      const img = container.querySelector("img")
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute("src", "https://example.com/avatar.png")
    })

    it("falls back to initials when image fails to load", () => {
      const { container } = renderWithTheme(<TodayHeader avatarUrl="https://example.com/invalid.png" userName="Alice" />)
      const img = container.querySelector("img")
      expect(img).toBeInTheDocument()

      // Simulate error
      if (img) fireEvent.error(img)

      expect(container.querySelector("img")).not.toBeInTheDocument()
      expect(screen.getByText("A")).toBeInTheDocument()
    })

    it("shows improved initials for multi-word names", () => {
      renderWithTheme(<TodayHeader userName="John Doe" />)
      expect(screen.getByText("JD")).toBeInTheDocument()
    })

    it("shows initials when avatarUrl is not provided", () => {
      renderWithTheme(<TodayHeader userName="Alice" />)
      const avatar = screen.getByRole("img", { name: /profil de alice/i })
      const span = avatar.querySelector("span")
      expect(span).toBeInTheDocument()
      expect(span?.textContent).toBe("A")
    })

    it("shows default initials 'U' when userName is not provided", () => {
      renderWithTheme(<TodayHeader />)
      const avatar = screen.getByRole("img", { name: /profil de u/i })
      const span = avatar.querySelector("span")
      expect(span).toBeInTheDocument()
      expect(span?.textContent).toBe("U")
    })

    it("shows loading state when userName is 'loading'", () => {
      renderWithTheme(<TodayHeader userName="loading" />)
      const avatar = screen.getByRole("img", { name: /chargement du profil/i })
      expect(avatar).toHaveClass("today-header__avatar--loading")
      expect(avatar.querySelector("span")).not.toBeInTheDocument()
    })

    it("avatar has aria-label with userName", () => {
      renderWithTheme(<TodayHeader userName="Alice" />)
      const avatar = screen.getByRole("img", { name: "Profil de Alice" })
      expect(avatar).toBeInTheDocument()
    })
  })
})
