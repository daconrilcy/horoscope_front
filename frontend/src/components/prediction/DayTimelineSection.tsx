import React, { useState } from 'react'
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
}

const PERIOD_INDICES: Record<DayPeriodKey, [number, number]> = {
  nuit: [0, 3],
  matin: [3, 6],
  apres_midi: [6, 9],
  soiree: [9, 12]
}

export const DayTimelineSection: React.FC<DayTimelineSectionProps> = ({ model, lang, agendaSlots }) => {
  const [selectedPeriod, setSelectedPeriod] = useState<DayPeriodKey | null>(null)

  if (model.periods.length === 0) {
    return null
  }

  const handleSelect = (key: DayPeriodKey) => {
    setSelectedPeriod(prev => (prev === key ? null : key))
  }

  const filteredSlots = selectedPeriod 
    ? agendaSlots.slice(PERIOD_INDICES[selectedPeriod][0], PERIOD_INDICES[selectedPeriod][1])
    : []

  return (
    <section className="day-timeline-section" id="timeline">
      <SectionTitle title={model.title} />
      <PeriodCardsRow 
        periods={model.periods} 
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
