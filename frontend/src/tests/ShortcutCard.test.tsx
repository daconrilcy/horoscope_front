import { MemoryRouter } from "react-router-dom"
import { describe, it, expect, vi, afterEach } from "vitest"
import { render, cleanup, screen, fireEvent } from "@testing-library/react"
import { MessageCircle, Layers } from "lucide-react"
import fs from "fs"
import path from "path"
import { ShortcutCard } from "../components/ShortcutCard"
import { ShortcutsSection } from "../components/ShortcutsSection"

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

    it("applique la classe subtitle--online quand isOnline est true", () => {
      const { container } = render(<ShortcutCard {...defaultProps} isOnline={true} />, { wrapper: MemoryRouter })
      const subtitle = container.querySelector(".shortcut-card__subtitle")
      expect(subtitle).toHaveClass("shortcut-card__subtitle--online")
    })

    it("n'applique pas la classe subtitle--online quand isOnline est false ou absent", () => {
      const { container } = render(<ShortcutCard {...defaultProps} />, { wrapper: MemoryRouter })
      const subtitle = container.querySelector(".shortcut-card__subtitle")
      expect(subtitle).not.toHaveClass("shortcut-card__subtitle--online")
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
  it("affiche le titre de section 'Activités'", () => {
    render(<ShortcutsSection />, { wrapper: MemoryRouter })
    expect(screen.getByRole("heading", { name: /activit/i })).toBeInTheDocument()
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

// ─── AC-17-12 & AC-17-14 Correctifs CSS non-régression (static analysis) ────

describe("AC-17-12 & AC-17-14 Correctifs ShortcutCard — analyse CSS statique (ShortcutCard.css)", () => {
  const shortcutCssPath = path.resolve(__dirname, "../components/ShortcutCard.css")
  const shortcutCssContent = fs.readFileSync(shortcutCssPath, "utf-8")

  it("AC#1 — .shortcut-card a text-decoration: none (pas de soulignement sur lien)", () => {
    const ruleContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card")
    expect(ruleContent).toMatch(/text-decoration\s*:\s*none/)
  })

  it("AC-17-14 — .shortcut-card__badge est 44x44 (badges plus grands)", () => {
    const badgeContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card__badge")
    expect(badgeContent).toMatch(/width\s*:\s*44px/)
    expect(badgeContent).toMatch(/height\s*:\s*44px/)
  })

  it("AC-17-14 — .shortcut-card__badge a border-radius: 16px", () => {
    const badgeContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card__badge")
    expect(badgeContent).toMatch(/border-radius\s*:\s*16px/)
  })

  it("AC#2 — .shortcut-card utilise --glass-shortcut pour le fond", () => {
    const ruleContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card")
    expect(ruleContent).toMatch(/background\s*:\s*var\(--glass-shortcut\)/)
  })

  it("AC#2 — .shortcut-card utilise --glass-shortcut-border pour la bordure", () => {
    const ruleContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card")
    expect(ruleContent).toMatch(/border\s*:.*var\(--glass-shortcut-border\)/)
  })

  it("AC-17-14 — .shortcut-card__title a font-size: 15px et font-weight: 650", () => {
    const ruleContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card__title")
    expect(ruleContent).toMatch(/font-size\s*:\s*15px/)
    expect(ruleContent).toMatch(/font-weight\s*:\s*650/)
  })

  it("AC-17-15 — .shortcut-card a une box-shadow (profondeur, détache du fond)", () => {
    const ruleContent = getLastCssRuleContent(shortcutCssContent, ".shortcut-card")
    expect(ruleContent).toMatch(/box-shadow\s*:/)
  })
})
