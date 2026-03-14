import { PageLayout } from "../layouts"
import { useAstrologyLabels } from "../i18n/astrology"
import { translateDashboardPage } from "../i18n/dashboard"
import { TodayHeader } from "../components/TodayHeader"
import { ShortcutsSection } from "../components/ShortcutsSection"
import { DashboardHoroscopeSummaryCardContainer } from "../components/dashboard/DashboardHoroscopeSummaryCardContainer"
import { SectionErrorBoundary } from "../components/ErrorBoundary"

import { useAccessTokenSnapshot } from "../utils/authToken"
import { useAuthMe } from "../api/authMe"
import { getUserDisplayName } from "../utils/user"

/**
 * Primary dashboard landing page (Story 45.2).
 * Provides high-level daily insights and quick access to main features.
 */
export function DashboardPage() {
  const { lang } = useAstrologyLabels()
  const { title, welcome, header } = translateDashboardPage(lang)
  const accessToken = useAccessTokenSnapshot()
  
  const { data: user, isLoading: isUserLoading } = useAuthMe(accessToken)
  
  const userName = isUserLoading 
    ? "loading" 
    : getUserDisplayName(user)

  return (
    <PageLayout
      className="panel dashboard-container"
    >
      <TodayHeader userName={userName} isLoading={isUserLoading} />
      
      <div>
        <h2 className="dashboard-title">{title}</h2>
        <p>{welcome}</p>
      </div>

      <div className="section-header">
        <h3 className="section-header__title">{header.title}</h3>
      </div>

      <SectionErrorBoundary>
        <DashboardHoroscopeSummaryCardContainer />
      </SectionErrorBoundary>

      <ShortcutsSection />
    </PageLayout>
  )
}
