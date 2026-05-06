// Helper de synthese quotidienne expose uniquement les champs editoriaux canoniques.
import type { DailyPredictionResponse } from '../types/dailyPrediction';

/**
 * Extrait le resume editorial canonique depuis une prediction quotidienne.
 */
export function getDailyEditorialSummary(prediction: DailyPredictionResponse): string {
  if (prediction.daily_synthesis) {
    return prediction.daily_synthesis;
  }

  if (prediction.day_climate?.summary) {
    return prediction.day_climate.summary;
  }

  return '';
}
