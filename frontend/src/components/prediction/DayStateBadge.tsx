import React from 'react'
import type { Lang } from '../../i18n/predictions'
import { getPredictionMessage } from '../../utils/predictionI18n'
import './DayStateBadge.css'

type ToneVariant = 'balanced' | 'dynamic' | 'calm' | 'intense' | 'reflective'

function deriveToneVariant(tone: string | null | undefined): ToneVariant {
  switch (tone) {
    case 'positive':
    case 'push':
      return 'dynamic'
    case 'negative':
      return 'intense'
    case 'careful':
      return 'reflective'
    case 'mixed':
    case 'open':
      return 'calm'
    case 'neutral':
    case 'steady':
    default:
      return 'balanced'
  }
}

interface Props {
  label: string
  tone?: string | null
  lang: Lang
  size?: 'sm' | 'md'
}

export const DayStateBadge: React.FC<Props> = ({ label, tone, lang, size = 'md' }) => {
  const variant = deriveToneVariant(tone)
  const ariaLabel = `${getPredictionMessage('day_state_label', lang)} : ${label}`

  return (
    <div
      className={`day-state-badge day-state-badge--${variant} day-state-badge--${size}`}
      aria-label={ariaLabel}
      role="status"
    >
      <span className="day-state-badge__icon" aria-hidden="true">✦</span>
      <span className="day-state-badge__label">{label}</span>
      <span className="day-state-badge__dot" aria-hidden="true" />
    </div>
  )
}
