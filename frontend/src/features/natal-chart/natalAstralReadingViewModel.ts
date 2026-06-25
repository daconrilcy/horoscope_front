// Normalisation des contrats d'interpretation natale Astral pour l'affichage public.
import type { AstralJobResponse, AstralPlan } from "../../api/astral"
import { translateAspect, translateHouse, translatePlanet, translateSign } from "../../i18n/astrology"
import { normalizeDisplayText } from "../../utils/strings"

export type NatalReadingTier = "free" | "basic" | "premium" | "unknown"
export type NatalReadingVariant = "full" | "simplified" | "unknown"
export type NatalReadingCompleteness = "completed" | "partial" | "unknown"
export type NatalReadingStatus = "success" | "empty" | "failed" | "safety_rejected"
export type NatalExplanationStatus = "complete" | "partial" | "unavailable" | "unknown"

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
  text: string | null
  highlights: string[]
}

export type NatalReadingExplanationViewModel = {
  kindLabel: string
  title: string
  explanation: string
  expressionPrimary: string | null
}

export type NatalReadingPillarViewModel = {
  code: "sun" | "moon" | "ascendant"
  icon: string
  title: string
  description: string
  lifeArea: string | null
}

export type NatalReadingAxisViewModel = {
  code: string
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
  explanationStatus: NatalExplanationStatus
  explanationLanguageCode: string | null
  summary: NatalReadingSummaryViewModel | null
  explanations: NatalReadingExplanationViewModel[]
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

type NatalExplanationItem = {
  kindCode: string
  title: string
  explanation: string
  expressionPrimary: string | null
  searchableId: string
}

type NatalExplanations = {
  status: NatalExplanationStatus
  languageCode: string | null
  items: NatalExplanationItem[]
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
const COMPLEMENTARY_FORCE_ORDER = ["mercury", "venus", "mars"] as const
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
const MAX_SUMMARY_HIGHLIGHTS = 4
const PUBLIC_OBJECT_LABELS: Record<string, string> = {
  ascendant: "Ascendant",
  descendant: "Descendant",
  midheaven: "Milieu du Ciel",
  mc: "Milieu du Ciel",
  imum_coeli: "Fond du Ciel",
  ic: "Fond du Ciel",
}

const HOUSE_AXIS_LABELS: Record<string, string> = {
  private_public: "privé/public",
  control_surrender: "contrôle / lâcher-prise",
  self_relationship: "soi / relation",
}

const HOUSE_EMPHASIS_LABELS: Record<string, string> = {
  career: "Carrière",
  resources: "Ressources",
  relationships: "Relations",
  home: "Foyer",
  identity: "Identité",
  communication: "Communication",
  transformation: "Transformation",
  community: "Communauté",
  philosophy: "Philosophie",
  creativity: "Créativité",
  unconscious: "Inconscient",
  values: "Valeurs",
  routines: "Routines",
  lifestyle_hygiene: "Hygiène de vie",
}

const PILLAR_PRESENTATION: Record<"sun" | "moon" | "ascendant", { icon: string }> = {
  sun: { icon: "☉" },
  moon: { icon: "☽" },
  ascendant: { icon: "ASC" },
}

const COMPLEMENTARY_FORCE_LABELS: Record<string, string> = {
  mercury: "Communication",
  venus: "Valeurs et attachement",
  mars: "Action",
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

function formatHouseShort(value: unknown): string | null {
  const text = asText(value)
  const number = asNumber(value) ?? (text && Number.isFinite(Number(text)) ? Number(text) : null)
  return number === null ? null : `Maison ${number}`
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

function explanationFactParts(factId: string): string[] {
  return factId.split(":").map((part) => normalizeCode(part))
}

function normalizeHouseAxisLabel(code: string | null): string | null {
  if (!code) return null
  return HOUSE_AXIS_LABELS[code] ?? code.replace(/_/g, " ")
}

function normalizeHouseEmphasisLabel(code: string | null): string | null {
  if (!code) return null
  return HOUSE_EMPHASIS_LABELS[code] ?? code.replace(/_/g, " ")
}

function normalizeExpressionPrimary(value: unknown): string | null {
  const text = asText(value)
  if (!text) return null
  const code = normalizeCode(text)
  return HOUSE_EMPHASIS_LABELS[code] ?? text
}

function buildExplanationTitle(item: {
  kindCode: string
  title: string
  searchableId: string
  expressionPrimary: string | null
}): string {
  const parts = explanationFactParts(item.searchableId)

  if (item.kindCode === "placement" && parts.length >= 5) {
    const object = formatObject(parts[1])
    const sign = formatSign(parts[2])
    const house = formatHouseShort(parts[4])
    if (object && sign && house) {
      return `${object} en ${sign} ${house.toLowerCase()}`
    }
  }

  if (item.kindCode === "angle" && parts.length >= 5) {
    const object = formatObject(parts[1])
    const sign = formatSign(parts[2])
    const house = formatHouseShort(parts[4])
    if (object && sign && house) {
      return `${object} en ${sign} ${house.toLowerCase()}`
    }
  }

  if (item.kindCode === "house_axis" && parts.length >= 2) {
    const axisLabel = normalizeHouseAxisLabel(parts[1])
    if (axisLabel) return `Axe maison : ${axisLabel}`
  }

  if (item.kindCode === "house_emphasis" && parts.length >= 3) {
    const emphasisLabel = normalizeExpressionPrimary(item.expressionPrimary) ?? normalizeHouseEmphasisLabel(parts[2])
    if (emphasisLabel) return `Emphase maison : ${emphasisLabel}`
  }

  return item.title
}

function normalizeExplanationStatus(value: unknown): NatalExplanationStatus {
  const text = asText(value)?.toLowerCase()
  if (text === "complete" || text === "partial" || text === "unavailable") return text
  return "unknown"
}

function normalizeExplanationItem(value: unknown): NatalExplanationItem | null {
  const item = asRecord(value)
  if (!item) return null
  const factId = asText(item.fact_id)
  const kindCode = asText(item.kind_code)
  const title = asText(item.title)
  const explanation = asText(item.explanation)
  if (!factId || !kindCode || !title || !explanation) return null
  const searchableId = normalizeCode(factId)
  const normalizedKindCode = normalizeCode(kindCode)
  const expressionPrimary = normalizeExpressionPrimary(item.expression_primary)
  return {
    kindCode: normalizedKindCode,
    title: buildExplanationTitle({
      kindCode: normalizedKindCode,
      title,
      searchableId,
      expressionPrimary,
    }),
    explanation,
    expressionPrimary,
    searchableId,
  }
}

function readNatalExplanations(result: Record<string, unknown>): NatalExplanations {
  const explanations = asRecord(result.explanations)
  const items = Array.isArray(explanations?.items)
    ? explanations.items.map(normalizeExplanationItem).filter((item): item is NatalExplanationItem => Boolean(item))
    : []
  return {
    status: normalizeExplanationStatus(explanations?.status),
    languageCode: asText(explanations?.language_code),
    items,
  }
}

function explanationMatchesObject(item: NatalExplanationItem, objectCode: string): boolean {
  const normalizedObject = normalizeCode(objectCode)
  return item.searchableId.split(":").includes(normalizedObject)
}

function firstExplanationForObject(items: NatalExplanationItem[], objectCode: string): NatalExplanationItem | null {
  return items.find((item) => explanationMatchesObject(item, objectCode)) ?? null
}

function isAxisExplanation(item: NatalExplanationItem): boolean {
  return item.kindCode.includes("axis")
}

function isAspectExplanation(item: NatalExplanationItem): boolean {
  return item.kindCode === "aspect" || item.searchableId.startsWith("aspect:")
}

function isHouseEmphasisExplanation(item: NatalExplanationItem): boolean {
  return item.kindCode === "house_emphasis" || item.searchableId.startsWith("house_emphasis:")
}

function expressionDetail(value: string | null): string | null {
  return value ? `Expression principale : ${value}` : null
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

function buildSummaryFromExplanations(items: NatalExplanationItem[]): NatalReadingSummaryViewModel | null {
  const highlights = [
    firstExplanationForObject(items, "sun")?.title,
    firstExplanationForObject(items, "moon")?.title,
    firstExplanationForObject(items, "ascendant")?.title,
    items.find(isHouseEmphasisExplanation)?.title,
  ].filter((item): item is string => Boolean(item))

  return highlights.length > 0 ? { text: null, highlights: highlights.slice(0, MAX_SUMMARY_HIGHLIGHTS) } : null
}

function explanationKindLabel(item: NatalExplanationItem): string {
  if (item.kindCode === "placement") return "Placement"
  if (item.kindCode === "angle") return "Angle"
  if (item.kindCode === "house_axis") return "Axe"
  if (item.kindCode === "house_emphasis") return "Domaine dominant"
  if (item.kindCode === "aspect") return "Aspect"
  return "Explication"
}

function buildExplanationsFromItems(items: NatalExplanationItem[]): NatalReadingExplanationViewModel[] {
  return items.map((item) => ({
    kindLabel: explanationKindLabel(item),
    title: item.title,
    explanation: item.explanation,
    expressionPrimary: item.expressionPrimary,
  }))
}

function buildPillarsFromExplanations(items: NatalExplanationItem[]): NatalReadingPillarViewModel[] {
  return (["sun", "moon", "ascendant"] as const)
    .map((code) => {
      const item = firstExplanationForObject(items, code)
      if (!item) return null
      return {
        code,
        icon: PILLAR_PRESENTATION[code].icon,
        title: item.title,
        description: item.explanation,
        lifeArea: expressionDetail(item.expressionPrimary),
      }
    })
    .filter((item): item is NatalReadingPillarViewModel => Boolean(item))
}

function buildAxesFromExplanations(items: NatalExplanationItem[]): NatalReadingAxisViewModel[] {
  return items
    .filter(isAxisExplanation)
    .map((item, index) => ({
      code: `axis-${index}`,
      label: "Axe",
      title: item.title,
      description: item.explanation,
    }))
}

function buildLifeAreasFromExplanations(items: NatalExplanationItem[]): NatalReadingLifeAreaViewModel[] {
  return items
    .filter(isHouseEmphasisExplanation)
    .map((item) => ({
      rank: "Domaine dominant",
      title: item.title,
      description: item.explanation,
      details: [],
    }))
}

function buildOtherForcesFromExplanations(items: NatalExplanationItem[]): NatalReadingOtherForceViewModel[] {
  return COMPLEMENTARY_FORCE_ORDER.map((code) => {
    const item = firstExplanationForObject(items, code)
    if (!item) return null
    return {
      title: item.title,
      functionLabel: COMPLEMENTARY_FORCE_LABELS[code],
      description: item.explanation,
      lifeArea: item.expressionPrimary,
    }
  }).filter((item): item is NatalReadingOtherForceViewModel => Boolean(item))
}

function buildReadingAspectsFromExplanations(items: NatalExplanationItem[]): NatalReadingAspectViewModel[] {
  return items
    .filter(isAspectExplanation)
    .map((item) => ({
      badge: item.expressionPrimary ?? "Dynamique",
      title: item.title,
      description: item.explanation,
      details: [],
    }))
    .slice(0, MAX_PUBLIC_READING_ASPECTS)
}

function buildCalculationReading(
  result: Record<string, unknown>,
  technicalGroups: NatalCalculationFactGroupViewModel[],
): NatalCalculationReadingViewModel | null {
  const explanations = readNatalExplanations(result)
  const publicItems = explanations.status === "unavailable" ? [] : explanations.items
  const reading: NatalCalculationReadingViewModel = {
    explanationStatus: explanations.status,
    explanationLanguageCode: explanations.languageCode,
    summary: buildSummaryFromExplanations(publicItems),
    explanations: buildExplanationsFromItems(publicItems),
    pillars: buildPillarsFromExplanations(publicItems),
    axes: buildAxesFromExplanations(publicItems),
    lifeAreas: buildLifeAreasFromExplanations(publicItems),
    otherForces: buildOtherForcesFromExplanations(publicItems),
    aspects: buildReadingAspectsFromExplanations(publicItems),
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
