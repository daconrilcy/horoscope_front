import type { DailyPredictionResponse, DailyPredictionTimeBlock } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { DayTimelineSectionModel, DayPeriodKey, AggregatedDayPeriod } from '../types/dayTimeline'
import { getPredictionMessage } from './predictionI18n'
import { buildDailyAgendaSlots } from './dailyAstrology'
import { PERIOD_LABELS, TONE_LABELS, NOTE_BAND_LABELS, getLabel } from '../i18n/predictions'

const PERIOD_SLOT_RANGES: Record<DayPeriodKey, [number, number]> = {
  nuit: [0, 3],
  matin: [3, 6],
  apres_midi: [6, 9],
  soiree: [9, 12]
}

const PERIOD_TIME_RANGES: Record<DayPeriodKey, string> = {
  nuit: '00:00 – 06:00',
  matin: '06:00 – 12:00',
  apres_midi: '12:00 – 18:00',
  soiree: '18:00 – 00:00',
}

function computeToneLabel(tone: string | null, lang: Lang): string {
  if (!tone) return getLabel(TONE_LABELS, 'neutral', lang)
  const fromTone = getLabel(TONE_LABELS, tone, lang)
  if (fromTone !== tone) return fromTone
  const fromBand = getLabel(NOTE_BAND_LABELS, tone, lang)
  if (fromBand !== tone) return fromBand
  return tone
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
      timeRange: PERIOD_TIME_RANGES[key],
      slots: periodSlots,
      tone,
      toneLabel: computeToneLabel(tone, lang),
      dominantCategories,
      hasTurningPoint
    }
  })

  return {
    title: getPredictionMessage('timeline_title', lang),
    periods
  }
}
