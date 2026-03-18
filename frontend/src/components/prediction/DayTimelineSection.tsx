import React from 'react'
import type { DayTimelineSectionModel, DayPeriodKey } from '../../types/dayTimeline'
import type { Lang } from '../../i18n/predictions'
import type { DailyAgendaSlot } from '../../utils/dailyAstrology'
import { SectionTitle } from './SectionTitle'
import { PeriodCardsRow } from './PeriodCardsRow'
import { TimelineRail } from './TimelineRail'
import { DayAgenda } from './DayAgenda'
import './DayTimelineSection.css'

interface DayTimelineSectionProps {
  model: DayTimelineSectionModel
  lang: Lang
  agendaSlots: DailyAgendaSlot[]
  selectedPeriod: DayPeriodKey | null
  onPeriodChange: (key: DayPeriodKey | null) => void
}

const PERIOD_INDICES: Record<DayPeriodKey, [number, number]> = {
  nuit: [0, 3],
  matin: [3, 6],
  apres_midi: [6, 9],
  soiree: [9, 12]
}

export const DayTimelineSection: React.FC<DayTimelineSectionProps> = ({ 
  model, 
  lang, 
  agendaSlots,
  selectedPeriod,
  onPeriodChange
}) => {
  if (model.periods.length === 0) {
    return null
  }

  const handleSelect = (key: DayPeriodKey) => {
    onPeriodChange(selectedPeriod === key ? null : key)
  }

  // Recalcule hasTurningPoint depuis les agendaSlots réels (qui incluent les keyMoments
  // non présents dans les slots internes du mapper).
  const periods = model.periods.map(period => {
    const [start, end] = PERIOD_INDICES[period.key]
    const hasTurningPoint = agendaSlots.slice(start, end).some(s => s.hasTurningPoint)
    return { ...period, hasTurningPoint }
  })

  const filteredSlots = selectedPeriod
    ? agendaSlots.slice(PERIOD_INDICES[selectedPeriod][0], PERIOD_INDICES[selectedPeriod][1])
    : []

  return (
    <section className="day-timeline-section" id="timeline">
      <SectionTitle title={model.title} />
      <PeriodCardsRow
        periods={periods}
        selectedPeriod={selectedPeriod}
        onSelect={handleSelect}
        lang={lang}
      />
      <TimelineRail selectedPeriod={selectedPeriod} />
      {selectedPeriod && (
        <div className="day-timeline-section__agenda">
          <DayAgenda slots={filteredSlots} lang={lang} />
        </div>
      )}
    </section>
  )
}
