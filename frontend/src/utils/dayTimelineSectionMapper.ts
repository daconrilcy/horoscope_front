import type { DailyPredictionResponse, DailyPredictionTimeBlock } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { DayTimelineSectionModel, DayPeriodKey, AggregatedDayPeriod } from '../types/dayTimeline'
import { getPredictionMessage, getCategoryMeta } from './predictionI18n'
import { buildDailyAgendaSlots } from './dailyAstrology'
import { PERIOD_LABELS } from '../i18n/predictions'

const PERIOD_ICONS: Record<DayPeriodKey, string> = {
  nuit: '🌙',
  matin: '☀️',
  apres_midi: '🌤️',
  soiree: '🌆'
}

const PERIOD_SLOT_RANGES: Record<DayPeriodKey, [number, number]> = {
  nuit: [0, 3],
  matin: [3, 6],
  apres_midi: [6, 9],
  soiree: [9, 12]
}

function derivePeriodTone(timeline: DailyPredictionTimeBlock[], startHour: number, endHour: number): string | null {
  const blocks = timeline.filter(b => {
    const bStart = new Date(b.start_local).getHours()
    const bEnd = new Date(b.end_local).getHours() || 24
    return bStart < endHour && bEnd > startHour
  })

  if (blocks.length === 0) return null

  const counts: Record<string, number> = {}
  let maxCount = 0
  let dominantTone = blocks[0].tone_code

  for (const b of blocks) {
    counts[b.tone_code] = (counts[b.tone_code] || 0) + 1
    if (counts[b.tone_code] > maxCount) {
      maxCount = counts[b.tone_code]
      dominantTone = b.tone_code
    }
  }

  return dominantTone
}

export function buildDayTimelineSectionModel(
  prediction: DailyPredictionResponse,
  lang: Lang
): DayTimelineSectionModel {
  const allSlots = buildDailyAgendaSlots(
    prediction.meta.date_local,
    prediction.decision_windows,
    prediction.timeline,
    prediction.categories,
    []
  )

  const periods: AggregatedDayPeriod[] = (['nuit', 'matin', 'apres_midi', 'soiree'] as DayPeriodKey[]).map(key => {
    const [startIdx, endIdx] = PERIOD_SLOT_RANGES[key]
    const periodSlots = allSlots.slice(startIdx, endIdx)
    
    const startHour = startIdx * 2
    const endHour = endIdx * 2
    const tone = derivePeriodTone(prediction.timeline, startHour, endHour)
    
    const categoriesSet = new Set<string>()
    periodSlots.forEach(s => s.topCategories.forEach(c => categoriesSet.add(c)))
    const dominantCategories = Array.from(categoriesSet).slice(0, 3)
    
    const hasTurningPoint = periodSlots.some(s => s.hasTurningPoint)
    
    return {
      key,
      label: PERIOD_LABELS[key][lang],
      icon: PERIOD_ICONS[key],
      slots: periodSlots,
      tone,
      dominantCategories,
      hasTurningPoint
    }
  })

  return {
    title: getPredictionMessage('timeline_title', lang),
    periods
  }
}
