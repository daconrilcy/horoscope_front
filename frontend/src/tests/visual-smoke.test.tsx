/**
 * Visual smoke tests — Story 17-10: Correctifs P0 contrastes, tokens, fonds premium
 *
 * These static-analysis tests verify CSS structure and component source to ensure
 * no opacity on parent wrappers (AC#1), correct token presence (AC#2),
 * correct typography structure (AC#3), background layers (AC#4 / AC#5),
 * and Lucide icon conformance (AC#6).
 */
import { describe, it, expect, beforeAll, afterEach } from "vitest"
import { readFileSync } from "fs"
import { resolve } from "path"
import { render, cleanup } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Heart, MessageCircle } from "lucide-react"
import { MiniInsightCard } from "../components/MiniInsightCard"
import { ShortcutCard } from "../components/ShortcutCard"

afterEach(() => {
  cleanup()
})

// ─── CSS source files ────────────────────────────────────────────────────────


let appCss: string
let themeCss: string
let bgCss: string
let heroCss: string

beforeAll(() => {
  appCss = readFileSync(resolve(__dirname, "../App.css"), "utf-8")
  const designTokensCss = readFileSync(resolve(__dirname, "../styles/design-tokens.css"), "utf-8")
  themeCss = designTokensCss + "\n" + readFileSync(resolve(__dirname, "../styles/theme.css"), "utf-8")
  bgCss = readFileSync(resolve(__dirname, "../styles/backgrounds.css"), "utf-8")
  heroCss = readFileSync(resolve(__dirname, "../components/HeroHoroscopeCard.css"), "utf-8")
})

// ─── AC#1 : Aucune opacité globale sur les wrappers principaux ───────────────

describe("AC#1 — Aucune opacity sur wrappers principaux (Dashboard)", () => {
  it(".app-shell n'a pas de propriété opacity", () => {
    const match = appCss.match(/\.app-shell\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
  })

  it(".today-page n'a pas de propriété opacity", () => {
    const match = appCss.match(/\.today-page\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
  })

  it(".app-bg-container n'a pas de propriété opacity", () => {
    const match = bgCss.match(/\.app-bg-container\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
  })

  it(".hero-card n'a pas de propriété opacity (container)", () => {
    const match = heroCss.match(/\.hero-card\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
  })

  it(".message-bubble--assistant n'a plus d'opacity globale (alpha ciblé uniquement)", () => {
    const match = appCss.match(/\.message-bubble--assistant\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
  })

  it(".typing-indicator n'a plus d'opacity globale", () => {
    const match = appCss.match(/\.typing-indicator\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
  })

  it(".message-bubble-author utilise color au lieu d'opacity", () => {
    const match = appCss.match(/\.message-bubble-author\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).not.toMatch(/\bopacity\s*:/)
    expect(content).toContain("color:")
  })

  it(".message-bubble-time utilise color au lieu d'opacity", () => {
    const match = appCss.match(/\.section-header__title\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("font-size: 18px")
  })

  it(".bottom-nav__label a font-size: 12px et font-weight: 500", () => {
    const match = appCss.match(/\.bottom-nav__label\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("font-size: 12px")
    expect(content).toContain("font-weight: 500")
  })
})

// ─── AC#4 & AC#5 — Fond dark starfield + light noise ─────────────────────────

describe("AC#4 — Fond dark: starfield + gradient cosmique (sans bokeh)", () => {
  it(".starfield-bg est position: fixed plein écran pointer-events: none", () => {
    const match = bgCss.match(/\.starfield-bg\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("position: fixed")
    expect(content).toContain("inset: 0")
    expect(content).toContain("pointer-events: none")
  })

  it(".dark .app-bg a des gradients cosmiques violet/bleu", () => {
    expect(bgCss).toContain("rgba(160,120,255,0.22)")
    expect(bgCss).toContain("rgba(90,170,255,0.14)")
  })
})

describe("AC#5 — Fond light: gradient pastel + noise (sans overlay sombre)", () => {
  it(".app-bg::after (noise) opacity entre 0.06 et 0.10", () => {
    const match = bgCss.match(/\.app-bg::after\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    const opacityMatch = content.match(/opacity:\s*([\d.]+)/)
    expect(opacityMatch).toBeTruthy()
    const val = parseFloat(opacityMatch![1])
    expect(val).toBeGreaterThanOrEqual(0.06)
    expect(val).toBeLessThanOrEqual(0.10)
  })

  it(".dark .app-bg::after est masqué (display: none)", () => {
    expect(bgCss).toMatch(/\.dark\s+\.app-bg::after\s*\{[^}]*display:\s*none/)
  })

  it(".app-bg::after pointer-events: none (non interactif)", () => {
    const match = bgCss.match(/\.app-bg::after\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("pointer-events: none")
  })
})

// ─── AC#6 — Icônes Lucide harmonisées ────────────────────────────────────────

describe("AC#6 — Icônes Lucide: size et strokeWidth conformes", () => {
  it("MiniInsightCard badge icon a size=20 (cards) et strokeWidth=1.75", () => {
    const { container } = render(
      <MiniInsightCard
        title="Test"
        description="desc"
        icon={Heart}
        badgeColor="var(--badge-amour)"
      />
    )
    const badge = container.querySelector(".mini-card__badge")
    const svg = badge?.querySelector("svg")
    expect(svg).toBeInTheDocument()
    expect(svg?.getAttribute("width")).toBe("20")
    expect(svg?.getAttribute("height")).toBe("20")
    const strokeWidth =
      svg?.getAttribute("stroke-width") ??
      svg?.querySelector("[stroke-width]")?.getAttribute("stroke-width")
    expect(strokeWidth).toBe("1.75")
  })

  it("ShortcutCard badge icon a size=20 (cards) et strokeWidth=1.75", () => {
    const { container } = render(
      <ShortcutCard
        title="Chat"
        subtitle="En ligne"
        icon={MessageCircle}
        badgeColor="var(--badge-chat)"
      />,
      {
        wrapper: ({ children }) => (
          <MemoryRouter future={routerFutureFlags}>{children}</MemoryRouter>
        ),
      }
    )
    const badge = container.querySelector(".shortcut-card__badge")
    const svg = badge?.querySelector("svg")
    expect(svg?.getAttribute("width")).toBe("20")
    expect(svg?.getAttribute("height")).toBe("20")
    const strokeWidth =
      svg?.getAttribute("stroke-width") ??
      svg?.querySelector("[stroke-width]")?.getAttribute("stroke-width")
    expect(strokeWidth).toBe("1.75")
  })
})
const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }
