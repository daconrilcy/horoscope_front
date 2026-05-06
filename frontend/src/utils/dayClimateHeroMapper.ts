import type { DailyPredictionResponse, DailyPredictionDayClimate } from '../types/dailyPrediction';

export function mapDayClimate(prediction: DailyPredictionResponse): DailyPredictionDayClimate | null {
  if (prediction.day_climate) {
    return prediction.day_climate;
  }
  return null;
}
