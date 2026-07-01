// Normalisation des contrats d'interpretation natale Astral pour l'affichage public.
import type { AstralJobResponse, AstralPlan } from "../../api/astral"
import type { BirthProfileData } from "../../api/birthProfile"
import { translateAspect, translateHouse, translatePlanet, translateSign } from "../../i18n/astrology"
import { normalizeDisplayText } from "../../utils/strings"

export type NatalReadingTier = "free" | "basic" | "premium" | "unknown"
export type NatalReadingVariant = "full" | "simplified" | "unknown"
export type NatalReadingCompleteness = "completed" | "partial" | "unknown"
export type NatalReadingStatus = "success" | "empty" | "failed" | "safety_rejected"

export type NatalReadingChapterViewModel = {
  code: string | null
  title: string
  summarySentence: string | null
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

export type NatalCalculationMethodViewModel = {
  detail: string | null
  label: string
  value: string
}

export type NatalCalculationFactsViewModel = {
  groups: NatalCalculationFactGroupViewModel[]
  methods: NatalCalculationMethodViewModel[]
  calculationReferenceMethods: NatalCalculationMethodViewModel[]
  sourceLabel: string
}

export type NatalHighlightFactViewModel = NatalCalculationFactItemViewModel

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
  explanations: NatalReadingChapterViewModel[]
  calculationFacts: NatalCalculationFactsViewModel | null
  highlightFacts: NatalHighlightFactViewModel[]
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
const CORE_OBJECT_ORDER = ["sun", "moon"] as const
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
const MAX_NOTABLE_PLACEMENTS = 6
const HIGHLIGHT_FACT_LABELS = ["Soleil", "Lune", "Ascendant"] as const
const ASTRAL_TEXT_REPLACEMENTS: ReadonlyArray<[RegExp, string]> = [
  [/\bHow to read your natal chart\b/gi, "Comment lire ton thème natal"],
  [/\bSun\b/gi, "Soleil"],
  [/\bMoon\b/gi, "Lune"],
  [/\bMercury\b/gi, "Mercure"],
  [/\bVenus\b/gi, "Vénus"],
  [/\bMars\b/gi, "Mars"],
  [/\bJupiter\b/gi, "Jupiter"],
  [/\bSaturn\b/gi, "Saturne"],
  [/\bUranus\b/gi, "Uranus"],
  [/\bNeptune\b/gi, "Neptune"],
  [/\bPluto\b/gi, "Pluton"],
  [/\bMidheaven\b/gi, "Milieu du Ciel"],
  [/\bMC\b/g, "Milieu du Ciel"],
  [/\bImum Coeli\b/gi, "Fond du Ciel"],
  [/\bIC\b/g, "Fond du Ciel"],
  [/\bAries\b/gi, "Bélier"],
  [/\bTaurus\b/gi, "Taureau"],
  [/\bGemini\b/gi, "Gémeaux"],
  [/\bCancer\b/gi, "Cancer"],
  [/\bLeo\b/gi, "Lion"],
  [/\bVirgo\b/gi, "Vierge"],
  [/\bLibra\b/gi, "Balance"],
  [/\bScorpio\b/gi, "Scorpion"],
  [/\bSagittarius\b/gi, "Sagittaire"],
  [/\bCapricorn\b/gi, "Capricorne"],
  [/\bAquarius\b/gi, "Verseau"],
  [/\bPisces\b/gi, "Poissons"],
  [/\bCareer\b/gi, "Carrière"],
  [/\bResources\b/gi, "Valeurs"],
  [/\bValues\b/gi, "Valeurs"],
  [/\bVery high\b/gi, "Très élevée"],
  [/\bBasic\b/gi, "Essentielle"],
  [/\bFree\b/gi, "Découverte"],
  [/\bConjunction\b/gi, "Conjonction"],
  [/\bSquare\b/gi, "Carré"],
  [/\bTrine\b/gi, "Trigone"],
  [/\bSextile\b/gi, "Sextile"],
  [/\bOpposition\b/gi, "Opposition"],
  [/\bHouse\b/gi, "maison"],
  [/\bin\b/gi, "en"],
]
const ASTRAL_METADATA_TRANSLATIONS: Record<string, string> = {
  career: "Carrière",
  communication: "Communication",
  home: "Foyer",
  resources: "Valeurs",
  spirituality: "Spiritualité",
  "very high": "Très élevée",
  high: "Élevée",
  medium: "Moyenne",
  low: "Limitée",
}
const PUBLIC_OBJECT_LABELS: Record<string, string> = {
  ascendant: "Ascendant",
  descendant: "Descendant",
  midheaven: "Milieu du Ciel",
  mc: "Milieu du Ciel",
  imum_coeli: "Fond du Ciel",
  ic: "Fond du Ciel",
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

function localizeAstralDisplayText(value: string): string {
  const readableValue = value.replace(/[_-]+/g, " ")
  return ASTRAL_TEXT_REPLACEMENTS.reduce(
    (currentValue, [pattern, replacement]) => currentValue.replace(pattern, replacement),
    readableValue,
  )
}

function localizedMetadataText(value: unknown): string | null {
  const text = asText(value)
  if (!text) return null
  return ASTRAL_METADATA_TRANSLATIONS[text.toLowerCase()] ?? localizeAstralDisplayText(text)
}

function formatDegree(value: unknown): string | null {
  const degree = asNumber(value)
  return degree === null ? null : `${degree.toFixed(2)}°`
}

function formatCoordinate(value: unknown, positiveSuffix: string, negativeSuffix: string): string | null {
  const coordinate = asNumber(value)
  if (coordinate === null) return null
  const suffix = coordinate >= 0 ? positiveSuffix : negativeSuffix
  return `${Math.abs(coordinate).toFixed(4)}° ${suffix}`
}

function formatBirthDate(value: string | null | undefined): string | null {
  if (!value) return null
  const [year, month, day] = value.split("-").map((part) => Number.parseInt(part, 10))
  if (!year || !month || !day) return value
  return new Intl.DateTimeFormat("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, day))
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
  return details.length > 0 ? details.join(" - ") : null
}

function joinUniqueDetails(values: Array<string | null>): string | null {
  const details: string[] = []
  for (const value of values) {
    if (value && !details.includes(value)) details.push(value)
  }
  return details.length > 0 ? details.join(" - ") : null
}

function pushUniqueFact(items: NatalCalculationFactItemViewModel[], item: NatalCalculationFactItemViewModel | null): void {
  if (!item) return
  const exists = items.some((candidate) => candidate.label === item.label && candidate.value === item.value)
  if (!exists) items.push(item)
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
  if (directText) return localizeAstralDisplayText(directText)

  const basis = asRecord(value)
  const label = localizedMetadataText(basis?.label) ?? localizedMetadataText(basis?.factor)
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
  if (tier === "free") return "Découverte"
  if (tier === "basic") return "Essentielle"
  if (tier === "premium") return "Premium"
  return "Lecture"
}

function confidenceLabel(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (text === "high") return "Confiance élevée"
  if (text === "medium") return "Confiance moyenne"
  if (text === "low") return "Confiance limitée"
  return asText(value)
}

function splitParagraphs(value: unknown): string[] {
  const text = asText(value)
  if (!text) return []
  return text
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
}

function firstText(...values: unknown[]): string | null {
  for (const value of values) {
    const text = asText(value)
    if (text) return text
  }
  return null
}

function chapterParagraphs(chapter: Record<string, unknown>): string[] {
  const directParagraphs = asTextArray(chapter.paragraphs)
  if (directParagraphs.length > 0) return directParagraphs

  return splitParagraphs(
    firstText(
      chapter.body,
      chapter.explanation,
      chapter.narrative,
      chapter.text,
      chapter.content,
      chapter.summary,
      chapter.interpretation,
    ),
  )
}

function evidenceLabels(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value
    .map((item) => {
      const record = asRecord(item)
      if (!record) return localizedMetadataText(item)
      const label = localizedMetadataText(record.label)
      const meaning = localizedMetadataText(record.meaning)
      if (label && meaning) return `${label}: ${meaning}`
      return label ?? meaning
    })
    .filter((item): item is string => Boolean(item))
}

function resolveChapterItems(reading: Record<string, unknown>): unknown[] {
  const candidates = [reading.chapters, reading.sections, reading.themes, reading.explanations]
  for (const candidate of candidates) {
    if (
      Array.isArray(candidate) &&
      candidate.some((item) => {
        const record = asRecord(item)
        return record ? chapterParagraphs(record).length > 0 : false
      })
    ) {
      return candidate
    }
  }

  for (const candidate of candidates) {
    if (Array.isArray(candidate) && candidate.length > 0) return candidate
  }
  return []
}

function explanationItems(value: unknown): Record<string, unknown>[] {
  const text = asText(value)
  if (text) return [{ title: "Explications", body: text }]

  if (Array.isArray(value)) {
    return value.map(asRecord).filter((item): item is Record<string, unknown> => Boolean(item))
  }

  const record = asRecord(value)
  if (!record) return []
  if (Array.isArray(record.items)) {
    return explanationItems(record.items)
  }

  if (Array.isArray(record.chapters) || Array.isArray(record.sections) || Array.isArray(record.themes)) {
    return resolveChapterItems(record).map(asRecord).filter((item): item is Record<string, unknown> => Boolean(item))
  }

  if (Array.isArray(record.explanations)) {
    return explanationItems(record.explanations)
  }

  if (chapterParagraphs(record).length > 0) {
    return [record]
  }

  return Object.entries(record)
    .filter(([key]) => key !== "language_code" && key !== "status")
    .map<Record<string, unknown> | null>(([key, entry]) => {
      const entryText = asText(entry)
      return entryText ? { title: localizeAstralDisplayText(key), body: entryText } : null
    })
    .filter((item): item is Record<string, unknown> => Boolean(item))
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
  const chapters = resolveChapterItems(reading)
  return chapters
    .map((chapter, index) => {
      const chapterRecord = asRecord(chapter)
      if (!chapterRecord) return null
      const paragraphs = chapterParagraphs(chapterRecord)
      return {
        code: asText(chapterRecord.code),
        title: localizedMetadataText(chapterRecord.title) ?? `Chapitre ${index + 1}`,
        summarySentence: asText(chapterRecord.summary_sentence),
        paragraphs,
        confidenceLabel: confidenceLabel(chapterRecord.confidence),
        astroBasis: [
          ...asAstroBasisLabels(chapterRecord.astro_basis),
          ...evidenceLabels(chapterRecord.public_evidence),
        ],
        safetyFlags: asTextArray(chapterRecord.safety_flags),
      }
    })
    .filter((chapter): chapter is NatalReadingChapterViewModel => Boolean(chapter))
}

function findLegacyBasicPayload(result: Record<string, unknown>): Record<string, unknown> | null {
  const reading = asRecord(result.reading)
  const nestedReading = asRecord(reading?.reading)
  return (
    asRecord(result.basic_natal_interpretation_v2) ??
    asRecord(reading?.basic_natal_interpretation_v2) ??
    asRecord(nestedReading?.basic_natal_interpretation_v2)
  )
}

function resultExplanationsContainer(result: Record<string, unknown>): Record<string, unknown> | null {
  const explanations = explanationItems(result.explanations)
  if (explanations.length === 0) return null

  const summary = asRecord(result.summary)
  return {
    summary: {
      title: asText(summary?.title) ?? asText(result.title) ?? "Lecture natale",
      short_text: asText(summary?.short_text) ?? asText(summary?.text) ?? asText(result.short_text),
    },
    chapters: explanations,
  }
}

function explanationChapters(reading: Record<string, unknown> | null): NatalReadingChapterViewModel[] {
  return reading ? buildChapters(reading) : []
}

function legacyBasicReading(result: Record<string, unknown>): Record<string, unknown> | null {
  const payload = findLegacyBasicPayload(result)
  const interpretation = asRecord(payload?.interpretation)
  if (!payload || !interpretation) return null

  const chapters: Record<string, unknown>[] = []
  const introduction = asText(interpretation.introduction)
  if (introduction) {
    chapters.push({
      code: "introduction",
      title: "Introduction",
      body: introduction,
      public_evidence: interpretation.public_evidence ?? payload.public_evidence,
    })
  }

  const themes = Array.isArray(interpretation.themes) ? interpretation.themes : []
  for (const theme of themes) {
    const themeRecord = asRecord(theme)
    if (!themeRecord) continue
    chapters.push({
      code: asText(themeRecord.code),
      title: asText(themeRecord.title) ?? "Thème",
      narrative: themeRecord.narrative,
      public_evidence: themeRecord.public_evidence,
    })
  }

  const conclusion = asText(interpretation.conclusion)
  if (conclusion) {
    chapters.push({
      code: "conclusion",
      title: "Conclusion",
      body: conclusion,
    })
  }

  return {
    summary: {
      title: interpretation.title,
      short_text: interpretation.summary,
    },
    chapters,
    legal: {
      disclaimer: asTextArray(payload.disclaimers).join(" "),
    },
  }
}

function hasChapterText(reading: Record<string, unknown>): boolean {
  return buildChapters(reading).some((chapter) => chapter.paragraphs.length > 0)
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
    const angle = asRecord(angles?.[code])
    const sign = formatSign(angle?.sign)
    if (angle && sign) {
      items.push({
        label,
        value: sign,
        detail: formatHouse(angle.house),
      })
      continue
    }

    const coreAngle = coreIdentity ? readCorePlacement(coreIdentity, code) : null
    if (coreAngle) items.push(coreAngle)
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
          item.is_retrograde === true ? "rétrograde" : null,
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
        asText(placement.motion)?.toLowerCase().includes("retrograde") ? "rétrograde" : null,
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
        value: localizedMetadataText(item.theme) ?? "Maison dominante",
        detail: localizedMetadataText(item.importance),
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
      const aspectCode = asText(item.aspect_code ?? item.type)
      const aspectLabel = aspectCode ? translateAspect(aspectCode, "fr") : directAspect ? localizeAstralDisplayText(directAspect) : null
      if (!aspectLabel || objects.length < 2) return null

      return {
        label: aspectLabel,
        value: objects.slice(0, 2).join(" - "),
        detail: joinDetails([
          formatDegree(item.orb ?? item.orb_degrees),
          asText(item.quality),
          asText(item.phase),
        ]),
      }
    })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))
}

