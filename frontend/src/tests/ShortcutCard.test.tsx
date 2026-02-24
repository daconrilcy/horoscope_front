import { MemoryRouter } from "react-router-dom"
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
      render(<ShortcutCard {...defaultProps} />, { wrapper: MemoryRouter })
      expect(screen.getByText(defaultProps.title)).toBeInTheDocument()
      expect(screen.getByText(defaultProps.subtitle)).toBeInTheDocument()
    })

    it("est un bouton par défaut si 'to' est absent", () => {
      render(<ShortcutCard {...defaultProps} />, { wrapper: MemoryRouter })
      const button = screen.getByRole("button")
      expect(button).toHaveAttribute("type", "button")
      expect(button).toHaveClass("shortcut-card")
    })

    it("est un lien si 'to' est présent", () => {
      render(<ShortcutCard {...defaultProps} to="/chat" />, { wrapper: MemoryRouter })
      const link = screen.getByRole("link")
      expect(link).toHaveAttribute("href", "/chat")
      expect(link).toHaveClass("shortcut-card")
    })

    it("rend le badge avec la bonne couleur", () => {
      const { container } = render(<ShortcutCard {...defaultProps} />, { wrapper: MemoryRouter })
      const badge = container.querySelector(".shortcut-card__badge") as HTMLElement
      expect(badge).toHaveStyle({ background: defaultProps.badgeColor })
    })
  })

  describe("Interactions", () => {
    it("appelle onClick lors du clic sur bouton", () => {
      const onClick = vi.fn()
      render(<ShortcutCard {...defaultProps} onClick={onClick} />, { wrapper: MemoryRouter })
      fireEvent.click(screen.getByRole("button"))
      expect(onClick).toHaveBeenCalledTimes(1)
    })

    it("appelle onClick lors du clic sur lien", () => {
      const onClick = vi.fn()
      render(<ShortcutCard {...defaultProps} to="/chat" onClick={onClick} />, { wrapper: MemoryRouter })
      fireEvent.click(screen.getByRole("link"))
      expect(onClick).toHaveBeenCalledTimes(1)
    })
  })
})

// ─── ShortcutsSection ────────────────────────────────────────────────────────

describe("ShortcutsSection", () => {
  it("affiche le titre de section 'Raccourcis'", () => {
    render(<ShortcutsSection />, { wrapper: MemoryRouter })
    expect(screen.getByRole("heading", { name: /raccourcis/i })).toBeInTheDocument()
  })

  it("rend les deux raccourcis par défaut sous forme de liens", () => {
    render(<ShortcutsSection />, { wrapper: MemoryRouter })
    expect(screen.getByText("Chat astrologue")).toBeInTheDocument()
    expect(screen.getByText("Tirage du jour")).toBeInTheDocument()
    expect(screen.getAllByRole("link")).toHaveLength(2)
  })

  it("déclenche onChatClick lors du clic sur le chat", () => {
    const onChatClick = vi.fn()
    render(<ShortcutsSection onChatClick={onChatClick} />, { wrapper: MemoryRouter })
    fireEvent.click(screen.getByRole("link", { name: /Chat astrologue/i }))
    expect(onChatClick).toHaveBeenCalledTimes(1)
  })

  it("déclenche onTirageClick lors du clic sur le tirage", () => {
    const onTirageClick = vi.fn()
    render(<ShortcutsSection onTirageClick={onTirageClick} />, { wrapper: MemoryRouter })
    fireEvent.click(screen.getByRole("link", { name: /Tirage du jour/i }))
    expect(onTirageClick).toHaveBeenCalledTimes(1)
  })

  it("utilise une structure sémantique <section>", () => {
    const { container } = render(<ShortcutsSection />, { wrapper: MemoryRouter })
    expect(container.querySelector("section")).toHaveClass("shortcuts-section")
  })
})
