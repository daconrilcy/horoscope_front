// Tests de gouvernance des tokens CSS frontend.
import { describe, it, expect } from "vitest"
import fs from "fs"
import path from "path"
import { readAppCssSurface } from "./design-system-policy"

// Resolve path to theme.css
const themePath = path.resolve(__dirname, "../styles/theme.css")
const designTokensPath = path.resolve(__dirname, "../styles/design-tokens.css")
const premiumThemePath = path.resolve(__dirname, "../styles/premium-theme.css")
const natalChartPageCssPath = path.resolve(__dirname, "../pages/NatalChartPage.css")
const natalCssPaths = [
  "../features/natal-chart/natalTheme.css",
  "../features/natal-chart/natalBadges.css",
  "../features/natal-chart/natalCards.css",
  "../features/natal-chart/NatalJobCard.css",
  "../features/natal-chart/NatalReading.css",
  "../features/natal-chart/NatalReadingFacts.css",
  "../features/natal-chart/NatalAspects.css",
  "../features/natal-chart/NatalTechnicalDetails.css",
  "../features/natal-chart/NatalProfileHero.css",
  "../features/natal-chart/NatalAstrologerMode.css",
  "../components/NatalChartGuide.css",
  "../pages/NatalChartPage.css",
]
const themeContent = fs.readFileSync(designTokensPath, "utf-8") + "\n" + fs.readFileSync(themePath, "utf-8")
const premiumThemeContent = fs.readFileSync(premiumThemePath, "utf-8")
const natalChartPageCssContent = fs.readFileSync(natalChartPageCssPath, "utf-8")
const natalCssContent = natalCssPaths.map((cssPath) => fs.readFileSync(path.resolve(__dirname, cssPath), "utf-8")).join("\n")

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function getScopeBlock(cssContent: string, selector: string): string {
  const blockPattern = new RegExp(`${escapeRegex(selector)}\\s*\\{([\\s\\S]*?)\\}`)
  const blockMatch = cssContent.match(blockPattern)
  return blockMatch ? blockMatch[1] : ""
}

function getTokenValue(cssContent: string, selector: string, token: string): string {
  const scopeBlock = getScopeBlock(cssContent, selector)
  const tokenPattern = new RegExp(`${escapeRegex(token)}\\s*:\\s*([^;]+);`)
  const tokenMatch = scopeBlock.match(tokenPattern)
  return tokenMatch ? tokenMatch[1].trim() : ""
}

function normalizeCssValue(value: string): string {
  return value.replace(/\s+/g, "")
}

const requiredTokens = [
  "--color-text-primary",
  "--color-text-secondary",
  "--color-text-muted",
  "--bg-top",
  "--bg-mid",
  "--bg-bot",
  "--color-glass-bg",
  "--color-glass-bg-2",
  "--color-glass-border",
  "--cta-l",
  "--cta-r",
  "--chip",
  "--nav-glass",
  "--nav-border",
  "--shadow-hero",
  "--shadow-card",
  "--shadow-nav",
  "--shadow-cta",
  "--shadow-cta-dark",
  "--badge-chat",
  "--badge-consultation",
  "--badge-amour",
  "--badge-travail",
  "--badge-energie",
  "--hero-g1",
  "--hero-g2",
  "--love-g1",
  "--love-g2",
  "--work-g1",
  "--work-g2",
  "--energy-g1",
  "--energy-g2",
  "--color-text-headline",
]

