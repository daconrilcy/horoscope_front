// Normalisation des contrats d'interpretation natale Astral pour l'affichage public.
import type { AstralJobResponse, AstralPlan } from "../../api/astral"

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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

function asText(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null
}

function asTextArray(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.map(asText).filter((item): item is string => Boolean(item))
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

function labelForReading(tier: NatalReadingTier, isPartial: boolean): string {
  if (isPartial) return "Lecture partielle"
  if (tier === "premium") return "Lecture approfondie"
  if (tier === "basic") return "Lecture structuree"
  if (tier === "free") return "Lecture courte"
  return "Lecture Astral"
}

function confidenceLabel(value: unknown): string | null {
  const text = asText(value)?.toLowerCase()
  if (text === "high") return "Confiance elevee"
  if (text === "medium") return "Confiance moyenne"
  if (text === "low") return "Confiance limitee"
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

function emptyViewModel(metadata: ReadingMetadata, message: string): NatalInterpretationViewModel {
  const isPartial = metadata.variant === "simplified" || metadata.completeness === "partial"
  return {
    status: "empty",
    title: "Lecture natale indisponible",
    shortText: message,
    tier: metadata.tier,
    variant: metadata.variant,
    label: labelForReading(metadata.tier, isPartial),
    completeness: metadata.completeness,
    isPartial,
    chapters: [],
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
        label: labelForReading(metadata.tier, isPartial),
        completeness: metadata.completeness,
        isPartial,
        chapters: [],
        disclaimer: null,
        error: null,
      }
    }
    return emptyViewModel(metadata, "La lecture est disponible mais sa forme publique n'est pas reconnue.")
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
      label: labelForReading(metadata.tier, isPartial),
      completeness: metadata.completeness,
      isPartial,
      chapters: [],
      disclaimer: null,
      error: resolveError(readingResponse),
    }
  }

  const reading = asRecord(readingResponse.reading)
  if (!reading) return emptyViewModel(metadata, "La lecture est disponible mais ne contient pas de texte public.")

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
    label: labelForReading(metadata.tier, isPartial),
    completeness: metadata.completeness,
    isPartial,
    chapters,
    disclaimer: asText(legal?.disclaimer),
    error: null,
  }
}