function buildSensitivePointFacts(projection: Record<string, unknown>): NatalCalculationFactItemViewModel[] {
  const points = Array.isArray(projection.astral_points) ? projection.astral_points : []
  return points
    .map((point) => {
      const item = asRecord(point)
      const label = formatObject(item?.code ?? item?.point_code)
      const sign = formatSign(item?.sign ?? item?.sign_code)
      if (!item || !label || !sign) return null
      return {
        label,
        value: sign,
        detail: joinDetails([
          formatHouse(item.house ?? item.house_number),
          formatDegree(item.longitude ?? item.degree_in_sign),
        ]),
      }
    })
    .filter((item): item is NatalCalculationFactItemViewModel => Boolean(item))
}

function buildBirthProfileFacts(birthProfile?: BirthProfileData | null): NatalCalculationFactItemViewModel[] {
  if (!birthProfile) return []

  const place = [birthProfile.birth_city, birthProfile.birth_country].filter(Boolean).join(", ") || birthProfile.birth_place
  const coordinates = joinDetails([
    formatCoordinate(birthProfile.birth_lat, "N", "S"),
    formatCoordinate(birthProfile.birth_lon, "E", "O"),
  ])
  const items: NatalCalculationFactItemViewModel[] = []
  pushUniqueFact(items, place ? { label: "Lieu", value: place, detail: coordinates } : null)
  pushUniqueFact(items, birthProfile.birth_date ? { label: "Date", value: formatBirthDate(birthProfile.birth_date) ?? birthProfile.birth_date, detail: null } : null)
  pushUniqueFact(items, birthProfile.birth_time ? { label: "Heure de naissance", value: birthProfile.birth_time, detail: null } : null)
  return items
}

