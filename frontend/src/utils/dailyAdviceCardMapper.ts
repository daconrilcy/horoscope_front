import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import { getPredictionMessage } from './predictionI18n'

export interface DailyAdviceCardModel {
  title: string;
  advice: string;
  emphasis: string;
}

export function buildDailyAdviceCardModel(
  _prediction: DailyPredictionResponse,
  lang: Lang
): DailyAdviceCardModel {
  // TODO: utiliser prediction.summary.llm_advice quand disponible
  return {
    title: getPredictionMessage('daily_advice_title', lang),
    advice: getPredictionMessage('daily_advice_placeholder', lang),
    emphasis: getPredictionMessage('daily_advice_emphasis_placeholder', lang),
  }
}
