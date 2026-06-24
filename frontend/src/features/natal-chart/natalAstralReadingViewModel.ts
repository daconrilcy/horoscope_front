// Normalisation des contrats d'interpretation natale Astral pour l'affichage public.
import type { AstralJobResponse, AstralPlan } from "../../api/astral"
import { normalizeSignCode, translateAspect, translateHouse, translatePlanet, translateSign } from "../../i18n/astrology"
import { normalizeDisplayText } from "../../utils/strings"

export type NatalReadingTier = "free" | "basic" | "premium" | "unknown"
export type NatalReadingVariant = "full" | "simplified" | "unknown"
export type NatalReadingCompleteness = "completed" | "partial" | "unknown"
export type NatalReadingStatus = "success" | "empty" | "failed" | "safety_rejected"

export type NatalReadingChapterViewModel = {
  code: string | null
  title: string
  paragraphs: string[]
  confidenceLabel: string | null
  astroBasis: string[]
  safetyFlags: string[]
}

export type NatalCalculationFactItemViewModel = {
  label: string
  value: string
  detail: string | null
}

export type NatalCalculationFactGroupViewModel = {
  title: string
  items: NatalCalculationFactItemViewModel[]
}

export type NatalCalculationFactsViewModel = {
  groups: NatalCalculationFactGroupViewModel[]
  sourceLabel: string
}

export type NatalReadingSummaryViewModel = {
  text: string
  highlights: string[]
}

export type NatalReadingPillarViewModel = {
  code: "sun" | "moon" | "ascendant"
  icon: string
  title: string
  description: string
  lifeArea: string | null
}

export type NatalReadingAxisViewModel = {
  code: "relationship_axis" | "public_private_axis"
  label: string
  title: string
  description: string
}

export type NatalReadingLifeAreaViewModel = {
  rank: string
  title: string
  description: string
  details: string[]
}

export type NatalReadingOtherForceViewModel = {
  title: string
  functionLabel: string
  description: string
  lifeArea: string | null
}

export type NatalReadingAspectViewModel = {
  badge: string
  title: string
  description: string
  details: Array<{ label: string; value: string }>
}

export type NatalCalculationReadingViewModel = {
  summary: NatalReadingSummaryViewModel | null
  pillars: NatalReadingPillarViewModel[]
  axes: NatalReadingAxisViewModel[]
  lifeAreas: NatalReadingLifeAreaViewModel[]
  otherForces: NatalReadingOtherForceViewModel[]
  aspects: NatalReadingAspectViewModel[]
  technicalGroups: NatalCalculationFactGroupViewModel[]
}

export type NatalInterpretationViewModel = {
  status: NatalReadingStatus
  title: string
  shortText: string | null
  tier: NatalReadingTier
  variant: NatalReadingVariant
  label: string
  completeness: NatalReadingCompleteness
  isPartial: boolean
  chapters: NatalReadingChapterViewModel[]
  calculationReading: NatalCalculationReadingViewModel | null
  calculationFacts: NatalCalculationFactsViewModel | null
  disclaimer: string | null
  error: {
    code: string | null
    message: string
    ruleId: string | null
  } | null
}

type ReadingMetadata = {
  tier: NatalReadingTier
  variant: NatalReadingVariant
  completeness: NatalReadingCompleteness
}

const DEFAULT_ERROR_MESSAGE = "La lecture Astral n'a pas pu etre affichee."
const CORE_OBJECT_ORDER = ["sun", "moon", "ascendant", "descendant", "midheaven", "mc"] as const
const NOTABLE_PLACEMENT_ORDER = [
  "mercury",
  "venus",
  "mars",
  "jupiter",
  "saturn",
  "uranus",
  "neptune",
  "pluto",
] as const
const PUBLIC_ASPECT_OBJECT_ORDER = [
  "sun",
  "moon",
  ...NOTABLE_PLACEMENT_ORDER,
  "north_node",
  "south_node",
] as const
const MAX_NOTABLE_PLACEMENTS = 6
const MAX_MAJOR_ASPECTS = 5
const MAX_PUBLIC_READING_ASPECTS = 1
const TECHNICAL_DETAIL_SEPARATOR = " - "
const PUBLIC_OBJECT_LABELS: Record<string, string> = {
  ascendant: "Ascendant",
  descendant: "Descendant",
  midheaven: "Milieu du Ciel",
  mc: "Milieu du Ciel",
  imum_coeli: "Fond du Ciel",
  ic: "Fond du Ciel",
}

const PILLAR_COPY: Record<"sun" | "moon" | "ascendant", { icon: string; description: string }> = {
  sun: {
    icon: "☉",
    description: "Une identite {signTone}, qui cherche a se construire dans {houseContext}.",
  },
  moon: {
    icon: "☽",
    description: "Une vie interieure {signTone}, avec des besoins emotionnels qui s'expriment dans {houseContext}.",
  },
  ascendant: {
    icon: "ASC",
    description: "Une maniere d'aborder le monde {signTone}, visible dans la premiere impression donnee.",
  },
}

