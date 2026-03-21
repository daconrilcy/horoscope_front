import type { DailyPredictionResponse } from '../types/dailyPrediction';

/**
 * Extract the canonical editorial summary from a daily prediction.
 * Source priority:
 * 1. daily_synthesis (LLM generated)
 * 2. day_climate.summary (climat template)
 * 3. summary.overall_summary (legacy fallback)
 */
export function getDailyEditorialSummary(prediction: DailyPredictionResponse): string {
  if (prediction.daily_synthesis) {
    return prediction.daily_synthesis;
  }

  if (prediction.day_climate?.summary) {
    return prediction.day_climate.summary;
  }

  return prediction.summary.overall_summary || '';
}
