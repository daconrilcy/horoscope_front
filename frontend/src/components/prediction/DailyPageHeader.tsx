import React from 'react'
import type { Lang } from '../../i18n/predictions'
import { getToneLabel } from '../../utils/predictionI18n'
import { getLocale } from '../../utils/locale'
import { DayStateBadge } from './DayStateBadge'
import './DailyPageHeader.css'

interface Props {
  date: string      // ISO date string, ex: "2026-03-16"
  tone: string | null
  lang: Lang
}

export const DailyPageHeader: React.FC<Props> = ({ date, tone, lang }) => {
  const locale = getLocale(lang)
  const toneLabel = getToneLabel(tone, lang)

  const formattedDate = new Date(date).toLocaleDateString(locale, {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  return (
    <header className="daily-page-header">
      <div className="daily-page-header__content">
        <h2 className="header-date">{formattedDate}</h2>
        <DayStateBadge label={toneLabel} tone={tone} lang={lang} />
      </div>
      <div className="daily-page-header__decoration" aria-hidden="true">
        <div className="daily-page-header__ambient-glow" />
      </div>
    </header>
  )
}
