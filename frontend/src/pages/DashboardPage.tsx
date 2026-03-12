import { type ReactNode } from "react"
import { useAstrologyLabels } from "../i18n/astrology"
import { translateDashboardPage } from "../i18n/dashboard"
import { TodayHeader } from "../components/TodayHeader"
import { ShortcutsSection } from "../components/ShortcutsSection"
import { DashboardHoroscopeSummaryCard } from "../components/dashboard/DashboardHoroscopeSummaryCard"

import { useAccessTokenSnapshot } from "../utils/authToken"
import { useAuthMe } from "../api/authMe"
import { getUserDisplayName } from "../utils/user"
import { useDailyPrediction } from "../api/useDailyPrediction"

/**
 * Primary dashboard landing page (Story 45.2).
 * Provides high-level daily insights and quick access to main features.
 */
export function DashboardPage() {
  const { lang } = useAstrologyLabels()
  const { title, welcome } = translateDashboardPage(lang)
  const accessToken = useAccessTokenSnapshot()
  
  const { data: user, isLoading: isUserLoading } = useAuthMe(accessToken)
  const { 
    data: prediction, 
    isLoading: isPredictionLoading, 
    isError: isPredictionError 
  } = useDailyPrediction(accessToken)
  
  const userName = isUserLoading 
    ? "loading" 
    : getUserDisplayName(user)

  return (
    <div className="panel dashboard-container">
      <TodayHeader userName={userName} isLoading={isUserLoading} />
      
      <div>
        <h2 className="dashboard-title">{title}</h2>
        <p>{welcome}</p>
      </div>

      <DashboardHoroscopeSummaryCard 
        prediction={prediction}
        isLoading={isPredictionLoading}
        isError={isPredictionError}
        locale={lang}
      />

      <ShortcutsSection />
    </div>
  )
}
