// Domaine API natal chart: contrats, requetes, hooks et effets navigateur associes.
import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch, ApiError, parseApiErrorDetails, type ApiResponseEnvelope } from "../client"
import { getSubjectFromAccessToken, useAccessTokenSnapshot } from "../../utils/authToken"
import { ANONYMOUS_SUBJECT } from "../../utils/constants"

export type PlanetPosition = {
  planet_code: string
  longitude: number
  sign_code: string
  house_number: number
  is_retrograde?: boolean
  speed_longitude?: number
}

export type HouseResult = {
  number: number
  cusp_longitude: number
}

export type AspectResult = {
  aspect_code: string
  planet_a: string
  planet_b: string
  angle: number
  orb: number
  orb_used?: number | null
}

export type ChartSectResult = {
  chart_sect: string
  sun_horizon_position: string
  sun_above_horizon: boolean
  calculation_basis: string
  reference_system: string
}

export type PlanetSectCondition = {
  planet_code: string
  chart_sect: string
  intrinsic_sect: string
  planet_sect_condition: string
  is_in_sect: boolean
  is_out_of_sect: boolean
  calculation_basis: string
  reference_system: string
}

export type DignityBreakdownItem = {
  type?: string
  dignity_type?: string
  dignity_type_code?: string
  source?: string
  reason?: string
  score_value?: number
  score?: number
  [key: string]: string | number | boolean | null | undefined
}

export type DignityPlanetPayload = {
  sect_condition?: PlanetSectCondition | null
  essential_score?: number
  accidental_score?: number
  total_score?: number
  functional_strength_score?: number
  expression_quality_score?: number
  intensity_score?: number
  essential_breakdown?: DignityBreakdownItem[]
  accidental_breakdown?: DignityBreakdownItem[]
}

export type DignitiesPayload = {
  score_profile?: string
  tradition?: string
  reference_version?: string
  sect?: ChartSectResult | null
  planets?: Record<string, DignityPlanetPayload>
}

export type PlanetConditionProfile = {
  planet_code?: string
  score_profile?: string
  tradition?: string
  reference_version?: string
  sect?: string
  functional_strength?: number
  visibility?: number
  stability?: number
  intensity?: number
  coherence?: number
  support?: number
  constraint?: number
  ranking_score?: number
  condition_level?: string
  breakdown?: Array<Record<string, string | number | boolean | null>>
  explanation_facts?: Array<Record<string, string | number | boolean | null>>
}

export type PlanetConditionSignal = {
  code?: string
  label?: string
  axis?: string
  level?: string
  level_min?: number
  level_max?: number
  axis_value?: number
  interpretation_use?: string
  priority_weight?: number
  prompt_hint?: string | null
}

export type AdvancedCondition = {
  planet_code?: string
  condition_code?: string
  condition_type?: string
  score_effect?: number
  axis_weights?: Record<string, number>
  evidence?: string[]
}

export type TraditionalHayzCondition = {
  planet_code: string
  is_hayz: boolean
  sect_match: boolean
  hemisphere_match?: boolean | null
  sign_gender_match?: boolean | null
  chart_sect: string
  intrinsic_sect: string
  planet_sect_condition: string
  planet_horizon_position: string
  sign_gender: string
  calculation_basis: string
  reference_system: string
  evidence?: string[]
}

export type TraditionalRejoicingCondition = {
  planet_code: string
  is_rejoicing: boolean
  current_house?: number | null
  rejoicing_house?: number | null
  calculation_basis: string
  reference_system: string
  evidence?: string[]
}

export type TraditionalPlanetCondition = {
  planet_code: string
  hayz: TraditionalHayzCondition
  rejoicing: TraditionalRejoicingCondition
}

export type TraditionalConditionsPayload = Record<string, TraditionalPlanetCondition>

export type DominantPlanetFactor = {
  factor_code?: string
  raw_value?: number
  normalized_value?: number
  weight?: number
  weighted_score?: number
  reason?: string
}

export type DominantPlanet = {
  planet_code?: string
  score?: number
  rank?: number
  factors?: DominantPlanetFactor[]
  explanation_facts?: string[]
}