const FORCE_COPY: Record<string, { functionLabel: string; description: string }> = {
  mercury: {
    functionLabel: "Communication",
    description: "{object} en {sign} indique une pensee {signTone}, qui peut s'exprimer dans {houseContext}.",
  },
  venus: {
    functionLabel: "Valeurs et attachement",
    description: "{object} en {sign} indique une maniere d'aimer et de choisir {signTone}, visible dans {houseContext}.",
  },
  mars: {
    functionLabel: "Action",
    description: "{object} en {sign} indique une energie d'action {signTone}, mobilisee dans {houseContext}.",
  },
  jupiter: {
    functionLabel: "Expansion",
    description: "{object} en {sign} indique une croissance {signTone}, qui peut se developper dans {houseContext}.",
  },
  saturn: {
    functionLabel: "Structure",
    description: "{object} en {sign} indique une construction {signTone}, qui demande de la maturite dans {houseContext}.",
  },
  uranus: {
    functionLabel: "Originalite",
    description: "{object} en {sign} indique une originalite {signTone}, qui bouscule les habitudes dans {houseContext}.",
  },
  neptune: {
    functionLabel: "Imaginaire",
    description: "{object} en {sign} indique une sensibilite {signTone}, qui inspire {houseContext}.",
  },
  pluto: {
    functionLabel: "Transformation",
    description: "{object} en {sign} indique une intensite {signTone}, qui transforme {houseContext}.",
  },
}

const HOUSE_THEME_LABELS: Record<string, string> = {
  career: "Carriere",
  home: "Foyer",
  resources: "Valeurs",
  relationships: "Relations",
  transformation: "Transformation",
  communication: "Communication",
  creativity: "Creativite",
  community: "Communaute",
  philosophy: "Philosophie",
  unconscious: "Inconscient",
}

const HOUSE_CONTEXT_LABELS: Record<number, string> = {
  1: "l'identite et l'image personnelle",
  2: "les valeurs, la securite et les ressources",
  3: "la communication et les apprentissages",
  4: "le foyer, les racines et la vie intime",
  5: "la creativite et l'expression personnelle",
  6: "les routines, le travail quotidien et l'hygiene de vie",
  7: "les relations et les engagements",
  8: "les transformations et les ressources partagees",
  9: "la vision du monde et les apprentissages profonds",
  10: "la carriere, l'ambition et la place sociale",
  11: "les groupes, les projets collectifs et la communaute",
  12: "la vie interieure, le retrait et l'inconscient",
}

const SIGN_TONE_LABELS: Record<string, string> = {
  aries: "directe, volontaire et reactive",
  taurus: "stable, concrete et patiente",
  gemini: "curieuse, mobile et adaptable",
  cancer: "sensible, prudente et protectrice",
  leo: "expressive, fiere et creative",
  virgo: "precise, utile et attentive aux details",
  libra: "relationnelle, harmonieuse et attentive a l'equilibre",
  scorpio: "intense, profonde et selective",
  sagittarius: "ouverte, franche et orientee vers l'exploration",
  capricorn: "structuree, responsable et exigeante",
  aquarius: "independante, originale et tournee vers les idees",
  pisces: "intuitive, permeable et imaginative",
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

function asText(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? normalizeDisplayText(value.trim()) : null
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null
}

function asTextArray(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.map(asText).filter((item): item is string => Boolean(item))
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null
}

function normalizeCode(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, "_")
}

function formatDegree(value: unknown): string | null {
  const degree = asNumber(value)
  return degree === null ? null : `${degree.toFixed(2)}°`
}

function formatHouse(value: unknown): string | null {
  const number = asNumber(value)
  if (number === null) return null
  return translateHouse(number, "fr")
}

function formatSign(value: unknown): string | null {
  const sign = asText(value)
  return sign ? translateSign(sign, "fr") : null
}

function formatObject(value: unknown): string | null {
  const object = asText(value)
  if (!object) return null
  const code = normalizeCode(object)
  return PUBLIC_OBJECT_LABELS[code] ?? translatePlanet(code, "fr")
}

function joinDetails(values: Array<string | null>): string | null {
  const details = values.filter((item): item is string => Boolean(item))
  return details.length > 0 ? details.join(TECHNICAL_DETAIL_SEPARATOR) : null
}

function objectCodeFromLabel(value: unknown): string | null {
  const text = asText(value)
  return text ? normalizeCode(text) : null
}

function roleLabel(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (text === "core") return "central"
  if (text === "supporting") return "appui"
  if (text === "nuance") return "nuance"
  return null
}

function astroBasisLabel(value: unknown): string | null {
  const directText = asText(value)
  if (directText) return directText

  const basis = asRecord(value)
  const label = asText(basis?.label) ?? asText(basis?.factor)
  if (!label) return null

  const role = roleLabel(basis?.interpretive_role)
  return role ? `${label} (${role})` : label
}

function asAstroBasisLabels(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.map(astroBasisLabel).filter((item): item is string => Boolean(item))
}

function asTier(value: unknown, fallbackPlan?: AstralPlan): NatalReadingTier {
  const text = asText(value)?.toLowerCase()
  if (text === "free" || text === "basic" || text === "premium") return text
  return fallbackPlan ?? "unknown"
}

function asVariant(value: unknown): NatalReadingVariant {
  const text = asText(value)?.toLowerCase()
  if (text === "full" || text === "simplified") return text
  return "unknown"
}

