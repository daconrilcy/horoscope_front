// Tests DOM de la landing pour verrouiller le rendu, les CTA et l'owner SEO/head.
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { LandingPage } from "../pages/landing/LandingPage"
import { LandingNavbar } from "../pages/landing/sections/LandingNavbar"
import { routerFutureFlags } from "./test-utils"

const originalTitle = document.title
const { trackMock } = vi.hoisted(() => ({
  trackMock: vi.fn(),
}))

vi.mock("../hooks/useAnalytics", () => ({
  getUtmParams: () => ({ utm_source: "test" }),
  useAnalytics: () => ({
    track: trackMock,
  }),
}))

function renderLandingPage() {
  return render(
    <MemoryRouter initialEntries={["/?utm_source=test"]} future={routerFutureFlags}>
      <LandingPage />
    </MemoryRouter>,
  )
}

function renderLandingNavbar() {
  return render(
    <MemoryRouter initialEntries={["/"]} future={routerFutureFlags}>
      <LandingNavbar />
    </MemoryRouter>,
  )
}

function metaByProperty(property: string) {
  return document.querySelector<HTMLMetaElement>(`meta[property="${property}"]`)
}

function jsonScript(id: string) {
  return document.getElementById(id) as HTMLScriptElement | null
}

beforeEach(() => {
  trackMock.mockClear()
})

afterEach(() => {
  document.title = originalTitle
  document.head.querySelector('meta[name="description"]')?.remove()
  document.head.querySelectorAll("meta[property]").forEach((element) => element.remove())
  document.head.querySelector('link[rel="canonical"]')?.remove()
  document.getElementById("json-ld-app")?.remove()
  document.getElementById("json-ld-faq")?.remove()
})

describe("LandingPage", () => {
  it("rend la composition landing et les CTA analytics sans boucle runtime", () => {
    renderLandingPage()

    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument()
    expect(screen.getAllByRole("link", { name: /démarrer gratuitement/i })[0]).toHaveAttribute("href", "/register")
    expect(screen.getByRole("link", { name: /découvrir comment ça marche/i })).toHaveAttribute(
      "href",
      "#how-it-works",
    )
  })

  it("expose un H1 accessible avec separateur sans dupliquer le titre principal", () => {
    renderLandingPage()

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1)
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "Votre guide astrologique personnel - Toujours disponible",
      }),
    ).toBeInTheDocument()
  })

  it("confine le focus dans le menu mobile, bloque le scroll et restaure le bouton", async () => {
    const user = userEvent.setup()
    const { container } = renderLandingNavbar()
    const menuButton = screen.getByRole("button", { name: /ouvrir le menu/i })

    await user.click(menuButton)

    const menu = await screen.findByRole("dialog", { name: /menu mobile/i })
    const focusableControls = Array.from(
      menu.querySelectorAll<HTMLElement>("a[href], button:not([disabled])"),
    )

    expect(document.body.style.overflow).toBe("hidden")
    await waitFor(() => expect(menu).toContainElement(document.activeElement as HTMLElement))
    expect(focusableControls.length).toBeGreaterThan(2)

    focusableControls[focusableControls.length - 1].focus()
    await user.tab()
    expect(document.activeElement).toBe(focusableControls[0])

    await user.tab({ shift: true })
    expect(document.activeElement).toBe(focusableControls[focusableControls.length - 1])

    await user.keyboard("{Escape}")

    expect(container.querySelector("#landing-mobile-menu")).not.toBeInTheDocument()
    expect(document.body.style.overflow).toBe("")
    await waitFor(() => expect(menuButton).toHaveFocus())
  })

  it("envoie les evenements analytics quand les CTA hero sont cliques", async () => {
    const user = userEvent.setup()
    renderLandingPage()
    trackMock.mockClear()

    await user.click(screen.getAllByRole("link", { name: /démarrer gratuitement/i })[0])
    await user.click(screen.getByRole("link", { name: /découvrir comment ça marche/i }))

    expect(trackMock).toHaveBeenCalledWith("hero_cta_click", { cta_label: "Démarrer gratuitement" })
    expect(trackMock).toHaveBeenCalledWith("secondary_cta_click", { cta_label: "Découvrir comment ça marche" })
  })

  it("pose les tags SEO, Open Graph, canonical et JSON-LD", () => {
    renderLandingPage()

    expect(document.title).toContain("Astrorizon")
    expect(document.querySelector('meta[name="description"]')?.getAttribute("content")).toContain("astrologue")
    expect(metaByProperty("og:title")?.getAttribute("content")).toContain("Astrorizon")
    expect(metaByProperty("og:description")?.getAttribute("content")).toContain("astrologique")
    expect(metaByProperty("og:type")?.getAttribute("content")).toBe("website")
    expect(metaByProperty("og:url")?.getAttribute("content")).toContain("localhost")
    expect(document.querySelector('link[rel="canonical"]')?.getAttribute("href")).toBe("https://astrorizon.ai/")
    expect(JSON.parse(jsonScript("json-ld-app")?.text ?? "{}")).toMatchObject({
      "@type": "SoftwareApplication",
      name: "Astrorizon",
    })
    expect(JSON.parse(jsonScript("json-ld-faq")?.text ?? "{}")).toMatchObject({
      "@type": "FAQPage",
    })
  })

  it("met a jour les tags preexistants puis les restaure au demontage", () => {
    document.title = "Titre initial"
    const description = document.createElement("meta")
    description.name = "description"
    description.content = "Description initiale"
    document.head.appendChild(description)

    const canonical = document.createElement("link")
    canonical.rel = "canonical"
    canonical.href = "https://example.test/original"
    document.head.appendChild(canonical)

    const ogTitle = document.createElement("meta")
    ogTitle.setAttribute("property", "og:title")
    ogTitle.content = "OG initial"
    document.head.appendChild(ogTitle)

    const appScript = document.createElement("script")
    appScript.type = "application/ld+json"
    appScript.id = "json-ld-app"
    appScript.text = JSON.stringify({ original: true })
    document.head.appendChild(appScript)

    const { unmount } = renderLandingPage()

    expect(document.title).not.toBe("Titre initial")
    expect(description.getAttribute("content")).not.toBe("Description initiale")
    expect(canonical.getAttribute("href")).toBe("https://astrorizon.ai/")
    expect(ogTitle.getAttribute("content")).not.toBe("OG initial")
    expect(JSON.parse(appScript.text)).toMatchObject({ "@type": "SoftwareApplication" })

    unmount()

    expect(document.title).toBe("Titre initial")
    expect(description.getAttribute("content")).toBe("Description initiale")
    expect(canonical.getAttribute("href")).toBe("https://example.test/original")
    expect(ogTitle.getAttribute("content")).toBe("OG initial")
    expect(JSON.parse(appScript.text)).toEqual({ original: true })
  })

  it("supprime les tags crees par la landing au demontage", () => {
    const { unmount } = renderLandingPage()

    expect(jsonScript("json-ld-app")).toBeInTheDocument()
    expect(jsonScript("json-ld-faq")).toBeInTheDocument()

    unmount()

    expect(document.querySelector('meta[name="description"]')).not.toBeInTheDocument()
    expect(metaByProperty("og:title")).not.toBeInTheDocument()
    expect(document.querySelector('link[rel="canonical"]')).not.toBeInTheDocument()
    expect(jsonScript("json-ld-app")).not.toBeInTheDocument()
    expect(jsonScript("json-ld-faq")).not.toBeInTheDocument()
  })
})