function firstMethodText(...values: unknown[]): string | null {
  for (const value of values) {
    const text = localizedMetadataText(value)
    if (text) return text
  }
  return null
}

function firstRawMethodText(...values: unknown[]): string | null {
  for (const value of values) {
    const text = asText(value)
    if (text) return text
  }
  return null
}

function buildCalculationMethods(
  result: Record<string, unknown>,
  projection: Record<string, unknown>,
  birthProfile?: BirthProfileData | null,
): NatalCalculationMethodViewModel[] {
  const metadata = asRecord(result.metadata)
  const quality = asRecord(result.quality)
  const preparedInput = asRecord(projection.prepared_input)
  const zodiac = firstMethodText(projection.zodiac, metadata?.zodiac)
  const houseSystem = firstMethodText(projection.house_system, metadata?.house_system)
  const referenceVersion = firstRawMethodText(metadata?.reference_version, result.reference_version, projection.reference_version)
  const engine = firstMethodText(projection.engine, metadata?.engine, result.engine)
  const referenceDetail = joinUniqueDetails([
    referenceVersion ? engine : null,
    firstRawMethodText(metadata?.ruleset_version, result.ruleset_version),
  ])
  const coordinates = joinDetails([
    formatCoordinate(birthProfile?.birth_lat, "N", "S"),
    formatCoordinate(birthProfile?.birth_lon, "E", "O"),
  ])
  const methods: NatalCalculationMethodViewModel[] = [
    {
      detail: zodiac ? houseSystem : null,
      label: "Système",
      value: zodiac ?? houseSystem ?? "",
    },
    {
      detail: referenceDetail,
      label: "Référence",
      value: referenceVersion ?? engine ?? "",
    },
    {
      detail: firstMethodText(preparedInput?.timezone_used, preparedInput?.birth_timezone, birthProfile?.birth_timezone),
      label: "Fuseau horaire",
      value: firstMethodText(preparedInput?.timezone_used, birthProfile?.birth_timezone) ?? "",
    },
    {
      detail: null,
      label: "Coordonnées",
      value: coordinates ?? "",
    },
    {
      detail: null,
      label: "Précision",
      value: firstMethodText(quality?.precision, projection.birth_date_precision) ?? "",
    },
  ]

  return methods.filter((method) => Boolean(method.value))
}

