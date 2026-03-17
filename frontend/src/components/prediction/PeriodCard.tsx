import React from 'react'
import { Moon, Sunrise, Sun, Sunset, ArrowRightLeft } from 'lucide-react'
import type { AggregatedDayPeriod, DayPeriodKey } from '../../types/dayTimeline'
import type { Lang } from '../../i18n/predictions'
import { getCategoryMeta, getPredictionMessage } from '../../utils/predictionI18n'
import './PeriodCard.css'

const PERIOD_ICONS: Record<DayPeriodKey, React.ComponentType<{ size?: number; strokeWidth?: number; className?: string }>> = {
  nuit: Moon,
  matin: Sunrise,
  apres_midi: Sun,
  soiree: Sunset,
}

const PERIOD_ICON_CLASS: Record<DayPeriodKey, string> = {
  nuit: 'period-card__icon--nuit',
  matin: 'period-card__icon--matin',
  apres_midi: 'period-card__icon--apres-midi',
  soiree: 'period-card__icon--soiree',
}

interface PeriodCardProps {
  period: AggregatedDayPeriod
  isSelected: boolean
  onClick: () => void
  lang: Lang
}

const STROKE_ICON = 3;

export const PeriodCard: React.FC<PeriodCardProps> = ({ period, isSelected, onClick, lang }) => {
  const IconComponent = PERIOD_ICONS[period.key]
  const pivotLabel = getPredictionMessage('aspect_shift_label', lang)
  const firstCat = period.dominantCategories[0]
  const firstCatLabel = firstCat ? getCategoryMeta(firstCat, lang).label : null

  return (
    <button
      className={`period-card${isSelected ? ' period-card--selected' : ''}${period.hasTurningPoint ? ' period-card--has-pivot' : ''}`}
      onClick={onClick}
      aria-pressed={isSelected}
    >
      <div className="period-card__header">
        <IconComponent
          size={18}
          strokeWidth={STROKE_ICON}
          className={`period-card__icon ${PERIOD_ICON_CLASS[period.key]}`}
          aria-hidden="true"
        />
        <span className="period-card__name">{period.label}</span>
      </div>
      <div className="period-card__time">{period.timeRange}</div>
      <hr className="period-card__divider" />
      <div className="period-card__footer">
        {period.hasTurningPoint ? (
          <>
            <ArrowRightLeft size={10} className="period-card__pivot-icon" aria-hidden="true" />
            <span className="period-card__pivot-label">{pivotLabel}</span>
            {firstCatLabel && (
              <>
                <span className="period-card__sep" aria-hidden="true">·</span>
                <span className="period-card__cat-label">{firstCatLabel}</span>
              </>
            )}
          </>
        ) : (
          <>
            <span className="period-card__tone-dot" data-tone={period.tone ?? 'neutral'} aria-hidden="true" />
            <span className="period-card__tone-label">{period.toneLabel}</span>
          </>
        )}
      </div>
    </button>
  )
}
