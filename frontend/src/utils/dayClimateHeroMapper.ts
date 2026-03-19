import type { DailyPredictionResponse, DailyPredictionDayClimate } from '../types/dailyPrediction';

export function mapDayClimate(prediction: DailyPredictionResponse): DailyPredictionDayClimate | null {
  if (prediction.day_climate) {
    return prediction.day_climate;
  }

  // Fallback for older API versions
  if (!prediction.summary) return null;

  return {
    label: prediction.summary.overall_tone === 'positive' ? 'Élan favorable'
      : prediction.summary.overall_tone === 'negative' ? 'Journée exigeante'
      : prediction.summary.overall_tone === 'mixed' ? 'Journée en relief'
      : 'Climat stable et fluide',
    tone: prediction.summary.overall_tone || 'neutral',
    intensity: 5.0,
    stability: 5.0,
    summary: prediction.summary.overall_summary || '',
    top_domains: prediction.summary.top_categories.slice(0, 2),
    watchout: prediction.summary.bottom_categories[0] || null,
    best_window_ref: prediction.summary.best_window?.start_local 
      ? new Date(prediction.summary.best_window.start_local).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      : null
  };
}
