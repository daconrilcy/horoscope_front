import React from 'react'
import type { AggregatedDayPeriod } from '../../types/dayTimeline'
import { getCategoryMeta } from '../../utils/predictionI18n'
import type { Lang } from '../../i18n/predictions'
import './PeriodCard.css'

interface PeriodCardProps {
  period: AggregatedDayPeriod
  isSelected: boolean
  onClick: () => void
  lang: Lang
}

export const PeriodCard: React.FC<PeriodCardProps> = ({ period, isSelected, onClick, lang }) => {
  return (
    <button 
      className={`period-card ${isSelected ? 'period-card--selected' : ''} ${period.hasTurningPoint ? 'period-card--has-pivot' : ''}`}
      onClick={onClick}
      aria-pressed={isSelected}
    >
      <span className="period-card__icon">{period.icon}</span>
      <span className="period-card__label">{period.label}</span>
      <div className="period-card__categories">
        {period.dominantCategories.slice(0, 2).map(cat => (
          <span key={cat} className="period-card__cat-icon" title={cat}>
            {getCategoryMeta(cat, lang).icon}
          </span>
        ))}
      </div>
      {period.hasTurningPoint && <span className="period-card__pivot-dot" aria-hidden="true" />}
    </button>
  )
}
