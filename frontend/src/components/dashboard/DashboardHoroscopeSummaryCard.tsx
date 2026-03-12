import React from "react"
import { useNavigate } from "react-router-dom"
import { ChevronRight } from "lucide-react"
import type { DailyPredictionResponse } from "../../types/dailyPrediction"
import { translateDashboardPage, type SupportedLocale } from "../../i18n/dashboard"

interface Props {
  prediction: DailyPredictionResponse | null
  isLoading: boolean
  isError: boolean
  locale: SupportedLocale
}

export const DashboardHoroscopeSummaryCard: React.FC<Props> = ({
  prediction,
  isLoading,
  isError,
  locale
}) => {
  const navigate = useNavigate()
  const { viewHoroscope, noPrediction } = translateDashboardPage(locale)

  const handleNavigate = () => {
    navigate("/dashboard/horoscope")
  }

  if (isLoading) {
    return (
      <div className="panel dashboard-summary-card dashboard-summary-card--loading">
        <div className="skeleton-line" style={{ width: "80%", marginBottom: "0.5rem" }} />
        <div className="skeleton-line" style={{ width: "60%" }} />
      </div>
    )
  }

  if (isError || !prediction) {
    return (
      <div 
        className="panel dashboard-summary-card dashboard-summary-card--empty"
        onClick={handleNavigate}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && handleNavigate()}
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
      className="panel dashboard-summary-card"
      onClick={handleNavigate}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && handleNavigate()}
      aria-label={`${viewHoroscope}: ${summary}`}
    >
      <div className="dashboard-summary-card__content">
        <p className="dashboard-summary-card__text">{summary}</p>
      </div>
      <div className="dashboard-summary-card__link">
        <span>{viewHoroscope}</span>
        <ChevronRight size={16} />
      </div>
    </div>
  )
}
