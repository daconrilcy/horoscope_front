import type { DailyPredictionResponse, DailyPredictionTurningPointPublic } from '../types/dailyPrediction';

export function mapTurningPoint(prediction: DailyPredictionResponse): DailyPredictionTurningPointPublic | null {
  if (prediction.turning_point) {
    return prediction.turning_point;
  }

  // Fallback for older API versions
  if (!prediction.summary?.main_turning_point) return null;

  return {
    time: new Date(prediction.summary.main_turning_point.occurred_at_local).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
    title: "Changement de dynamique",
    change_type: "recomposition",
    affected_domains: prediction.summary.top_categories.slice(0, 2),
    what_changes: prediction.summary.main_turning_point.summary || "Un changement notable intervient dans votre journée.",
    do: "Observer et s'adapter",
    avoid: "Forcer le destin"
  };
}
