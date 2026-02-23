import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  translateSign,
  translatePlanet,
  translateHouse,
  translateAspect,
  useAstrologyLabels,
  detectLang,
} from "../i18n/astrology"

const ALL_SIGNS = [
  ["aries", "Bélier", "Aries", "Aries"],
  ["taurus", "Taureau", "Taurus", "Tauro"],
  ["gemini", "Gémeaux", "Gemini", "Géminis"],
  ["cancer", "Cancer", "Cancer", "Cáncer"],
  ["leo", "Lion", "Leo", "Leo"],
  ["virgo", "Vierge", "Virgo", "Virgo"],
  ["libra", "Balance", "Libra", "Libra"],
  ["scorpio", "Scorpion", "Scorpio", "Escorpio"],
  ["sagittarius", "Sagittaire", "Sagittarius", "Sagitario"],
  ["capricorn", "Capricorne", "Capricorn", "Capricornio"],
  ["aquarius", "Verseau", "Aquarius", "Acuario"],
  ["pisces", "Poissons", "Pisces", "Piscis"],
] as const

describe("translateSign", () => {
  it.each(ALL_SIGNS)("translates %s correctly in FR/EN/ES", (code, fr, en, es) => {
    expect(translateSign(code, "fr")).toBe(fr)
    expect(translateSign(code, "en")).toBe(en)
    expect(translateSign(code, "es")).toBe(es)
  })

  it("handles uppercase codes (case-insensitive)", () => {
    expect(translateSign("ARIES", "fr")).toBe("Bélier")
    expect(translateSign("GEMINI", "en")).toBe("Gemini")
  })

  it("returns raw code as fallback for unknown sign", () => {
    expect(translateSign("unknown_sign", "fr")).toBe("unknown_sign")
  })
})

const ALL_PLANETS = [
  ["sun", "Soleil", "Sun", "Sol"],
  ["moon", "Lune", "Moon", "Luna"],
  ["mercury", "Mercure", "Mercury", "Mercurio"],
  ["venus", "Vénus", "Venus", "Venus"],
  ["mars", "Mars", "Mars", "Marte"],
  ["jupiter", "Jupiter", "Jupiter", "Júpiter"],
  ["saturn", "Saturne", "Saturn", "Saturno"],
  ["uranus", "Uranus", "Uranus", "Urano"],
  ["neptune", "Neptune", "Neptune", "Neptuno"],
  ["pluto", "Pluton", "Pluto", "Plutón"],
] as const

describe("translatePlanet", () => {
  it.each(ALL_PLANETS)("translates %s correctly in FR/EN/ES", (code, fr, en, es) => {
    expect(translatePlanet(code, "fr")).toBe(fr)
    expect(translatePlanet(code, "en")).toBe(en)
    expect(translatePlanet(code, "es")).toBe(es)
  })

  it("handles uppercase codes (case-insensitive)", () => {
    expect(translatePlanet("SUN", "fr")).toBe("Soleil")
    expect(translatePlanet("MOON", "en")).toBe("Moon")
  })

  it("returns raw code as fallback for unknown planet", () => {
    expect(translatePlanet("chiron", "fr")).toBe("chiron")
  })
})

const ALL_HOUSES = [
  [1, "Maison I — Identité", "House I — Identity", "Casa I — Identidad"],
  [2, "Maison II — Valeurs", "House II — Values", "Casa II — Valores"],
  [3, "Maison III — Communication", "House III — Communication", "Casa III — Comunicación"],
  [4, "Maison IV — Foyer", "House IV — Home", "Casa IV — Hogar"],
  [5, "Maison V — Créativité", "House V — Creativity", "Casa V — Creatividad"],
  [6, "Maison VI — Santé", "House VI — Health", "Casa VI — Salud"],
  [7, "Maison VII — Relations", "House VII — Relationships", "Casa VII — Relaciones"],
  [8, "Maison VIII — Transformation", "House VIII — Transformation", "Casa VIII — Transformación"],
  [9, "Maison IX — Philosophie", "House IX — Philosophy", "Casa IX — Filosofía"],
  [10, "Maison X — Carrière", "House X — Career", "Casa X — Carrera"],
  [11, "Maison XI — Communauté", "House XI — Community", "Casa XI — Comunidad"],
  [12, "Maison XII — Inconscient", "House XII — Unconscious", "Casa XII — Inconsciente"],
] as const

describe("translateHouse", () => {
  it.each(ALL_HOUSES)("translates house %i correctly in FR/EN/ES", (num, fr, en, es) => {
    expect(translateHouse(num, "fr")).toBe(fr)
    expect(translateHouse(num, "en")).toBe(en)
    expect(translateHouse(num, "es")).toBe(es)
  })

  it.each([
    [13, "fr", "Maison 13"],
    [99, "en", "House 99"],
    [14, "es", "Casa 14"],
    [0, "fr", "Maison 0"],
  ] as const)("returns fallback for house %i in %s", (num, lang, expected) => {
    expect(translateHouse(num, lang)).toBe(expected)
  })
})

