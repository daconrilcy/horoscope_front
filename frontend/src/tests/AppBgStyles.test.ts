import { describe, it, expect, beforeAll } from "vitest"
import { readFileSync } from "fs"
import { resolve } from "path"

describe("App Background CSS (AC1, AC2, AC3, AC6)", () => {
  let cssContent: string

  beforeAll(() => {
    const themePath = resolve(__dirname, "../styles/theme.css")
    const designTokensPath = resolve(__dirname, "../styles/design-tokens.css")
    const bgPath = resolve(__dirname, "../styles/backgrounds.css")
    cssContent = readFileSync(designTokensPath, "utf-8") + "\n" + readFileSync(themePath, "utf-8") + "\n" + readFileSync(bgPath, "utf-8")
  })

  describe("Theme token definitions", () => {
    it("defines --primary and --primary-strong in :root", () => {
      expect(cssContent).toMatch(/--color-primary:\s*#[0-9A-Fa-f]{6}/)
      expect(cssContent).toMatch(/--color-primary-strong:\s*#[0-9A-Fa-f]{6}/)
    })

    it("defines --primary and --primary-strong in .dark", () => {
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-primary:\s*#[0-9A-Fa-f]{6}/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-primary-strong:\s*#[0-9A-Fa-f]{6}/)
    })

    it("defines text tokens --text-1, --text-2, --text-3 in :root", () => {
      expect(cssContent).toMatch(/--text-1:/)
      expect(cssContent).toMatch(/--text-2:/)
      expect(cssContent).toMatch(/--text-3:/)
    })

    it("defines text tokens --text-1, --text-2, --text-3 in .dark", () => {
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-text-primary:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-text-secondary:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-text-muted:/)
    })

    it("defines different --text-1 values for light and dark themes", () => {
      const lightMatch = cssContent.match(/--color-text-primary:\s*([^;]+)/)
      const darkMatch = cssContent.match(/\.dark[\s\S]*?--color-text-primary:\s*([^;]+)/)
      
      expect(lightMatch).toBeTruthy()
      expect(darkMatch).toBeTruthy()
      expect(lightMatch![1]).not.toEqual(darkMatch![1])
    })

    it("defines different --glass values for light and dark themes", () => {
      const lightGlassMatch = cssContent.match(/--color-glass-bg:\s*([^;]+)/)
      const darkGlassMatch = cssContent.match(/\.dark[\s\S]*?--color-glass-bg:\s*([^;]+)/)
      
      expect(lightGlassMatch).toBeTruthy()
      expect(darkGlassMatch).toBeTruthy()
      expect(lightGlassMatch![1]).not.toEqual(darkGlassMatch![1])
    })

    it("defines different --bg-top values for light and dark themes", () => {
      const lightBgMatch = cssContent.match(/--color-bg-top:\s*([^;]+)/)
      const darkBgMatch = cssContent.match(/\.dark[\s\S]*?--color-bg-top:\s*([^;]+)/)
      
      expect(lightBgMatch).toBeTruthy()
      expect(darkBgMatch).toBeTruthy()
      expect(lightBgMatch![1]).not.toEqual(darkBgMatch![1])
    })

    it("defines --bg-mid in :root and .dark with different values", () => {
      const lightMatch = cssContent.match(/--color-bg-mid:\s*([^;]+)/)
      const darkMatch = cssContent.match(/\.dark[\s\S]*?--color-bg-mid:\s*([^;]+)/)
      
      expect(lightMatch).toBeTruthy()
      expect(darkMatch).toBeTruthy()
      expect(lightMatch![1]).not.toEqual(darkMatch![1])
    })

    it("defines --bg-bot in :root and .dark with different values", () => {
      const lightMatch = cssContent.match(/--color-bg-bot:\s*([^;]+)/)
      const darkMatch = cssContent.match(/\.dark[\s\S]*?--color-bg-bot:\s*([^;]+)/)
      
      expect(lightMatch).toBeTruthy()
      expect(darkMatch).toBeTruthy()
      expect(lightMatch![1]).not.toEqual(darkMatch![1])
    })
  })

  describe("AC1: Fond gradient light correct", () => {
    it("defines .app-bg class with min-height 100dvh", () => {
      expect(cssContent).toMatch(/\.app-bg\s*\{[^}]*min-height:\s*100dvh/)
    })

    it("defines .app-bg class with position relative", () => {
      expect(cssContent).toMatch(/\.app-bg\s*\{[^}]*position:\s*relative/)
    })

    it("defines light gradient with radial-gradient", () => {
      expect(cssContent).toMatch(
        /\.app-bg\s*\{[^}]*radial-gradient\(1200px 800px at 20% 10%/
      )
      expect(cssContent).toMatch(
        /\.app-bg\s*\{[^}]*radial-gradient\(900px 700px at 80% 60%/
      )
    })

    it("defines light gradient with linear-gradient using tokens", () => {
      expect(cssContent).toMatch(
        /\.app-bg\s*\{[^}]*linear-gradient\(180deg, var\(--bg-top\) 0%, var\(--bg-mid\) \d+%, var\(--bg-bot\) 100%\)/
      )
    })
  })

  describe("AC2: Couche noise en mode light", () => {
    it("defines .app-bg::after pseudo-element for noise", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{/)
    })

    it("sets content: '' for ::after pseudo-element", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*content:\s*['"]/)
    })

    it("sets noise opacity approximately 0.08", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*opacity:\s*0\.08/)
    })

    it("sets mix-blend-mode: soft-light for noise", () => {
      expect(cssContent).toMatch(
        /\.app-bg::after\s*\{[^}]*mix-blend-mode:\s*soft-light/
      )
    })

    it("hides noise layer in dark mode", () => {
      expect(cssContent).toMatch(/\.dark\s+\.app-bg::after\s*\{[^}]*display:\s*none/)
    })
  })

  describe("AC3: Fond gradient dark cosmic correct", () => {
    it("defines .dark .app-bg class with dark gradients", () => {
      expect(cssContent).toMatch(/\.dark\s+\.app-bg\s*\{/)
    })

    it("uses different radial-gradient opacities for dark mode", () => {
      expect(cssContent).toMatch(
        /\.dark\s+\.app-bg\s*\{[^}]*rgba\(160,120,255,0\.22\)/
      )
      expect(cssContent).toMatch(
        /\.dark\s+\.app-bg\s*\{[^}]*rgba\(90,170,255,0\.14\)/
      )
    })
  })

  describe("AC6: Container centré max-width 1100px desktop", () => {
    it("defines .app-bg-container class with max-width 1100px on desktop", () => {
      expect(cssContent).toMatch(/@media\s*\(min-width:\s*769px\)[^{]*\{[^}]*\.app-bg-container\s*\{[^}]*max-width:\s*1100px/)
    })

    it("centers container with auto margins", () => {
      expect(cssContent).toMatch(/\.app-bg-container\s*\{[^}]*margin-left:\s*auto/)
      expect(cssContent).toMatch(/\.app-bg-container\s*\{[^}]*margin-right:\s*auto/)
    })

    it("sets z-index for proper layering", () => {
      expect(cssContent).toMatch(/\.app-bg-container\s*\{[^}]*z-index:\s*1/)
    })

    it("sets min-height 100dvh for full viewport", () => {
      expect(cssContent).toMatch(/\.app-bg-container\s*\{[^}]*min-height:\s*100dvh/)
    })

    it("sets position relative for stacking context", () => {
      expect(cssContent).toMatch(/\.app-bg-container\s*\{[^}]*position:\s*relative/)
    })

    it("increases max-width to 1100px on desktop", () => {
      expect(cssContent).toMatch(/@media\s*\(min-width:\s*769px\)\s*\{[^}]*\.app-bg-container\s*\{[^}]*max-width:\s*1100px/)
    })
  })

  describe("AC4: Starfield background styling", () => {
    it("defines .starfield-bg class", () => {
      expect(cssContent).toMatch(/\.starfield-bg\s*\{/)
    })

    it("sets starfield position fixed with inset 0", () => {
      expect(cssContent).toMatch(/\.starfield-bg\s*\{[^}]*position:\s*fixed/)
      expect(cssContent).toMatch(/\.starfield-bg\s*\{[^}]*inset:\s*0/)
    })

    it("sets starfield pointer-events none", () => {
      expect(cssContent).toMatch(/\.starfield-bg\s*\{[^}]*pointer-events:\s*none/)
    })

    it("sets starfield opacity 0.4", () => {
      expect(cssContent).toMatch(/\.starfield-bg\s*\{[^}]*opacity:\s*0\.4/)
    })

    it("sets starfield z-index 0 for proper layering", () => {
      expect(cssContent).toMatch(/\.starfield-bg\s*\{[^}]*z-index:\s*0/)
    })
  })

  describe("Noise overlay SVG", () => {
    it("uses feTurbulence SVG filter in ::after", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*data:image\/svg\+xml/)
      expect(cssContent).toMatch(/feTurbulence/)
      expect(cssContent).toMatch(/fractalNoise/)
    })

    it("uses correct feTurbulence parameters", () => {
      expect(cssContent).toMatch(/baseFrequency='0\.65'/)
      expect(cssContent).toMatch(/numOctaves='3'/)
      expect(cssContent).toMatch(/stitchTiles='stitch'/)
    })

    it("sets noise ::after z-index 0 for proper layering", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*z-index:\s*0/)
    })

    it("sets noise background-size 200px 200px", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*background-size:\s*200px\s+200px/)
    })

    it("sets noise ::after position fixed for full-screen coverage", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*position:\s*fixed/)
    })

    it("sets noise ::after pointer-events none to avoid UI interference", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*pointer-events:\s*none/)
    })

    it("sets noise ::after inset 0 for full-screen coverage", () => {
      expect(cssContent).toMatch(/\.app-bg::after\s*\{[^}]*inset:\s*0/)
    })
  })

  describe("Semantic tokens", () => {
    it("defines --btn-text in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-btn-text:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-btn-text:/)
    })

    it("defines --bg-2 in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-bg-2:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-bg-2:/)
    })

    it("defines --success in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-success:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-success:/)
    })

    it("defines --error in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-error:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-error:/)
    })

    it("defines --star-fill in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-star-fill:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-star-fill:/)
    })

    it("defines --glass-2 and --glass-border in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-glass-bg-2:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-glass-bg-2:/)
      expect(cssContent).toMatch(/--color-glass-border:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-glass-border:/)
    })

    it("defines --nav-glass and --nav-border in :root and .dark", () => {
      expect(cssContent).toMatch(/--color-nav-glass:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-nav-glass:/)
      expect(cssContent).toMatch(/--color-nav-border:/)
      expect(cssContent).toMatch(/\.dark[\s\S]*?--color-nav-border:/)
    })

    it("defines --cta-l and --cta-r in :root and .dark with different values", () => {
      const lightCtaL = cssContent.match(/--color-cta-left:\s*([^;]+)/)
      const darkCtaL = cssContent.match(/\.dark[\s\S]*?--color-cta-left:\s*([^;]+)/)
      const lightCtaR = cssContent.match(/--color-cta-right:\s*([^;]+)/)
      const darkCtaR = cssContent.match(/\.dark[\s\S]*?--color-cta-right:\s*([^;]+)/)
      
      expect(lightCtaL).toBeTruthy()
      expect(darkCtaL).toBeTruthy()
      expect(lightCtaR).toBeTruthy()
      expect(darkCtaR).toBeTruthy()
      expect(lightCtaL![1]).not.toEqual(darkCtaL![1])
      expect(lightCtaR![1]).not.toEqual(darkCtaR![1])
    })

    it("defines --line in :root and .dark with different values", () => {
      const lightLine = cssContent.match(/--color-line:\s*([^;]+)/)
      const darkLine = cssContent.match(/\.dark[\s\S]*?--color-line:\s*([^;]+)/)
      
      expect(lightLine).toBeTruthy()
      expect(darkLine).toBeTruthy()
      expect(lightLine![1]).not.toEqual(darkLine![1])
    })
  })
})
