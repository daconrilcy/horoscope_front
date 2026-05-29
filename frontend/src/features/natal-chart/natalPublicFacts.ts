// Helpers de lecture publique du theme natal: aucune regle astrologique n'est recalculee ici.
import type {
  AspectResult,
  AstralPoint,
  DominantAspect,
  HouseResult,
  InterpretationAdapterResult,
  PlanetPosition,
} from "../../api/natalChart"

export type PublicCopyLang = "fr" | "en" | "es" | "de"

export type AstrologyLabelers = {
  translatePlanet: (code: string) => string
  translateSign: (code: string) => string
  translateHouse: (house: number) => string
  /** Connecteur de placement (« en », « in ») selon la locale active. */
  placementIn?: string
}

const DEFAULT_PLACEMENT_IN = " en "

const ASTRAL_POINT_CODES: Record<string, readonly string[]> = {
  NORTH: ["NORTH_NODE", "TRUE_NODE", "MEAN_NODE", "north_node", "true_node", "mean_node"],
  SOUTH: ["SOUTH_NODE", "south_node"],
}

/** Lit le code d'un point astral public (`code` backend ou `point_code` legacy). */
export function getAstralPointCode(point: AstralPoint): string {
  return (point.point_code ?? point.code ?? "").trim()
}

function normalizeToken(value: string): string {
  return value.trim().toUpperCase().replace(/-/g, "_")
}

function matchesAstralPointCode(pointCode: string, requestedCodes: string[]): boolean {
  const normalizedPoint = normalizeToken(pointCode)
  if (!normalizedPoint) return false
  for (const requested of requestedCodes) {
    const normalizedRequested = normalizeToken(requested)
    if (normalizedPoint === normalizedRequested) return true
    if (normalizedRequested.includes("NORTH")) {
      if (ASTRAL_POINT_CODES.NORTH.some((alias) => normalizeToken(alias) === normalizedPoint)) return true
    }
    if (normalizedRequested.includes("SOUTH")) {
      if (ASTRAL_POINT_CODES.SOUTH.some((alias) => normalizeToken(alias) === normalizedPoint)) return true
    }
  }
  return false
}

export function getPlanetPosition(positions: PlanetPosition[] | undefined, code: string): PlanetPosition | null {
  return positions?.find((position) => position.planet_code.toUpperCase() === code.toUpperCase()) ?? null
}

export function getAstralPoint(points: AstralPoint[] | undefined, codes: string[]): AstralPoint | null {
  return points?.find((point) => matchesAstralPointCode(getAstralPointCode(point), codes)) ?? null
}

export function getHouse(houses: HouseResult[] | undefined, number: number): HouseResult | null {
  return houses?.find((house) => house.number === number) ?? null
}

function astralPointSign(point: AstralPoint): string | null {
  const raw = point.sign_code ?? point.sign
  return raw ? raw.trim() : null
}

function astralPointHouse(point: AstralPoint): number | null {
  const raw = point.house_number ?? point.house
  return typeof raw === "number" ? raw : null
}

function formatAstralPointLabel(code: string, labels: AstrologyLabelers): string {
  const normalized = normalizeToken(code)
  if (normalized.includes("NORTH")) return labels.translatePlanet("NORTH_NODE")
  if (normalized.includes("SOUTH")) return labels.translatePlanet("SOUTH_NODE")
  return labels.translatePlanet(code)
}

export function formatPlacement(
  item: PlanetPosition | AstralPoint | HouseResult | null | undefined,
  labels: AstrologyLabelers,
  fallback: string,
): string {
  if (!item) return fallback
  const placementIn = labels.placementIn ?? DEFAULT_PLACEMENT_IN
  if ("planet_code" in item) {
    return `${labels.translatePlanet(item.planet_code)}${placementIn}${labels.translateSign(item.sign_code)}`
  }
  if ("number" in item) {
    return labels.translateHouse(item.number)
  }
  const point = item as AstralPoint
  const code = getAstralPointCode(point)
  const signRaw = astralPointSign(point)
  const sign = signRaw ? labels.translateSign(signRaw.toUpperCase()) : fallback
  const houseNumber = astralPointHouse(point)
  const house = typeof houseNumber === "number" ? `, ${labels.translateHouse(houseNumber)}` : ""
  return `${formatAstralPointLabel(code, labels)}${placementIn}${sign}${house}`
}

export function getAdapterTexts(adapter: InterpretationAdapterResult | null | undefined, category?: string): string[] {
  const signals = adapter?.signals ?? []
  const themes = adapter?.activated_themes ?? []
  return [
    ...signals
      .filter((signal) => !category || signal.theme_category === category || signal.semantic_category === category)
      .map((signal) => signal.explanation_fact ?? signal.theme ?? signal.signal)
      .filter((value): value is string => Boolean(value)),
    ...themes
      .filter((theme) => !category || theme.theme_category === category)
      .map((theme) => theme.theme)
      .filter((value): value is string => Boolean(value)),
  ]
}

export function firstAvailable(items: Array<string | null | undefined>, fallback: string): string {
  return items.find((item): item is string => Boolean(item && item.trim().length > 0)) ?? fallback
}

export type ResolvedMajorAspect = DominantAspect & {
  aspect_code: string
  planet_a: string
  planet_b: string
}

function aspectIdentityKey(aspect: Pick<AspectResult, "planet_a" | "planet_b" | "aspect_code">): string {
  return `${aspect.planet_a}:${aspect.planet_b}:${aspect.aspect_code}`.toLowerCase()
}

/**
 * Relie le ranking public `chart_balance.dominant_aspects` aux aspects deja calcules,
 * sans re-scorer ni re-trier localement au-dela du rang fourni par l'API.
 */
export function resolveMajorAspects(
  dominantAspects: DominantAspect[] | undefined,
  aspects: AspectResult[] | undefined,
  limit = 10,
): ResolvedMajorAspect[] {
  const rankedDominant = [...(dominantAspects ?? [])]
    .filter((entry) => typeof entry.rank === "number" || entry.code || entry.aspect_code)
    .sort((current, next) => (current.rank ?? Number.MAX_SAFE_INTEGER) - (next.rank ?? Number.MAX_SAFE_INTEGER))

  const usedAspectKeys = new Set<string>()
  const resolved: ResolvedMajorAspect[] = []

  for (const entry of rankedDominant) {
    if (resolved.length >= limit) break
    const dominantCode = (entry.code ?? entry.aspect_code ?? "").trim().toLowerCase()
    if (!dominantCode && !(entry.planet_a && entry.planet_b && entry.aspect_code)) {
      continue
    }

    if (entry.planet_a && entry.planet_b && entry.aspect_code) {
      resolved.push({
        ...entry,
        aspect_code: entry.aspect_code,
        planet_a: entry.planet_a,
        planet_b: entry.planet_b,
      })
      continue
    }

    const match = aspects?.find((aspect) => {
      const key = aspectIdentityKey(aspect)
      if (usedAspectKeys.has(key)) return false
      return (aspect.aspect_code ?? "").trim().toLowerCase() === dominantCode
    })

    if (!match?.planet_a || !match.planet_b || !match.aspect_code) continue

    usedAspectKeys.add(aspectIdentityKey(match))
    resolved.push({
      ...entry,
      aspect_code: match.aspect_code,
      planet_a: match.planet_a,
      planet_b: match.planet_b,
      dominance_score: entry.dominance_score ?? entry.score,
    })
  }

  return resolved
}
