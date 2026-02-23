import { describe, it, expect, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import { TodayHeader } from "../components/TodayHeader"

describe("TodayHeader", () => {
  afterEach(() => {
    cleanup()
  })

  describe("AC1: Kicker rendu correctement", () => {
    it("renders kicker with text 'Aujourd'hui'", () => {
      render(<TodayHeader />)
      const kicker = screen.getByText("Aujourd'hui")
      expect(kicker).toBeInTheDocument()
    })

    it("renders kicker as a p element", () => {
      render(<TodayHeader />)
      const kicker = screen.getByText("Aujourd'hui")
      expect(kicker.tagName).toBe("P")
    })

    it("kicker has class today-header__kicker", () => {
      render(<TodayHeader />)
      const kicker = screen.getByText("Aujourd'hui")
      expect(kicker).toHaveClass("today-header__kicker")
    })
  })

  describe("AC2: H1 'Horoscope' rendu correctement", () => {
    it("renders H1 with text 'Horoscope'", () => {
      render(<TodayHeader />)
      const title = screen.getByRole("heading", { level: 1 })
      expect(title).toBeInTheDocument()
      expect(title.textContent).toBe("Horoscope")
    })

    it("H1 has class today-header__title", () => {
      render(<TodayHeader />)
      const title = screen.getByRole("heading", { level: 1 })
      expect(title).toHaveClass("today-header__title")
    })
  })

  describe("AC3 & AC4: Structure sémantique et avatar", () => {
    it("renders header element as container with content wrapper", () => {
      render(<TodayHeader />)
      const header = document.querySelector("header.today-header")
      const content = header?.querySelector(".today-header__content")
      expect(header).toBeInTheDocument()
      expect(content).toBeInTheDocument()
    })

    it("renders avatar div with class today-header__avatar and role img", () => {
      render(<TodayHeader />)
      const avatar = screen.getByRole("img", { name: /profil de/i })
      expect(avatar).toHaveClass("today-header__avatar")
    })

    it("shows img when avatarUrl is provided", () => {
      const { container } = render(<TodayHeader avatarUrl="https://example.com/avatar.png" userName="Alice" />)
      const img = container.querySelector("img")
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute("src", "https://example.com/avatar.png")
    })

    it("falls back to initials when image fails to load", () => {
      const { container } = render(<TodayHeader avatarUrl="https://example.com/invalid.png" userName="Alice" />)
      const img = container.querySelector("img")
      expect(img).toBeInTheDocument()
      
      // Simulate error
      if (img) fireEvent.error(img)
      
      expect(container.querySelector("img")).not.toBeInTheDocument()
      expect(screen.getByText("A")).toBeInTheDocument()
    })

    it("shows improved initials for multi-word names", () => {
      render(<TodayHeader userName="John Doe" />)
      expect(screen.getByText("JD")).toBeInTheDocument()
    })

    it("shows initials when avatarUrl is not provided", () => {
      render(<TodayHeader userName="Alice" />)
      const avatar = screen.getByRole("img", { name: /profil de alice/i })
      const span = avatar.querySelector("span")
      expect(span).toBeInTheDocument()
      expect(span?.textContent).toBe("A")
    })

    it("shows default initials 'U' when userName is not provided", () => {
      render(<TodayHeader />)
      const avatar = screen.getByRole("img", { name: /profil de u/i })
      const span = avatar.querySelector("span")
      expect(span).toBeInTheDocument()
      expect(span?.textContent).toBe("U")
    })

    it("avatar has aria-label with userName", () => {
      render(<TodayHeader userName="Alice" />)
      const avatar = screen.getByRole("img", { name: "Profil de Alice" })
      expect(avatar).toBeInTheDocument()
    })
  })
})
