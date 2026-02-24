import { describe, it, expect, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
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

  describe("AC2: H1 'Horoscope' rendu correctement", () => {
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

  describe("AC3 & AC4: Structure sémantique et avatar", () => {
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

  describe("AC6: Bouton toggle theme", () => {
    it("affiche le bouton toggle theme avec aria-label", () => {
      renderWithTheme(<TodayHeader />)
      const toggleBtn = screen.getByRole("button", { name: /passer en mode/i })
      expect(toggleBtn).toBeInTheDocument()
      expect(toggleBtn).toHaveClass("today-header__theme-toggle")
    })

    it("bascule le thème au clic", async () => {
      const user = userEvent.setup()
      renderWithTheme(<TodayHeader />)
      const toggleBtn = screen.getByRole("button", { name: /passer en mode/i })
      // Le label initial dépend du thème système, on vérifie juste que le clic change le label
      const initialLabel = toggleBtn.getAttribute("aria-label")
      await user.click(toggleBtn)
      const newLabel = screen.getByRole("button", { name: /passer en mode/i }).getAttribute("aria-label")
      expect(newLabel).not.toBe(initialLabel)
    })

    it("affiche l'icône Moon en mode light", () => {
      localStorage.setItem("theme", "light")
      renderWithTheme(<TodayHeader />)
      const toggleBtn = screen.getByRole("button", { name: "Passer en mode sombre" })
      expect(toggleBtn).toBeInTheDocument()
    })

    it("affiche l'icône Sun en mode dark", () => {
      localStorage.setItem("theme", "dark")
      renderWithTheme(<TodayHeader />)
      const toggleBtn = screen.getByRole("button", { name: "Passer en mode clair" })
      expect(toggleBtn).toBeInTheDocument()
    })
  })
})
