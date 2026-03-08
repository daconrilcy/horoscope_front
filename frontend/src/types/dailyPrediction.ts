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
  summary: string | null;
}

export interface DailyPredictionDriver {
  label?: string | null;
  event_type?: string | null;
  [key: string]: unknown;
}

export interface DailyPredictionTurningPoint {
  occurred_at_local: string;
  severity: number | string;
  summary: string | null;
  drivers: DailyPredictionDriver[];
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
}

export interface DailyPredictionResponse {
  meta: DailyPredictionMeta;
  summary: DailyPredictionSummary;
  categories: DailyPredictionCategory[];
  timeline: DailyPredictionTimeBlock[];
  turning_points: DailyPredictionTurningPoint[];
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
