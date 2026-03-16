import React from 'react'
import type { DailyPredictionTurningPoint } from '../../types/dailyPrediction'
import type { Lang } from '../../i18n/predictions'
import { getLocale } from '../../utils/locale'
import { getCategoryMeta, humanizeTurningPointSemantic } from '../../utils/predictionI18n'
import './KeyPointCard.css'

interface Props {
  moment: DailyPredictionTurningPoint
  lang: Lang
}

export const KeyPointCard: React.FC<Props> = ({ moment, lang }) => {
  const locale = getLocale(lang)
  const time = new Date(moment.occurred_at_local).toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
  })
  const semantic = humanizeTurningPointSemantic(moment, lang)
  const categories = (moment.impacted_categories ?? moment.next_categories ?? []).slice(0, 3)

  return (
    <div className="panel key-point-card">
      <span className="key-point-card__time">{time}</span>
      <span className="key-point-card__title">{semantic.title || semantic.cause}</span>
      <div className="key-point-card__categories">
        {categories.map((c) => (
          <span key={c} title={getCategoryMeta(c, lang).label}>
            {getCategoryMeta(c, lang).icon}
          </span>
        ))}
      </div>
    </div>
  )
}
