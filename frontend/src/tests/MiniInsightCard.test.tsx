import { describe, it, expect } from "vitest"
import { render, cleanup, screen } from "@testing-library/react"
import { Heart, Briefcase, Zap } from "lucide-react"
import { afterEach } from "vitest"
import { MiniInsightCard } from "../components/MiniInsightCard"
import { AmourSection } from "../components/AmourSection"

afterEach(() => {
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

    it("le titre a la classe mini-card__title", () => {
      render(
        <MiniInsightCard
          title="Amour"
          description="Balance dans ta relation"
          icon={Heart}
          badgeColor="var(--badge-amour)"
        />
      )
      const title = document.querySelector(".mini-card__title")
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

// ─── AmourSection ─────────────────────────────────────────────────────────────

describe("AmourSection", () => {
  describe("AC1: En-tête de section correct", () => {
    it("affiche le titre 'Amour' dans l'en-tête", () => {
      render(<AmourSection />)
      const header = document.querySelector(".section-header__title")
      expect(header).toBeInTheDocument()
      expect(header?.textContent).toBe("Amour")
    })

    it("l'en-tête a la classe section-header", () => {
      render(<AmourSection />)
      const header = document.querySelector(".section-header")
      expect(header).toBeInTheDocument()
    })

    it("rend un SVG ChevronRight dans l'en-tête", () => {
      render(<AmourSection />)
      const header = document.querySelector(".section-header")
      const svg = header?.querySelector("svg")
      expect(svg).toBeInTheDocument()
    })
  })

  describe("AC2: Grille 3 colonnes avec 3 MiniInsightCards", () => {
    it("rend exactement 3 MiniInsightCards", () => {
      render(<AmourSection />)
      const cards = document.querySelectorAll(".mini-card")
      expect(cards).toHaveLength(3)
    })

    it("la grille a la classe mini-cards-grid", () => {
      render(<AmourSection />)
      const grid = document.querySelector(".mini-cards-grid")
      expect(grid).toBeInTheDocument()
    })
  })

  describe("AC3, AC4, AC5: Données statiques des 3 cards", () => {
    it("affiche le titre 'Amour' (card + en-tête)", () => {
      render(<AmourSection />)
      const amourElements = screen.getAllByText("Amour")
      expect(amourElements.length).toBeGreaterThanOrEqual(1)
    })

    it("affiche la description 'Balance dans ta relation'", () => {
      render(<AmourSection />)
      expect(screen.getByText("Balance dans ta relation")).toBeInTheDocument()
    })

    it("affiche le titre 'Travail'", () => {
      render(<AmourSection />)
      expect(screen.getByText("Travail")).toBeInTheDocument()
    })

    it("affiche la description 'Nouvelle opportunité à saisir'", () => {
      render(<AmourSection />)
      expect(screen.getByText("Nouvelle opportunité à saisir")).toBeInTheDocument()
    })

    it("affiche le titre 'Énergie'", () => {
      render(<AmourSection />)
      expect(screen.getByText("Énergie")).toBeInTheDocument()
    })

    it("affiche la description 'Énergie haute, humeur positive'", () => {
      render(<AmourSection />)
      expect(screen.getByText("Énergie haute, humeur positive")).toBeInTheDocument()
    })
  })

  describe("AC3: Badges avec les bonnes couleurs", () => {
    it("la card Amour a le badge avec var(--badge-amour)", () => {
      render(<AmourSection />)
      const badges = document.querySelectorAll(".mini-card__badge") as NodeListOf<HTMLElement>
      expect(badges[0]?.style.background).toBe("var(--badge-amour)")
    })

    it("la card Travail a le badge avec var(--badge-travail)", () => {
      render(<AmourSection />)
      const badges = document.querySelectorAll(".mini-card__badge") as NodeListOf<HTMLElement>
      expect(badges[1]?.style.background).toBe("var(--badge-travail)")
    })

    it("la card Énergie a le badge avec var(--badge-energie)", () => {
      render(<AmourSection />)
      const badges = document.querySelectorAll(".mini-card__badge") as NodeListOf<HTMLElement>
      expect(badges[2]?.style.background).toBe("var(--badge-energie)")
    })
  })
})
