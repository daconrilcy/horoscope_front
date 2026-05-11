import { describe, it, expect, beforeEach, afterEach } from "vitest"
import { render, cleanup, fireEvent, act, screen } from "@testing-library/react"
import { readFileSync } from "fs"
import { resolve } from "path"
import { ThemeProvider, useTheme } from "../state/ThemeProvider"
import { StarfieldBackground, STAR_COUNT, STAR_SEED, STARS, SHOOTING_STAR_COUNT, SHOOTING_STAR_SEED, SHOOTING_STARS, seededRandom, generateStars, generateShootingStars, STAR_RADIUS_MIN, STAR_RADIUS_RANGE, STAR_OPACITY_MIN, STAR_OPACITY_RANGE, VIEWBOX_SIZE, LCG_MULTIPLIER, LCG_INCREMENT, LCG_MODULUS, type Star, type ShootingStar } from "../components/StarfieldBackground"

describe("StarfieldBackground", () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove("dark")
  })

  afterEach(() => {
    cleanup()
  })

  describe("AC4: Starfield en mode dark", () => {
    it("renders SVG starfield when theme is dark", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const container = document.querySelector("[aria-hidden='true']")
      expect(container).toBeInTheDocument()

      const svg = container?.querySelector("svg")
      expect(svg).toBeInTheDocument()

      const circles = svg?.querySelectorAll("circle")
      expect(circles?.length).toBe(STAR_COUNT)

      const shootingStars = svg?.querySelectorAll(".starfield-bg__shooting")
      expect(shootingStars?.length).toBe(SHOOTING_STAR_COUNT)
    })

    it("does not render starfield when theme is light", () => {
      localStorage.setItem("theme", "light")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const container = document.querySelector("[aria-hidden='true']")
      expect(container).not.toBeInTheDocument()
    })

    it("does not render when theme context is not available (useThemeSafe fallback)", () => {
      render(<StarfieldBackground />)

      const container = document.querySelector("[aria-hidden='true']")
      expect(container).not.toBeInTheDocument()
    })
  })

  describe("Starfield properties", () => {
    it("renders stars with correct opacity range", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      const circles = svg?.querySelectorAll("circle")

      circles?.forEach((circle) => {
        const opacity = parseFloat(circle.getAttribute("opacity") || "0")
        expect(opacity).toBeGreaterThanOrEqual(STAR_OPACITY_MIN)
        expect(opacity).toBeLessThanOrEqual(STAR_OPACITY_MIN + STAR_OPACITY_RANGE)
      })
    })

    it("renders stars with correct radius range", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      const circles = svg?.querySelectorAll("circle")

      circles?.forEach((circle) => {
        const radius = parseFloat(circle.getAttribute("r") || "0")
        expect(radius).toBeGreaterThanOrEqual(STAR_RADIUS_MIN)
        expect(radius).toBeLessThanOrEqual(STAR_RADIUS_MIN + STAR_RADIUS_RANGE)
      })
    })

    it("has starfield-bg class for styling", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const container = document.querySelector("[aria-hidden='true']")
      expect(container).toHaveClass("starfield-bg")
    })

    it("renders stars with CSS variable fill color", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      const circles = svg?.querySelectorAll("circle")

      circles?.forEach((circle) => {
        expect(circle.getAttribute("fill")).toBe("var(--star-fill)")
        expect(circle.getAttribute("class")).toMatch(/starfield-bg__star/)
      })
    })

    it("renders a diffuse Milky Way layer and rare shooting stars", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      expect(document.querySelector(".starfield-bg__milky-way")).toBeInTheDocument()
      expect(document.querySelectorAll(".starfield-bg__shooting")).toHaveLength(SHOOTING_STAR_COUNT)
      expect(SHOOTING_STAR_COUNT).toBeLessThanOrEqual(3)
    })

    it("renders SVG with correct viewBox attribute using VIEWBOX_SIZE", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      expect(svg?.getAttribute("viewBox")).toBe(`0 0 ${VIEWBOX_SIZE} ${VIEWBOX_SIZE}`)
      expect(VIEWBOX_SIZE).toBe(100)
    })

    it("renders SVG with correct preserveAspectRatio attribute", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      expect(svg?.getAttribute("preserveAspectRatio")).toBe("xMidYMid slice")
    })

    it("renders SVG with 100% width and height", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      expect(svg?.getAttribute("width")).toBe("100%")
      expect(svg?.getAttribute("height")).toBe("100%")
    })

    it("renders SVG with correct xmlns attribute", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const svg = document.querySelector("svg")
      expect(svg?.getAttribute("xmlns")).toBe("http://www.w3.org/2000/svg")
    })
  })

  describe("Integration with ThemeProvider toggle", () => {
    function ToggleButton() {
      const { toggleTheme } = useTheme()
      return <button onClick={toggleTheme}>Toggle</button>
    }

    it("shows/hides starfield when theme is toggled", () => {
      localStorage.setItem("theme", "light")

      render(
        <ThemeProvider>
          <StarfieldBackground />
          <ToggleButton />
        </ThemeProvider>
      )

      expect(document.querySelector("[aria-hidden='true']")).not.toBeInTheDocument()

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(document.querySelector("[aria-hidden='true']")).toBeInTheDocument()
      expect(document.querySelector("svg")).toBeInTheDocument()

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(document.querySelector("[aria-hidden='true']")).not.toBeInTheDocument()
    })
  })

  describe("Deterministic star generation", () => {
    it("generates same star positions with same seed", () => {
      localStorage.setItem("theme", "dark")

      const { unmount } = render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const firstRenderCircles = Array.from(document.querySelectorAll("circle")).map((c) => ({
        cx: c.getAttribute("cx"),
        cy: c.getAttribute("cy"),
        r: c.getAttribute("r"),
      }))

      unmount()
      cleanup()

      render(
        <ThemeProvider>
          <StarfieldBackground />
        </ThemeProvider>
      )

      const secondRenderCircles = Array.from(document.querySelectorAll("circle")).map((c) => ({
        cx: c.getAttribute("cx"),
        cy: c.getAttribute("cy"),
        r: c.getAttribute("r"),
      }))

      expect(firstRenderCircles).toEqual(secondRenderCircles)
      expect(firstRenderCircles.length).toBe(STAR_COUNT)
    })

    it("exports STAR_SEED constant for documentation", () => {
      expect(STAR_SEED).toBe(12345)
    })
  })

  describe("seededRandom function", () => {
    it("generates deterministic sequence from same seed", () => {
      const random1 = seededRandom(42)
      const random2 = seededRandom(42)

      const seq1 = [random1(), random1(), random1()]
      const seq2 = [random2(), random2(), random2()]

      expect(seq1).toEqual(seq2)
    })

    it("generates different sequences from different seeds", () => {
      const random1 = seededRandom(42)
      const random2 = seededRandom(123)

      expect(random1()).not.toEqual(random2())
    })

    it("returns values in range [0, 1)", () => {
      const random = seededRandom(STAR_SEED)
      for (let i = 0; i < 100; i++) {
        const value = random()
        expect(value).toBeGreaterThanOrEqual(0)
        expect(value).toBeLessThan(1)
      }
    })
  })

  describe("Star interface", () => {
    it("allows typing star objects correctly", () => {
      const star: Star = {
        id: "test-star",
        cx: 50,
        cy: 50,
        r: 0.5,
        opacity: 0.5,
        className: "starfield-bg__star starfield-bg__star--mid",
      }
      expect(star.id).toBe("test-star")
      expect(star.cx).toBe(50)
    })

    it("allows typing shooting star objects correctly", () => {
      const shootingStar: ShootingStar = {
        id: "test-shooting-star",
        x1: 12,
        y1: 20,
        x2: 28,
        y2: 16,
        opacity: 0.4,
        className: "starfield-bg__shooting starfield-bg__shooting--1",
      }
      expect(shootingStar.id).toBe("test-shooting-star")
      expect(shootingStar.className).toContain("shooting")
    })
  })

  describe("generateStars function", () => {
    it("generates correct number of stars", () => {
      const stars = generateStars(50, 999)
      expect(stars.length).toBe(50)
    })

    it("generates stars with valid properties", () => {
      const stars = generateStars(10, 42)
      stars.forEach((star, i) => {
        expect(star.id).toBe(`star-42-${i}`)
        expect(star.cx).toBeGreaterThanOrEqual(0)
        expect(star.cx).toBeLessThan(VIEWBOX_SIZE)
        expect(star.cy).toBeGreaterThanOrEqual(0)
        expect(star.cy).toBeLessThan(VIEWBOX_SIZE)
        expect(star.r).toBeGreaterThanOrEqual(STAR_RADIUS_MIN)
        expect(star.r).toBeLessThanOrEqual(STAR_RADIUS_MIN + STAR_RADIUS_RANGE)
        expect(star.opacity).toBeGreaterThanOrEqual(STAR_OPACITY_MIN)
        expect(star.opacity).toBeLessThanOrEqual(STAR_OPACITY_MIN + STAR_OPACITY_RANGE)
        expect(star.className).toContain("starfield-bg__star")
      })
    })

    it("generates deterministic stars with same seed", () => {
      const stars1 = generateStars(5, 123)
      const stars2 = generateStars(5, 123)
      expect(stars1).toEqual(stars2)
    })

    it("generates different stars with different seed", () => {
      const stars1 = generateStars(5, 111)
      const stars2 = generateStars(5, 222)
      expect(stars1[0].cx).not.toEqual(stars2[0].cx)
    })
  })

  describe("generateShootingStars function", () => {
    it("generates deterministic rare shooting stars", () => {
      const stars1 = generateShootingStars(3, SHOOTING_STAR_SEED)
      const stars2 = generateShootingStars(3, SHOOTING_STAR_SEED)

      expect(stars1).toEqual(stars2)
      expect(stars1).toEqual(SHOOTING_STARS)
      expect(SHOOTING_STARS.length).toBe(SHOOTING_STAR_COUNT)
    })
  })

  describe("Star range constants", () => {
    it("exports STAR_RADIUS_MIN and STAR_RADIUS_RANGE", () => {
      expect(STAR_RADIUS_MIN).toBe(0.16)
      expect(STAR_RADIUS_RANGE).toBe(0.24)
      expect(STAR_RADIUS_MIN + STAR_RADIUS_RANGE).toBe(0.4)
    })

    it("exports STAR_OPACITY_MIN and STAR_OPACITY_RANGE", () => {
      expect(STAR_OPACITY_MIN).toBe(0.24)
      expect(STAR_OPACITY_RANGE).toBe(0.58)
      expect(STAR_OPACITY_MIN + STAR_OPACITY_RANGE).toBe(0.82)
    })
  })

  describe("LCG constants", () => {
    it("exports LCG_MULTIPLIER with glibc value", () => {
      expect(LCG_MULTIPLIER).toBe(1103515245)
    })

    it("exports LCG_INCREMENT with glibc value", () => {
      expect(LCG_INCREMENT).toBe(12345)
    })

    it("exports LCG_MODULUS as 0x7fffffff", () => {
      expect(LCG_MODULUS).toBe(0x7fffffff)
      expect(LCG_MODULUS).toBe(2147483647)
    })
  })

  describe("STARS constant", () => {
    it("exports pre-generated STARS array", () => {
      expect(STARS).toBeDefined()
      expect(STARS.length).toBe(STAR_COUNT)
    })

    it("STARS matches generateStars output with same parameters", () => {
      const freshStars = generateStars(STAR_COUNT, STAR_SEED)
      expect(STARS).toEqual(freshStars)
    })

    it("STARS elements have valid star properties", () => {
      STARS.forEach((star) => {
        expect(star.id).toMatch(/^star-\d+-\d+$/)
        expect(star.cx).toBeGreaterThanOrEqual(0)
        expect(star.cy).toBeGreaterThanOrEqual(0)
        expect(star.r).toBeGreaterThanOrEqual(STAR_RADIUS_MIN)
        expect(star.opacity).toBeGreaterThanOrEqual(STAR_OPACITY_MIN)
      })
    })
  })

  describe("Motion accessibility", () => {
    it("disables shooting star motion for reduced motion and mobile", () => {
      const backgroundsCss = readFileSync(resolve(__dirname, "../styles/backgrounds.css"), "utf-8")

      expect(backgroundsCss).toContain("@media (prefers-reduced-motion: reduce)")
      expect(backgroundsCss).toMatch(/\.starfield-bg__shooting\s*\{[^}]*animation:\s*none/)
      expect(backgroundsCss).toContain("@media (max-width: 768px)")
    })
  })
})
