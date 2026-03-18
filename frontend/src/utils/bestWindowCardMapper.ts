import type { DailyPredictionResponse, DailyPredictionBestWindow } from '../types/dailyPrediction';

export function mapBestWindow(prediction: DailyPredictionResponse): DailyPredictionBestWindow | null {
  if (prediction.best_window) {
    return prediction.best_window;
  }

  // Fallback for older API versions
  if (!prediction.summary?.best_window) return null;

  return {
    time_range: `${new Date(prediction.summary.best_window.start_local).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}–${new Date(prediction.summary.best_window.end_local).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`,
    label: "Votre meilleur créneau",
    why: "Les conditions astrologiques convergent favorablement.",
    recommended_actions: ["Suivez votre intuition", "Restez à l'écoute de votre rythme"],
    is_pivot: false
  };
}