const ALL_ASPECTS = [
  ["conjunction", "Conjonction", "Conjunction", "Conjunción"],
  ["sextile", "Sextile", "Sextile", "Sextil"],
  ["square", "Carré", "Square", "Cuadratura"],
  ["trine", "Trigone", "Trine", "Trígono"],
  ["opposition", "Opposition", "Opposition", "Oposición"],
  ["semisextile", "Semi-sextile", "Semi-sextile", "Semisextil"],
  ["quincunx", "Quinconce", "Quincunx", "Quincuncio"],
  ["semisquare", "Semi-carré", "Semi-square", "Semicuadratura"],
  ["sesquiquadrate", "Sesqui-carré", "Sesquiquadrate", "Sesquicuadratura"],
] as const

describe("translateAspect", () => {
  it.each(ALL_ASPECTS)("translates %s correctly in FR/EN/ES", (code, fr, en, es) => {
    expect(translateAspect(code, "fr")).toBe(fr)
    expect(translateAspect(code, "en")).toBe(en)
    expect(translateAspect(code, "es")).toBe(es)
  })

  it("handles uppercase codes (case-insensitive)", () => {
    expect(translateAspect("TRINE", "fr")).toBe("Trigone")
    expect(translateAspect("SQUARE", "en")).toBe("Square")
  })

  it("returns raw code as fallback for unknown aspect", () => {
    expect(translateAspect("unknown", "fr")).toBe("unknown")
  })
})

describe("detectLang", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("returns French when navigator.language is fr-FR", () => {
    vi.stubGlobal("navigator", { language: "fr-FR" })
    expect(detectLang()).toBe("fr")
  })

  it("returns English when navigator.language is en-US", () => {
    vi.stubGlobal("navigator", { language: "en-US" })
    expect(detectLang()).toBe("en")
  })

  it("returns Spanish when navigator.language is es-ES", () => {
    vi.stubGlobal("navigator", { language: "es-ES" })
    expect(detectLang()).toBe("es")
  })

  it("falls back to French for unsupported language", () => {
    vi.stubGlobal("navigator", { language: "de-DE" })
    expect(detectLang()).toBe("fr")
  })

  it("prefers localStorage lang over navigator.language", () => {
    vi.stubGlobal("navigator", { language: "en-US" })
    localStorage.setItem("lang", "es")
    expect(detectLang()).toBe("es")
  })

  it("ignores invalid localStorage lang and uses navigator", () => {
    vi.stubGlobal("navigator", { language: "en-US" })
    localStorage.setItem("lang", "invalid")
    expect(detectLang()).toBe("en")
  })

  it("falls back to French when navigator.language is empty string", () => {
    vi.stubGlobal("navigator", { language: "" })
    expect(detectLang()).toBe("fr")
  })

  it("falls back to French when navigator.language is undefined", () => {
    vi.stubGlobal("navigator", { language: undefined })
    expect(detectLang()).toBe("fr")
  })

  it("falls back to French when navigator is undefined", () => {
    vi.stubGlobal("navigator", undefined)
    expect(detectLang()).toBe("fr")
  })
})

describe("useAstrologyLabels", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubGlobal("navigator", { language: "fr-FR" })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("returns current language from detectLang", () => {
    const { result } = renderHook(() => useAstrologyLabels())
    expect(result.current.lang).toBe("fr")
  })

  it("returns bound translation functions that work without lang parameter", () => {
    const { result } = renderHook(() => useAstrologyLabels())
    expect(result.current.translateSign("aries")).toBe("Bélier")
    expect(result.current.translatePlanet("sun")).toBe("Soleil")
    expect(result.current.translateHouse(1)).toBe("Maison I — Identité")
    expect(result.current.translateAspect("trine")).toBe("Trigone")
  })

  it("exposes setLang to change language programmatically", () => {
    const { result } = renderHook(() => useAstrologyLabels())
    expect(result.current.lang).toBe("fr")
    
    act(() => {
      result.current.setLang("es")
    })
    
    expect(result.current.lang).toBe("es")
    expect(result.current.translateSign("aries")).toBe("Aries")
  })

  it("setLang persists the new language to localStorage", () => {
    const { result } = renderHook(() => useAstrologyLabels())
    expect(localStorage.getItem("lang")).toBeNull()
    
    act(() => {
      result.current.setLang("en")
    })
    
    expect(localStorage.getItem("lang")).toBe("en")
    expect(result.current.lang).toBe("en")
  })

  it("updates lang when localStorage changes in another tab (storage event)", () => {
    const { result } = renderHook(() => useAstrologyLabels())
    expect(result.current.lang).toBe("fr")

    act(() => {
      localStorage.setItem("lang", "en")
      window.dispatchEvent(new StorageEvent("storage", { key: "lang", newValue: "en" }))
    })

    expect(result.current.lang).toBe("en")
    expect(result.current.translatePlanet("sun")).toBe("Sun")
  })

  it("ignores storage events for other keys", () => {
    const { result } = renderHook(() => useAstrologyLabels())
    expect(result.current.lang).toBe("fr")

    act(() => {
      window.dispatchEvent(new StorageEvent("storage", { key: "other", newValue: "value" }))
    })

    expect(result.current.lang).toBe("fr")
  })

  it("cleans up storage event listener on unmount", () => {
    const removeEventListenerSpy = vi.spyOn(window, "removeEventListener")
    const { unmount } = renderHook(() => useAstrologyLabels())
    
    unmount()
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith("storage", expect.any(Function))
    removeEventListenerSpy.mockRestore()
  })
})
