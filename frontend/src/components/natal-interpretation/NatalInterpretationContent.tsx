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

type AggregatedBasicEvidence = BasicNatalPublicEvidenceView & {
  usedInSections: string[]
}

type PublicEvidenceItem = BasicNatalPublicEvidenceView & {
  usedInSections?: string[]
}

function resolveUseCase(data: NatalInterpretationViewData): string | null {
  return data.use_case ?? data.meta.use_case ?? null
}

function hasItems<T>(items: T[] | null | undefined): items is T[] {
  return Array.isArray(items) && items.length > 0
}

function normalizePublicText(value: string | null | undefined): string {
  return (value ?? "").trim().replace(/\s+/g, " ").toLowerCase()
}

function getEvidenceKey(item: BasicNatalPublicEvidenceView): string {
  if (item.source_id?.trim()) {
    return `source:${item.source_id.trim()}`
  }

  return [
    "public",
    normalizePublicText(item.source_type),
    normalizePublicText(item.label),
    normalizePublicText(item.meaning),
  ].join("\u0000")
}

function collectUsageLabels(item: BasicNatalPublicEvidenceView, themeTitle?: string): string[] {
  return [themeTitle, item.theme, ...(item.used_in_sections ?? [])]
    .map((usage) => usage?.trim())
    .filter((usage): usage is string => Boolean(usage))
}

// Agrege les preuves Basic V2 en une annexe stable sans perdre les themes d'usage.
function collectBasicPublicEvidence(reading: BasicNatalInterpretationView): AggregatedBasicEvidence[] {
  const merged: AggregatedBasicEvidence[] = []
  const seen = new Set<string>()

  const append = (item: BasicNatalPublicEvidenceView, themeTitle?: string) => {
    const key = getEvidenceKey(item)
    const usageLabels = collectUsageLabels(item, themeTitle)
    const existingIndex = merged.findIndex((entry) => getEvidenceKey(entry) === key)

    if (existingIndex >= 0) {
      const existing = merged[existingIndex]
      merged[existingIndex] = {
        ...existing,
        usedInSections: Array.from(new Set([...existing.usedInSections, ...usageLabels])),
      }
      return
    }

    if (seen.has(key)) {
      return
    }
    seen.add(key)

    merged.push({
      ...item,
      usedInSections: Array.from(new Set(usageLabels)),
    })
  }

  for (const theme of reading.interpretation.themes) {
    for (const item of theme.public_evidence) {
      append(item, theme.title)
    }
  }

  for (const item of reading.interpretation.public_evidence) {
    append(item)
  }

  for (const item of reading.public_evidence) {
    append(item)
  }

  return merged
}

// Fusionne les textes publics Basic V2 pour conserver une seule zone legale finale.
function mergePublicLegalLines(...groups: Array<string[] | null | undefined>): string[] {
  const merged: string[] = []
  const seen = new Set<string>()

  for (const group of groups) {
    for (const item of group ?? []) {
      const key = normalizePublicText(item)
      if (!key || seen.has(key)) {
        continue
      }
      seen.add(key)
      merged.push(item)
    }
  }

  return merged
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
  evidence,
  t,
}: {
  evidence?: PublicEvidenceItem[] | null
  t: InterpretationTranslations
}) {
  if (!hasItems(evidence)) {
    return null
  }

  return (
    <section className="ni-content-card ni-content-card--public-evidence">
      <h4 className="ni-section-label ni-section-label--card">{t.evidenceTitle}</h4>
      <p className="ni-public-evidence-intro">{t.evidenceIntro}</p>
      <div className="ni-public-evidence-list">
        {evidence.map((item, index) => {
          const usedInSections = item.usedInSections ?? []

          return (
            <article key={`${getEvidenceKey(item)}-${index}`} className="ni-public-evidence-item">
              <h5 className="ni-public-evidence-item__label">{item.label}</h5>
              <p className="ni-public-evidence-item__meaning">{item.meaning}</p>
              {usedInSections.length > 0 && (
                <p className="ni-public-evidence-item__usage">
                  {t.evidenceUsagePrefix} : {usedInSections.join(", ")}
                </p>
              )}
            </article>
          )
        })}
      </div>
    </section>
  )
}

function FreePublicReading({
  data,
  t,
}: {
  data: NatalInterpretationViewData
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

      <PublicDisclaimers disclaimers={interpretation.disclaimers} t={t} />
    </>
  )
}

function BasicV2Reading({
  legalNoticeLines,
  reading,
  t,
}: {
  legalNoticeLines: string[]
  reading: BasicNatalInterpretationView
  t: InterpretationTranslations
}) {
  const { interpretation } = reading
  const publicEvidence = collectBasicPublicEvidence(reading)
  const legalLines = mergePublicLegalLines(reading.limitations, reading.disclaimers, legalNoticeLines)

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
            </article>
          ))}
        </div>
      </section>

      <div className="ni-content-card ni-content-card--summary">
        <p className="ni-section-label ni-section-label--card">{t.conclusionTitle}</p>
        <p className="ni-summary">{interpretation.conclusion}</p>
      </div>

      <PublicEvidenceList evidence={publicEvidence} t={t} />

      {hasItems(legalLines) && (
        <section className="ni-content-card ni-content-card--disclaimers ni-content-card--basic-legal">
          <h4 className="ni-section-label ni-section-label--card">{t.disclaimerTitle}</h4>
          <PublicList items={legalLines} />
        </section>
      )}
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
        <FreePublicReading data={data} t={t} />
      )}

      {narrativeReading ? (
        <>
          {renderNarrativeReading?.(narrativeReading, lang)}
          {renderReadingSources?.(narrativeReading.used_astrological_elements, lang)}
        </>
      ) : basicReading ? (
        <BasicV2Reading legalNoticeLines={legalNoticeLines} reading={basicReading} t={t} />
      ) : shouldShowNarrativeMissing ? (
        <div className="ni-content-card ni-content-card--missing-narrative" role="note">
          <p className="ni-section-label">{t.narrativeMissingTitle}</p>
          <p className="ni-summary">{t.narrativeMissingBody}</p>
        </div>
      ) : null}

      {!basicReading && legalNoticeLines.length > 0 && (
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