function asCompleteness(value: unknown): NatalReadingCompleteness {
  const text = asText(value)?.toLowerCase()
  if (text === "completed" || text === "complete") return "completed"
  if (text === "partial") return "partial"
  return "unknown"
}

function labelForReading(tier: NatalReadingTier): string {
  return tier
}

function confidenceLabel(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (text === "high") return "Confiance elevee"
  if (text === "medium") return "Confiance moyenne"
  if (text === "low") return "Confiance limitee"
  return asText(value)
}

function normalizeImportance(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (!text) return null
  if (text === "very high" || text === "very_high" || text === "major") return "Tres marque"
  if (text === "high" || text === "strong") return "Marque"
  if (text === "medium" || text === "moderate") return "Present"
  if (text === "low" || text === "secondary") return "Secondaire"
  return asText(value)
}

function normalizeMotion(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (!text) return null
  if (text.includes("retrograde")) return "retrograde apparent"
  if (text.includes("direct")) return "direct"
  return asText(value)
}

function normalizeAspectQuality(value: unknown, aspectLabel: string | null): string | null {
  const text = asText(value)?.toLowerCase()
  if (text === "flow" || text === "harmony" || text === "harmonious") return "Fluidite"
  if (text === "tension" || text === "challenge" || text === "challenging") return "Tension"
  if (text === "intensity" || text === "intense") return "Intensite"
  if (text === "neutral") return "Neutre"

  const normalizedAspect = aspectLabel?.toLowerCase()
  if (normalizedAspect === "trigone" || normalizedAspect === "sextile") return "Fluidite"
  if (normalizedAspect === "carre" || normalizedAspect === "opposition") return "Tension"
  if (normalizedAspect === "conjonction") return "Intensite"
  return asText(value)
}

function normalizeAspectPhase(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (!text) return null
  if (text === "separating" || text === "separant") return "Separant"
  if (text === "applying" || text === "appliquant") return "Appliquant"
  return asText(value)
}

function inferAspectCode(value: string | null): string | null {
  if (!value) return null
  const text = value.toLowerCase()
  const knownCodes = [
    "conjunction",
    "sextile",
    "square",
    "trine",
    "opposition",
    "semisextile",
    "quincunx",
    "semisquare",
    "sesquiquadrate",
  ]
  return knownCodes.find((code) => text.includes(code)) ?? null
}

function inferAspectObjects(value: string | null): string[] {
  if (!value) return []
  const normalizedText = normalizeCode(value)
  return PUBLIC_ASPECT_OBJECT_ORDER
    .filter((code) => normalizedText.includes(code))
    .map((code) => formatObject(code))
    .filter((object): object is string => Boolean(object))
    .slice(0, 2)
}

function formatPlacementTitle(objectLabel: string, sign: string): string {
  return `${objectLabel} en ${sign}`
}

function signTone(value: string): string {
  const code = normalizeSignCode(value) ?? normalizeCode(value)
  return SIGN_TONE_LABELS[code] ?? `marquee par le ${value}`
}

function houseContext(houseNumber: number | null): string {
  return houseNumber ? (HOUSE_CONTEXT_LABELS[houseNumber] ?? "ce domaine de vie") : "le theme"
}

function compactHouseLabel(house: string | null): string | null {
  return house?.split(" - ")[0] ?? null
}

function fillTemplate(
  template: string,
  values: { object?: string; sign?: string; signTone: string; houseContext: string },
): string {
  return template
    .replace("{object}", values.object ?? "")
    .replace("{sign}", values.sign ?? "")
    .replace("{signTone}", values.signTone)
    .replace("{houseContext}", values.houseContext)
}

function houseTitle(number: number, theme: unknown): string {
  const translatedHouse = translateHouse(number, "fr")
  const themeLabel = asText(theme)
  if (!themeLabel) return translatedHouse
  const normalizedTheme = normalizeCode(themeLabel)
  const translatedTheme = HOUSE_THEME_LABELS[normalizedTheme]
  if (translatedTheme) return `${translatedHouse.split(" - ")[0] ?? translatedHouse} - ${translatedTheme}`
  const housePrefix = translatedHouse.split(" - ")[0] ?? translatedHouse
  return `${housePrefix} - ${themeLabel}`
}

function shortLifeAreaDescription(title: string, detailCount: number): string {
  const countText = detailCount > 1 ? "plusieurs elements importants" : "un element important"
  return `${title} ressort fortement parce que ${countText} du theme s'y concentre. Cette zone indique ou l'energie principale cherche a se rendre visible.`
}

function aspectTitle(objects: string[], aspectLabel: string, quality: string | null): string {
  const [first, second] = objects
  if (!first || !second) return aspectLabel
  if (quality === "Fluidite") return `${first} en harmonie avec ${second}`
  if (quality === "Tension") return `${first} en tension avec ${second}`
  if (aspectLabel.toLowerCase() === "conjonction") return `${first} conjoint a ${second}`
  return `${first} en relation avec ${second}`
}

