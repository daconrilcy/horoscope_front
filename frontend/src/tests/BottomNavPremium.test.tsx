import { describe, it, expect, afterEach, beforeAll } from "vitest"
import { render, cleanup, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BottomNav } from "../components/layout/BottomNav"
import { readFileSync } from "fs"
import { resolve } from "path"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

// ─── CSS source files (AC1 / AC2 conformance) ────────────────────────────────

let appCss: string
let themeCss: string

beforeAll(() => {
  appCss = readFileSync(resolve(__dirname, "../App.css"), "utf-8")
  themeCss = readFileSync(resolve(__dirname, "../styles/theme.css"), "utf-8")
})

// ─── AC1 : Container bottom-nav conforme ─────────────────────────────────────

describe("AC1 — Container .bottom-nav conforme (CSS)", () => {
  it("a position: fixed et bottom/left/right à 16px", () => {
    const match = appCss.match(/\.bottom-nav\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("position: fixed")
    expect(content).toContain("bottom: 16px")
    expect(content).toContain("left: 16px")
    expect(content).toContain("right: 16px")
  })

  it("a border-radius 24px et padding 10px", () => {
    const match = appCss.match(/\.bottom-nav\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("border-radius: 24px")
    expect(content).toContain("padding: 10px")
  })

  it("applique backdrop-filter (blur 14px via --glass-blur)", () => {
    const match = appCss.match(/\.bottom-nav\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toMatch(/backdrop-filter/)
  })

  it("utilise --nav-glass, --nav-border et --shadow-nav", () => {
    const match = appCss.match(/\.bottom-nav\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("var(--nav-glass)")
    expect(content).toContain("var(--nav-border)")
    expect(content).toContain("var(--shadow-nav)")
  })
})

// ─── AC2 : Items et actif premium ────────────────────────────────────────────

describe("AC2 — Items nav premium (CSS)", () => {
  it(".bottom-nav__item a border-radius 18px (premium, non-tile)", () => {
    const match = appCss.match(/\.bottom-nav__item\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("border-radius: 18px")
  })

  it(".bottom-nav__item--active utilise var(--nav-active-bg)", () => {
    const match = appCss.match(/\.bottom-nav__item--active\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("var(--nav-active-bg)")
  })

  it(".bottom-nav__item--active utilise var(--text-1) pour contraste renforcé", () => {
    const match = appCss.match(/\.bottom-nav__item--active\s*\{([^}]*)\}/)
    const content = match ? match[1] : ""
    expect(content).toContain("var(--text-1)")
  })

  it("light --nav-active-bg est rgba(134,108,208,0.16) (discret premium)", () => {
    const rootMatch = themeCss.match(/:root\s*\{([^}]*)\}/)
    const rootContent = rootMatch ? rootMatch[1] : ""
    expect(rootContent).toContain("--nav-active-bg: rgba(134, 108, 208, 0.16)")
  })

  it("dark --nav-active-bg est rgba(150,110,255,0.18) (discret premium)", () => {
    const darkMatch = themeCss.match(/\.dark\s*\{([^}]*)\}/)
    const darkContent = darkMatch ? darkMatch[1] : ""
    expect(darkContent).toContain("--nav-active-bg: rgba(150, 110, 255, 0.18)")
  })
})

afterEach(() => {
  cleanup()
})

function renderWithRouter(initialPath = "/dashboard") {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialPath]}>
        <BottomNav />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

// ─── AC2 : 5 items présents ─────────────────────────────────────────────────

describe("AC2 : 5 items de navigation présents", () => {
  it("affiche exactement 5 liens", () => {
    renderWithRouter()
    const links = screen.getAllByRole("link")
    expect(links).toHaveLength(5)
  })

  it("affiche les labels : Aujourd'hui, Chat, Thème, Tirages, Profil", () => {
    renderWithRouter()
    expect(screen.getByText("Aujourd'hui")).toBeInTheDocument()
    expect(screen.getByText("Chat")).toBeInTheDocument()
    expect(screen.getByText("Thème")).toBeInTheDocument()
    expect(screen.getByText("Tirages")).toBeInTheDocument()
    expect(screen.getByText("Profil")).toBeInTheDocument()
  })

  it("chaque item a la classe bottom-nav__item", () => {
    renderWithRouter()
    const links = screen.getAllByRole("link")
    links.forEach((link) => {
      expect(link).toHaveClass("bottom-nav__item")
    })
  })

  it("chaque item contient une icône SVG", () => {
    const { container } = renderWithRouter()
    const svgs = container.querySelectorAll("svg")
    expect(svgs).toHaveLength(5)
  })

  it("chaque item contient un span avec classe bottom-nav__label", () => {
    const { container } = renderWithRouter()
    const labels = container.querySelectorAll(".bottom-nav__label")
    expect(labels).toHaveLength(5)
  })
})

// ─── AC3 : Icônes correctes ──────────────────────────────────────────────────

describe("AC3 : Icônes Lucide (size=24, strokeWidth=1.75)", () => {
  it("les SVG ont strokeWidth=1.75", () => {
    const { container } = renderWithRouter()
    const svgs = container.querySelectorAll("svg")
    svgs.forEach((svg) => {
      // Lucide icons render stroke-width on the <svg> or first child
      const strokeWidth =
        svg.getAttribute("stroke-width") ??
        svg.querySelector("[stroke-width]")?.getAttribute("stroke-width")
      expect(strokeWidth).toBe("1.75")
    })
  })

  it("les SVG ont width=24 et height=24", () => {
    const { container } = renderWithRouter()
    const svgs = container.querySelectorAll("svg")
    svgs.forEach((svg) => {
      expect(svg).toHaveAttribute("width", "24")
      expect(svg).toHaveAttribute("height", "24")
    })
  })
})

// ─── AC4 : État actif ────────────────────────────────────────────────────────

describe("AC4 : État actif détecté via la route courante", () => {
  it("marque 'Aujourd'hui' actif sur /dashboard", () => {
    renderWithRouter("/dashboard")
    const link = screen.getByText("Aujourd'hui").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
    expect(link).toHaveAttribute("aria-current", "page")
  })

  it("ne marque pas 'Aujourd'hui' actif sur /chat", () => {
    renderWithRouter("/chat")
    const link = screen.getByText("Aujourd'hui").closest("a")!
    expect(link).not.toHaveClass("bottom-nav__item--active")
    expect(link).not.toHaveAttribute("aria-current")
  })

  it("marque 'Chat' actif sur /chat", () => {
    renderWithRouter("/chat")
    const link = screen.getByText("Chat").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
    expect(link).toHaveAttribute("aria-current", "page")
  })

  it("marque 'Chat' actif sur /chat/123 (sous-route)", () => {
    renderWithRouter("/chat/123")
    const link = screen.getByText("Chat").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
  })

  it("marque 'Thème' actif sur /natal", () => {
    renderWithRouter("/natal")
    const link = screen.getByText("Thème").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
  })

  it("marque 'Tirages' actif sur /consultations", () => {
    renderWithRouter("/consultations")
    const link = screen.getByText("Tirages").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
  })

  it("marque 'Profil' actif sur /settings/account", () => {
    renderWithRouter("/settings/account")
    const link = screen.getByText("Profil").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
    expect(link).toHaveAttribute("aria-current", "page")
  })

  it("marque 'Profil' actif sur /settings/subscription (sous-page)", () => {
    renderWithRouter("/settings/subscription")
    const link = screen.getByText("Profil").closest("a")!
    expect(link).toHaveClass("bottom-nav__item--active")
  })

  it("n'a qu'un seul item actif à la fois sur /dashboard", () => {
    renderWithRouter("/dashboard")
    const activeLinks = screen
      .getAllByRole("link")
      .filter((l) => l.classList.contains("bottom-nav__item--active"))
    expect(activeLinks).toHaveLength(1)
  })
})

// ─── AC5 : Navigation fonctionnelle ──────────────────────────────────────────

describe("AC5 : Les liens pointent vers les bonnes routes", () => {
  it("'Aujourd'hui' pointe vers /dashboard", () => {
    renderWithRouter()
    expect(screen.getByText("Aujourd'hui").closest("a")).toHaveAttribute("href", "/dashboard")
  })

  it("'Chat' pointe vers /chat", () => {
    renderWithRouter()
    expect(screen.getByText("Chat").closest("a")).toHaveAttribute("href", "/chat")
  })

  it("'Thème' pointe vers /natal", () => {
    renderWithRouter()
    expect(screen.getByText("Thème").closest("a")).toHaveAttribute("href", "/natal")
  })

  it("'Tirages' pointe vers /consultations", () => {
    renderWithRouter()
    expect(screen.getByText("Tirages").closest("a")).toHaveAttribute("href", "/consultations")
  })

  it("'Profil' pointe vers /settings", () => {
    renderWithRouter()
    expect(screen.getByText("Profil").closest("a")).toHaveAttribute("href", "/settings")
  })
})

// ─── Structure et accessibilité ───────────────────────────────────────────────

describe("Structure et accessibilité", () => {
  it("rend un <nav> avec aria-label='Navigation principale'", () => {
    renderWithRouter()
    const nav = screen.getByRole("navigation", { name: "Navigation principale" })
    expect(nav).toHaveClass("bottom-nav")
  })

  it("les items inactifs n'ont pas d'aria-current", () => {
    renderWithRouter("/dashboard")
    const chatLink = screen.getByText("Chat").closest("a")!
    expect(chatLink).not.toHaveAttribute("aria-current")
  })
})