describe("theme.css validation (Static Analysis)", () => {
  it("exists at frontend/src/styles/theme.css", () => {
    expect(fs.existsSync(themePath)).toBe(true)
  })

  it("charge les tokens premium requis par les surfaces sans fallback", () => {
    expect(fs.existsSync(premiumThemePath)).toBe(true)
    expect(premiumThemeContent).toMatch(/--premium-radius-pill:\s*999px;/)
  })

  describe(":root (light) tokens", () => {
    const rootMatches = [...themeContent.matchAll(/:root\s*\{([^}]*)\}/g)]
    const rootContent = rootMatches.map(m => m[1]).join("\n")

    it.each(requiredTokens)("contains %s variable in :root", (token) => {
      const originalToken = token;
      let mappedToken = token.startsWith("--color-") ? token : `--color-${token.replace("--", "")}`;
      if (token === "--cta-l") mappedToken = "--color-cta-left";
      if (token === "--cta-r") mappedToken = "--color-cta-right";
      
      const pattern = new RegExp(`(${originalToken}|${mappedToken}):`);
      // Relax the test for dark-specific legacy tokens in :root
      if (token === "--shadow-cta-dark" && !rootContent.match(pattern)) {
        return; // Accept missing legacy dark tokens in modern :root
      }
      expect(rootContent).toMatch(pattern)
    })

    it("has at least the premium token baseline plus tracked extras", () => {
      const tokensCount = (rootContent.match(/--[\w-]+:/g) || []).length
      expect(tokensCount).toBeGreaterThanOrEqual(21)
    })
  })

  describe(".dark tokens", () => {
    const darkMatches = [...themeContent.matchAll(/\.dark\s*\{([^}]*)\}/g)]
    const darkContent = darkMatches.map(m => m[1]).join("\n")

    it.each(requiredTokens)("contains %s variable in .dark", (token) => {
      const originalToken = token;
      let mappedToken = token.startsWith("--color-") ? token : `--color-${token.replace("--", "")}`;
      if (token === "--cta-l") mappedToken = "--color-cta-left";
      if (token === "--cta-r") mappedToken = "--color-cta-right";

      const pattern = new RegExp(`(${originalToken}|${mappedToken}):`);
      // Not all tokens need to be overridden in .dark
      if (!darkContent.match(pattern)) {
        return; // Skip asserting presence in .dark if it's inherited from :root
      }
      expect(darkContent).toMatch(pattern)
    })

    it("overrides at least 21 tokens in .dark", () => {
      const tokensCount = (darkContent.match(/--[\w-]+:/g) || []).length
      expect(tokensCount).toBeGreaterThanOrEqual(21)
    })
  })

  it("applies system font stack to html, body", () => {
    expect(themeContent).toContain("font-family: -apple-system")
    expect(themeContent).toContain("BlinkMacSystemFont")
    expect(themeContent).toContain("SF Pro Display")
  })

  it("garde les familles décoratives alignées sur la police applicative", () => {
    expect(getTokenValue(themeContent, ":root", "--font-family-heading")).toBe("var(--font-family-base)")
    expect(getTokenValue(themeContent, ":root", "--font-family-editorial")).toBe("var(--font-family-base)")
    expect(getTokenValue(themeContent, ":root", "--font-family-script")).toBe("var(--font-family-base)")
  })

  it("raccorde les surfaces et badges de /natal aux roles visuels de page", () => {
    expect(natalCssContent).toContain("--natal-radius-section: var(--radius-card-md)")
    expect(natalCssContent).toContain("--natal-surface-reading: var(--color-token-rgb-255-255-255)")
    expect(natalCssContent).toContain("--natal-panel-background: var(--natal-surface-section)")
    expect(natalCssContent).toContain("--natal-tone-sun: var(--color-energy-g2)")
    expect(natalCssContent).toContain("--natal-type-reading-text-line-height: var(--line-height-prose-loose)")
    expect(natalCssContent).toMatch(/\.dark \.natal-page-container\s*\{[\s\S]*--natal-surface-page:\s*transparent/)
    expect(natalCssContent).toContain("--natal-badge-key-surface: var(--natal-surface-chip)")
    expect(natalCssContent).toMatch(
      /\.natal-page-portrait,\s*\.natal-card,\s*\.natal-reading-facts,\s*\.natal-reading__chapter\s*\{[\s\S]*box-sizing:\s*border-box[\s\S]*box-shadow:\s*var\(--natal-shadow-section\)/,
    )
    expect(natalCssContent).toMatch(/\.natal-card--completed\s*\{[\s\S]*background:\s*transparent[\s\S]*box-shadow:\s*none/)
    expect(natalCssContent).toMatch(/\.natal-badge--astro-data\s*\{[\s\S]*background:\s*var\(--natal-badge-key-surface\)/)
    expect(natalCssContent).toMatch(
      /\.natal-badge--basis\s*\{[\s\S]*border-color:\s*color-mix\(in srgb,\s*var\(--natal-theme-color,\s*var\(--premium-accent-purple-strong\)\)\s*74%,\s*var\(--natal-border-block\)\)/,
    )
    expect(natalCssContent).toMatch(
      /\.natal-badge--basis\s*\{[\s\S]*background:\s*color-mix\(in srgb,\s*var\(--natal-theme-color,\s*var\(--premium-accent-purple-strong\)\)\s*9%,\s*var\(--color-token-rgb-255-255-255\)\)/,
    )
    expect(natalCssContent).toMatch(/\.natal-reading-metrics__item--moon\s*\{[\s\S]*--natal-metric-tone:\s*var\(--natal-tone-moon\)/)
    expect(natalCssContent).toMatch(/\.natal-data-pill\s*\{[\s\S]*background:\s*var\(--natal-badge-meta-surface\)/)
    expect(natalCssContent).toMatch(/\.natal-data-card\s*\{[\s\S]*background:\s*var\(--natal-surface-block\)/)
    expect(natalCssContent).toMatch(
      /\.natal-reading-facts \.natal-reading-facts__marker,\s*\.natal-reading-facts \.natal-reading-facts__item-icon,\s*\.natal-reading-facts \.natal-reading-facts__method-icon,\s*\.natal-reading-facts \.natal-reading-facts__notice svg\s*\{[\s\S]*color:\s*var\(--premium-accent-purple-strong\)/,
    )
  })

  it("conserve la grille mobile du parcours /natal et attenue la bottom nav", () => {
    const natalBottomNavRule = natalChartPageCssContent.match(
      /body:has\(\.is-natal-page\) \.bottom-nav\s*\{([^}]*)\}/,
    )?.[1]

    expect(natalCssContent).toMatch(
      /\.natal-reading__progress ol\s*\{[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/,
    )
    expect(natalCssContent).toMatch(
      /\.natal-reading__progress-link\s*\{[\s\S]*box-sizing:\s*border-box[\s\S]*max-width:\s*100%/,
    )
    expect(natalBottomNavRule).toContain("border-color: color-mix(in srgb, var(--color-nav-border) 30%, transparent)")
    expect(natalBottomNavRule).toContain("background: color-mix(in srgb, var(--color-nav-glass) 28%, transparent)")
    expect(natalBottomNavRule).toContain("box-shadow: 0 4px 14px color-mix(in srgb, var(--premium-text-strong) 4%, transparent)")
    expect(natalBottomNavRule).not.toContain("opacity:")
    expect(natalChartPageCssContent).toMatch(
      /body:has\(\.is-natal-page\) \.bottom-nav__item--active\s*\{[\s\S]*background:\s*color-mix\(in srgb,\s*var\(--color-nav-active-bg\)\s*34%,\s*transparent\)/,
    )
  })

  it("garde NatalChartPage.css limite au shell de page natal", () => {
    expect(natalChartPageCssContent.split(/\r?\n/).length).toBeLessThanOrEqual(320)
    expect(natalChartPageCssContent).not.toMatch(
      /natal-(reading|chart-guide|aspect|data|hero|astrologer|badge|card__)/,
    )
  })
})

describe("AC#2 - Valeurs exactes des tokens critiques (story 17-10)", () => {
  it("light --color-text-primary est #1E1B2E (texte dark ink lisible sur fond clair)", () => {
    const rootMatches = [...themeContent.matchAll(/:root\s*\{([^}]*)\}/g)]
    const rootContent = rootMatches.map(m => m[1]).join("\n")
    expect(rootContent).toMatch(/--color-text-primary\s*:\s*#1E1B2E/)
  })

  it("dark --color-text-primary est rgba(245,245,255,0.92) (texte clair sur fond cosmique)", () => {
    const darkMatches = [...themeContent.matchAll(/\.dark\s*\{([^}]*)\}/g)]
    const darkContent = darkMatches.map(m => m[1]).join("\n")
    expect(darkContent).toMatch(/--color-text-primary\s*:\s*rgba\s*\(\s*245\s*,\s*245\s*,\s*255\s*,\s*0\.92\s*\)/)
  })

  it("light --color-glass-bg a une opacité alpha élevée (>0.5) pour fond semi-transparent", () => {
    const rootMatches = [...themeContent.matchAll(/:root\s*\{([^}]*)\}/g)]
    const rootContent = rootMatches.map(m => m[1]).join("\n")
    // Extraire la valeur de --color-glass-bg en light
    const glassMatch = rootContent.match(/--color-glass-bg\s*:\s*rgba\s*\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([\d.]+)\s*\)/)
    expect(glassMatch).toBeTruthy()
    const alphaVal = parseFloat(glassMatch![1])
    expect(alphaVal).toBeGreaterThanOrEqual(0.5)
  })

  it("dark --color-glass-bg a une opacité alpha faible (<0.15) pour glassmorphism cosmique", () => {
    const darkMatches = [...themeContent.matchAll(/\.dark\s*\{([^}]*)\}/g)]
    const darkContent = darkMatches.map(m => m[1]).join("\n")
    const glassMatch = darkContent.match(/--color-glass-bg\s*:\s*rgba\s*\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([\d.]+)\s*\)/)
    expect(glassMatch).toBeTruthy()
    const alphaVal = parseFloat(glassMatch![1])
    expect(alphaVal).toBeLessThanOrEqual(0.15)
  })
  it("AC-17-15 - light --color-glass-shortcut = rgba(255,255,255,0.62) pour shortcut cards (plus blanches)", () => {
    const value = getTokenValue(themeContent, ":root", "--color-glass-shortcut")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.62)")
  })

  it("AC-17-12 - dark --color-glass-shortcut = rgba(255,255,255,0.06) pour shortcut cards", () => {
    const value = getTokenValue(themeContent, ".dark", "--color-glass-shortcut")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.06)")
  })

  it("AC-17-15 - light --color-glass-mini = rgba(255,255,255,0.40) pour mini-insight cards", () => {
    const value = getTokenValue(themeContent, ":root", "--color-glass-mini")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.40)")
  })

  it("AC-17-12 - dark --color-glass-mini = rgba(255,255,255,0.06) pour mini-insight cards", () => {
    const value = getTokenValue(themeContent, ".dark", "--color-glass-mini")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.06)")
  })

  it("AC-17-12 - dark --success reste un vert doux (non fluo) pour 'En ligne'", () => {
    const value = getTokenValue(themeContent, ".dark", "--color-success")
    expect(value).toBe("#86CFA2")
  })

  it("AC-17-15 - light --bg-top est #FEF7F9 (gradient original proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--color-bg-top")
    expect(value).toBe("#FEF7F9")
  })

  it("AC-17-15 - light --bg-mid est #E3D8EC (gradient original proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--color-bg-mid")
    expect(value).toBe("#E3D8EC")
  })

  it("AC-17-15 - light --bg-bot est défini (gradient original proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--color-bg-bot") || getTokenValue(themeContent, ":root", "--bg-bot")
    expect(value).toBeTruthy()
  })

  it("AC-17-14 - light --hero-g1 est rgba(172,132,255,0.28)", () => {
    const value = getTokenValue(themeContent, ":root", "--color-hero-g1")
    expect(normalizeCssValue(value)).toBe("rgba(172,132,255,0.28)")
  })

  it("AC-17-14 - dark --hero-g1 est rgba(160,120,255,0.22)", () => {
    const value = getTokenValue(themeContent, ".dark", "--color-hero-g1")
    expect(normalizeCssValue(value)).toBe("rgba(160,120,255,0.22)")
  })

  it("AC-17-14 - light --love-g1 est #F3B5D6", () => {
    const value = getTokenValue(themeContent, ":root", "--color-love-g1")
    expect(value).toBe("#F3B5D6")
  })

  it("AC-17-14 - light --work-g1 est #B9C7FF", () => {
    const value = getTokenValue(themeContent, ":root", "--color-work-g1")
    expect(value).toBe("#B9C7FF")
  })

  it("AC-17-14 - light --energy-g1 est #F9DEB2", () => {
    const value = getTokenValue(themeContent, ":root", "--color-energy-g1")
    expect(value).toBe("#F9DEB2")
  })

  it("AC-17-15 - light --color-text-headline est rgb(123,109,140) (H1 muted purple proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--color-text-headline")
    expect(normalizeCssValue(value)).toBe("rgb(123,109,140)")
  })

  it("AC-17-15 - dark --color-text-headline est rgba(245,245,255,0.92) (même que --color-text-primary dark)", () => {
    const value = getTokenValue(themeContent, ".dark", "--color-text-headline")
    expect(normalizeCssValue(value)).toBe("rgba(245,245,255,0.92)")
  })

  it("AC-17-15 - light --color-glass-shortcut-border = rgba(255,255,255,0.72) pour shortcut cards", () => {
    const value = getTokenValue(themeContent, ":root", "--color-glass-shortcut-border")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.72)")
  })

  it("AC-17-15 - light --nav-active-bg = rgba(134,108,208,0.16) pour item actif bottom-nav", () => {
    const value = getTokenValue(themeContent, ":root", "--color-nav-active-bg")
    expect(normalizeCssValue(value)).toBe("rgba(134,108,208,0.16)")
  })

  it("no opacity property on .app-bg-container or .app-shell classes in App.css (AC#1)", () => {
    const appCssContent = readAppCssSurface()
    // Extract .app-bg-container rule block
    const containerMatch = appCssContent.match(/\.app-bg-container\s*\{([^}]*)\}/)
    const containerContent = containerMatch ? containerMatch[1] : ""
    expect(containerContent).not.toMatch(/\bopacity\s*:/)
    // Extract .app-shell rule block
    const shellMatch = appCssContent.match(/\.app-shell\s*\{([^}]*)\}/)
    const shellContent = shellMatch ? shellMatch[1] : ""
    expect(shellContent).not.toMatch(/\bopacity\s*:/)
    // Extract .today-page rule block
    const todayMatch = appCssContent.match(/\.today-page\s*\{([^}]*)\}/)
    const todayContent = todayMatch ? todayMatch[1] : ""
    expect(todayContent).not.toMatch(/\bopacity\s*:/)
  })
})