function aspectDescription(quality: string | null): string {
  if (quality === "Fluidite") {
    return "Cette dynamique facilite l'action rapide, l'inventivite et la capacite a sortir des cadres habituels."
  }
  if (quality === "Tension") {
    return "Cette dynamique cree une tension a transformer en action consciente, surtout quand deux besoins tirent dans des directions differentes."
  }
  if (quality === "Intensite") {
    return "Cette dynamique concentre fortement l'energie des planetes concernees et rend leur interaction difficile a ignorer."
  }
  return "Cette dynamique relie deux fonctions importantes du theme et montre une maniere particuliere d'agir ou de reagir."
}

function splitParagraphs(value: unknown): string[] {
  const text = asText(value)
  if (!text) return []
  return text
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
}

function metadataFromProductCode(productCode: string | null): Partial<ReadingMetadata> {
  if (!productCode) return {}
  const tier = productCode.includes("premium")
    ? "premium"
    : productCode.includes("basic")
      ? "basic"
      : productCode.includes("free")
        ? "free"
        : "unknown"
  const variant = productCode.includes("simplified")
    ? "simplified"
    : productCode.includes("full")
      ? "full"
      : "unknown"
  return { tier, variant }
}

function extractMetadata(job: AstralJobResponse | undefined, fallbackPlan?: AstralPlan): ReadingMetadata {
  const result = asRecord(job?.result)
  const metadata = asRecord(result?.metadata)
  const quality = asRecord(result?.quality)
  const calculation = asRecord(result?.calculation)
  const readingHint = asRecord(calculation?.reading_hint)
  const productMetadata = metadataFromProductCode(asText(metadata?.product_code) ?? asText(job?.service_code))
  const serviceCode = asText(job?.service_code)

  const tier = asTier(metadata?.tier ?? productMetadata.tier, fallbackPlan)
  const variant =
    asVariant(metadata?.variant ?? productMetadata.variant) !== "unknown"
      ? asVariant(metadata?.variant ?? productMetadata.variant)
      : serviceCode === "natal_simplified"
        ? "simplified"
        : "unknown"
  const completeness =
    asCompleteness(quality?.reading_completeness) !== "unknown"
      ? asCompleteness(quality?.reading_completeness)
      : asCompleteness(readingHint?.reading_completeness)

  return { tier, variant, completeness }
}

function resolveReadingContainer(result: Record<string, unknown>): Record<string, unknown> | null {
  const reading = asRecord(result.reading)
  if (!reading) return null
  if (isRecord(reading.reading) || asText(reading.status)) return reading
  return { status: "success", reading }
}

function resolveError(readingResponse: Record<string, unknown> | null): NatalInterpretationViewModel["error"] {
  const error = asRecord(readingResponse?.error)
  return {
    code: asText(error?.code),
    message: asText(error?.message) ?? DEFAULT_ERROR_MESSAGE,
    ruleId: asText(error?.rule_id),
  }
}

function buildChapters(reading: Record<string, unknown>): NatalReadingChapterViewModel[] {
  const chapters = Array.isArray(reading.chapters) ? reading.chapters : []
  return chapters
    .map((chapter, index) => {
      const chapterRecord = asRecord(chapter)
      if (!chapterRecord) return null
      const paragraphs = splitParagraphs(chapterRecord.body)
      return {
        code: asText(chapterRecord.code),
        title: asText(chapterRecord.title) ?? `Chapitre ${index + 1}`,
        paragraphs,
        confidenceLabel: confidenceLabel(chapterRecord.confidence),
        astroBasis: asAstroBasisLabels(chapterRecord.astro_basis),
        safetyFlags: asTextArray(chapterRecord.safety_flags),
      }
    })
    .filter((chapter): chapter is NatalReadingChapterViewModel => Boolean(chapter))
}

function readCorePlacement(source: Record<string, unknown>, code: string): NatalCalculationFactItemViewModel | null {
  const value = asRecord(source[code])
  if (!value) return null

  const placement = asRecord(value.placement) ?? value
  const label = formatObject(code) ?? code
  const sign = formatSign(placement.sign ?? value.sign)
  if (!sign) return null

  return {
    label,
    value: sign,
    detail: joinDetails([
      formatHouse(asRecord(placement.house)?.number ?? placement.house ?? value.house),
      formatDegree(placement.longitude_deg ?? value.longitude_deg),
    ]),
  }
}

function buildCoreFacts(projection: Record<string, unknown>): NatalCalculationFactItemViewModel[] {
  const coreIdentity = asRecord(projection.core_identity)
  const angles = asRecord(projection.angles)
  const items: NatalCalculationFactItemViewModel[] = []

  if (coreIdentity) {
    for (const code of CORE_OBJECT_ORDER) {
      const item = readCorePlacement(coreIdentity, code)
      if (item) items.push(item)
    }
  }

  if (angles) {
    const angleMappings: Array<[string, string]> = [
      ["ascendant", "Ascendant"],
      ["descendant", "Descendant"],
      ["midheaven", "Milieu du Ciel"],
      ["mc", "Milieu du Ciel"],
      ["imum_coeli", "Fond du Ciel"],
      ["ic", "Fond du Ciel"],
    ]

    for (const [code, label] of angleMappings) {
      if (items.some((item) => item.label === label)) continue
      const angle = asRecord(angles[code])
      const sign = formatSign(angle?.sign)
      if (!angle || !sign) continue
      items.push({
        label,
        value: sign,
        detail: formatHouse(angle.house),
      })
    }
  }

  return items
}