export type DominantPlanetsResult = {
  top_planet_code?: string | null
  chart_ruler_code?: string | null
  most_elevated_planet_code?: string | null
  planets?: DominantPlanet[]
}

export type DominantAspect = {
  /** Code de dominance public (`chart_balance.dominant_aspects[].code`). */
  code?: string
  score?: number
  source?: string
  aspect_code?: string
  planet_a?: string
  planet_b?: string
  rank?: number
  dominance_score?: number
  reasons?: string[]
  meaning?: string
  manifestation?: string
  positive_expression?: string
  attention_point?: string
}

export type ChartSignature = {
  primary_element?: string | null
  primary_modality?: string | null
  primary_polarity?: string | null
}

export type ChartBalance = {
  dominant_aspects?: DominantAspect[]
}

export type AstralPoint = {
  /** Forme publique backend (`json_builder._serialize_astral_points`). */
  code?: string
  sign?: string | null
  house?: number | null
  longitude?: number | null
  degree_in_sign?: number | null
  /** Alias legacy/tests. */
  point_code?: string
  sign_code?: string | null
  house_number?: number | null
}

export type InterpretationAdapterSignal = {
  signal?: string
  theme?: string
  source_type?: string
  source_code?: string
  priority?: string
  priority_rank?: number
  weight?: number
  semantic_category?: string
  theme_category?: string
  explanation_fact?: string
}

export type InterpretationAdapterTheme = {
  theme?: string
  theme_category?: string
  activation_score?: number
  priority?: string
  priority_rank?: number
  contributing_signals?: string[]
}

export type InterpretationAdapterResult = {
  signals?: InterpretationAdapterSignal[]
  activated_themes?: InterpretationAdapterTheme[]
  dominant_topics?: string[]
  dominant_axes?: string[]
  tension_patterns?: string[]
  support_patterns?: string[]
  critical_patterns?: string[]
  narrative_priorities?: string[]
}

type NatalResult = {
  reference_version: string
  ruleset_version: string
  engine?: string
  zodiac?: string
  frame?: string
  ayanamsa?: string | null
  altitude_m?: number | null
  ephemeris_path_version?: string | null
  ephemeris_path_hash?: string | null
  prepared_input: {
    birth_datetime_local: string
    birth_datetime_utc: string
    timestamp_utc: number
    julian_day: number
    birth_timezone: string
    jd_ut: number
    timezone_used: string
  }
  planet_positions: PlanetPosition[]
  houses: HouseResult[]
  aspects: AspectResult[]
  dignities?: DignitiesPayload
  planet_condition_profiles?: Record<string, PlanetConditionProfile>
  planet_condition_signals?: Record<string, PlanetConditionSignal[]>
  advanced_conditions?: AdvancedCondition[]
  traditional_conditions?: TraditionalConditionsPayload | null
  dominant_planets?: DominantPlanetsResult | null
  interpretation_adapter?: InterpretationAdapterResult | null
  chart_signature?: ChartSignature | null
  chart_balance?: ChartBalance | null
  astral_points?: AstralPoint[]
}

export type LatestNatalChart = {
  chart_id: string
  result: NatalResult
  metadata: {
    reference_version: string
    ruleset_version: string
    engine: string
    house_system: string
    ephemeris_path_version?: string | null
    ephemeris_path_hash?: string | null
    degraded_mode?: "no_location" | "no_time" | "no_location_no_time" | null
  }
  created_at: string
  astro_profile?: {
    sun_sign_code: string | null
    ascendant_sign_code: string | null
    missing_birth_time: boolean
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await parseApiErrorDetails(response, {})
    throw new ApiError(
      error.code,
      error.message,
      response.status,
      error.requestId ?? undefined,
    )
  }

  const payload = (await response.json()) as ApiResponseEnvelope<T>
  return payload.data
}

async function handleResponsePossiblyUnwrapped<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await parseApiErrorDetails(response, {})
    throw new ApiError(
      error.code,
      error.message,
      response.status,
      error.requestId ?? undefined,
    )
  }

  const payload = (await response.json()) as T | { data: T }
  if (
    payload !== null &&
    typeof payload === "object" &&
    "data" in payload &&
    (payload as { data?: T }).data !== undefined
  ) {
    return (payload as { data: T }).data
  }
  return payload as T
}

