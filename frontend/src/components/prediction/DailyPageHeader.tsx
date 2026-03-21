import React from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, RefreshCw } from 'lucide-react'
import type { Lang } from '../../i18n/predictions'
import { getToneLabel } from '../../utils/predictionI18n'
import { getLocale } from '../../utils/locale'
import { DayStateBadge } from './DayStateBadge'
import './DailyPageHeader.css'

interface Props {
  date: string      // ISO date string, ex: "2026-03-16"
  tone: string | null
  lang: Lang
  onRefresh: () => void
  refreshLabel: string
}

export const DailyPageHeader: React.FC<Props> = ({ date, tone, lang, onRefresh, refreshLabel }) => {
  const navigate = useNavigate()
  const locale = getLocale(lang)
  const toneLabel = getToneLabel(tone, lang)
  const eyebrow = lang === 'fr' ? "Aujourd'hui" : 'Today'

  const d = new Date(date)
  const dayName = d.toLocaleDateString(locale, { weekday: 'long' })
  const dayNum = d.toLocaleDateString(locale, { day: 'numeric' })
  const monthName = d.toLocaleDateString(locale, { month: 'long' })

  return (
    <header className="daily-page-header">
      <button 
        className="daily-page-header__back" 
        onClick={() => navigate('/dashboard')}
        aria-label={lang === 'fr' ? 'Retour au tableau de bord' : 'Back to dashboard'}
      >
        <ChevronLeft size={24} />
      </button>

      <div className="daily-page-header__content">
        <div className="daily-page-header__eyebrow">{eyebrow}</div>
        <h1 className="header-date">
          <span className="header-date__weekday">{dayName}</span>
          {' '}
          <span className="header-date__day">{dayNum}</span>
          {' '}
          <span className="header-date__month">{monthName}</span>
        </h1>
        <div className="daily-page-header__badge-row">
          <DayStateBadge label={toneLabel} tone={tone} lang={lang} />
        </div>
      </div>

      <div className="daily-page-header__actions">
        <button
          type="button"
          className="daily-page-header__refresh"
          onClick={onRefresh}
          aria-label={refreshLabel}
        >
          <RefreshCw size={16} aria-hidden="true" />
        </button>
      </div>
    </header>
  )
}