function buildLegacyPlacementFacts(source: Record<string, unknown>): NatalCalculationFactItemViewModel[] {
  const planetPositions = Array.isArray(source.planet_positions) ? source.planet_positions : []
  return planetPositions
    .map((position) => {
      const item = asRecord(position)
      if (!item) return null
      const objectCode = objectCodeFromLabel(item.planet_code ?? item.object_code)
      const objectLabel = objectCode ? formatObject(objectCode) : null
      const sign = formatSign(item.sign_code ?? item.sign)
      if (!objectLabel || !sign) return null
      return {
        label: objectLabel,
        value: sign,
        detail: joinDetails([
          formatHouse(item.house_number ?? item.house),
          formatDegree(item.longitude ?? item.longitude_deg),
          item.is_retrograde === true ? "retrograde" : null,
        ]),
      }
    })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))
}

function flattenProjectionPlacements(projection: Record<string, unknown>): Record<string, unknown>[] {
  const placements = asRecord(projection.placements)
  if (!placements) return []
  return ["primary", "supporting", "background"].flatMap((key) => {
    const entries = placements[key]
    return Array.isArray(entries) ? entries.map(asRecord).filter((item): item is Record<string, unknown> => Boolean(item)) : []
  })
}

function buildNotablePlacementFacts(projection: Record<string, unknown>): NatalCalculationFactItemViewModel[] {
  const placements = flattenProjectionPlacements(projection)
  const byObject = new Map<string, Record<string, unknown>>()
  for (const placement of placements) {
    const code = objectCodeFromLabel(placement.object)
    if (code && !byObject.has(code)) byObject.set(code, placement)
  }

  return NOTABLE_PLACEMENT_ORDER.map((code) => {
    const placement = byObject.get(code)
    const sign = formatSign(placement?.sign)
    if (!placement || !sign) return null
    return {
      label: formatObject(code) ?? code,
      value: sign,
      detail: joinDetails([
        formatHouse(asRecord(placement.house)?.number),
        formatDegree(placement.longitude_deg),
        normalizeMotion(placement.motion),
      ]),
    }
  })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))
    .slice(0, MAX_NOTABLE_PLACEMENTS)
}

function buildHouseFacts(source: Record<string, unknown>, projection: Record<string, unknown>): NatalCalculationFactItemViewModel[] {
  const houses = Array.isArray(source.houses) ? source.houses : []
  const legacyHouses = houses
    .map((house) => {
      const item = asRecord(house)
      const number = asNumber(item?.number ?? item?.house_number)
      if (!item || number === null) return null
      return {
        label: translateHouse(number, "fr"),
        value: formatSign(item.sign ?? item.sign_code) ?? formatDegree(item.cusp_longitude) ?? "Disponible",
        detail: formatDegree(item.cusp_longitude ?? item.longitude_deg),
      }
    })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))

  if (legacyHouses.length > 0) return legacyHouses

  const dominantThemes = asRecord(projection.dominant_themes)
  const dominantHouses = Array.isArray(dominantThemes?.houses) ? dominantThemes.houses : []
  return dominantHouses
    .map((house) => {
      const item = asRecord(house)
      const number = asNumber(item?.number ?? item?.house_number)
      if (!item || number === null) return null
      return {
        label: translateHouse(number, "fr"),
        value: "Domaine dominant",
        detail: normalizeImportance(item.importance),
      }
    })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))
}

function buildAspectFacts(source: Record<string, unknown>, projection: Record<string, unknown>): NatalCalculationFactItemViewModel[] {
  const legacyAspects = Array.isArray(source.aspects) ? source.aspects : []
  const dynamics = asRecord(projection.dynamics)
  const projectionAspects: unknown[] = Array.isArray(dynamics?.major_aspects)
    ? dynamics.major_aspects
    : []
  const aspects: unknown[] = legacyAspects.length > 0 ? legacyAspects : projectionAspects

  return aspects
    .map((aspect) => {
      const item = asRecord(aspect)
      if (!item) return null
      const objects = Array.isArray(item.objects)
        ? item.objects.map(formatObject).filter((object): object is string => Boolean(object))
        : [
            formatObject(item.planet_a ?? item.source_object_code),
            formatObject(item.planet_b ?? item.target_object_code),
          ].filter((object): object is string => Boolean(object))
      const directAspect = asText(item.aspect)
      const inferredObjects = objects.length >= 2 ? objects : inferAspectObjects(directAspect)
      const aspectCode = asText(item.aspect_code ?? item.type) ?? inferAspectCode(directAspect)
      const aspectLabel = aspectCode ? translateAspect(aspectCode, "fr") : directAspect
      if (!aspectLabel || inferredObjects.length < 2) return null

      return {
        label: aspectLabel,
        value: inferredObjects.slice(0, 2).join(" - "),
        detail: joinDetails([
          formatDegree(item.orb ?? item.orb_degrees),
          normalizeAspectQuality(item.quality, aspectLabel),
          normalizeAspectPhase(item.phase),
        ]),
      }
    })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))
    .slice(0, MAX_MAJOR_ASPECTS)
}

