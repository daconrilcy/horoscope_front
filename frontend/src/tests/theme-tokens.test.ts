import { describe, it, expect } from "vitest"
import fs from "fs"
import path from "path"

// Resolve path to theme.css
const themePath = path.resolve(__dirname, "../styles/theme.css")
const themeContent = fs.readFileSync(themePath, "utf-8")

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
  "--shadow-card",
  "--shadow-nav",
  "--badge-chat",
  "--badge-tirage",
  "--badge-amour",
  "--badge-travail",
  "--badge-energie",
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

