import type { DailyPredictionResponse, DailyPredictionTurningPoint } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { KeyPointsSectionModel, KeyPointItem } from '../types/keyPointsSection'
import { humanizeTurningPointSemantic, getCategoryMeta, getPredictionMessage } from './predictionI18n'
import { buildDailyKeyMoments } from './dailyAstrology'

function toFallbackTurningPoint(m: ReturnType<typeof buildDailyKeyMoments>[number]): DailyPredictionTurningPoint {
  return {
    occurred_at_local: m.occurredAtLocal,
    severity: 0.5,
    impacted_categories: m.impactedCategories,
    change_type: 'recomposition',
    summary: null,
    drivers: [],
    primary_driver: null,
    previous_categories: m.previousCategories,
    next_categories: m.nextCategories,
  } as DailyPredictionTurningPoint
}

export function buildKeyPointsSectionModel(
  prediction: DailyPredictionResponse,
  lang: Lang
): KeyPointsSectionModel {
  const title = getPredictionMessage('key_points_title', lang)

  // Start with turning_points (up to 3), supplement with fallback moments if fewer than 3
  const apiMoments = prediction.turning_points.slice(0, 3)
  const needed = 3 - apiMoments.length

  const fallbackMoments: DailyPredictionTurningPoint[] = needed > 0
    ? buildDailyKeyMoments(
        prediction.meta.date_local,
        prediction.decision_windows,
        prediction.timeline,
        prediction.categories
      ).slice(0, needed).map(toFallbackTurningPoint)
    : []

  const sourceMoments: DailyPredictionTurningPoint[] = [...apiMoments, ...fallbackMoments]

  const items: KeyPointItem[] = sourceMoments.map((moment) => {
    const semantic = humanizeTurningPointSemantic(moment, lang)
    const label = semantic.title || semantic.cause || '—'

    const categories = moment.impacted_categories?.length
      ? moment.impacted_categories
      : moment.next_categories?.length
        ? moment.next_categories
        : []

    const icon = categories.length > 0
      ? (getCategoryMeta(categories[0], lang).icon ?? '✦')
      : '✦'

    // Number() handles string severities; || 0.5 handles 0 and NaN (no data → mid-range default)
    const rawSeverity = Number(moment.severity)
    const strength = Math.min(100, Math.round((rawSeverity || 0.5) * 100))

    return {
      id: moment.occurred_at_local,
      label,
      icon,
      strength,
      tone: moment.change_type ?? undefined,
    }
  })

  return { title, items }
}
