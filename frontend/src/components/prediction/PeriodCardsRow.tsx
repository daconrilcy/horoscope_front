import React from 'react'
import type { AggregatedDayPeriod, DayPeriodKey } from '../../types/dayTimeline'
import { PeriodCard } from './PeriodCard'
import type { Lang } from '../../i18n/predictions'
import './PeriodCardsRow.css'

interface PeriodCardsRowProps {
  periods: AggregatedDayPeriod[]
  selectedPeriod: DayPeriodKey | null
  onSelect: (key: DayPeriodKey) => void
  lang: Lang
}

export const PeriodCardsRow: React.FC<PeriodCardsRowProps> = ({ periods, selectedPeriod, onSelect, lang }) => {
  return (
    <div className="period-cards-row">
      {periods.map(p => (
        <PeriodCard
          key={p.key}
          period={p}
          isSelected={selectedPeriod === p.key}
          onClick={() => onSelect(p.key)}
          lang={lang}
        />
      ))}
    </div>
  )
}
