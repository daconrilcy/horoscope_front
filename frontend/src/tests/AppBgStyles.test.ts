import { describe, it, expect, beforeAll } from "vitest"
import { readFileSync } from "fs"
import { resolve } from "path"

describe("App Background CSS (AC1, AC2, AC3, AC6)", () => {
  let cssContent: string

  beforeAll(() => {
    const themePath = resolve(__dirname, "../styles/theme.css")
    const bgPath = resolve(__dirname, "../styles/backgrounds.css")
    cssContent = readFileSync(themePath, "utf-8") + "\n" + readFileSync(bgPath, "utf-8")
  })

  describe("Theme token definitions", () => {
    it("defines --primary and --primary-strong in :root", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--primary:\s*#[0-9A-Fa-f]{6}/)
      expect(cssContent).toMatch(/:root\s*\{[^}]*--primary-strong:\s*#[0-9A-Fa-f]{6}/)
    })

    it("defines --primary and --primary-strong in .dark", () => {
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--primary:\s*#[0-9A-Fa-f]{6}/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--primary-strong:\s*#[0-9A-Fa-f]{6}/)
    })

    it("defines text tokens --text-1, --text-2, --text-3 in :root", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--text-1:/)
      expect(cssContent).toMatch(/:root\s*\{[^}]*--text-2:/)
      expect(cssContent).toMatch(/:root\s*\{[^}]*--text-3:/)
    })

    it("defines text tokens --text-1, --text-2, --text-3 in .dark", () => {
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--text-1:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--text-2:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--text-3:/)
    })

    it("defines different --text-1 values for light and dark themes", () => {
      const lightMatch = cssContent.match(/:root\s*\{[^}]*--text-1:\s*([^;]+)/)
      const darkMatch = cssContent.match(/\.dark\s*\{[^}]*--text-1:\s*([^;]+)/)
      
      expect(lightMatch).toBeTruthy()
      expect(darkMatch).toBeTruthy()
      expect(lightMatch![1]).not.toEqual(darkMatch![1])
    })

    it("defines different --glass values for light and dark themes", () => {
      const lightGlassMatch = cssContent.match(/:root\s*\{[^}]*--glass:\s*([^;]+)/)
      const darkGlassMatch = cssContent.match(/\.dark\s*\{[^}]*--glass:\s*([^;]+)/)
      
      expect(lightGlassMatch).toBeTruthy()
      expect(darkGlassMatch).toBeTruthy()
      expect(lightGlassMatch![1]).not.toEqual(darkGlassMatch![1])
    })

    it("defines different --bg-top values for light and dark themes", () => {
      const lightBgMatch = cssContent.match(/:root\s*\{[^}]*--bg-top:\s*([^;]+)/)
      const darkBgMatch = cssContent.match(/\.dark\s*\{[^}]*--bg-top:\s*([^;]+)/)
      
      expect(lightBgMatch).toBeTruthy()
      expect(darkBgMatch).toBeTruthy()
      expect(lightBgMatch![1]).not.toEqual(darkBgMatch![1])
    })

    it("defines --bg-mid in :root and .dark with different values", () => {
      const lightMatch = cssContent.match(/:root\s*\{[^}]*--bg-mid:\s*([^;]+)/)
      const darkMatch = cssContent.match(/\.dark\s*\{[^}]*--bg-mid:\s*([^;]+)/)
      
      expect(lightMatch).toBeTruthy()
      expect(darkMatch).toBeTruthy()
      expect(lightMatch![1]).not.toEqual(darkMatch![1])
    })

    it("defines --bg-bot in :root and .dark with different values", () => {
      const lightMatch = cssContent.match(/:root\s*\{[^}]*--bg-bot:\s*([^;]+)/)
      const darkMatch = cssContent.match(/\.dark\s*\{[^}]*--bg-bot:\s*([^;]+)/)
      
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
        /\.app-bg\s*\{[^}]*linear-gradient\(180deg, var\(--bg-top\) 0%, var\(--bg-mid\) 55%, var\(--bg-bot\) 100%\)/
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

  describe("AC6: Container centré max-width 420px", () => {
    it("defines .app-bg-container class with max-width 420px", () => {
      expect(cssContent).toMatch(/\.app-bg-container\s*\{[^}]*max-width:\s*420px/)
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
      expect(cssContent).toMatch(/:root\s*\{[^}]*--btn-text:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--btn-text:/)
    })

    it("defines --bg-2 in :root and .dark", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--bg-2:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--bg-2:/)
    })

    it("defines --success in :root and .dark", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--success:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--success:/)
    })

    it("defines --error in :root and .dark", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--error:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--error:/)
    })

    it("defines --star-fill in :root and .dark", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--star-fill:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--star-fill:/)
    })

    it("defines --glass-2 and --glass-border in :root and .dark", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--glass-2:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--glass-2:/)
      expect(cssContent).toMatch(/:root\s*\{[^}]*--glass-border:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--glass-border:/)
    })

    it("defines --nav-glass and --nav-border in :root and .dark", () => {
      expect(cssContent).toMatch(/:root\s*\{[^}]*--nav-glass:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--nav-glass:/)
      expect(cssContent).toMatch(/:root\s*\{[^}]*--nav-border:/)
      expect(cssContent).toMatch(/\.dark\s*\{[^}]*--nav-border:/)
    })

    it("defines --cta-l and --cta-r in :root and .dark with different values", () => {
      const lightCtaL = cssContent.match(/:root\s*\{[^}]*--cta-l:\s*([^;]+)/)
      const darkCtaL = cssContent.match(/\.dark\s*\{[^}]*--cta-l:\s*([^;]+)/)
      const lightCtaR = cssContent.match(/:root\s*\{[^}]*--cta-r:\s*([^;]+)/)
      const darkCtaR = cssContent.match(/\.dark\s*\{[^}]*--cta-r:\s*([^;]+)/)
      
      expect(lightCtaL).toBeTruthy()
      expect(darkCtaL).toBeTruthy()
      expect(lightCtaR).toBeTruthy()
      expect(darkCtaR).toBeTruthy()
      expect(lightCtaL![1]).not.toEqual(darkCtaL![1])
      expect(lightCtaR![1]).not.toEqual(darkCtaR![1])
    })

    it("defines --line in :root and .dark with different values", () => {
      const lightLine = cssContent.match(/:root\s*\{[^}]*--line:\s*([^;]+)/)
      const darkLine = cssContent.match(/\.dark\s*\{[^}]*--line:\s*([^;]+)/)
      
      expect(lightLine).toBeTruthy()
      expect(darkLine).toBeTruthy()
      expect(lightLine![1]).not.toEqual(darkLine![1])
    })
  })
})
