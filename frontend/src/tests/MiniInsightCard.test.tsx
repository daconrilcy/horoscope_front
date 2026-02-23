import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import { Heart, Briefcase, Zap } from "lucide-react"
import { afterEach } from "vitest"
import { MiniInsightCard } from "../components/MiniInsightCard"
import { DailyInsightsSection } from "../components/DailyInsightsSection"

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

afterEach(() => {
  localStorage.clear()
  cleanup()
})

// ─── MiniInsightCard ──────────────────────────────────────────────────────────

describe("MiniInsightCard", () => {
  describe("AC3 & AC4 & AC5: Rendu titre + description", () => {
    it("affiche le titre", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      expect(screen.getByText("Amour")).toBeInTheDocument()
    })

    it("affiche la description", () => {
      render(
        <MiniInsightCard
          title="Travail"
          description="Nouvelle opportunité à saisir"
          icon={Briefcase}
          badgeColor="var(--badge-travail)"
        />
      )
      expect(screen.getByText("Nouvelle opportunité à saisir")).toBeInTheDocument()
    })

    it("le titre est un h3 avec la classe mini-card__title", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      const title = document.querySelector("h3.mini-card__title")
      expect(title).toBeInTheDocument()
      expect(title?.textContent).toBe("Amour")
    })

    it("la description a la classe mini-card__desc", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      const desc = document.querySelector(".mini-card__desc")
      expect(desc).toBeInTheDocument()
      expect(desc?.textContent).toBe("Balance dans ta relation")
    })
  })

  describe("AC3: Badge rendu avec la couleur correcte", () => {
    it("le badge applique la couleur de fond via la prop badgeColor", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      const badge = document.querySelector(".mini-card__badge") as HTMLElement
      expect(badge?.style.background).toBe("var(--badge-amour)")
    })

    it("le badge est caché pour les lecteurs d'écran (aria-hidden)", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      const badge = document.querySelector(".mini-card__badge")
      expect(badge).toHaveAttribute("aria-hidden", "true")
    })

    it("le badge a la classe mini-card__badge", () => {
      render(
        <MiniInsightCard
          title="Travail"
          description="Nouvelle opportunité à saisir"
          icon={Briefcase}
          badgeColor="var(--badge-travail)"
        />
      )
      const badge = document.querySelector(".mini-card__badge")
      expect(badge).toBeInTheDocument()
    })

    it("rend un SVG dans le badge", () => {
      render(
        <MiniInsightCard
          title="Énergie"
          description="Énergie haute, humeur positive"
          icon={Zap}
          badgeColor="var(--badge-energie)"
        />
      )
      const badge = document.querySelector(".mini-card__badge")
      const svg = badge?.querySelector("svg")
      expect(svg).toBeInTheDocument()
    })
  })

  describe("AC6: Glassmorphism - classe CSS conteneur", () => {
    it("le conteneur a la classe mini-card", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      const card = document.querySelector(".mini-card")
      expect(card).toBeInTheDocument()
    })
  })
})

// ─── DailyInsightsSection ─────────────────────────────────────────────────────

describe("DailyInsightsSection", () => {
  describe("AC1: En-tête de section correct", () => {
    it("affiche le titre 'Insights du jour' dans un h2", () => {
      render(<DailyInsightsSection />)
      const header = document.querySelector("h2.section-header__title")
      expect(header).toBeInTheDocument()
      expect(header?.textContent).toBe("Insights du jour")
    })

    it("l'en-tête a la classe section-header", () => {
      render(<DailyInsightsSection />)
      const header = document.querySelector(".section-header")
      expect(header).toBeInTheDocument()
    })

    it("appelle onSectionClick quand on clique sur l'en-tête", () => {
      const handleClick = vi.fn()
      render(<DailyInsightsSection onSectionClick={handleClick} />)
      const header = document.querySelector(".section-header")
      if (header) fireEvent.click(header)
      expect(handleClick).toHaveBeenCalled()
    })

    it("l'en-tête est un bouton quand onSectionClick est présent", () => {
      const handleClick = vi.fn()
      render(<DailyInsightsSection onSectionClick={handleClick} />)
      const header = screen.getByRole("button", { name: /Voir tous les insights du jour/i })
      expect(header).toBeInTheDocument()
    })

    it("rend un SVG ChevronRight dans l'en-tête", () => {
      render(<DailyInsightsSection />)
      const header = document.querySelector(".section-header")
      const svg = header?.querySelector("svg")
      expect(svg).toBeInTheDocument()
    })
  })

  describe("AC2: Grille 3 colonnes avec 3 MiniInsightCards", () => {
    it("rend exactement 3 MiniInsightCards", () => {
      render(<DailyInsightsSection />)
      const cards = document.querySelectorAll(".mini-card")
      expect(cards).toHaveLength(3)
    })

    it("la grille a la classe mini-cards-grid", () => {
      render(<DailyInsightsSection />)
      const grid = document.querySelector(".mini-cards-grid")
      expect(grid).toBeInTheDocument()
    })
  })

  describe("AC3, AC4, AC5: Données statiques des 3 cards", () => {
    it("affiche le titre 'Amour' dans une card", () => {
      render(<DailyInsightsSection />)
      const amourTitle = screen.getByText("Amour")
      expect(amourTitle).toBeInTheDocument()
    })

    it("affiche la description 'Balance dans ta relation'", () => {
      render(<DailyInsightsSection />)
      expect(screen.getByText("Balance dans ta relation")).toBeInTheDocument()
    })

    it("affiche le titre 'Travail'", () => {
      render(<DailyInsightsSection />)
      expect(screen.getByText("Travail")).toBeInTheDocument()
    })

    it("affiche la description 'Nouvelle opportunité à saisir'", () => {
      render(<DailyInsightsSection />)
      expect(screen.getByText("Nouvelle opportunité à saisir")).toBeInTheDocument()
    })

    it("affiche le titre 'Énergie'", () => {
      render(<DailyInsightsSection />)
      expect(screen.getByText("Énergie")).toBeInTheDocument()
    })

    it("affiche la description 'Énergie haute, humeur positive'", () => {
      render(<DailyInsightsSection />)
      expect(screen.getByText("Énergie haute, humeur positive")).toBeInTheDocument()
    })
  })

  describe("AC3: Badges avec les bonnes couleurs", () => {
    it("la card Amour a le badge avec var(--badge-amour)", () => {
      render(<DailyInsightsSection />)
      const badges = document.querySelectorAll(".mini-card__badge") as NodeListOf<HTMLElement>
      expect(badges[0]?.style.background).toBe("var(--badge-amour)")
    })

    it("la card Travail a le badge avec var(--badge-travail)", () => {
      render(<DailyInsightsSection />)
      const badges = document.querySelectorAll(".mini-card__badge") as NodeListOf<HTMLElement>
      expect(badges[1]?.style.background).toBe("var(--badge-travail)")
    })

    it("la card Énergie a le badge avec var(--badge-energie)", () => {
      render(<DailyInsightsSection />)
      const badges = document.querySelectorAll(".mini-card__badge") as NodeListOf<HTMLElement>
      expect(badges[2]?.style.background).toBe("var(--badge-energie)")
    })
  })
})