function readPlacementFromContainers(
  projection: Record<string, unknown>,
  code: string,
): Record<string, unknown> | null {
  const coreIdentity = asRecord(projection.core_identity)
  const angles = asRecord(projection.angles)
  const directCore = asRecord(coreIdentity?.[code])
  const placement = asRecord(directCore?.placement) ?? directCore
  if (placement) return placement

  if (code === "midheaven") {
    return asRecord(angles?.midheaven) ?? asRecord(angles?.mc)
  }
  if (code === "imum_coeli") {
    return asRecord(angles?.imum_coeli) ?? asRecord(angles?.ic)
  }
  return asRecord(angles?.[code])
}

function placementHouseText(placement: Record<string, unknown>): string | null {
  return formatHouse(asRecord(placement.house)?.number ?? placement.house)
}

function readPublicPlacement(
  projection: Record<string, unknown>,
  code: string,
): { code: string; label: string; sign: string; house: string | null; houseNumber: number | null } | null {
  const placement = readPlacementFromContainers(projection, code)
  const sign = formatSign(placement?.sign)
  const label = formatObject(code)
  if (!placement || !sign || !label) return null
  const houseValue = asRecord(placement.house)?.number ?? placement.house
  return {
    code,
    label,
    sign,
    house: placementHouseText(placement),
    houseNumber: asNumber(houseValue),
  }
}

function buildSummary(
  projection: Record<string, unknown>,
  lifeAreas: NatalReadingLifeAreaViewModel[],
): NatalReadingSummaryViewModel | null {
  const sun = readPublicPlacement(projection, "sun")
  const moon = readPublicPlacement(projection, "moon")
  const ascendant = readPublicPlacement(projection, "ascendant")
  const dominantArea = lifeAreas[0]
  const highlights = [sun, moon, ascendant]
    .filter((item): item is NonNullable<ReturnType<typeof readPublicPlacement>> => Boolean(item))
    .map((placement) => formatPlacementTitle(placement.label, placement.sign))

  if (dominantArea) highlights.push(`${dominantArea.title} ${dominantArea.rank.toLowerCase()}`)
  if (highlights.length === 0) return null

  const toneSource = sun ?? moon ?? ascendant
  const tone = toneSource ? signTone(toneSource.sign) : "coherente"
  const focus = dominantArea ? `, avec un accent net sur ${dominantArea.title}` : ""
  return {
    text: `Ce theme met en avant une dynamique ${tone}${focus}.`,
    highlights,
  }
}

function buildPillars(projection: Record<string, unknown>): NatalReadingPillarViewModel[] {
  return (["sun", "moon", "ascendant"] as const)
    .map((code) => {
      const placement = readPublicPlacement(projection, code)
      if (!placement) return null
      return {
        code,
        icon: PILLAR_COPY[code].icon,
        title: formatPlacementTitle(placement.label, placement.sign),
        description: fillTemplate(PILLAR_COPY[code].description, {
          signTone: signTone(placement.sign),
          houseContext: houseContext(placement.houseNumber),
        }),
        lifeArea: placement.house ? `Expression principale : ${placement.house}` : null,
      }
    })
    .filter((item): item is NatalReadingPillarViewModel => Boolean(item))
}

function buildAxes(projection: Record<string, unknown>): NatalReadingAxisViewModel[] {
  const ascendant = readPublicPlacement(projection, "ascendant")
  const descendant = readPublicPlacement(projection, "descendant")
  const imumCoeli = readPublicPlacement(projection, "imum_coeli")
  const midheaven = readPublicPlacement(projection, "midheaven")
  const axes: NatalReadingAxisViewModel[] = []

  if (ascendant && descendant) {
    axes.push({
      code: "relationship_axis",
      label: "Soi / Relations",
      title: `${ascendant.sign} / ${descendant.sign}`,
      description: `Cet axe relie une presentation ${signTone(ascendant.sign)} a une recherche relationnelle ${signTone(descendant.sign)}.`,
    })
  }

  if (imumCoeli && midheaven) {
    axes.push({
      code: "public_private_axis",
      label: "Vie intime / Vie publique",
      title: `${imumCoeli.sign} / ${midheaven.sign}`,
      description: `Cet axe relie un socle intime ${signTone(imumCoeli.sign)} a une trajectoire publique ${signTone(midheaven.sign)}.`,
    })
  }

  return axes
}

function allPlacementsForHouseDetails(projection: Record<string, unknown>, houseNumber: number): string[] {
  const coreCodes = ["sun", "moon", "ascendant", "descendant", "midheaven", "imum_coeli"]
  const coreDetails = coreCodes
    .map((code) => readPublicPlacement(projection, code))
    .filter((item): item is NonNullable<ReturnType<typeof readPublicPlacement>> => Boolean(item))
    .filter((placement) => placement.houseNumber === houseNumber)
    .map((placement) => placement.label)

  const placementDetails = flattenProjectionPlacements(projection)
    .map((placement) => {
      const code = objectCodeFromLabel(placement.object)
      const number = asNumber(asRecord(placement.house)?.number)
      const label = code ? formatObject(code) : null
      if (!label || number !== houseNumber) return null
      return label
    })
    .filter((item): item is string => Boolean(item))

  return Array.from(new Set([...coreDetails, ...placementDetails])).slice(0, 6)
}

