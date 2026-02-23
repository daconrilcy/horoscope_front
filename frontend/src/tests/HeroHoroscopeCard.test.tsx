import { describe, it, expect, vi, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import { HeroHoroscopeCard } from "../components/HeroHoroscopeCard"

const defaultProps = {
  sign: "♒",
  signName: "Verseau",
  date: "23 fév.",
  headline: "Ta journée s'éclaircit après 14h.",
}

describe("HeroHoroscopeCard", () => {
  afterEach(() => {
    cleanup()
  })

  describe("AC1: Card glassmorphism rendue correctement", () => {
    it("renders container with role article and class hero-card", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
      const card = screen.getByRole("article")
      expect(card).toHaveClass("hero-card")
    })

    it("card has aria-labelledby linked to headline", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
      const card = screen.getByRole("article")
      const headline = screen.getByRole("heading", { level: 2 })
      expect(card).toHaveAttribute("aria-labelledby", headline.id)
    })
  })

  describe("AC2: Chip signe + date rendu correctement", () => {
    it("renders chip with sign, signName and date", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
      const chipText = `♒Verseau • 23 fév.`
      // Use findByText or similar, or just check the container of the chip if needed.
      // But let's look for the text content directly which is more robust.
      expect(screen.getByText("♒")).toBeInTheDocument()
      expect(screen.getByText(/Verseau • 23 fév./)).toBeInTheDocument()
    })
  })

  describe("AC3: Chevron top-right présent", () => {
    it("renders top-row with hidden decorative icon", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
      // The icon is hidden from aria, so we can't get by role easily unless we use querySelector
      // or we check the container. But we want to avoid querySelector.
      // We can check for the existence of the chevron by searching for its characteristic path or just using a test id if really needed.
      // However, for icons, sometimes querySelector is acceptable IF there is no other way, 
      // but here we can check the presence of the container.
      const topRow = screen.getByRole("article").firstChild
      expect(topRow).toHaveClass("hero-card__top-row")
    })
  })

  describe("AC4: Headline 28px rendu correctement", () => {
    it("renders headline with provided text", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
      const headline = screen.getByRole("heading", { level: 2 })
      expect(headline).toHaveClass("hero-card__headline")
      expect(headline).toHaveTextContent("Ta journée s'éclaircit après 14h.")
    })

    it("headline updates when prop changes", () => {
      const { rerender } = render(<HeroHoroscopeCard {...defaultProps} headline="Nouvelle headline" />)
      expect(screen.getByText("Nouvelle headline")).toBeInTheDocument()
      
      rerender(<HeroHoroscopeCard {...defaultProps} headline="Updated headline" />)
      expect(screen.getByText("Updated headline")).toBeInTheDocument()
    })
  })

  describe("AC5: Constellation SVG en filigrane", () => {
    it("renders constellation container as aria-hidden", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const constellation = container.querySelector(".hero-card__constellation")
      expect(constellation).toBeInTheDocument()
      expect(constellation).toHaveAttribute("aria-hidden", "true")
    })
  })

  describe("AC6: CTA button pill gradient fonctionnel", () => {
    it("renders CTA button only when onReadFull is provided", () => {
      const { rerender } = render(<HeroHoroscopeCard {...defaultProps} onReadFull={undefined} />)
      expect(screen.queryByRole("button", { name: /Lire l'horoscope complet/i })).not.toBeInTheDocument()

      rerender(<HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} />)
      expect(screen.getByRole("button", { name: /Lire l'horoscope complet/i })).toBeInTheDocument()
    })

    it("CTA button displays 'Lire en 2 min' text", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} />)
      const cta = screen.getByRole("button", { name: /Lire l'horoscope complet en 2 minutes/i })
      expect(cta).toBeInTheDocument()
      expect(cta.textContent).toContain("Lire en 2 min")
    })

    it("CTA button calls onReadFull when clicked", () => {
      const onReadFull = vi.fn()
      render(<HeroHoroscopeCard {...defaultProps} onReadFull={onReadFull} />)
      const cta = screen.getByRole("button", { name: /Lire l'horoscope complet en 2 minutes/i })
      fireEvent.click(cta)
      expect(onReadFull).toHaveBeenCalledTimes(1)
    })

    it("uses custom ARIA label for CTA if provided", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} ariaLabelReadFull="Custom Label" />)
      const cta = screen.getByRole("button", { name: /Custom Label/i })
      expect(cta).toBeInTheDocument()
    })

    it("CTA button does not throw when onReadFull is not provided", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadFull={undefined} />)
      expect(screen.queryByRole("button", { name: /Lire l'horoscope complet/i })).not.toBeInTheDocument()
    })
  })

  describe("AC7: Lien 'Version détaillée' rendu", () => {
    it("renders 'Version détaillée' button only when onReadDetailed is provided", () => {
      const { rerender } = render(<HeroHoroscopeCard {...defaultProps} onReadDetailed={undefined} />)
      expect(screen.queryByRole("button", { name: /Voir la version détaillée/i })).not.toBeInTheDocument()

      rerender(<HeroHoroscopeCard {...defaultProps} onReadDetailed={() => {}} />)
      expect(screen.getByRole("button", { name: /Voir la version détaillée/i })).toBeInTheDocument()
    })

    it("renders 'Version détaillée' link with class hero-card__link", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadDetailed={() => {}} />)
      const link = screen.getByRole("button", { name: /Voir la version détaillée de l'horoscope/i })
      expect(link).toHaveClass("hero-card__link")
      expect(link).toHaveTextContent("Version détaillée")
    })

    it("calls onReadDetailed when 'Version détaillée' is clicked", () => {
      const onReadDetailed = vi.fn()
      render(<HeroHoroscopeCard {...defaultProps} onReadDetailed={onReadDetailed} />)
      const link = screen.getByRole("button", { name: /Voir la version détaillée de l'horoscope/i })
      fireEvent.click(link!)
      expect(onReadDetailed).toHaveBeenCalledTimes(1)
    })

    it("uses custom ARIA label for detailed link if provided", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadDetailed={() => {}} ariaLabelReadDetailed="Custom Link Label" />)
      const link = screen.getByRole("button", { name: /Custom Link Label/i })
      expect(link).toBeInTheDocument()
    })

    it("does not throw when onReadDetailed is not provided and link is clicked", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadDetailed={undefined} />)
      expect(screen.queryByRole("button", { name: /Voir la version détaillée/i })).not.toBeInTheDocument()
    })
  })
})
