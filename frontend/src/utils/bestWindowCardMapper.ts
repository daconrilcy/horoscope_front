import type { DailyPredictionResponse, DailyPredictionBestWindow } from '../types/dailyPrediction';

export function mapBestWindow(prediction: DailyPredictionResponse): DailyPredictionBestWindow | null {
  if (prediction.best_window) {
    return prediction.best_window;
  }
  return null;
}
