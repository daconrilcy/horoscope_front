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
  const defaultProps = {
    title: "Chat astrologue",
    subtitle: "En ligne",
    icon: MessageCircle,
    badgeColor: "var(--badge-chat)",
  }

  describe("Rendu et Structure", () => {
    it("affiche le titre et le sous-titre", () => {
      render(<ShortcutCard {...defaultProps} />)
      expect(screen.getByText(defaultProps.title)).toBeInTheDocument()
      expect(screen.getByText(defaultProps.subtitle)).toBeInTheDocument()
    })

    it("est un bouton de type 'button'", () => {
      render(<ShortcutCard {...defaultProps} />)
      const button = screen.getByRole("button")
      expect(button).toHaveAttribute("type", "button")
      expect(button).toHaveClass("shortcut-card")
    })

    it("rend le badge avec la bonne couleur", () => {
      const { container } = render(<ShortcutCard {...defaultProps} />)
      const badge = container.querySelector(".shortcut-card__badge") as HTMLElement
      expect(badge).toHaveStyle({ background: defaultProps.badgeColor })
    })

    it("rend l'icône Lucide", () => {
      const { container } = render(<ShortcutCard {...defaultProps} />)
      const svg = container.querySelector("svg")
      expect(svg).toBeInTheDocument()
    })
  })

  describe("Interactions", () => {
    it("appelle onClick lors du clic", () => {
      const onClick = vi.fn()
      render(<ShortcutCard {...defaultProps} onClick={onClick} />)
      fireEvent.click(screen.getByRole("button"))
      expect(onClick).toHaveBeenCalledTimes(1)
    })

    it("ne plante pas sans onClick", () => {
      render(<ShortcutCard {...defaultProps} />)
      expect(() => fireEvent.click(screen.getByRole("button"))).not.toThrow()
    })
  })
})

// ─── ShortcutsSection ────────────────────────────────────────────────────────

describe("ShortcutsSection", () => {
  it("affiche le titre de section 'Raccourcis'", () => {
    render(<ShortcutsSection />)
    expect(screen.getByRole("heading", { name: /raccourcis/i })).toBeInTheDocument()
  })

  it("rend les deux raccourcis par défaut", () => {
    render(<ShortcutsSection />)
    expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
    expect(screen.getByText("Tirage du jour")).toBeInTheDocument()
    expect(screen.getAllByRole("button")).toHaveLength(2)
  })

  it("déclenche onChatClick lors du clic sur le chat", () => {
    const onChatClick = vi.fn()
    render(<ShortcutsSection onChatClick={onChatClick} />)
    fireEvent.click(screen.getByText("Chat astrologue").closest("button")!)
    expect(onChatClick).toHaveBeenCalledTimes(1)
  })

  it("déclenche onTirageClick lors du clic sur le tirage", () => {
    const onTirageClick = vi.fn()
    render(<ShortcutsSection onTirageClick={onTirageClick} />)
    fireEvent.click(screen.getByText("Tirage du jour").closest("button")!)
    expect(onTirageClick).toHaveBeenCalledTimes(1)
  })

  it("utilise une structure sémantique <section>", () => {
    const { container } = render(<ShortcutsSection />)
    expect(container.querySelector("section")).toHaveClass("shortcuts-section")
  })
})