function buildLifeAreas(projection: Record<string, unknown>): NatalReadingLifeAreaViewModel[] {
  const dominantThemes = asRecord(projection.dominant_themes)
  const dominantHouses = Array.isArray(dominantThemes?.houses) ? dominantThemes.houses : []
  return dominantHouses
    .map((house) => {
      const item = asRecord(house)
      const number = asNumber(item?.number ?? item?.house_number)
      if (!item || number === null) return null
      const title = houseTitle(number, item.theme)
      const details = allPlacementsForHouseDetails(projection, number)
      return {
        rank: normalizeImportance(item.importance) ?? "Marque",
        title,
        description: shortLifeAreaDescription(title, details.length),
        details,
      }
    })
    .filter((item): item is NatalReadingLifeAreaViewModel => Boolean(item))
}

function buildOtherForces(projection: Record<string, unknown>): NatalReadingOtherForceViewModel[] {
  const placements = flattenProjectionPlacements(projection)
  const byObject = new Map<string, Record<string, unknown>>()
  for (const placement of placements) {
    const code = objectCodeFromLabel(placement.object)
    if (code && FORCE_COPY[code] && !byObject.has(code)) byObject.set(code, placement)
  }

  return NOTABLE_PLACEMENT_ORDER.map((code) => {
    const placement = byObject.get(code)
    const sign = formatSign(placement?.sign)
    const label = formatObject(code)
    if (!placement || !sign || !label) return null
    const copy = FORCE_COPY[code]
    return {
      title: formatPlacementTitle(label, sign),
      functionLabel: copy.functionLabel,
      description: fillTemplate(copy.description, {
        object: label,
        sign,
        signTone: signTone(sign),
        houseContext: houseContext(asNumber(asRecord(placement.house)?.number)),
      }),
      lifeArea: compactHouseLabel(placementHouseText(placement)),
    }
  })
    .filter((item): item is NatalReadingOtherForceViewModel => Boolean(item))
    .slice(0, MAX_NOTABLE_PLACEMENTS)
}

function buildReadingAspects(projection: Record<string, unknown>): NatalReadingAspectViewModel[] {
  const dynamics = asRecord(projection.dynamics)
  const sourceAspects = Array.isArray(projection.aspects)
    ? projection.aspects
    : Array.isArray(dynamics?.major_aspects)
      ? dynamics.major_aspects
      : []

  return sourceAspects
    .map((aspect) => {
      const item = asRecord(aspect)
      if (!item) return null
      const objects = Array.isArray(item.objects)
        ? item.objects.map(formatObject).filter((object): object is string => Boolean(object))
        : [
            formatObject(item.planet_a ?? item.source_object_code),
            formatObject(item.planet_b ?? item.target_object_code),
          ].filter((object): object is string => Boolean(object))
      const directAspect = asText(item.aspect)
      const inferredObjects = objects.length >= 2 ? objects : inferAspectObjects(directAspect)
      const aspectCode = asText(item.aspect_code ?? item.type) ?? inferAspectCode(directAspect)
      const aspectLabel = aspectCode ? translateAspect(aspectCode, "fr") : directAspect
      if (!aspectLabel || inferredObjects.length < 2) return null
      const quality = normalizeAspectQuality(item.quality, aspectLabel)
      const orb = formatDegree(item.orb ?? item.orb_degrees)
      const phase = normalizeAspectPhase(item.phase)
      const details = [
        { label: "Aspect", value: aspectLabel },
        { label: "Planetes", value: inferredObjects.slice(0, 2).join(" et ") },
        orb ? { label: "Orbe", value: orb } : null,
        phase ? { label: "Phase", value: phase } : null,
      ].filter((detail): detail is { label: string; value: string } => Boolean(detail))

      return {
        badge: quality ?? "Dynamique",
        title: aspectTitle(inferredObjects, aspectLabel, quality),
        description: aspectDescription(quality),
        details,
      }
    })
    .filter((item): item is NatalReadingAspectViewModel => Boolean(item))
    .slice(0, MAX_PUBLIC_READING_ASPECTS)
}

function buildCalculationReading(
  result: Record<string, unknown>,
  technicalGroups: NatalCalculationFactGroupViewModel[],
): NatalCalculationReadingViewModel | null {
  const projection = resolveCalculationProjection(result)
  const lifeAreas = buildLifeAreas(projection)
  const reading: NatalCalculationReadingViewModel = {
    summary: buildSummary(projection, lifeAreas),
    pillars: buildPillars(projection),
    axes: buildAxes(projection),
    lifeAreas,
    otherForces: buildOtherForces(projection),
    aspects: buildReadingAspects(projection),
    technicalGroups,
  }
  const hasPublicSections =
    reading.summary !== null ||
    reading.pillars.length > 0 ||
    reading.axes.length > 0 ||
    reading.lifeAreas.length > 0 ||
    reading.otherForces.length > 0 ||
    reading.aspects.length > 0
  return hasPublicSections || technicalGroups.length > 0 ? reading : null
}