function resolveCalculationReference(result: Record<string, unknown>): Record<string, unknown> | null {
  const reading = asRecord(result.reading)
  const nestedReading = asRecord(reading?.reading)
  return (
    asRecord(nestedReading?.calculation_reference) ??
    asRecord(reading?.calculation_reference) ??
    asRecord(result.calculation_reference)
  )
}

function buildCalculationReferenceMethods(result: Record<string, unknown>): NatalCalculationMethodViewModel[] {
  const reference = resolveCalculationReference(result)
  if (!reference) return []

  const methods: NatalCalculationMethodViewModel[] = [
    {
      detail: null,
      label: "Version",
      value: firstMethodText(reference.version) ?? "",
    },
    {
      detail: null,
      label: "Système zodiacal",
      value: firstMethodText(reference.zodiacal_reference_system) ?? "",
    },
    {
      detail: null,
      label: "Coordonnées",
      value: firstMethodText(reference.coordinate_reference_system) ?? "",
    },
    {
      detail: null,
      label: "Maisons",
      value: firstMethodText(reference.house_system) ?? "",
    },
    {
      detail: null,
      label: "Éphémérides",
      value: firstMethodText(reference.ephemeris_reference) ?? "",
    },
    {
      detail: null,
      label: "Précision",
      value: firstMethodText(reference.precision) ?? "",
    },
  ]

  return methods.filter((method) => Boolean(method.value))
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

function buildCalculationFacts(
  result: Record<string, unknown>,
  birthProfile?: BirthProfileData | null,
): NatalCalculationFactsViewModel | null {
  const projection = resolveCalculationProjection(result)
  const groups: NatalCalculationFactGroupViewModel[] = []
  const coreFacts = buildCoreFacts(projection)
  const legacyPlacementFacts = buildLegacyPlacementFacts(projection)
  const notablePlacements = buildNotablePlacementFacts(projection)
  const houseFacts = buildHouseFacts(projection, projection)
  const aspectFacts = buildAspectFacts(projection, projection)
  const sensitivePointFacts = buildSensitivePointFacts(projection)
  const methods = buildCalculationMethods(result, projection, birthProfile)
  const calculationReferenceMethods = buildCalculationReferenceMethods(result)

  const mainFacts = [...(coreFacts.length > 0 ? coreFacts : legacyPlacementFacts.slice(0, 5))]
  for (const profileFact of buildBirthProfileFacts(birthProfile)) {
    pushUniqueFact(mainFacts, profileFact)
  }
  if (mainFacts.length > 0) groups.push({ title: "Repères principaux", items: mainFacts })
  if (houseFacts.length > 0) groups.push({ title: "Maisons", items: houseFacts })
  if (sensitivePointFacts.length > 0) {
    groups.push({ title: "Positions sensibles", items: sensitivePointFacts })
  } else if (notablePlacements.length > 0) {
    groups.push({ title: "Positions sensibles", items: notablePlacements })
  }
  if (aspectFacts.length > 0) groups.push({ title: "Aspects majeurs", items: aspectFacts })

  return groups.length > 0 || methods.length > 0 || calculationReferenceMethods.length > 0
    ? { groups, methods, calculationReferenceMethods, sourceLabel: "Calculs du thème natal" }
    : null
}

/** Sélectionne les marqueurs affichés en en-tête sans recalculer l'astrologie côté React. */
function buildHighlightFacts(
  calculationFacts: NatalCalculationFactsViewModel | null,
): NatalHighlightFactViewModel[] {
  if (!calculationFacts) return []

  const mainGroup =
    calculationFacts.groups.find((group) => group.title === "Repères principaux") ??
    calculationFacts.groups[0]
  const allItems = calculationFacts.groups.flatMap((group) => group.items)
  const selected = new Map<string, NatalCalculationFactItemViewModel>()

  for (const label of HIGHLIGHT_FACT_LABELS) {
    const item = mainGroup?.items.find((candidate) => candidate.label === label)
    if (item) selected.set(item.label, item)
  }

  for (const item of allItems) {
    if (selected.size >= 3) break
    if (!selected.has(item.label)) selected.set(item.label, item)
  }

  return Array.from(selected.values()).slice(0, 3)
}

function emptyViewModel(
  metadata: ReadingMetadata,
  message: string,
  calculationFacts: NatalCalculationFactsViewModel | null = null,
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
    explanations: [],
    calculationFacts,
    highlightFacts: buildHighlightFacts(calculationFacts),
    disclaimer: null,
    error: null,
  }
}

