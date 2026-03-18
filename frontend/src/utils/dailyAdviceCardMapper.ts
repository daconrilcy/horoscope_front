import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { DailyAdviceCardModel } from '../types/detailScores'
import { getPredictionMessage } from './predictionI18n'

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
