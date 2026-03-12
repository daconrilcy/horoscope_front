export interface DailyPredictionMeta {
  date_local: string;
  timezone: string;
  computed_at: string;
  reference_version: string;
  ruleset_version: string;
  was_reused: boolean;
  house_system_effective: string | null;
  is_provisional_calibration?: boolean | null;
  calibration_label?: string | null;
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
  severity: number | string;
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
    severity: number | string;
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

export interface DailyPredictionResponse {
  meta: DailyPredictionMeta;
  summary: DailyPredictionSummary;
  categories: DailyPredictionCategory[];
  timeline: DailyPredictionTimeBlock[];
  turning_points: DailyPredictionTurningPoint[];
  decision_windows?: DailyPredictionDecisionWindow[] | null;
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
