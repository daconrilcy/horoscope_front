import type { DailyPredictionResponse, DailyPredictionTurningPointPublic } from '../types/dailyPrediction';

export function mapTurningPoint(prediction: DailyPredictionResponse): DailyPredictionTurningPointPublic | null {
  if (prediction.turning_point) {
    return prediction.turning_point;
  }
  return null;
}
