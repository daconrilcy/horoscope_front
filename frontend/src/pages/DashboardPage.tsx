import { PageLayout } from "../layouts"
import { useAstrologyLabels } from "../i18n/astrology"
import { translateDashboardPage } from "../i18n/dashboard"
import { ShortcutsSection } from "../components/ShortcutsSection"
import { DashboardHoroscopeSummaryCardContainer } from "../components/dashboard/DashboardHoroscopeSummaryCardContainer"
import { SectionErrorBoundary } from "../components/ErrorBoundary"

/**
 * Primary dashboard landing page (Story 45.2).
 * Provides high-level daily insights and quick access to main features.
 */
export function DashboardPage() {
  const { lang } = useAstrologyLabels()
  const { title, welcome, header } = translateDashboardPage(lang)

  return (
    <PageLayout
      className="panel dashboard-container"
    >
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