async function fetchLatestNatalChart(accessToken: string): Promise<LatestNatalChart> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/natal-chart/latest`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })

  return handleResponse<LatestNatalChart>(response)
}

export async function generateNatalChart(
  accessToken: string,
  accurate: boolean = false,
): Promise<LatestNatalChart> {
  const response = await apiFetch(`${API_BASE_URL}/v1/users/me/natal-chart`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ accurate }),
  })

  return handleResponse<LatestNatalChart>(response)
}

export function useLatestNatalChart() {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const fetchForCurrentUser = async () => {
    if (!accessToken) {
      throw new ApiError("unauthorized", "access token is required", 401)
    }
    return fetchLatestNatalChart(accessToken)
  }
  return useQuery({
    queryKey: ["latest-natal-chart", tokenSubject],
    queryFn: fetchForCurrentUser,
    enabled: Boolean(accessToken),
    retryOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 2
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// --- Interpretation ---

export type AstroSection = {
  key: string
  heading: string
  content: string
}

export type AstroInterpretation = {
  title: string
  summary: string
  sections: AstroSection[]
  highlights: string[]
  advice: string[]
  evidence: string[]
  disclaimers?: string[]
}

export type NarrativeChapterKey =
  | "personality"
  | "emotional_world"
  | "relationships"
  | "vocation"
  | "evolution_path"

export type NarrativeNatalReadingChapterV1 = {
  key: NarrativeChapterKey
  title: string
  narrative: string
  key_points: string[]
}

export type UsedAstrologicalElementV1 = {
  astrological_label: string
  consequence: string
}

export type BasicNatalPublicEvidenceV2 = {
  source_id?: string | null
  source_type?: string | null
  label: string
  meaning: string
  theme?: string
  used_in_sections?: string[] | null
}

export type BasicNatalPublicThemeV2 = {
  title: string
  narrative: string
  public_evidence: BasicNatalPublicEvidenceV2[]
}

export type BasicNatalSynthesisV2 = {
  title: string
  introduction: string
  themes: BasicNatalPublicThemeV2[]
  conclusion: string
  public_evidence: BasicNatalPublicEvidenceV2[]
}

export type BasicNatalInterpretationV2 = {
  locale: string
  level: "basic"
  engine_version: "basic-natal-reading-v1"
  schema_version: "basic_natal_interpretation_v2"
  taxonomy_version: "basic-natal-theme-taxonomy-v1"
  salience_version: "basic-natal-salience-v1"
  prompt_version: "basic-natal-draft-prompt-v1"
  validator_version: "basic-natal-validator-v1"
  interpretation: BasicNatalSynthesisV2
  limitations: string[]
  disclaimers: string[]
  public_evidence: BasicNatalPublicEvidenceV2[]
}

export type NarrativeNatalReadingV1 = {
  contract_version: "narrative_natal_reading_v1"
  editorial_profile: "free" | "basic" | "premium"
  chapters: NarrativeNatalReadingChapterV1[]
  used_astrological_elements: UsedAstrologicalElementV1[]
}

export type InterpretationMeta = {
  id?: number | null
  level: "short" | "complete"
  use_case: string
  persona_id: string | null
  persona_name: string | null
  prompt_version_id: string | null
  validation_status: string
  repair_attempted: boolean
  fallback_triggered: boolean
  was_fallback: boolean
  latency_ms: number | null
  request_id: string | null
  persisted_at: string | null
}

type ThemeNatalPublicChapter = {
  key?: string
  title?: string
  text?: string
}

export type ThemeNatalReadingPublicPayload = {
  chart_id?: string
  schema_version?: string
  title?: string
  introduction?: string
  chapters?: ThemeNatalPublicChapter[]
  conclusion?: string
  use_case?: string | null
  interpretation: AstroInterpretation
  meta: InterpretationMeta
  degraded_mode: string | null
  narrative_natal_reading_v1?: NarrativeNatalReadingV1 | null
  basic_natal_interpretation_v2?: BasicNatalInterpretationV2 | null
  disclaimers?: string[]
}

export type NatalInterpretationListItem = {
  id: number
  chart_id: string
  level: "short" | "complete"
  persona_id: string | null
  persona_name: string | null
  module: string | null
  created_at: string
  use_case: string
  prompt_version_id: string | null
  was_fallback: boolean
}

export type NatalInterpretationListResponse = {
  items: NatalInterpretationListItem[]
  total: number
  limit: number
  offset: number
}

export type NatalPdfTemplateItem = {
  key: string
  name: string
  description: string | null
  locale: string
  is_default: boolean
}

export type NatalPdfTemplateListResponse = {
  items: NatalPdfTemplateItem[]
}

export type ThemeNatalReadingAction = "preview" | "generate_full" | "regenerate" | "download"

export type ThemeNatalReadingSlotState =
  | "accepted"
  | "generating"
  | "failed_retriable"
  | "locked"
  | "paywall"
  | "rejected"

type ThemeNatalReadingApiState = ThemeNatalReadingSlotState | "readonly"

export type ThemeNatalReadingCommandRequest = {
  chart_id: string
  action: ThemeNatalReadingAction
  persona_profile_id?: string | null
  locale: string
  client_request_id: string
}

export type ThemeNatalReadingCommandResponse = {
  state: ThemeNatalReadingApiState
  data: unknown | null
  details: Record<string, unknown>
}

export type UseThemeNatalReadingResult = Omit<
  ReturnType<typeof useQuery<ThemeNatalReadingCommandResponse>>,
  "data"
> & {
  data: ThemeNatalReadingPublicPayload | null
  state: ThemeNatalReadingSlotState | null
  details: Record<string, unknown>
}

/** Envoie une intention produit publique sans exposer les anciens controles techniques LLM. */
export async function requestThemeNatalReadingAction(
  accessToken: string,
  command: ThemeNatalReadingCommandRequest,
): Promise<ThemeNatalReadingCommandResponse> {
  const response = await apiFetch(`${API_BASE_URL}/v1/theme-natal/readings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(command),
  })

  if (!response.ok) {
    const error = await parseApiErrorDetails(response, {})
    throw new ApiError(
      error.code,
      error.message,
      response.status,
      error.requestId ?? undefined,
    )
  }

  return handleResponsePossiblyUnwrapped<ThemeNatalReadingCommandResponse>(response)
}

