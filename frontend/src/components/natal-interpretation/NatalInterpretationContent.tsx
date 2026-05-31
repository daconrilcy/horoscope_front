// Rendu presentational du contenu d'une interpretation natale publique.
import type { ReactNode } from "react"
import { AlertCircle } from "lucide-react"

import { natalChartTranslations } from "../../i18n/natalChart"
import type {
  BasicNatalInterpretationView,
  BasicNatalPublicEvidenceView,
  InterpretationTranslations,
  NatalInterpretationLocale,
  NatalInterpretationSectionView,
  NatalInterpretationViewData,
  NatalNarrativeReadingView,
  UsedAstrologicalElementView,
} from "./NatalInterpretationTypes"

function resolveUseCase(data: NatalInterpretationViewData): string | null {
  return data.use_case ?? data.meta.use_case ?? null
}

function hasItems<T>(items: T[] | null | undefined): items is T[] {
  return Array.isArray(items) && items.length > 0
}

function PublicList({ className, items }: { className?: string; items: string[] }) {
  return (
    <ul className={className ?? "ni-public-list"}>
      {items.map((item, index) => (
        <li key={`${item}-${index}`} className="ni-public-list__item">
          {item}
        </li>
      ))}
    </ul>
  )
}

function PublicDisclaimers({ disclaimers, t }: { disclaimers?: string[] | null; t: InterpretationTranslations }) {
  if (!hasItems(disclaimers)) {
    return null
  }

  return (
    <div className="ni-content-card ni-content-card--disclaimers">
      <p className="ni-section-label ni-section-label--card">{t.disclaimerTitle}</p>
      <PublicList items={disclaimers} />
    </div>
  )
}

function PublicEvidenceList({
  embedded = false,
  evidence,
  t,
}: {
  embedded?: boolean
  evidence?: BasicNatalPublicEvidenceView[] | null
  t: InterpretationTranslations
}) {
  if (!hasItems(evidence)) {
    return null
  }

  const Wrapper = embedded ? "div" : "section"

  return (
    <Wrapper className={embedded ? "ni-public-evidence-inline" : "ni-content-card ni-content-card--public-evidence"}>
      <h4 className="ni-section-label ni-section-label--card">{t.evidenceTitle}</h4>
      <div className="ni-public-evidence-list">
        {evidence.map((item, index) => (
          <article key={`${item.label}-${index}`} className="ni-public-evidence-item">
            <h5 className="ni-public-evidence-item__label">{item.label}</h5>
            <p className="ni-public-evidence-item__meaning">{item.meaning}</p>
          </article>
        ))}
      </div>
    </Wrapper>
  )
}

function FreePublicReading({
  data,
  includePayloadDisclaimers,
  t,
}: {
  data: NatalInterpretationViewData
  includePayloadDisclaimers: boolean
  t: InterpretationTranslations
}) {
  const { interpretation } = data
  const sections = interpretation.sections ?? []
  const highlights = interpretation.highlights ?? []
  const advice = interpretation.advice ?? []

  return (
    <>
      <div className="ni-content-card ni-content-card--summary">
        <h3 className="ni-interpretation-title">{interpretation.title}</h3>
        <p className="ni-summary">{interpretation.summary}</p>
      </div>

      {hasItems(sections) && (
        <div className="ni-public-sections">
          {sections.map((section: NatalInterpretationSectionView) => (
            <article key={section.key} className="ni-public-section">
              {section.heading && <h4 className="ni-public-section__title">{section.heading}</h4>}
              <p className="ni-public-section__content">{section.content}</p>
            </article>
          ))}
        </div>
      )}

      {hasItems(highlights) && (
        <section className="ni-content-card ni-content-card--public-list">
          <h4 className="ni-section-label ni-section-label--card">{t.highlightsTitle}</h4>
          <PublicList className="ni-highlights ni-highlights--public" items={highlights} />
        </section>
      )}

      {hasItems(advice) && (
        <section className="ni-content-card ni-content-card--public-list">
          <h4 className="ni-section-label ni-section-label--card">{t.adviceTitle}</h4>
          <PublicList className="ni-advice-list" items={advice} />
        </section>
      )}

      {includePayloadDisclaimers && <PublicDisclaimers disclaimers={interpretation.disclaimers} t={t} />}
    </>
  )
}

