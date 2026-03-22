import type { DailyPredictionResponse, DailyPredictionTurningPointPublic } from '../types/dailyPrediction';

function normalizeLegacyTurningPointSummary(summary: string | null | undefined): string {
  const text = summary?.trim();
  if (!text) {
    return "Un changement notable intervient dans votre journée.";
  }

  if (text.includes("theme_rotation")) {
    return "La dynamique de la journée se réorganise et demande de vous adapter.";
  }

  return text;
}

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
    affected_domains: [],
    what_changes: normalizeLegacyTurningPointSummary(prediction.summary.main_turning_point.summary),
    do: "Observer et s'adapter",
    avoid: "Forcer le destin"
  };
}
