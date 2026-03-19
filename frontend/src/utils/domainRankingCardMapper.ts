import type { DailyPredictionResponse, DailyPredictionPublicDomainScore } from '../types/dailyPrediction';

export function mapDomainRanking(prediction: DailyPredictionResponse): DailyPredictionPublicDomainScore[] {
  if (prediction.domain_ranking) {
    return prediction.domain_ranking;
  }

  // Fallback for older API versions
  if (!prediction.categories) return [];

  return prediction.categories.slice(0, 5).map((cat, i) => ({
    key: cat.code,
    label: cat.code,
    internal_codes: [cat.code],
    display_order: i + 1,
    score_10: Math.round(cat.note_20 / 2 * 10) / 10,
    level: cat.note_20 >= 18 ? 'très_favorable'
      : cat.note_20 >= 15 ? 'favorable'
      : cat.note_20 >= 12 ? 'stable'
      : cat.note_20 >= 9 ? 'mitigé'
      : 'exigeant',
    rank: cat.rank || i + 1,
    note_20_internal: cat.note_20,
    signal_label: null
  }));
}
