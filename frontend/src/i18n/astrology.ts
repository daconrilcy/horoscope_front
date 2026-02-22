export type AstrologyLang = "fr" | "en" | "es"

const SIGNS: Record<string, Record<AstrologyLang, string>> = {
  aries: { fr: "Bélier", en: "Aries", es: "Aries" },
  taurus: { fr: "Taureau", en: "Taurus", es: "Tauro" },
  gemini: { fr: "Gémeaux", en: "Gemini", es: "Géminis" },
  cancer: { fr: "Cancer", en: "Cancer", es: "Cáncer" },
  leo: { fr: "Lion", en: "Leo", es: "Leo" },
  virgo: { fr: "Vierge", en: "Virgo", es: "Virgo" },
  libra: { fr: "Balance", en: "Libra", es: "Libra" },
  scorpio: { fr: "Scorpion", en: "Scorpio", es: "Escorpio" },
  sagittarius: { fr: "Sagittaire", en: "Sagittarius", es: "Sagitario" },
  capricorn: { fr: "Capricorne", en: "Capricorn", es: "Capricornio" },
  aquarius: { fr: "Verseau", en: "Aquarius", es: "Acuario" },
  pisces: { fr: "Poissons", en: "Pisces", es: "Piscis" },
}

const PLANETS: Record<string, Record<AstrologyLang, string>> = {
  sun: { fr: "Soleil", en: "Sun", es: "Sol" },
  moon: { fr: "Lune", en: "Moon", es: "Luna" },
  mercury: { fr: "Mercure", en: "Mercury", es: "Mercurio" },
  venus: { fr: "Vénus", en: "Venus", es: "Venus" },
  mars: { fr: "Mars", en: "Mars", es: "Marte" },
  jupiter: { fr: "Jupiter", en: "Jupiter", es: "Júpiter" },
  saturn: { fr: "Saturne", en: "Saturn", es: "Saturno" },
  uranus: { fr: "Uranus", en: "Uranus", es: "Urano" },
  neptune: { fr: "Neptune", en: "Neptune", es: "Neptuno" },
  pluto: { fr: "Pluton", en: "Pluto", es: "Plutón" },
}

const HOUSES: Record<number, Record<AstrologyLang, string>> = {
  1: { fr: "Maison I — Identité", en: "House I — Identity", es: "Casa I — Identidad" },
  2: { fr: "Maison II — Valeurs", en: "House II — Values", es: "Casa II — Valores" },
  3: { fr: "Maison III — Communication", en: "House III — Communication", es: "Casa III — Comunicación" },
  4: { fr: "Maison IV — Foyer", en: "House IV — Home", es: "Casa IV — Hogar" },
  5: { fr: "Maison V — Créativité", en: "House V — Creativity", es: "Casa V — Creatividad" },
  6: { fr: "Maison VI — Santé", en: "House VI — Health", es: "Casa VI — Salud" },
  7: { fr: "Maison VII — Relations", en: "House VII — Relationships", es: "Casa VII — Relaciones" },
  8: { fr: "Maison VIII — Transformation", en: "House VIII — Transformation", es: "Casa VIII — Transformación" },
  9: { fr: "Maison IX — Philosophie", en: "House IX — Philosophy", es: "Casa IX — Filosofía" },
  10: { fr: "Maison X — Carrière", en: "House X — Career", es: "Casa X — Carrera" },
  11: { fr: "Maison XI — Communauté", en: "House XI — Community", es: "Casa XI — Comunidad" },
  12: { fr: "Maison XII — Inconscient", en: "House XII — Unconscious", es: "Casa XII — Inconsciente" },
}

const ASPECTS: Record<string, Record<AstrologyLang, string>> = {
  conjunction: { fr: "Conjonction", en: "Conjunction", es: "Conjunción" },
  sextile: { fr: "Sextile", en: "Sextile", es: "Sextil" },
  square: { fr: "Carré", en: "Square", es: "Cuadratura" },
  trine: { fr: "Trigone", en: "Trine", es: "Trígono" },
  opposition: { fr: "Opposition", en: "Opposition", es: "Oposición" },
}

export function translateSign(code: string, lang: AstrologyLang): string {
  const entry = SIGNS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

export function translatePlanet(code: string, lang: AstrologyLang): string {
  const entry = PLANETS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

export function translateHouse(number: number, lang: AstrologyLang): string {
  const entry = HOUSES[number]
  if (!entry) {
    const prefix = lang === "en" ? "House" : lang === "es" ? "Casa" : "Maison"
    return `${prefix} ${number}`
  }
  return entry[lang]
}

export function translateAspect(code: string, lang: AstrologyLang): string {
  const entry = ASPECTS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

function detectLang(): AstrologyLang {
  const stored = typeof localStorage !== "undefined" ? localStorage.getItem("lang") : null
  if (stored && ["fr", "en", "es"].includes(stored)) {
    return stored as AstrologyLang
  }
  const nav = typeof navigator !== "undefined" ? navigator.language?.substring(0, 2) : "fr"
  if (["fr", "en", "es"].includes(nav)) {
    return nav as AstrologyLang
  }
  return "fr"
}

export function useAstrologyLabels() {
  const lang = detectLang()
  return {
    lang,
    translateSign,
    translatePlanet,
    translateHouse,
    translateAspect,
  }
}