function resolveCalculationProjection(result: Record<string, unknown>): Record<string, unknown> {
  const calculation = asRecord(result.calculation)
  const calculationLlmPayload = asRecord(calculation?.llm_payload)
  const auditPayload = asRecord(calculation?.audit_payload)
  const auditPayloadBody = asRecord(auditPayload?.payload)
  const reading = asRecord(result.reading)
  const readingCalculation = asRecord(reading?.calculation)
  const nestedReading = asRecord(reading?.reading)
  const nestedReadingCalculation = asRecord(nestedReading?.calculation)
  return (
    nestedReadingCalculation ??
    readingCalculation ??
    calculationLlmPayload ??
    auditPayloadBody ??
    calculation ??
    result
  )
}

function buildCalculationFacts(result: Record<string, unknown>): NatalCalculationFactsViewModel | null {
  const projection = resolveCalculationProjection(result)
  const groups: NatalCalculationFactGroupViewModel[] = []
  const coreFacts = buildCoreFacts(projection)
  const legacyPlacementFacts = buildLegacyPlacementFacts(projection)
  const notablePlacements = buildNotablePlacementFacts(projection)
  const houseFacts = buildHouseFacts(projection, projection)
  const aspectFacts = buildAspectFacts(projection, projection)

  const mainFacts = coreFacts.length > 0 ? coreFacts : legacyPlacementFacts.slice(0, 5)
  if (mainFacts.length > 0) groups.push({ title: "Repères principaux", items: mainFacts })
  if (houseFacts.length > 0) groups.push({ title: "Maisons", items: houseFacts })
  if (notablePlacements.length > 0) groups.push({ title: "Planètes notables", items: notablePlacements })
  if (aspectFacts.length > 0) groups.push({ title: "Aspects notables", items: aspectFacts })

  return groups.length > 0 ? { groups, sourceLabel: "Données de calcul Astral" } : null
}

function emptyViewModel(
  metadata: ReadingMetadata,
  message: string,
  calculationFacts: NatalCalculationFactsViewModel | null = null,
  calculationReading: NatalCalculationReadingViewModel | null = null,
): NatalInterpretationViewModel {
  const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"
  return {
    status: "empty",
    title: "Lecture natale indisponible",
    shortText: message,
    tier: metadata.tier,
    variant: metadata.variant,
    label: labelForReading(metadata.tier),
    completeness: metadata.completeness,
    isPartial,
    chapters: [],
    calculationReading,
    calculationFacts,
    disclaimer: null,
    error: null,
  }
}

/** Convertit un job Astral ou une enveloppe gateway en modele stable pour l'UI publique. */
export function buildNatalInterpretationViewModel(
  job: AstralJobResponse | undefined,
  fallbackPlan?: AstralPlan,
): NatalInterpretationViewModel | null {
  const result = asRecord(job?.result)
  if (!result) return null

  const metadata = extractMetadata(job, fallbackPlan)
  const calculationFacts = buildCalculationFacts(result)
  const calculationReading = buildCalculationReading(result, calculationFacts?.groups ?? [])
  const readingResponse = resolveReadingContainer(result)
  if (!readingResponse) {
    if (typeof result.reading === "string") {
      const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"
      return {
        status: "success",
        title: "Lecture natale",
        shortText: asText(result.reading),
        tier: metadata.tier,
        variant: metadata.variant,
        label: labelForReading(metadata.tier),
        completeness: metadata.completeness,
        isPartial,
        chapters: [],
        calculationReading,
        calculationFacts,
        disclaimer: null,
        error: null,
      }
    }
    return emptyViewModel(
      metadata,
      "La lecture est disponible mais sa forme publique n'est pas reconnue.",
      calculationFacts,
      calculationReading,
    )
  }

  const responseStatus = asText(readingResponse.status)?.toLowerCase()
  if (responseStatus === "failed" || responseStatus === "safety_rejected") {
    const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"
    return {
      status: responseStatus,
      title: responseStatus === "safety_rejected" ? "Lecture non generee" : "Lecture indisponible",
      shortText: null,
      tier: metadata.tier,
      variant: metadata.variant,
      label: labelForReading(metadata.tier),
      completeness: metadata.completeness,
      isPartial,
      chapters: [],
      calculationReading,
      calculationFacts,
      disclaimer: null,
      error: resolveError(readingResponse),
    }
  }

  const reading = asRecord(readingResponse.reading)
  if (!reading) {
    return emptyViewModel(
      metadata,
      "La lecture est disponible mais ne contient pas de texte public.",
      calculationFacts,
      calculationReading,
    )
  }

  const summary = asRecord(reading.summary)
  const legal = asRecord(reading.legal)
  const chapters = buildChapters(reading)
  const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"

  return {
    status: "success",
    title: asText(summary?.title) ?? "Lecture natale",
    shortText: asText(summary?.short_text),
    tier: metadata.tier,
    variant: metadata.variant,
    label: labelForReading(metadata.tier),
    completeness: metadata.completeness,
    isPartial,
    chapters,
    calculationReading,
    calculationFacts,
    disclaimer: asText(legal?.disclaimer),
    error: null,
  }
}
