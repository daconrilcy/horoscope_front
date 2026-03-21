export interface DailyPredictionMeta {
  date_local: string;
  timezone: string;
  computed_at: string;
  reference_version: string;
  ruleset_version: string;
  was_reused: boolean;
  house_system_effective: string | null;
  is_provisional_calibration: boolean | null;
  calibration_label: string | null;
  v3_evidence_version?: string | null;
  payload_version?: string;
}


export interface DailyPredictionCategory {
  code: string;
  note_20: number;
  raw_score: number;
  power: number;
  volatility: number;
  rank: number;
  is_provisional?: boolean | null;
  summary: string | null;
}

export interface DailyPredictionDriver {
  label?: string | null;
  event_type?: string | null;
  [key: string]: unknown;
}

export interface DailyPredictionMovement {
  strength: number;
  previous_composite: number;
  next_composite: number;
  delta_composite: number;
  direction: "rising" | "falling" | "recomposition";
}

export interface DailyPredictionCategoryDelta {
  code: string;
  direction: "up" | "down" | "stable";
  delta_score: number;
  delta_intensity: number;
  delta_rank: number | null;
}

export interface DailyPredictionTurningPoint {
  occurred_at_local: string;
  severity: number;
  summary: string | null;
  drivers: DailyPredictionDriver[];
  // Story 43.1
  change_type?: string;
  impacted_categories?: string[];
  previous_categories?: string[];
  next_categories?: string[];
  primary_driver?: {
    event_type: string;
    body?: string;
    target?: string;
    aspect?: string;
    orb_deg?: number | null;
    phase?: string | null;
    priority?: number | null;
    base_weight?: number | null;
    metadata?: Record<string, unknown>;
  } | null;
  // Story 44.1
  movement?: DailyPredictionMovement | null;
  category_deltas?: DailyPredictionCategoryDelta[];
}

export interface DailyPredictionTimeBlock {
  start_local: string;
  end_local: string;
  tone_code: string;
  dominant_categories: string[];
  summary: string | null;
  turning_point: boolean;
}

export interface DailyPredictionSummary {
  overall_tone: string | null;
  overall_summary: string | null;
  calibration_note?: string | null;
  top_categories: string[];
  bottom_categories: string[];
  best_window: {
    start_local: string;
    end_local: string;
    dominant_category: string;
  } | null;
  main_turning_point: {
    occurred_at_local: string;
    severity: number;
    summary: string | null;
  } | null;
  low_score_variance?: boolean;
}

export interface DailyPredictionDecisionWindow {
  start_local: string;
  end_local: string;
  window_type: 'favorable' | 'prudence' | 'pivot';
  score: number;
  confidence: number;
  dominant_categories: string[];
}

export interface DailyPredictionDayClimate {
  label: string;
  tone: string;
  intensity: number;
  stability: number;
  summary: string;
  top_domains: string[];
  watchout: string | null;
  best_window_ref: string | null;
}

export interface DailyPredictionPublicDomainScore {
  key: string;
  label: string;
  internal_codes: string[];
  display_order: number;
  score_10: number;
  level: string;
  rank: number;
  note_20_internal: number;
  signal_label: string | null;
}

export interface DailyPredictionTimeWindow {
  period_key: string;
  time_range: string;
  label: string;
  regime: string;
  top_domains: string[];
  action_hint: string;
  astro_events: string[];
  narrative?: string | null;
}

export interface DailyPredictionTurningPointPublic {
  time: string;
  title: string;
  change_type: string;
  affected_domains: string[];
  what_changes: string;
  do: string;
  avoid: string;
  narrative?: string | null;
}

export interface DailyPredictionDailyAdvice {
  advice: string;
  emphasis: string;
}

export interface DailyPredictionBestWindow {
  time_range: string;
  label: string;
  why: string;
  recommended_actions: string[];
  is_pivot: boolean;
}

export interface AstroKeyMovement {
  planet: string;
  event_type: string;
  target: string | null;
  orb_deg: number | null;
  effect_label: string;
}

export interface AstroActivatedHouse {
  house_number: number;
  house_label: string;
  domain_label: string;
}

export interface AstroDominantAspect {
  aspect_type: string;
  planet_a: string;
  planet_b: string | null;
  tonality: string;
  effect_label: string;
}

export interface DailyPredictionAstroFoundation {
  headline: string;
  key_movements: AstroKeyMovement[];
  activated_houses: AstroActivatedHouse[];
  dominant_aspects: AstroDominantAspect[];
  interpretation_bridge: string;
}

export interface DailyPredictionIngress {
  text: string;
  time: string | null;
}

export interface DailyPredictionAstroDailyEvents {
  ingresses: DailyPredictionIngress[];
  aspects: string[];
  planet_positions?: string[];
  returns?: string[];
  progressions?: string[];
  nodes?: string[];
  sky_aspects?: string[];
  fixed_stars?: string[];
}

export interface DailyPredictionMicroTrend {
  category_code: string;
  z_score: number | null;
  percentile: number;
  rank: number;
  wording: string;
}

export interface DailyPredictionResponse {
  meta: DailyPredictionMeta;
  summary: DailyPredictionSummary;
  day_climate?: DailyPredictionDayClimate;
  daily_synthesis?: string | null;
  astro_events_intro?: string | null;
  daily_advice?: DailyPredictionDailyAdvice | null;
  has_llm_narrative: boolean;
  domain_ranking?: DailyPredictionPublicDomainScore[];
  time_windows?: DailyPredictionTimeWindow[];
  turning_point?: DailyPredictionTurningPointPublic;
  best_window?: DailyPredictionBestWindow;
  astro_foundation?: DailyPredictionAstroFoundation;
  astro_daily_events?: DailyPredictionAstroDailyEvents;
  categories: DailyPredictionCategory[];
  categories_internal?: DailyPredictionCategory[];
  timeline: DailyPredictionTimeBlock[];
  turning_points: DailyPredictionTurningPoint[];
  decision_windows?: DailyPredictionDecisionWindow[] | null;
  micro_trends?: DailyPredictionMicroTrend[];
}

export interface DailyHistoryItem {
  date_local: string;
  overall_tone: string | null;
  categories: Record<string, number>;
  pivot_count: number;
  computed_at: string;
  was_recomputed: boolean | null;
}

export interface DailyHistoryResponse {
  items: DailyHistoryItem[];
  total: number;
}