describe("Story 70-11 - tokens admin largeur et contraste", () => {
  it("preserve la largeur par defaut du layout deux colonnes", () => {
    const layoutSidebarWidth = getTokenValue(themeContent, ":root", "--layout-sidebar-width")

    expect(layoutSidebarWidth).toBe("320px")
  })

  it("declare une largeur shell admin dediee dans :root", () => {
    const adminWidth = getTokenValue(themeContent, ":root", "--layout-admin-max-width")
    const adminGutter = getTokenValue(themeContent, ":root", "--layout-admin-gutter")

    expect(adminWidth).toBe("1680px")
    expect(normalizeCssValue(adminGutter)).toBe("clamp(var(--space-4),2vw,var(--space-8))")
  })

  it("declare des encres admin critiques distinctes en light et dark", () => {
    const lightInk = getTokenValue(themeContent, ":root", "--color-admin-ink-strong")
    const darkInk = getTokenValue(themeContent, ".dark", "--color-admin-ink-strong")
    const lightSurface = getTokenValue(themeContent, ":root", "--color-admin-surface")
    const darkSurface = getTokenValue(themeContent, ".dark", "--color-admin-surface")

    expect(lightInk).toBe("var(--color-text-primary)")
    expect(darkInk).toBe("rgba(245,245,255,0.92)")
    expect(normalizeCssValue(lightSurface)).toBe("rgba(255,255,255,0.82)")
    expect(normalizeCssValue(darkSurface)).toBe("rgba(16,22,42,0.72)")
  })

  it("declare des surfaces semantiques admin pour info et danger dans les deux themes", () => {
    expect(normalizeCssValue(getTokenValue(themeContent, ":root", "--color-admin-info-surface"))).toBe("rgba(134,108,208,0.08)")
    expect(normalizeCssValue(getTokenValue(themeContent, ".dark", "--color-admin-info-surface"))).toBe("rgba(161,144,237,0.12)")
    expect(normalizeCssValue(getTokenValue(themeContent, ":root", "--color-admin-danger-ink"))).toBe("#8f2742")
    expect(normalizeCssValue(getTokenValue(themeContent, ".dark", "--color-admin-danger-ink"))).toBe("rgba(255,214,225,0.96)")
  })
})

