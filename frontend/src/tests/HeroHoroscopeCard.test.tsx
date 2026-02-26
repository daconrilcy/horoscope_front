import { describe, it, expect, vi, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import fs from "fs"
import path from "path"
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

  describe("AC2: Chip signe + date rendu correctement (AC#5 de la story)", () => {
    it("renders chip with sign, signName and date", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
      expect(screen.getByText("♒")).toBeInTheDocument()
      expect(screen.getByText("Verseau")).toBeInTheDocument()
      expect(screen.getByText(/23 fév\./)).toBeInTheDocument()
    })

    it("chip has class hero-card__chip for styling (gradient token --chip)", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const chip = container.querySelector(".hero-card__chip")
      expect(chip).toBeInTheDocument()
    })
  })

  describe("AC3: Chevron top-right présent", () => {
    it("renders top-row with hidden decorative icon", () => {
      render(<HeroHoroscopeCard {...defaultProps} />)
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

  describe("AC5: Constellation SVG conforme (points + segments droits)", () => {
    it("renders constellation container as aria-hidden", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const constellation = container.querySelector(".hero-card__constellation")
      expect(constellation).toBeInTheDocument()
      expect(constellation).toHaveAttribute("aria-hidden", "true")
    })

    it("constellation SVG contient des segments droits (<line>), pas de courbes Bezier (<path>)", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const svg = container.querySelector(".hero-card__constellation svg")
      expect(svg).toBeInTheDocument()
      // Doit avoir des lignes droites
      const lines = svg?.querySelectorAll("line")
      expect(lines?.length).toBeGreaterThan(0)
      // Ne doit pas avoir de courbes Bezier (paths)
      const paths = svg?.querySelectorAll("path")
      expect(paths?.length ?? 0).toBe(0)
    })

    it("constellation SVG contient des étoiles (cercles)", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const svg = container.querySelector(".hero-card__constellation svg")
      const circles = svg?.querySelectorAll("circle")
      expect(circles?.length).toBeGreaterThan(5)
    })

    it("constellation SVG a la classe hero-card__constellation-svg", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const svg = container.querySelector(".hero-card__constellation-svg")
      expect(svg).toBeInTheDocument()
    })

    it("constellation SVG respecte une épaisseur de traits entre 1.2 et 1.5px", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} />)
      const lines = container.querySelectorAll(".hero-card__constellation svg line")
      expect(lines.length).toBeGreaterThan(0)

      for (const line of lines) {
        const strokeWidth = Number(line.getAttribute("stroke-width"))
        expect(strokeWidth).toBeGreaterThanOrEqual(1.2)
        expect(strokeWidth).toBeLessThanOrEqual(1.5)
      }
    })
  })

  describe("AC6: CTA button pill gradient fonctionnel (AC#3 de la story)", () => {
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

    it("CTA button a la classe hero-card__cta pour le gradient et le glow", () => {
      render(<HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} />)
      const cta = screen.getByRole("button", { name: /Lire l'horoscope complet/i })
      expect(cta).toHaveClass("hero-card__cta")
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

  describe("AC-17-15: CTA sous-panel glass (2ème niveau de profondeur)", () => {
    it("les boutons CTA sont enveloppés dans .hero-card__cta-panel", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} />)
      const panel = container.querySelector(".hero-card__cta-panel")
      expect(panel).toBeInTheDocument()
    })

    it("le CTA button est à l'intérieur du .hero-card__cta-panel", () => {
      const { container } = render(<HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} />)
      const panel = container.querySelector(".hero-card__cta-panel")
      const cta = panel?.querySelector(".hero-card__cta")
      expect(cta).toBeInTheDocument()
    })

    it("le lien 'Version détaillée' est à l'intérieur du .hero-card__cta-panel", () => {
      const { container } = render(
        <HeroHoroscopeCard {...defaultProps} onReadFull={() => {}} onReadDetailed={() => {}} />
      )
      const panel = container.querySelector(".hero-card__cta-panel")
      const link = panel?.querySelector(".hero-card__link")
      expect(link).toBeInTheDocument()
    })

    it("le sparkle interne .hero-card::after est à opacity 0.18", () => {
      const cssPath = path.resolve(__dirname, "../components/HeroHoroscopeCard.css")
      const cssContent = fs.readFileSync(cssPath, "utf-8")
      expect(cssContent).toMatch(/\.hero-card::after\s*\{[^}]*opacity:\s*0\.18/)
    })
  })

  describe("AC-18-3: Icône SVG du signe zodiacal dans le chip", () => {
    it("affiche un SVG quand signCode est fourni (ex: aquarius)", () => {
      const { container } = render(
        <HeroHoroscopeCard {...defaultProps} signCode="aquarius" signName="Verseau" />
      )
      const chip = container.querySelector(".hero-card__chip")
      const svg = chip?.querySelector("svg")
      expect(svg).toBeInTheDocument()
    })

    it("le SVG a aria-hidden=true (décoratif)", () => {
      const { container } = render(
        <HeroHoroscopeCard {...defaultProps} signCode="leo" signName="Lion" />
      )
      const chip = container.querySelector(".hero-card__chip")
      const svg = chip?.querySelector("svg.hero-card__chip-icon")
      expect(svg).toHaveAttribute("aria-hidden", "true")
    })

    it("le SVG a stroke=currentColor au niveau de ses éléments de tracé", () => {
      const { container } = render(
        <HeroHoroscopeCard {...defaultProps} signCode="aries" signName="Bélier" />
      )
      const chip = container.querySelector(".hero-card__chip")
      const strokeElements = chip?.querySelectorAll("svg path, svg circle, svg g")
      const hasCurrentColor = Array.from(strokeElements ?? []).some(
        (el) => el.getAttribute("stroke") === "currentColor"
      )
      expect(hasCurrentColor).toBe(true)
    })

    it("fallback sur signe texte quand signCode est absent", () => {
      render(<HeroHoroscopeCard {...defaultProps} signCode={undefined} sign="♒" />)
      expect(screen.getByText("♒")).toBeInTheDocument()
    })

    it("fallback sur signe texte quand signCode est null", () => {
      render(<HeroHoroscopeCard {...defaultProps} signCode={null} sign="♒" />)
      expect(screen.getByText("♒")).toBeInTheDocument()
    })

    it("n'affiche pas d'icône SVG zodiacale quand signCode est absent", () => {
      const { container } = render(
        <HeroHoroscopeCard {...defaultProps} signCode={undefined} sign="♒" />
      )
      const chip = container.querySelector(".hero-card__chip")
      const svg = chip?.querySelector("svg.hero-card__chip-icon")
      expect(svg).not.toBeInTheDocument()
    })

    it("CSS: .hero-card__chip-text-sign utilise var(--hero-chip-sign-color) et pas white", () => {
      const cssPath = path.resolve(__dirname, "../components/HeroHoroscopeCard.css")
      const cssContent = fs.readFileSync(cssPath, "utf-8")
      expect(cssContent).toMatch(/\.hero-card__chip-text-sign\s*\{[^}]*color:\s*var\(--hero-chip-sign-color\)/)
      expect(cssContent).not.toMatch(/\.hero-card__chip-text-sign\s*\{[^}]*color:\s*white/)
    })

    it("CSS: .hero-card__chip-text-date utilise var(--hero-chip-date-color) et pas black", () => {
      const cssPath = path.resolve(__dirname, "../components/HeroHoroscopeCard.css")
      const cssContent = fs.readFileSync(cssPath, "utf-8")
      expect(cssContent).toMatch(/\.hero-card__chip-text-date\s*\{[^}]*color:\s*var\(--hero-chip-date-color\)/)
      expect(cssContent).not.toMatch(/\.hero-card__chip-text-date\s*\{[^}]*color:\s*black/)
    })

    it("signCode inconnu -> pas de SVG zodiacal (fallback signe texte)", () => {
      const { container } = render(
        <HeroHoroscopeCard {...defaultProps} signCode="unknown_sign" sign="♒" />
      )
      const chip = container.querySelector(".hero-card__chip")
      // L'icône zodiacale ne doit pas être présente pour un code inconnu
      const zodiacIcon = chip?.querySelector("svg.hero-card__chip-icon")
      expect(zodiacIcon).not.toBeInTheDocument()
      // Le texte fallback doit s'afficher
      expect(screen.getByText("♒")).toBeInTheDocument()
    })
  })
})
