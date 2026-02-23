import { useCallback, useEffect, useState } from "react"

/** Langues supportées pour la traduction astrologique */
export type AstrologyLang = "fr" | "en" | "es"

/** Préfixes de fallback pour les maisons non répertoriées, par langue */
const HOUSE_FALLBACK_PREFIX: Record<AstrologyLang, string> = {
  fr: "Maison",
  en: "House",
  es: "Casa",
}

export type GeocodingMessageKey = "loading" | "success" | "error_not_found" | "error_unavailable"

export const GEOCODING_MESSAGES: Record<GeocodingMessageKey, Record<AstrologyLang, string>> = {
  loading: {
    fr: "Géolocalisation en cours...",
    en: "Geocoding in progress...",
    es: "Geolocalización en curso...",
  },
  success: {
    fr: "Lieu résolu",
    en: "Location resolved",
    es: "Ubicación resuelta",
  },
  error_not_found: {
    fr: "Ville ou pays introuvable. Vérifiez l'orthographe. Le thème sera calculé en mode dégradé (maisons égales).",
    en: "City or country not found. Check spelling. Chart will be calculated in degraded mode (equal houses).",
    es: "Ciudad o país no encontrado. Verifique la ortografía. El tema se calculará en modo degradado (casas iguales).",
  },
  error_unavailable: {
    fr: "Service de géolocalisation temporairement indisponible. Le thème sera calculé en mode dégradé (maisons égales).",
    en: "Geocoding service temporarily unavailable. Chart will be calculated in degraded mode (equal houses).",
    es: "Servicio de geolocalización temporalmente no disponible. El tema se calculará en modo degradado (casas iguales).",
  },
}

export type DegradedModeMessageKey = "no_location" | "no_time"

export const DEGRADED_MODE_MESSAGES: Record<DegradedModeMessageKey, Record<AstrologyLang, string>> = {
  no_location: {
    fr: "Thème calculé en maisons égales — lieu de naissance non renseigné ou non trouvé. Pour un calcul précis, renseignez votre ville et pays dans votre profil.",
    en: "Chart calculated with equal houses — birth location not provided or not found. For accurate calculation, enter your city and country in your profile.",
    es: "Tema calculado con casas iguales — lugar de nacimiento no proporcionado o no encontrado. Para un cálculo preciso, ingrese su ciudad y país en su perfil.",
  },
  no_time: {
    fr: "Thème calculé en thème solaire — heure de naissance non renseignée. Les positions des maisons et de la Lune peuvent être inexactes.",
    en: "Chart calculated as solar chart — birth time not provided. House and Moon positions may be inaccurate.",
    es: "Tema calculado como tema solar — hora de nacimiento no proporcionada. Las posiciones de las casas y la Luna pueden ser inexactas.",
  },
}

export type TimezoneSelectMessageKey = "placeholder" | "no_results" | "hint"

export const TIMEZONE_SELECT_MESSAGES: Record<TimezoneSelectMessageKey, Record<AstrologyLang, string>> = {
  placeholder: {
    fr: "Rechercher un fuseau horaire...",
    en: "Search for a timezone...",
    es: "Buscar zona horaria...",
  },
  no_results: {
    fr: "Aucun fuseau horaire trouvé",
    en: "No timezone found",
    es: "No se encontró zona horaria",
  },
  hint: {
    fr: "Tapez pour filtrer",
    en: "Type to filter",
    es: "Escriba para filtrar",
  },
}

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
  semisextile: { fr: "Semi-sextile", en: "Semi-sextile", es: "Semisextil" },
  quincunx: { fr: "Quinconce", en: "Quincunx", es: "Quincuncio" },
  semisquare: { fr: "Semi-carré", en: "Semi-square", es: "Semicuadratura" },
  sesquiquadrate: { fr: "Sesqui-carré", en: "Sesquiquadrate", es: "Sesquicuadratura" },
}

/** Liste des langues supportées pour validation */
export const SUPPORTED_LANGS: AstrologyLang[] = ["fr", "en", "es"]

/**
 * Traduit un code de signe zodiacal vers la langue spécifiée.
 * @param code - Code du signe (ex: "aries", "GEMINI") - case-insensitive
 * @param lang - Langue cible
 * @returns Traduction ou code brut si non trouvé (fallback AC3)
 */
