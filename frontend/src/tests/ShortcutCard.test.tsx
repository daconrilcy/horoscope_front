import { describe, it, expect, vi, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import { MessageCircle, Layers } from "lucide-react"
import { ShortcutCard } from "../components/ShortcutCard"
import { ShortcutsSection } from "../components/ShortcutsSection"

afterEach(() => {
  cleanup()
})

// ─── ShortcutCard ────────────────────────────────────────────────────────────

describe("ShortcutCard", () => {
  describe("AC3 & AC4: Rendu titre + sous-titre", () => {
    it("affiche le titre", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
    })

    it("affiche le sous-titre", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      expect(screen.getByText("En ligne")).toBeInTheDocument()
    })

    it("le titre a la classe shortcut-card__title", () => {
      render(
        <ShortcutCard
          title="Tirage du jour"
          subtitle="3 cartes"
          icon={Layers}
          badgeColor="var(--badge-tirage)"
        />
      )
      const title = document.querySelector(".shortcut-card__title")
      expect(title).toBeInTheDocument()
      expect(title?.textContent).toBe("Tirage du jour")
    })

    it("le sous-titre a la classe shortcut-card__subtitle", () => {
      render(
        <ShortcutCard
          title="Tirage du jour"
          subtitle="3 cartes"
          icon={Layers}
          badgeColor="var(--badge-tirage)"
        />
      )
      const subtitle = document.querySelector(".shortcut-card__subtitle")
      expect(subtitle).toBeInTheDocument()
      expect(subtitle?.textContent).toBe("3 cartes")
    })
  })

  describe("AC5: Glassmorphism - classes CSS", () => {
    it("le conteneur a la classe shortcut-card", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      const card = document.querySelector(".shortcut-card")
      expect(card).toBeInTheDocument()
    })

    it("le badge a la classe shortcut-card__badge", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      const badge = document.querySelector(".shortcut-card__badge")
      expect(badge).toBeInTheDocument()
    })

    it("le badge applique la couleur de fond via le prop badgeColor", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      const badge = document.querySelector(".shortcut-card__badge") as HTMLElement
      expect(badge?.style.background).toBe("var(--badge-chat)")
    })
  })

  describe("AC3: Icône dans le badge", () => {
    it("rend un SVG dans le badge", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      const badge = document.querySelector(".shortcut-card__badge")
      const svg = badge?.querySelector("svg")
      expect(svg).toBeInTheDocument()
    })
  })

  describe("AC6: Clic → callback appelé", () => {
    it("appelle onClick quand on clique sur la card", () => {
      const onClick = vi.fn()
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
          onClick={onClick}
        />
      )
      const card = document.querySelector(".shortcut-card") as HTMLElement
      fireEvent.click(card)
      expect(onClick).toHaveBeenCalledTimes(1)
    })

    it("ne lance pas d'erreur si onClick est absent", () => {
      render(
        <ShortcutCard
          title="Chat astrologue"
          subtitle="En ligne"
          icon={MessageCircle}
          badgeColor="var(--badge-chat)"
        />
      )
      const card = document.querySelector(".shortcut-card") as HTMLElement
      expect(() => fireEvent.click(card)).not.toThrow()
    })
  })
})

// ─── ShortcutsSection ────────────────────────────────────────────────────────

describe("ShortcutsSection", () => {
  describe("AC1: Titre de section rendu correctement", () => {
    it("affiche le titre 'Raccourcis'", () => {
      render(<ShortcutsSection />)
      expect(screen.getByText("Raccourcis")).toBeInTheDocument()
    })

    it("le titre a la classe shortcuts-section__title", () => {
      render(<ShortcutsSection />)
      const title = document.querySelector(".shortcuts-section__title")
      expect(title).toBeInTheDocument()
    })
  })

  describe("AC2: Grille 2 colonnes", () => {
    it("rend exactement 2 ShortcutCards", () => {
      render(<ShortcutsSection />)
      const cards = document.querySelectorAll(".shortcut-card")
      expect(cards).toHaveLength(2)
    })

    it("la grille a la classe shortcuts-grid", () => {
      render(<ShortcutsSection />)
      const grid = document.querySelector(".shortcuts-grid")
      expect(grid).toBeInTheDocument()
    })
  })

  describe("AC3 & AC4: Données statiques des cards", () => {
    it("la première card affiche 'Chat astrologue'", () => {
      render(<ShortcutsSection />)
      expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
    })

    it("la première card affiche 'En ligne'", () => {
      render(<ShortcutsSection />)
      expect(screen.getByText("En ligne")).toBeInTheDocument()
    })

    it("la deuxième card affiche 'Tirage du jour'", () => {
      render(<ShortcutsSection />)
      expect(screen.getByText("Tirage du jour")).toBeInTheDocument()
    })

    it("la deuxième card affiche '3 cartes'", () => {
      render(<ShortcutsSection />)
      expect(screen.getByText("3 cartes")).toBeInTheDocument()
    })
  })

  describe("AC6: Callbacks onChatClick / onTirageClick", () => {
    it("appelle onChatClick quand on clique sur la card Chat", () => {
      const onChatClick = vi.fn()
      render(<ShortcutsSection onChatClick={onChatClick} />)
      const cards = document.querySelectorAll(".shortcut-card")
      fireEvent.click(cards[0])
      expect(onChatClick).toHaveBeenCalledTimes(1)
    })

    it("appelle onTirageClick quand on clique sur la card Tirage", () => {
      const onTirageClick = vi.fn()
      render(<ShortcutsSection onTirageClick={onTirageClick} />)
      const cards = document.querySelectorAll(".shortcut-card")
      fireEvent.click(cards[1])
      expect(onTirageClick).toHaveBeenCalledTimes(1)
    })
  })
})
