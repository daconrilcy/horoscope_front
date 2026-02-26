import { describe, it, expect } from "vitest"
import fs from "fs"
import path from "path"

// Resolve path to theme.css
const themePath = path.resolve(__dirname, "../styles/theme.css")
const themeContent = fs.readFileSync(themePath, "utf-8")

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
  "--text-1",
  "--text-2",
  "--text-3",
  "--bg-top",
  "--bg-mid",
  "--bg-bot",
  "--glass",
  "--glass-2",
  "--glass-border",
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
  "--badge-tirage",
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
  "--text-headline",
]

describe("theme.css validation (Static Analysis)", () => {
  it("exists at frontend/src/styles/theme.css", () => {
    expect(fs.existsSync(themePath)).toBe(true)
  })

  describe(":root (light) tokens", () => {
    const rootMatch = themeContent.match(/:root\s*{([^}]*)}/)
    const rootContent = rootMatch ? rootMatch[1] : ""

    it.each(requiredTokens)("contains %s variable in :root", (token) => {
      expect(rootContent).toContain(`${token}:`)
    })

    it("has exactly 21 premium tokens + extra compatibility tokens", () => {
      const tokensCount = (rootContent.match(/--[\w-]+:/g) || []).length
      expect(tokensCount).toBeGreaterThanOrEqual(21)
    })
  })

  describe(".dark tokens", () => {
    const darkMatch = themeContent.match(/\.dark\s*{([^}]*)}/)
    const darkContent = darkMatch ? darkMatch[1] : ""

    it.each(requiredTokens)("contains %s variable in .dark", (token) => {
      expect(darkContent).toContain(`${token}:`)
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
})

describe("AC#2 — Valeurs exactes des tokens critiques (story 17-10)", () => {
  it("light --text-1 est #1E1B2E (texte dark ink lisible sur fond clair)", () => {
    const rootMatch = themeContent.match(/:root\s*\{([^}]*)\}/)   
    const rootContent = rootMatch ? rootMatch[1] : ""
    expect(rootContent).toMatch(/--text-1\s*:\s*#1E1B2E/)
  })

  it("dark --text-1 est rgba(245,245,255,0.92) (texte clair sur fond cosmique)", () => {
    const darkMatch = themeContent.match(/\.dark\s*\{([^}]*)\}/)  
    const darkContent = darkMatch ? darkMatch[1] : ""
    expect(darkContent).toMatch(/--text-1\s*:\s*rgba\s*\(\s*245\s*,\s*245\s*,\s*255\s*,\s*0\.92\s*\)/)
  })

  it("light --glass a une opacité alpha élevée (>0.5) pour fond semi-transparent", () => {
    const rootMatch = themeContent.match(/:root\s*\{([^}]*)\}/)   
    const rootContent = rootMatch ? rootMatch[1] : ""
    // Extraire la valeur de --glass en light
    const glassMatch = rootContent.match(/--glass\s*:\s*rgba\s*\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([\d.]+)\s*\)/)
    expect(glassMatch).toBeTruthy()
    const alphaVal = parseFloat(glassMatch![1])
    expect(alphaVal).toBeGreaterThanOrEqual(0.5)
  })

  it("dark --glass a une opacité alpha faible (<0.15) pour glassmorphism cosmique", () => {
    const darkMatch = themeContent.match(/\.dark\s*\{([^}]*)\}/)  
    const darkContent = darkMatch ? darkMatch[1] : ""
    const glassMatch = darkContent.match(/--glass\s*:\s*rgba\s*\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([\d.]+)\s*\)/)
    expect(glassMatch).toBeTruthy()
    const alphaVal = parseFloat(glassMatch![1])
    expect(alphaVal).toBeLessThanOrEqual(0.15)
  })
  it("AC-17-15 — light --glass-shortcut = rgba(255,255,255,0.62) pour shortcut cards (plus blanches)", () => {
    const value = getTokenValue(themeContent, ":root", "--glass-shortcut")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.62)")
  })

  it("AC-17-12 — dark --glass-shortcut = rgba(255,255,255,0.06) pour shortcut cards", () => {
    const value = getTokenValue(themeContent, ".dark", "--glass-shortcut")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.06)")
  })

  it("AC-17-15 — light --glass-mini = rgba(255,255,255,0.40) pour mini-insight cards", () => {
    const value = getTokenValue(themeContent, ":root", "--glass-mini")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.40)")
  })

  it("AC-17-12 — dark --glass-mini = rgba(255,255,255,0.06) pour mini-insight cards", () => {
    const value = getTokenValue(themeContent, ".dark", "--glass-mini")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.06)")
  })

  it("AC-17-12 — dark --success reste un vert doux (non fluo) pour 'En ligne'", () => {
    const value = getTokenValue(themeContent, ".dark", "--success")
    expect(value).toBe("#86CFA2")
  })

  it("AC-17-15 — light --bg-top est #FEF7F9 (gradient original proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--bg-top")
    expect(value).toBe("#FEF7F9")
  })

  it("AC-17-15 — light --bg-mid est #E3D8EC (gradient original proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--bg-mid")
    expect(value).toBe("#E3D8EC")
  })

  it("AC-17-15 — light --bg-bot est défini (gradient original proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--bg-bot")
    expect(value).toBeTruthy()
  })

  it("AC-17-14 — light --hero-g1 est rgba(172,132,255,0.28)", () => {
    const value = getTokenValue(themeContent, ":root", "--hero-g1")
    expect(normalizeCssValue(value)).toBe("rgba(172,132,255,0.28)")
  })

  it("AC-17-14 — dark --hero-g1 est rgba(160,120,255,0.22)", () => {
    const value = getTokenValue(themeContent, ".dark", "--hero-g1")
    expect(normalizeCssValue(value)).toBe("rgba(160,120,255,0.22)")
  })

  it("AC-17-14 — light --love-g1 est #F3B5D6", () => {
    const value = getTokenValue(themeContent, ":root", "--love-g1")
    expect(value).toBe("#F3B5D6")
  })

  it("AC-17-14 — light --work-g1 est #B9C7FF", () => {
    const value = getTokenValue(themeContent, ":root", "--work-g1")
    expect(value).toBe("#B9C7FF")
  })

  it("AC-17-14 — light --energy-g1 est #F9DEB2", () => {
    const value = getTokenValue(themeContent, ":root", "--energy-g1")
    expect(value).toBe("#F9DEB2")
  })

  it("AC-17-15 — light --text-headline est rgb(123,109,140) (H1 muted purple proche maquette)", () => {
    const value = getTokenValue(themeContent, ":root", "--text-headline")
    expect(normalizeCssValue(value)).toBe("rgb(123,109,140)")
  })

  it("AC-17-15 — dark --text-headline est rgba(245,245,255,0.92) (même que --text-1 dark)", () => {
    const value = getTokenValue(themeContent, ".dark", "--text-headline")
    expect(normalizeCssValue(value)).toBe("rgba(245,245,255,0.92)")
  })

  it("AC-17-15 — light --glass-shortcut-border = rgba(255,255,255,0.72) pour shortcut cards", () => {
    const value = getTokenValue(themeContent, ":root", "--glass-shortcut-border")
    expect(normalizeCssValue(value)).toBe("rgba(255,255,255,0.72)")
  })

  it("AC-17-15 — light --nav-active-bg = rgba(134,108,208,0.16) pour item actif bottom-nav", () => {
    const value = getTokenValue(themeContent, ":root", "--nav-active-bg")
    expect(normalizeCssValue(value)).toBe("rgba(134,108,208,0.16)")
  })

  it("no opacity property on .app-bg-container or .app-shell classes in App.css (AC#1)", () => {
    const appCssPath = path.resolve(__dirname, "../App.css")
    const appCssContent = fs.readFileSync(appCssPath, "utf-8")
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