function normalizeThemeNatalReadingState(
  response?: ThemeNatalReadingCommandResponse,
): ThemeNatalReadingSlotState | null {
  if (!response) return null
  if (response.state === "readonly") return "accepted"
  if (
    response.state === "locked" &&
    response.details.reason_code === "full_reading_requires_paid_entitlement"
  ) {
    return "paywall"
  }
  return response.state
}

type ThemeNatalPublicData = {
  schema_version?: string
  title?: string
  introduction?: string
  chapters?: ThemeNatalPublicChapter[]
  conclusion?: string
  disclaimers?: string[]
}

function isThemeNatalPublicData(value: unknown): value is ThemeNatalPublicData {
  if (value === null || typeof value !== "object") return false
  const schemaVersion = "schema_version" in value ? value.schema_version : undefined
  return typeof schemaVersion === "string" && schemaVersion.startsWith("theme_natal")
}

function normalizeThemeNatalReadingPublicPayload(
  command: ThemeNatalReadingCommandRequest,
  response?: ThemeNatalReadingCommandResponse,
): ThemeNatalReadingPublicPayload | null {
  if (!response || response.state !== "accepted" || !response.data) return null
  if (!isThemeNatalPublicData(response.data)) return null

  const chapters = response.data.chapters ?? []
  return {
    chart_id: command.chart_id,
    schema_version: response.data.schema_version,
    title: response.data.title,
    introduction: response.data.introduction,
    chapters,
    conclusion: response.data.conclusion,
    use_case: null,
    interpretation: {
      title: response.data.title ?? "",
      summary: response.data.introduction ?? "",
      highlights: chapters.map((chapter) => chapter.title ?? "").filter(Boolean),
      sections: chapters.map((chapter, index) => ({
        key: chapter.key ?? `chapter-${index + 1}`,
        heading: chapter.title ?? "",
        content: chapter.text ?? "",
      })),
      advice: response.data.conclusion ? [response.data.conclusion] : [],
      evidence: [],
      disclaimers: response.data.disclaimers ?? [],
    },
    meta: {
      id: null,
      level: "complete",
      use_case: "theme_natal_reading",
      persona_id: command.persona_profile_id ?? null,
      persona_name: null,
      prompt_version_id: null,
      validation_status: "accepted",
      repair_attempted: false,
      fallback_triggered: false,
      was_fallback: false,
      latency_ms: null,
      request_id: command.client_request_id,
      persisted_at: null,
    },
    degraded_mode: null,
    disclaimers: response.data.disclaimers ?? [],
  }
}