function BasicV2Reading({ reading, t }: { reading: BasicNatalInterpretationView; t: InterpretationTranslations }) {
  const { interpretation } = reading

  return (
    <>
      <div className="ni-content-card ni-content-card--summary">
        <h3 className="ni-interpretation-title">{interpretation.title}</h3>
        <p className="ni-summary">{interpretation.introduction}</p>
      </div>

      <section className="ni-content-card ni-content-card--basic-themes">
        <h4 className="ni-section-label ni-section-label--card">{t.themesTitle}</h4>
        <div className="ni-basic-theme-list">
          {interpretation.themes.map((theme, index) => (
            <article key={`${theme.title}-${index}`} className="ni-basic-theme">
              <h5 className="ni-basic-theme__title">{theme.title}</h5>
              <p className="ni-basic-theme__narrative">{theme.narrative}</p>
              <PublicEvidenceList embedded evidence={theme.public_evidence} t={t} />
            </article>
          ))}
        </div>
      </section>

      <div className="ni-content-card ni-content-card--summary">
        <p className="ni-section-label ni-section-label--card">{t.conclusionTitle}</p>
        <p className="ni-summary">{interpretation.conclusion}</p>
      </div>

      <PublicEvidenceList evidence={reading.public_evidence} t={t} />

      {hasItems(reading.limitations) && (
        <section className="ni-content-card ni-content-card--public-list">
          <h4 className="ni-section-label ni-section-label--card">{t.limitationsTitle}</h4>
          <PublicList items={reading.limitations} />
        </section>
      )}

      <PublicDisclaimers disclaimers={reading.disclaimers} t={t} />
    </>
  )
}

export function InterpretationContent({
  data,
  lang,
  renderNarrativeReading,
  renderReadingSources,
}: {
  data: NatalInterpretationViewData
  lang: NatalInterpretationLocale
  renderNarrativeReading?: (reading: NatalNarrativeReadingView, lang: NatalInterpretationLocale) => ReactNode
  renderReadingSources?: (elements: UsedAstrologicalElementView[], lang: NatalInterpretationLocale) => ReactNode
}) {
  const t = natalChartTranslations[lang].interpretation
  const { meta, degraded_mode, narrative_natal_reading_v1: narrativeReading, basic_natal_interpretation_v2: basicReading } = data
  const isCompleteLevel = meta.level === "complete"
  const useCase = resolveUseCase(data)
  const isFreeLongInterpretation = useCase === "natal_long_free"
  const shouldShowFreePublicReading = !narrativeReading && !basicReading && (!isCompleteLevel || isFreeLongInterpretation)
  const shouldShowNarrativeMissing = isCompleteLevel && !narrativeReading && !basicReading && !isFreeLongInterpretation
  const legalNoticeLines = t.legalNoticeLines

  return (
    <div className="ni-content">
      {degraded_mode && (
        <div className="ni-degraded-notice">
          <AlertCircle size={16} className="ni-degraded-notice__icon" />
          {t.degradedNotice}
        </div>
      )}

      {shouldShowFreePublicReading && (
        <FreePublicReading data={data} includePayloadDisclaimers={isFreeLongInterpretation} t={t} />
      )}

      {narrativeReading ? (
        <>
          {renderNarrativeReading?.(narrativeReading, lang)}
          {renderReadingSources?.(narrativeReading.used_astrological_elements, lang)}
        </>
      ) : basicReading ? (
        <BasicV2Reading reading={basicReading} t={t} />
      ) : shouldShowNarrativeMissing ? (
        <div className="ni-content-card ni-content-card--missing-narrative" role="note">
          <p className="ni-section-label">{t.narrativeMissingTitle}</p>
          <p className="ni-summary">{t.narrativeMissingBody}</p>
        </div>
      ) : null}

      {legalNoticeLines.length > 0 && (
        <footer className="ni-disclaimer-footer">
          <div className="ni-degraded-notice ni-degraded-notice--disclaimer">
            <p className="ni-disclaimer-title">
              <AlertCircle size={14} />
              {t.disclaimerTitle}
            </p>
            <div className="ni-disclaimer-list">
              {legalNoticeLines.map((line, index) => (
                <p key={index} className="ni-disclaimer-item">{line}</p>
              ))}
            </div>
          </div>
        </footer>
      )}
    </div>
  )
}
