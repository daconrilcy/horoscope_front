import React from "react"
import { useNavigate } from "react-router-dom"
import { ChevronRight } from "lucide-react"
import type { DailyPredictionResponse } from "../../types/dailyPrediction"
import { translateDashboardPage, type SupportedLocale } from "../../i18n/dashboard"
import { AstroMoodBackground } from "../astro/AstroMoodBackground"
import type { ZodiacSign } from "../astro/zodiacPatterns"

interface Props {
  prediction: DailyPredictionResponse | null
  isLoading: boolean
  isError: boolean
  locale: SupportedLocale
  sign?: ZodiacSign
  userId?: string
  dateKey?: string
  dayScore?: number
  onRetry?: () => void
}

export const DashboardHoroscopeSummaryCard: React.FC<Props> = ({
  prediction,
  isLoading,
  isError,
  locale,
  sign = 'neutral',
  userId = 'anonymous',
  dateKey = '',
  dayScore = 12,
  onRetry,
}) => {
  const navigate = useNavigate()
  const { viewHoroscope, noPrediction, errorPrediction, retry, summaryLoading } = translateDashboardPage(locale)

  const handleNavigate = () => {
    navigate("/dashboard/horoscope")
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault()
      handleNavigate()
    }
  }

  if (isLoading) {
    return (
      <div
        className="panel dashboard-summary-card dashboard-summary-card--loading"
        aria-busy="true"
        aria-label={summaryLoading}
      >
        <div className="skeleton-line" style={{ width: "80%", marginBottom: "0.5rem" }} />
        <div className="skeleton-line" style={{ width: "60%" }} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="panel dashboard-summary-card dashboard-summary-card--empty" role="status">
        <p>{errorPrediction}</p>
        <div className="dashboard-summary-card__actions">
          <button type="button" className="button-ghost" onClick={onRetry}>
            {retry}
          </button>
        </div>
      </div>
    )
  }

  if (!prediction) {
    return (
      <div
        className="panel dashboard-summary-card dashboard-summary-card--empty"
        onClick={handleNavigate}
        role="button"
        tabIndex={0}
        onKeyDown={handleKeyDown}
        aria-label={viewHoroscope}
      >
        <p>{noPrediction}</p>
        <div className="dashboard-summary-card__link">
          <span>{viewHoroscope}</span>
          <ChevronRight size={16} />
        </div>
      </div>
    )
  }

  const summary = prediction.summary.overall_summary

  return (
    <div 
      className="dashboard-summary-card-wrapper"
      onClick={handleNavigate}
      role="button"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      aria-label={`${viewHoroscope}: ${summary}`}
    >
      <AstroMoodBackground
        sign={sign}
        userId={userId}
        dateKey={dateKey}
        dayScore={dayScore}
        className="dashboard-summary-card-bg"
      >
        <div className="dashboard-summary-card__content">
          <p className="dashboard-summary-card__text">{summary}</p>
        </div>
        <div className="dashboard-summary-card__link">
          <span>{viewHoroscope}</span>
          <ChevronRight size={16} />
        </div>
      </AstroMoodBackground>
    </div>
  )
}
