import type { DailyAgendaSlot } from '../utils/dailyAstrology'

export type DayPeriodKey = 'nuit' | 'matin' | 'apres_midi' | 'soiree'

export type AggregatedDayPeriod = {
  key: DayPeriodKey
  label: string           // traduit via lang
  icon: string            // emoji fixe par période
  slots: DailyAgendaSlot[]   // 3 créneaux de 2h agrégés
  tone: string | null     // tone_code dominant parmi les timeline blocks de la période
  dominantCategories: string[]  // union des topCategories des 3 slots, dédoublonnée, max 3
  hasTurningPoint: boolean      // true si au moins un slot.hasTurningPoint
}

export type DayTimelineSectionModel = {
  title: string
  periods: AggregatedDayPeriod[]
}
