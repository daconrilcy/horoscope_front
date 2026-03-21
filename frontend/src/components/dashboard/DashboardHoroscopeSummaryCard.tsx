import React from "react"
import { useNavigate } from "react-router-dom"
import { ChevronRight } from "lucide-react"
import type { DailyPredictionResponse } from "../../types/dailyPrediction"
import { translateDashboardPage, type SupportedLocale } from "../../i18n/dashboard"
import { translateSign } from "../../i18n/astrology"
import { AstroMoodBackground } from "../astro/AstroMoodBackground"
import { getZodiacIcon } from "../../components/zodiacSignIconMap"
import type { ZodiacSign } from "../astro/zodiacPatterns"
import { getDailyEditorialSummary } from "../../utils/dailySummaryHelper"

import { SkeletonGroup } from "../ui"

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

  const formattedDate = dateKey
    ? new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'short' }).format(new Date(dateKey))
    : '';

  const ZodiacIcon = getZodiacIcon(sign);

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
        <SkeletonGroup count={2} widths={["80%", "60%"]} height="1.25rem" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="panel dashboard-summary-card dashboard-summary-card--empty" role="status">
        <p>{errorPrediction}</p>
        <div className="dashboard-summary-card__actions">
          <button type="button" onClick={onRetry}>
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

  const summary = getDailyEditorialSummary(prediction)

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
          {ZodiacIcon && (
            <div className="default_card_pill">
              <ZodiacIcon className="default_card_pill-icon" />
              <span>{translateSign(sign, locale)} • {formattedDate}</span>
            </div>
          )}
          <p className="dashboard-summary-card__text">
            {summary}
          </p>
        </div>
        <div className="dashboard-summary-card__link">
          <span>{viewHoroscope}</span>
          <ChevronRight size={16} />
        </div>
      </AstroMoodBackground>
    </div>
  )
}
