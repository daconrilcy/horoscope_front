/**
 * Visual smoke tests — Story 17-10: Correctifs P0 contrastes, tokens, fonds premium
 *
 * These static-analysis tests verify CSS structure and component source to ensure
 * no opacity on parent wrappers (AC#1), correct token presence (AC#2),
 * correct typography structure (AC#3), background layers (AC#4 / AC#5),
 * and Lucide icon conformance (AC#6).
 */
import { describe, it, expect, beforeAll, afterEach, vi } from "vitest"
import { readFileSync } from "fs"
import { resolve } from "path"
import { render, cleanup, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Route, Routes } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MessageCircle } from "lucide-react"
import { ShortcutCard } from "../components/ShortcutCard"
import { SettingsLayout } from "../layouts/SettingsLayout"
import { readAppCssSurface } from "./design-system-policy"
import { AstrologersPage } from "../pages/AstrologersPage"
import { AstrologerProfilePage } from "../pages/AstrologerProfilePage"

const { mockUseAstrologers, mockUseUserSettings, mockUseAstrologer } = vi.hoisted(() => ({
  mockUseAstrologers: vi.fn(),
  mockUseUserSettings: vi.fn(),
  mockUseAstrologer: vi.fn(),
}))

vi.mock("@hooks/useAstrologers", () => ({
  useAstrologers: () => mockUseAstrologers(),
}))

vi.mock("@api/userSettings", () => ({
  useUserSettings: () => mockUseUserSettings(),
  useUpdateUserSettings: () => ({ mutate: vi.fn(), isPending: false }),
}))

vi.mock("../api/astrologers", async () => {
  const actual = await vi.importActual<typeof import("../api/astrologers")>("../api/astrologers")
  return {
    ...actual,
    useAstrologer: (id: string | undefined) => mockUseAstrologer(id),
    rateAstrologer: vi.fn(),
  }
})

afterEach(() => {
  cleanup()
  mockUseAstrologers.mockReset()
  mockUseUserSettings.mockReset()
  mockUseAstrologer.mockReset()
})

// ─── CSS source files ────────────────────────────────────────────────────────


let appCss: string
let designTokensCss: string
let themeCss: string
let bgCss: string
let premiumThemeCss: string
let settingsCss: string
let landingLayoutCss: string
let landingPageCss: string
let landingHeroSectionSource: string

beforeAll(() => {
  appCss = readAppCssSurface()
  designTokensCss = readFileSync(resolve(__dirname, "../styles/design-tokens.css"), "utf-8")
  premiumThemeCss = readFileSync(resolve(__dirname, "../styles/premium-theme.css"), "utf-8")
  themeCss = designTokensCss + "\n" + readFileSync(resolve(__dirname, "../styles/theme.css"), "utf-8") + "\n" + premiumThemeCss
  bgCss = readFileSync(resolve(__dirname, "../styles/backgrounds.css"), "utf-8")
  settingsCss = readFileSync(resolve(__dirname, "../pages/settings/Settings.css"), "utf-8")
  landingLayoutCss = readFileSync(resolve(__dirname, "../layouts/LandingLayout.css"), "utf-8")
  landingPageCss = readFileSync(resolve(__dirname, "../pages/landing/LandingPage.css"), "utf-8")
  landingHeroSectionSource = readFileSync(resolve(__dirname, "../pages/landing/sections/HeroSection.tsx"), "utf-8")
})

function expectDeclarationToUseDefinedToken(css: string, property: string, token: string) {
  expect(css).toContain(`${property}: var(${token})`)
  expect(designTokensCss).toMatch(new RegExp(`${token}:\\s*[^;]+;`))
}

