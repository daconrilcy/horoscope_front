// Page thème natal: composition UI de la lecture Astral et du guide pédagogique.

import { PageLayout } from "../layouts"
import { NatalJobCard } from "../features/natal-chart/NatalJobCard"
import { resolveNatalJobViewState } from "../features/natal-chart/natalJobViewState"
import { useNatalAstralJob } from "../features/natal-chart/useNatalAstralJob"
import { NatalChartGuide } from "../components/NatalChartGuide"
import { useAstrologyLabels } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"
import "../features/natal-chart/natalTheme.css"
import "../features/natal-chart/natalBadges.css"
import "../features/natal-chart/natalCards.css"
import "./NatalChartPage.css"

/** Compose la page thème natal à partir des modules feature dédiés. */
export function NatalChartPage() {
  const { lang } = useAstrologyLabels()
  const copy = natalChartTranslations[lang].page
  const natalJob = useNatalAstralJob()
  const viewState = resolveNatalJobViewState({
    hasTransportError: natalJob.hasTransportError,
    isWorking: natalJob.isWorking,
    currentJob: natalJob.currentJob,
  })

  return (
    <PageLayout className="natal-page-container is-natal-page">
      <div className="natal-page-container__bg-halo" aria-hidden="true" />
      <div className="natal-page-container__noise" aria-hidden="true" />
      <header className="natal-page-header">
        <span className="natal-page-header__meta">{copy.meta}</span>
        <h1 className="natal-page-header__title">{copy.title}</h1>
        <p className="natal-page-header__context">{copy.context}</p>
        {natalJob.natalReading?.highlightFacts.length ? (
          <div className="natal-page-portrait" aria-label={copy.portraitLabel}>
            <div className="natal-page-portrait__copy">
              <div className="natal-page-portrait__head">
                <div className="natal-page-portrait__title-block">
                  <span className="natal-section-eyebrow">{copy.portraitLabel}</span>
                  <p>{natalJob.natalReading.shortText ?? copy.context}</p>
                </div>
                <span className="natal-page-portrait__status natal-badge natal-badge--report-status">
                  {natalJob.natalReading.label}
                </span>
              </div>
            </div>
            <div className="natal-page-portrait__facts" aria-label={copy.portraitFactsLabel}>
              {natalJob.natalReading.highlightFacts.map((fact) => (
                <span
                  className="natal-page-portrait__fact natal-badge natal-badge--astro-data"
                  key={`${fact.label}-${fact.value}-${fact.detail ?? ""}`}
                >
                  <span className="natal-page-portrait__label">{fact.label}</span>
                  <strong>{fact.value}</strong>
                  {fact.detail ? <span className="natal-page-portrait__detail">{fact.detail}</span> : null}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </header>

      <NatalJobCard
        viewState={viewState}
        currentJob={natalJob.currentJob}
        reading={natalJob.natalReading}
        copy={copy}
        canStart={natalJob.canStart}
        canRetry={natalJob.canRetry}
        onStart={natalJob.startJob}
        onRetry={natalJob.startJob}
      />

      <NatalChartGuide lang={lang} missingBirthTime={Boolean(natalJob.natalReading?.isPartial)} />
    </PageLayout>
  )
}
