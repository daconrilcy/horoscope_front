import type { DailyPredictionResponse, DailyPredictionAstroFoundation } from '../types/dailyPrediction';

export function mapAstroFoundation(prediction: DailyPredictionResponse): DailyPredictionAstroFoundation | null {
  if (prediction.astro_foundation) {
    return prediction.astro_foundation;
  }

  return null; // No fallback possible for this section if data is missing
}