function expectBlockToContain(css: string, selector: string, declarations: string[]) {
  const escapedSelector = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  const match = css.match(new RegExp(`${escapedSelector}\\s*\\{([^}]*)\\}`))
  expect(match).toBeTruthy()
  const block = match?.[1] ?? ""

  for (const declaration of declarations) {
    expect(block).toContain(declaration)
  }
}

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

  it(".section-header__title utilise le token typographique de titre compact", () => {
    const match = appCss.match(/\.section-header__title\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expectDeclarationToUseDefinedToken(content, "font-size", "--font-size-lg")
  })

  it(".bottom-nav__label utilise les tokens typographiques de navigation", () => {
    const match = appCss.match(/\.bottom-nav__label\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expectDeclarationToUseDefinedToken(content, "font-size", "--font-size-xs")
    expectDeclarationToUseDefinedToken(content, "font-weight", "--font-weight-medium")
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

  it(".dark .app-bg a des couches astrales avant l'aube", () => {
    expect(bgCss).toMatch(/\.dark\s+\.app-bg\s*\{[^}]*background:\s*var\(--premium-app-bg\)/)
    expect(premiumThemeCss).toMatch(/rgba\(255,\s*190,\s*82,\s*0\.52\)/)
    expect(premiumThemeCss).toMatch(/linear-gradient\(124deg/)
    expect(premiumThemeCss).toMatch(/linear-gradient\(180deg,\s*transparent 0%,\s*transparent 92%/)
    expect(premiumThemeCss).not.toMatch(/linear-gradient\(90deg,\s*transparent 0%,\s*rgba\(255,\s*158,\s*67/)
    expect(premiumThemeCss).toContain("--starfield-star-lavender")
    expect(premiumThemeCss).toContain("--starfield-milky-mid")
    expect(bgCss).toContain("starfield-bg__milky-way")
    expect(bgCss).toContain("starfield-bg__milky-way--smoke")
    expect(bgCss).toContain("starfield-bg__milky-way--veil")
    expect(bgCss).toContain("starfield-bg__milky-way--dust")
    expect(bgCss).toContain("starfield-bg__milky-way--core")
    expect(bgCss).toContain("astral-milky-breath")
    expect(bgCss).toContain("astral-star-twinkle")
    expect(bgCss).toContain("astral-dawn-breath")
    expect(bgCss).toContain("starfield-bg__shooting")
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
  it("ShortcutCard badge icon a size=20 (cards) et strokeWidth=1.75", () => {
    const { container } = render(
      <ShortcutCard
        title="Chat"
        subtitle="En ligne"
        icon={MessageCircle}
        badgeColor="var(--color-badge-chat)"
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

function renderAstrologersPageSmoke() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/astrologers"]} future={routerFutureFlags}>
        <AstrologersPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

function renderAstrologerProfileSmoke() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/astrologers/luna"]} future={routerFutureFlags}>
        <Routes>
          <Route path="/astrologers/:id" element={<AstrologerProfilePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe("CS-084 — rendu smoke Settings", () => {
  it("rend le layout Settings avec le halo heritant du proprietaire semantique", () => {
    const { container } = render(
      <SettingsLayout title="Parametres">
        <section aria-label="Surface Settings">Contenu Settings</section>
      </SettingsLayout>,
      {
        wrapper: ({ children }) => (
          <MemoryRouter initialEntries={["/settings"]} future={routerFutureFlags}>
            {children}
          </MemoryRouter>
        ),
      },
    )

    const page = container.querySelector(".is-settings-page")
    const halo = container.querySelector(".settings-bg-halo")

    expect(page).toBeInTheDocument()
    expect(halo).toBeInTheDocument()
    expect(page).toContainElement(halo)
    expect(container.querySelector(".settings-container")).toHaveTextContent("Contenu Settings")
    expect(settingsCss).toContain("--settings-page-bg: var(--premium-app-bg)")
    expect(settingsCss).toMatch(/\.settings-bg-halo\s*\{[^}]*background:\s*none/)
  })
})

describe("CS-085 — rendu smoke Landing", () => {
  it("expose le scope owner landing et des styles representatifs token-backed", () => {
    expect(landingLayoutCss).toMatch(/\.landing-layout\s*\{[^}]*--landing-page-atmosphere:\s*var\(--premium-app-bg\)/)
    expect(landingLayoutCss).toMatch(/\.landing-layout\s*\{[^}]*background:\s*transparent/)
    expect(landingPageCss).toMatch(/\.hero-content h1\s*\{[^}]*font-size:\s*var\(--landing-type-hero-title-size\)/)
    expect(landingPageCss).toMatch(/\.hero-device\s*\{[^}]*box-shadow:\s*var\(--landing-hero-device-shadow\)/)
    expect(landingPageCss).not.toMatch(/\.hero-device\s*\{[^}]*animation:\s*hero-device-breathe/)
  })

  it("garde le hero landing sans timer JS tout en conservant les CTA analytics", () => {
    expect(landingHeroSectionSource).not.toMatch(/window\.setInterval|setInterval\(|setTimeout\(|requestAnimationFrame/)
    expect(landingHeroSectionSource).toContain('track("hero_cta_click"')
    expect(landingHeroSectionSource).toContain('track("secondary_cta_click"')
    expect(landingPageCss).toContain("@media (prefers-reduced-motion: no-preference)")
    expect(landingPageCss).toContain("hero-tool-cycle")
  })
})

describe("CS-128 — rendu smoke Astrologers compact", () => {
  it("evite une deuxieme atmosphere floutee sur le catalogue dark", () => {
    expectBlockToContain(appCss, ".dark #root", [
      "--app-astro-catalog-page-bg: transparent",
      "--app-astro-catalog-atmosphere: transparent",
    ])
    expectBlockToContain(appCss, ".dark .people-page", [
      "backdrop-filter: blur(18px)",
      "-webkit-backdrop-filter: blur(18px)",
    ])
    expectBlockToContain(appCss, ".dark .people-page::before", [
      "filter: none",
      "opacity: 0",
    ])
    expectBlockToContain(appCss, ".dark .people-page::after", [
      "display: none",
      "opacity: 0",
      "background-image: none",
    ])
    expectBlockToContain(appCss, ".dark .people-page .person-card", [
      "backdrop-filter: none",
      "-webkit-backdrop-filter: none",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-tag", [
      "backdrop-filter: none",
      "-webkit-backdrop-filter: none",
    ])
  })

  it("conserve la matiere token-backed des cartes compactes", () => {
    expectBlockToContain(appCss, ".people-page .person-card", [
      "background: var(--app-person-card-compact-background)",
      "border: var(--app-person-card-compact-border)",
      "box-shadow: var(--app-person-card-compact-box-shadow)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card--featured", [
      "grid-column: span 2",
      "background: var(--app-person-card-compact-featured-background)",
      "border-color: var(--app-person-card-compact-featured-border-color)",
      "box-shadow: var(--app-person-card-compact-featured-box-shadow)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-icon", [
      "position: absolute",
      "z-index: 5",
      "background: var(--app-person-card-compact-icon-background)",
      "border: var(--app-person-card-compact-icon-border)",
      "box-shadow: var(--app-person-card-compact-icon-box-shadow)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-icon::before", [
      "background: var(--app-person-card-compact-icon-ring-background)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-style,\n.people-page .person-card--featured .person-card-style", [
      "color: var(--app-person-card-compact-style-color)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-avatar,\n.people-page .person-card--featured .person-card-avatar", [
      "background: var(--app-person-card-compact-avatar-background)",
      "border: var(--app-person-card-compact-avatar-border)",
      "box-shadow: var(--app-person-card-compact-avatar-box-shadow)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-tag", [
      "background: var(--app-person-card-compact-tag-background)",
      "border: var(--app-person-card-compact-tag-border)",
      "box-shadow: var(--app-person-card-compact-tag-box-shadow)",
    ])
    expectBlockToContain(appCss, ".people-page .person-card-provider-badge,\n.people-page .person-card-featured-badge,\n.people-page .person-default-badge", [
      "display: none",
    ])
  })

  it("rend le DOM /astrologers avec icone, avatar, chips et badges compacts", () => {
    mockUseAstrologers.mockReturnValue({
      astrologers: [
        {
          id: "luna",
          name: "Luna Celeste",
          first_name: "Luna",
          last_name: "Caron",
          avatar_url: "/avatars/luna.jpg",
          provider_type: "ia",
          specialties: ["Theme natal", "Transits", "Relations"],
          style: "Bienveillant et direct",
          bio_short: "Lecture relationnelle.",
        },
        {
          id: "orion",
          name: "Orion Mystique",
          first_name: "Orion",
          last_name: "Vasseur",
          avatar_url: "/avatars/orion.jpg",
          provider_type: "real",
          specialties: ["Carriere", "Evenements"],
          style: "Analytique et precis",
          bio_short: "Astrologie previsionnelle.",
        },
      ],
      isLoading: false,
      error: null,
    })
    mockUseUserSettings.mockReturnValue({
      data: { default_astrologer_id: "luna" },
      isLoading: false,
    })

    const { container } = renderAstrologersPageSmoke()
    const peoplePage = container.querySelector(".people-page")
    const cards = container.querySelectorAll(".person-card")
    const firstCard = cards[0]

    expect(peoplePage).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Nos Astrologues" })).toBeInTheDocument()
    expect(cards).toHaveLength(2)
    expect(firstCard).toHaveClass("person-card--featured")
    expect(firstCard.querySelector(".person-card-icon")).toBeInTheDocument()
    expect(firstCard.querySelector(".person-card-avatar")).toBeInTheDocument()
    expect(firstCard.querySelectorAll(".person-card-tag")).toHaveLength(3)
    expect(firstCard.querySelector(".person-card-provider-badge")).toBeInTheDocument()
    expect(firstCard.querySelector(".person-card-featured-badge")).toBeInTheDocument()
    expect(firstCard.querySelector(".person-default-badge")).toBeInTheDocument()
    expect(screen.getByAltText("Avatar de Luna Caron")).toBeInTheDocument()
  })
})

describe("CS-129 — rendu smoke Profil astrologue", () => {
  it("rend le hero CTA, la methode aidee et l'etat avis vide sans contradiction", () => {
    mockUseAstrologer.mockReturnValue({
      data: {
        id: "luna",
        name: "Luna Celeste",
        first_name: "Luna",
        last_name: "Caron",
        avatar_url: "/avatars/luna.jpg",
        provider_type: "ia",
        specialties: ["Theme natal", "Transits"],
        style: "Pedagogique",
        bio_short: "Astrologue generaliste.",
        bio_full: "Lecture claire et progressive du theme.",
        gender: "female",
        age: 36,
        location: "Paris",
        quote: "Je vous aide a relire votre theme avec douceur.",
        mission_statement: "Comprendre avant d'agir.",
        ideal_for: "Ideal pour debutants",
        metrics: {
          total_experience_years: 5,
          experience_years: 7,
          consultations_count: 2400,
          average_rating: 4.8,
        },
        specialties_details: [],
        professional_background: ["5 ans accompagnement", "7 ans astrologue"],
        key_skills: [],
        behavioral_style: [],
        reviews: [],
        review_summary: {
          average_rating: 4.8,
          review_count: 0,
        },
        action_state: {
          has_chat: false,
          has_natal_interpretation: false,
        },
      },
      isPending: false,
      error: null,
      refetch: vi.fn(),
    })
    mockUseUserSettings.mockReturnValue({
      data: { default_astrologer_id: null },
      isLoading: false,
    })

    const { container } = renderAstrologerProfileSmoke()

    expect(container.querySelector(".profile-hero-actions")).toBeInTheDocument()
    expect(container.querySelector(".profile-hero-cta")).toBeInTheDocument()
    expect(container.querySelector(".profile-metrics-bar")).toBeInTheDocument()
    expect(container.querySelector(".profile-reviews-summary--empty")).toBeInTheDocument()
    expect(screen.getByText("Votre carte sert de point d'ancrage.")).toBeInTheDocument()
    expect(screen.getByText("Nouvel astrologue")).toBeInTheDocument()
    expect(screen.queryByText("4.8/5")).not.toBeInTheDocument()
    expect(screen.queryByText("(0 avis)")).not.toBeInTheDocument()
  })
})
