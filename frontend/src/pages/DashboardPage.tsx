import { PageLayout } from "../layouts"
import { useAstrologyLabels } from "../i18n/astrology"
import { translateDashboardPage } from "../i18n/dashboard"
import { ShortcutsSection } from "../components/ShortcutsSection"
import { DashboardHoroscopeSummaryCardContainer } from "../components/dashboard/DashboardHoroscopeSummaryCardContainer"
import { SectionErrorBoundary } from "../components/ErrorBoundary"
import "./DashboardPage.css"

/**
 * Primary dashboard landing page (Story 45.2).
 * Provides high-level daily insights and quick access to main features.
 */
export function DashboardPage() {
  const { lang } = useAstrologyLabels()
  const { title, welcome, header } = translateDashboardPage(lang)

  return (
    <PageLayout
      className="dashboard-container"
    >
      <div className="dashboard-container__bg-halo-3" />
      
      <header className="dashboard-header">
        <h2 className="dashboard-title">{title}</h2>
        <p className="dashboard-welcome">{welcome}</p>
      </header>

      <div className="dashboard-section-header">
        <h3 className="dashboard-section-title">{header.title}</h3>
      </div>

      <SectionErrorBoundary>
        <DashboardHoroscopeSummaryCardContainer />
      </SectionErrorBoundary>

      <ShortcutsSection />
    </PageLayout>
  )
}
