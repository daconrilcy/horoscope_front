import { useAstrologyLabels } from "../i18n/astrology"
import { translateDashboardPage } from "../i18n/dashboard"
import { TodayHeader } from "../components/TodayHeader"
import { ShortcutsSection } from "../components/ShortcutsSection"
import { DashboardHoroscopeSummaryCard } from "../components/dashboard/DashboardHoroscopeSummaryCard"

import { useAccessTokenSnapshot } from "../utils/authToken"
import { useAuthMe } from "../api/authMe"
import { getUserDisplayName } from "../utils/user"
import { useDailyPrediction } from "../api/useDailyPrediction"
import { useDashboardAstroSummary } from "../components/dashboard/useDashboardAstroSummary"

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
    isError: isPredictionError,
    refetch: refetchPrediction,
  } = useDailyPrediction(accessToken)

  const astroSummary = useDashboardAstroSummary(accessToken)
  
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
        prediction={prediction ?? null}
        isLoading={isPredictionLoading}
        isError={isPredictionError}
        locale={lang}
        sign={astroSummary.sign}
        userId={astroSummary.userId}
        dateKey={astroSummary.dateKey}
        dayScore={astroSummary.dayScore}
        onRetry={() => {
          void refetchPrediction()
        }}
      />

      <ShortcutsSection />
    </div>
  )
}