export function translateSign(code: string, lang: AstrologyLang): string {
  const entry = SIGNS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

/**
 * Traduit un code de planète vers la langue spécifiée.
 * @param code - Code de la planète (ex: "sun", "MOON") - case-insensitive
 * @param lang - Langue cible
 * @returns Traduction ou code brut si non trouvé (fallback AC3)
 */
export function translatePlanet(code: string, lang: AstrologyLang): string {
  const entry = PLANETS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

/**
 * Traduit un numéro de maison vers son nom symbolique.
 * @param number - Numéro de la maison (1-12)
 * @param lang - Langue cible
 * @returns Nom complet (ex: "Maison I — Identité") ou fallback "Maison N" si hors range
 */
export function translateHouse(number: number, lang: AstrologyLang): string {
  const entry = HOUSES[number]
  if (!entry) {
    return `${HOUSE_FALLBACK_PREFIX[lang]} ${number}`
  }
  return entry[lang]
}

/**
 * Traduit un code d'aspect vers la langue spécifiée.
 * @param code - Code de l'aspect (ex: "trine", "CONJUNCTION") - case-insensitive
 * @param lang - Langue cible
 * @returns Traduction ou code brut si non trouvé (fallback AC3)
 */
export function translateAspect(code: string, lang: AstrologyLang): string {
  const entry = ASPECTS[code.toLowerCase()]
  return entry?.[lang] ?? code
}

/**
 * Détecte la langue de l'utilisateur selon la priorité:
 * 1. localStorage.getItem("lang") si valide
 * 2. navigator.language (préfixe 2 lettres) si supporté
 * 3. Fallback sur "fr"
 * 
 * @returns Langue détectée parmi "fr" | "en" | "es", avec "fr" comme fallback par défaut
 * 
 * @usage
 * - Pour les composants simples n'ayant besoin que de la langue: `const lang = detectLang()`
 * - Pour les composants nécessitant les traductions astrologiques: `const { lang, translatePlanet, ... } = useAstrologyLabels()`
 */
export function detectLang(): AstrologyLang {
  const stored = typeof localStorage !== "undefined" ? localStorage.getItem("lang") : null
  if (stored && SUPPORTED_LANGS.includes(stored as AstrologyLang)) {
    return stored as AstrologyLang
  }
  const navLang = typeof navigator !== "undefined" ? navigator.language : null
  if (navLang && navLang.length >= 2) {
    const prefix = navLang.substring(0, 2)
    if (SUPPORTED_LANGS.includes(prefix as AstrologyLang)) {
      return prefix as AstrologyLang
    }
  }
  return "fr"
}

/** Clé localStorage utilisée pour stocker la préférence de langue */
const LANG_STORAGE_KEY = "lang"

/**
 * Hook React pour les labels astrologiques avec réactivité au changement de langue.
 * 
 * Écoute les changements de localStorage (événement "storage") pour mettre à jour
 * automatiquement la langue quand elle est modifiée depuis un autre onglet.
 * 
 * @returns Object avec:
 * - `lang`: langue courante (AstrologyLang)
 * - `setLang`: fonction pour changer la langue (persiste dans localStorage)
 * - `translateSign`, `translatePlanet`, `translateHouse`, `translateAspect`: fonctions de traduction bound (sans paramètre lang)
 * 
 * @example
 * const { translatePlanet, translateSign } = useAstrologyLabels()
 * translatePlanet("sun") // → "Soleil" (si lang = "fr")
 */
export function useAstrologyLabels() {
  const [lang, setLangState] = useState<AstrologyLang>(detectLang)

  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === LANG_STORAGE_KEY) {
        setLangState(detectLang())
      }
    }

    window.addEventListener("storage", handleStorageChange)
    return () => window.removeEventListener("storage", handleStorageChange)
  }, [])

  const setLang = useCallback((newLang: AstrologyLang) => {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(LANG_STORAGE_KEY, newLang)
    }
    setLangState(newLang)
  }, [])

  const boundTranslateSign = useCallback((code: string) => translateSign(code, lang), [lang])
  const boundTranslatePlanet = useCallback((code: string) => translatePlanet(code, lang), [lang])
  const boundTranslateHouse = useCallback((number: number) => translateHouse(number, lang), [lang])
  const boundTranslateAspect = useCallback((code: string) => translateAspect(code, lang), [lang])

  return {
    lang,
    setLang,
    translateSign: boundTranslateSign,
    translatePlanet: boundTranslatePlanet,
    translateHouse: boundTranslateHouse,
    translateAspect: boundTranslateAspect,
  }
}
