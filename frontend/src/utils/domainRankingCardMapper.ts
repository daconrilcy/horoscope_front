import type { DailyPredictionResponse, DailyPredictionPublicDomainScore } from '../types/dailyPrediction';

export function mapDomainRanking(prediction: DailyPredictionResponse): DailyPredictionPublicDomainScore[] {
  if (prediction.domain_ranking) {
    return prediction.domain_ranking;
  }
  return [];
}
