import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  translateSign,
  translatePlanet,
  translateHouse,
  translateAspect,
  useAstrologyLabels,
} from "../i18n/astrology"

describe("translateSign", () => {
  it("translates aries to Bélier in French", () => {
    expect(translateSign("aries", "fr")).toBe("Bélier")
  })

  it("translates aries to Aries in English", () => {
    expect(translateSign("aries", "en")).toBe("Aries")
  })

  it("translates aries to Aries in Spanish", () => {
    expect(translateSign("aries", "es")).toBe("Aries")
  })

  it("handles uppercase codes (case-insensitive)", () => {
    expect(translateSign("ARIES", "fr")).toBe("Bélier")
  })

  it("returns raw code as fallback for unknown sign", () => {
    expect(translateSign("unknown_sign", "fr")).toBe("unknown_sign")
  })

  it("translates all 12 signs correctly in French", () => {
    expect(translateSign("taurus", "fr")).toBe("Taureau")
    expect(translateSign("gemini", "fr")).toBe("Gémeaux")
    expect(translateSign("cancer", "fr")).toBe("Cancer")
    expect(translateSign("leo", "fr")).toBe("Lion")
    expect(translateSign("virgo", "fr")).toBe("Vierge")
    expect(translateSign("libra", "fr")).toBe("Balance")
    expect(translateSign("scorpio", "fr")).toBe("Scorpion")
    expect(translateSign("sagittarius", "fr")).toBe("Sagittaire")
    expect(translateSign("capricorn", "fr")).toBe("Capricorne")
    expect(translateSign("aquarius", "fr")).toBe("Verseau")
    expect(translateSign("pisces", "fr")).toBe("Poissons")
  })
})

describe("translatePlanet", () => {
  it("translates sun to Soleil in French", () => {
    expect(translatePlanet("sun", "fr")).toBe("Soleil")
  })

  it("handles uppercase codes (case-insensitive)", () => {
    expect(translatePlanet("SUN", "fr")).toBe("Soleil")
  })

  it("returns raw code as fallback for unknown planet", () => {
    expect(translatePlanet("chiron", "fr")).toBe("chiron")
  })

  it("translates all 10 planets correctly in French", () => {
    expect(translatePlanet("moon", "fr")).toBe("Lune")
    expect(translatePlanet("mercury", "fr")).toBe("Mercure")
    expect(translatePlanet("venus", "fr")).toBe("Vénus")
    expect(translatePlanet("mars", "fr")).toBe("Mars")
    expect(translatePlanet("jupiter", "fr")).toBe("Jupiter")
    expect(translatePlanet("saturn", "fr")).toBe("Saturne")
    expect(translatePlanet("uranus", "fr")).toBe("Uranus")
    expect(translatePlanet("neptune", "fr")).toBe("Neptune")
    expect(translatePlanet("pluto", "fr")).toBe("Pluton")
  })
})

describe("translateHouse", () => {
  it("translates house 1 to Maison I — Identité in French", () => {
    expect(translateHouse(1, "fr")).toBe("Maison I — Identité")
  })

  it("translates house 1 to House I — Identity in English", () => {
    expect(translateHouse(1, "en")).toBe("House I — Identity")
  })

  it("returns fallback format for unknown house number", () => {
    expect(translateHouse(13, "fr")).toBe("Maison 13")
  })

  it("returns English fallback for unknown house number in English", () => {
    expect(translateHouse(99, "en")).toBe("House 99")
  })

  it("returns Spanish fallback for unknown house number in Spanish", () => {
    expect(translateHouse(14, "es")).toBe("Casa 14")
  })

  it("translates all 12 houses correctly in French", () => {
    expect(translateHouse(2, "fr")).toBe("Maison II — Valeurs")
    expect(translateHouse(3, "fr")).toBe("Maison III — Communication")
    expect(translateHouse(4, "fr")).toBe("Maison IV — Foyer")
    expect(translateHouse(5, "fr")).toBe("Maison V — Créativité")
    expect(translateHouse(6, "fr")).toBe("Maison VI — Santé")
    expect(translateHouse(7, "fr")).toBe("Maison VII — Relations")
    expect(translateHouse(8, "fr")).toBe("Maison VIII — Transformation")
    expect(translateHouse(9, "fr")).toBe("Maison IX — Philosophie")
    expect(translateHouse(10, "fr")).toBe("Maison X — Carrière")
    expect(translateHouse(11, "fr")).toBe("Maison XI — Communauté")
    expect(translateHouse(12, "fr")).toBe("Maison XII — Inconscient")
  })
})

describe("translateAspect", () => {
  it("translates conjunction to Conjonction in French", () => {
    expect(translateAspect("conjunction", "fr")).toBe("Conjonction")
  })

  it("handles uppercase codes (case-insensitive)", () => {
    expect(translateAspect("TRINE", "fr")).toBe("Trigone")
  })

  it("returns raw code as fallback for unknown aspect", () => {
    expect(translateAspect("unknown", "fr")).toBe("unknown")
  })

  it("translates all 5 major aspects correctly in French", () => {
    expect(translateAspect("sextile", "fr")).toBe("Sextile")
    expect(translateAspect("square", "fr")).toBe("Carré")
    expect(translateAspect("trine", "fr")).toBe("Trigone")
    expect(translateAspect("opposition", "fr")).toBe("Opposition")
  })
})

describe("useAstrologyLabels", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("returns French when navigator.language is fr-FR", () => {
    vi.stubGlobal("navigator", { language: "fr-FR" })
    const { lang } = useAstrologyLabels()
    expect(lang).toBe("fr")
  })

  it("returns English when navigator.language is en-US", () => {
    vi.stubGlobal("navigator", { language: "en-US" })
    const { lang } = useAstrologyLabels()
    expect(lang).toBe("en")
  })

  it("returns Spanish when navigator.language is es-ES", () => {
    vi.stubGlobal("navigator", { language: "es-ES" })
    const { lang } = useAstrologyLabels()
    expect(lang).toBe("es")
  })

  it("falls back to French for unsupported language", () => {
    vi.stubGlobal("navigator", { language: "de-DE" })
    const { lang } = useAstrologyLabels()
    expect(lang).toBe("fr")
  })

  it("prefers localStorage lang over navigator.language", () => {
    vi.stubGlobal("navigator", { language: "en-US" })
    localStorage.setItem("lang", "es")
    const { lang } = useAstrologyLabels()
    expect(lang).toBe("es")
  })

  it("ignores invalid localStorage lang and uses navigator", () => {
    vi.stubGlobal("navigator", { language: "en-US" })
    localStorage.setItem("lang", "invalid")
    const { lang } = useAstrologyLabels()
    expect(lang).toBe("en")
  })

  it("returns all translation functions", () => {
    vi.stubGlobal("navigator", { language: "fr-FR" })
    const result = useAstrologyLabels()
    expect(result.translateSign).toBe(translateSign)
    expect(result.translatePlanet).toBe(translatePlanet)
    expect(result.translateHouse).toBe(translateHouse)
    expect(result.translateAspect).toBe(translateAspect)
  })
})