export function useNatalInterpretationsList(options: {
  enabled: boolean
  chartId?: string
  level?: "short" | "complete"
  limit?: number
  offset?: number
}) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT

  return useQuery({
    queryKey: [
      "natal-interpretations-list",
      tokenSubject,
      options.chartId,
      options.level,
      options.limit,
      options.offset,
    ],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      const emptyHistory: NatalInterpretationListResponse = {
        items: [],
        total: 0,
        limit: options.limit ?? 20,
        offset: options.offset ?? 0,
      }
      return emptyHistory
    },
    enabled: options.enabled && Boolean(accessToken),
    staleTime: 1000 * 60 * 5,
  })
}

export function useNatalPdfTemplates(options: { enabled: boolean; locale?: string }) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  return useQuery({
    queryKey: ["natal-pdf-templates", tokenSubject, options.locale],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      return {
        items: [
          {
            key: "theme_natal_default",
            name: options.locale === "fr" ? "Theme natal" : "Natal chart",
            description: null,
            locale: options.locale ?? "fr",
            is_default: true,
          },
        ],
      }
    },
    enabled: options.enabled && Boolean(accessToken),
    staleTime: 1000 * 60 * 10,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 1
    },
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  })
}

export function useNatalInterpretationById(options: {
  enabled: boolean
  interpretationId?: number
  locale?: string
}) {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT

  return useQuery({
    queryKey: ["natal-interpretation-by-id", tokenSubject, options.interpretationId, options.locale],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      if (!options.interpretationId) {
        throw new Error("interpretationId is required")
      }
      throw new ApiError(
        "historical_interpretation_read_removed",
        `Historical interpretation read is no longer public: ${options.interpretationId}`,
        410,
      )
    },
    enabled: options.enabled && Boolean(accessToken) && Boolean(options.interpretationId),
    staleTime: 1000 * 60 * 10,
  })
}

export function useNatalInterpretation(options: {
  enabled: boolean
  chartId?: string
  action: ThemeNatalReadingAction
  personaProfileId?: string | null
  locale?: string
  clientRequestId?: string
}): UseThemeNatalReadingResult {
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const canRunInterpretationQuery =
    options.enabled &&
    Boolean(accessToken) &&
    Boolean(options.chartId) &&
    Boolean(options.clientRequestId)
  const command: ThemeNatalReadingCommandRequest | null =
    options.chartId && options.clientRequestId
      ? {
          chart_id: options.chartId,
          action: options.action,
          persona_profile_id: options.personaProfileId ?? null,
          locale: options.locale || "fr-FR",
          client_request_id: options.clientRequestId,
        }
      : null

  const { data: actionResponse, ...query } = useQuery({
    queryKey: [
      "theme-natal-reading-action",
      tokenSubject,
      options.chartId,
      options.action,
      options.personaProfileId,
      options.locale,
      options.clientRequestId,
    ],
    queryFn: async () => {
      if (!accessToken) {
        throw new ApiError("unauthorized", "access token is required", 401)
      }
      if (!command) {
        throw new ApiError("invalid_request", "theme natal product action is incomplete", 400)
      }
      return requestThemeNatalReadingAction(accessToken, command)
    },
    enabled: canRunInterpretationQuery,
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 1
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  })

  return {
    ...query,
    data: command ? normalizeThemeNatalReadingPublicPayload(command, actionResponse) : null,
    state: normalizeThemeNatalReadingState(actionResponse),
    details: actionResponse?.details ?? {},
  }
}
