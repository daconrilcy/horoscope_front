import type { DailyPredictionResponse, DailyPredictionBestWindow } from '../types/dailyPrediction';

function _toHHMM(isoString: string): string {
  const d = new Date(isoString);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

export function mapBestWindow(prediction: DailyPredictionResponse): DailyPredictionBestWindow | null {
  if (prediction.best_window) {
    return prediction.best_window;
  }

  // Fallback for older API versions
  if (!prediction.summary?.best_window) return null;

  return {
    time_range: `${_toHHMM(prediction.summary.best_window.start_local)}–${_toHHMM(prediction.summary.best_window.end_local)}`,
    label: "Votre meilleur créneau",
    why: "Les conditions astrologiques convergent favorablement.",
    recommended_actions: ["Suivez votre intuition", "Restez à l'écoute de votre rythme"],
    is_pivot: false
  };
}
