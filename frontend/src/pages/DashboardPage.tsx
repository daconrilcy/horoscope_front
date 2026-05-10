import { PageLayout } from "../layouts"
import { useAstrologyLabels } from "../i18n/astrology"
import { translateDashboardPage } from "../i18n/dashboard"
import { ShortcutsSection } from "../components/ShortcutsSection"
import { DashboardHoroscopeSummaryCardContainer } from "../features/dashboard/components/DashboardHoroscopeSummaryCardContainer"
import { SectionErrorBoundary } from "../components/ErrorBoundary"

/**
 * Primary overview landing page (Story 45.2).
 * Provides high-level daily insights and quick access to main features.
 */
export function DashboardPage() {
  const { lang } = useAstrologyLabels()
  const { title, welcome, header } = translateDashboardPage(lang)

  return (
    <PageLayout
      className="summary-container"
    >
      <div className="summary-container__bg-halo-3" />
      
      <header className="summary-header">
        <p className="summary-header__kicker">{header.kicker}</p>
        <h2 className="summary-title">{title}</h2>
        <p className="summary-welcome">{welcome}</p>
      </header>

      <div className="summary-section-header">
        <h3 className="summary-section-title">{header.title}</h3>
      </div>

      <SectionErrorBoundary>
        <DashboardHoroscopeSummaryCardContainer />
      </SectionErrorBoundary>

      <ShortcutsSection />
    </PageLayout>
  )
}