function successViewModel(
  reading: Record<string, unknown>,
  metadata: ReadingMetadata,
  calculationFacts: NatalCalculationFactsViewModel | null,
  explanations: NatalReadingChapterViewModel[] = [],
): NatalInterpretationViewModel {
  const summary = asRecord(reading.summary)
  const legal = asRecord(reading.legal)
  const chapters = buildChapters(reading)
  const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"

  return {
    status: "success",
    title: localizedMetadataText(summary?.title) ?? "Lecture natale",
    shortText: asText(summary?.short_text),
    tier: metadata.tier,
    variant: metadata.variant,
    label: labelForReading(metadata.tier),
    completeness: metadata.completeness,
    isPartial,
    chapters,
    explanations,
    calculationFacts,
    highlightFacts: buildHighlightFacts(calculationFacts),
    disclaimer: asText(legal?.disclaimer),
    error: null,
  }
}

/** Convertit un job Astral ou une enveloppe gateway en modele stable pour l'UI publique. */
export function buildNatalInterpretationViewModel(
  job: AstralJobResponse | undefined,
  fallbackPlan?: AstralPlan,
  birthProfile?: BirthProfileData | null,
): NatalInterpretationViewModel | null {
  const result = asRecord(job?.result)
  if (!result) return null

  const metadata = extractMetadata(job, fallbackPlan)
  const calculationFacts = buildCalculationFacts(result, birthProfile)
  const explanationsReading = resultExplanationsContainer(result)
  const legacyReading = legacyBasicReading(result)
  const readingResponse = resolveReadingContainer(result)
  if (!readingResponse) {
    if (explanationsReading) {
      return successViewModel(explanationsReading, metadata, calculationFacts)
    }

    if (legacyReading) {
      return successViewModel(legacyReading, metadata, calculationFacts)
    }

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
        explanations: [],
        calculationFacts,
        highlightFacts: buildHighlightFacts(calculationFacts),
        disclaimer: null,
        error: null,
      }
    }
    return emptyViewModel(
      metadata,
      "La lecture est disponible mais sa forme publique n'est pas reconnue.",
      calculationFacts,
    )
  }

  const responseStatus = asText(readingResponse.status)?.toLowerCase()
  if (responseStatus === "failed" || responseStatus === "safety_rejected") {
    const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"
    return {
      status: responseStatus,
      title: responseStatus === "safety_rejected" ? "Lecture non générée" : "Lecture indisponible",
      shortText: null,
      tier: metadata.tier,
      variant: metadata.variant,
      label: labelForReading(metadata.tier),
      completeness: metadata.completeness,
      isPartial,
      chapters: [],
      explanations: [],
      calculationFacts,
      highlightFacts: buildHighlightFacts(calculationFacts),
      disclaimer: null,
      error: resolveError(readingResponse),
    }
  }

  const reading = asRecord(readingResponse.reading)
  if (!reading) {
    if (explanationsReading) {
      return successViewModel(explanationsReading, metadata, calculationFacts)
    }

    if (legacyReading) {
      return successViewModel(legacyReading, metadata, calculationFacts)
    }

    return emptyViewModel(
      metadata,
      "La lecture est disponible mais ne contient pas de texte public.",
      calculationFacts,
    )
  }

  if (!hasChapterText(reading) && hasChapterText(legacyReading ?? {}) && legacyReading) {
    return successViewModel(legacyReading, metadata, calculationFacts)
  }

  return successViewModel(reading, metadata, calculationFacts, explanationChapters(explanationsReading))
}
