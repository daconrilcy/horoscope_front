import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { KeyPointsSectionModel, KeyPointItem } from '../types/keyPointsSection'
import { humanizeTurningPointSemantic, getCategoryMeta, getPredictionMessage } from './predictionI18n'
import { buildDailyKeyMoments } from './dailyAstrology'

export function buildKeyPointsSectionModel(
  prediction: DailyPredictionResponse,
  lang: Lang
): KeyPointsSectionModel {
  const title = getPredictionMessage('key_points_title', lang)
  
  // Use turning_points if present, otherwise fallback to built moments
  const sourceMoments = prediction.turning_points.length > 0
    ? prediction.turning_points.slice(0, 3)
    : buildDailyKeyMoments(
        prediction.meta.date_local,
        prediction.decision_windows,
        prediction.timeline,
        prediction.categories
      ).slice(0, 3).map(m => ({
        occurred_at_local: m.occurredAtLocal,
        severity: 0.5,
        impacted_categories: m.impactedCategories,
        change_type: 'recomposition',
        summary: null,
        drivers: [],
        primary_driver: null,
        previous_categories: m.previousCategories,
        next_categories: m.nextCategories
      }))

  const items: KeyPointItem[] = sourceMoments.map((moment) => {
    const semantic = humanizeTurningPointSemantic(moment as any, lang)
    const label = semantic.title || semantic.cause || '—'
    
    // Get icon from the first impacted or next category
    const categories = moment.impacted_categories?.length 
      ? moment.impacted_categories 
      : moment.next_categories?.length 
        ? moment.next_categories 
        : []
    
    const icon = categories.length > 0 
      ? (getCategoryMeta(categories[0], lang).icon ?? '✦')
      : '✦'
    
    const strength = Math.min(100, Math.round((moment.severity ?? 0.5) * 100))
    
    return {
      id: moment.occurred_at_local,
      label,
      icon,
      strength,
      tone: moment.change_type ?? undefined
    }
  })

  return {
    title,
    items
  }
}
