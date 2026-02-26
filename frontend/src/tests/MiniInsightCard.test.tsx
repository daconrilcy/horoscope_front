import { describe, it, expect, beforeEach } from "vitest"
import { render, cleanup, screen } from "@testing-library/react"
import { Heart, Briefcase, Zap } from "lucide-react"
import { afterEach } from "vitest"
import fs from "fs"
import path from "path"
import { MiniInsightCard } from "../components/MiniInsightCard"
import { DailyInsightsSection } from "../components/DailyInsightsSection"

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function getLastCssRuleContent(cssContent: string, selector: string): string {
  const selectorPattern = new RegExp(`${escapeRegex(selector)}\\s*\\{([^}]*)\\}`, "g")
  let lastRule = ""
  let match: RegExpExecArray | null
  while ((match = selectorPattern.exec(cssContent)) !== null) {
    lastRule = match[1]
  }
  return lastRule
}

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
  describe("AC1: Section sans titre, mais accessible", () => {
    it("n'affiche pas de titre de section en h2", () => {
      render(<DailyInsightsSection />)
      const header = document.querySelector("h2.section-header__title")
      expect(header).not.toBeInTheDocument()
    })

    it("n'affiche pas d'en-tête section-header", () => {
      render(<DailyInsightsSection />)
      const header = document.querySelector(".section-header")
      expect(header).not.toBeInTheDocument()
    })

    it("expose un label de région pour l'accessibilité", () => {
      render(<DailyInsightsSection />)
      expect(screen.getByRole("region", { name: /Voir tous les insights amour/i })).toBeInTheDocument()
    })

    it("n'affiche pas de bouton de header même si onSectionClick est présent", () => {
      render(<DailyInsightsSection onSectionClick={() => {}} />)
      const button = screen.queryByRole("button", { name: /Voir tous les insights amour/i })
      expect(button).not.toBeInTheDocument()
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
      expect(screen.getByText("Amour")).toBeInTheDocument()
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

// ─── AC-17-12 & AC-17-14 Correctifs CSS non-régression (static analysis) ─────

describe("AC-17-12 Correctifs MiniInsightCard — analyse CSS statique (MiniInsightCard.css)", () => {
  const miniCssPath = path.resolve(__dirname, "../components/MiniInsightCard.css")
  const miniCssContent = fs.readFileSync(miniCssPath, "utf-8")

  it("AC#5 — .mini-card__title est 15px semibold", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card__title")
    expect(ruleContent).toMatch(/font-size\s*:\s*15px/)
  })

  it("AC#5 — .mini-card utilise --glass-mini pour le fond", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card")
    expect(ruleContent).toMatch(/background\s*:\s*var\(--glass-mini\)/)
  })

  it("AC#5 — .mini-card utilise --glass-mini-border pour la bordure", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card")
    expect(ruleContent).toMatch(/border\s*:.*var\(--glass-mini-border\)/)
  })

  it("AC#3 — .mini-card__badge est 36x36 radius 14", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card__badge")
    expect(ruleContent).toMatch(/width\s*:\s*36px/)
    expect(ruleContent).toMatch(/height\s*:\s*36px/)
    expect(ruleContent).toMatch(/border-radius\s*:\s*14px/)
  })

  it("AC-17-14 — .mini-card--love::before utilise linear-gradient avec --love-g1/g2", () => {
    expect(miniCssContent).toMatch(/\.mini-card--love::before/)
    expect(miniCssContent).toMatch(/var\(--love-g1\)/)
    expect(miniCssContent).toMatch(/var\(--love-g2\)/)
  })

  it("AC-17-14 — .mini-card--work::before utilise linear-gradient avec --work-g1/g2", () => {
    expect(miniCssContent).toMatch(/\.mini-card--work::before/)
    expect(miniCssContent).toMatch(/var\(--work-g1\)/)
    expect(miniCssContent).toMatch(/var\(--work-g2\)/)
  })

  it("AC-17-14 — .mini-card--energy::before utilise linear-gradient avec --energy-g1/g2", () => {
    expect(miniCssContent).toMatch(/\.mini-card--energy::before/)
    expect(miniCssContent).toMatch(/var\(--energy-g1\)/)
    expect(miniCssContent).toMatch(/var\(--energy-g2\)/)
  })

  it("AC-17-14 — .mini-card__content a z-index 2", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card__content")
    expect(ruleContent).toMatch(/z-index\s*:\s*2/)
  })

  it("AC-17-15 — .mini-card::before opacity est <= 0.2 (wash subtil, pas de color block)", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card::before")
    const opacityMatch = ruleContent.match(/opacity\s*:\s*([\d.]+)/)
    expect(opacityMatch).toBeTruthy()
    const opacityVal = parseFloat(opacityMatch![1])
    expect(opacityVal).toBeLessThanOrEqual(0.2)
  })

  it("AC-17-15 — .mini-card a une box-shadow (profondeur, détache du fond)", () => {
    const ruleContent = getLastCssRuleContent(miniCssContent, ".mini-card")
    expect(ruleContent).toMatch(/box-shadow\s*:/)
  })
})

describe("AC-17-14 MiniInsightCard — data-type attribute", () => {
  it("la card Amour a data-type='love'", () => {
    render(
      <MiniInsightCard
        title="Amour"
        description="Balance dans ta relation"
        icon={Heart}
        badgeColor="var(--badge-amour)"
        type="love"
      />
    )
    const card = document.querySelector(".mini-card")
    expect(card).toHaveAttribute("data-type", "love")
    expect(card).toHaveClass("mini-card--love")
  })

  it("la card Travail a data-type='work'", () => {
    render(
      <MiniInsightCard
        title="Travail"
        description="Nouvelle opportunité"
        icon={Briefcase}
        badgeColor="var(--badge-travail)"
        type="work"
      />
    )
    const card = document.querySelector(".mini-card")
    expect(card).toHaveAttribute("data-type", "work")
    expect(card).toHaveClass("mini-card--work")
  })

  it("la card Énergie a data-type='energy'", () => {
    render(
      <MiniInsightCard
        title="Énergie"
        description="Énergie haute"
        icon={Zap}
        badgeColor="var(--badge-energie)"
        type="energy"
      />
    )
    const card = document.querySelector(".mini-card")
    expect(card).toHaveAttribute("data-type", "energy")
    expect(card).toHaveClass("mini-card--energy")
  })

  it("le contenu est dans mini-card__content (z-index 2)", () => {
    render(
      <MiniInsightCard
        title="Amour"
        description="Balance"
        icon={Heart}
        badgeColor="var(--badge-amour)"
        type="love"
      />
    )
    const content = document.querySelector(".mini-card__content")
    expect(content).toBeInTheDocument()
    const badge = content?.querySelector(".mini-card__badge")
    expect(badge).toBeInTheDocument()
  })
})
