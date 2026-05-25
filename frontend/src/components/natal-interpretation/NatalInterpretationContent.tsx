// Rendu presentational du contenu d'une interpretation natale.
import { useState } from "react"
import { AlertCircle, ChevronDown, ChevronUp, Sparkles } from "lucide-react"

import { LockedSection, UpgradeCTA } from "@ui"
import { getNatalLockedSectionCopy, getNatalSectionTeaser, natalChartTranslations } from "../../i18n/natalChart"
import { stripLeadingNumber, stripLeadingNumbering } from "@utils/strings"
import { EvidenceTags } from "./NatalInterpretationEvidence"
import type {
  NatalInterpretationLocale,
  NatalInterpretationSectionView,
  NatalInterpretationViewData,
} from "./NatalInterpretationTypes"

export type AstrologyProjectionViewData = {
  projection_type: "beginner_summary_v1" | "client_interpretation_projection_v1"
  projection_version: string
  payload: Record<string, unknown>
}

export type AstrologyProjectionPanelState = {
  isLoading: boolean
  isEntitlementError: boolean
  isApiError: boolean
  projections: AstrologyProjectionViewData[]
  refetchAll: () => void
}

export function InterpretationContent({
  data,
  lang,
  fallbackEvidence,
  isLockedFree,
  projectionState,
}: {
  data: NatalInterpretationViewData
  lang: NatalInterpretationLocale
  fallbackEvidence?: string[]
  isLockedFree?: boolean
  projectionState?: AstrologyProjectionPanelState
}) {
  const t = natalChartTranslations[lang].interpretation
  const { interpretation, meta, degraded_mode } = data
  const highlights = Array.isArray(interpretation.highlights) ? interpretation.highlights : []
  const sections = Array.isArray(interpretation.sections) ? interpretation.sections : []
  const advice = Array.isArray(interpretation.advice) ? interpretation.advice : []
  const evidence =
    Array.isArray(interpretation.evidence) && interpretation.evidence.length > 0
      ? interpretation.evidence
      : fallbackEvidence ?? []
  const legalNoticeLines = t.legalNoticeLines

  return (
    <div className="ni-content">
      {degraded_mode && (
        <div className="ni-degraded-notice">
          <AlertCircle size={16} className="ni-degraded-notice__icon" />
          {t.degradedNotice}
        </div>
      )}

      <div className="ni-content-card ni-content-card--summary">
        <h3 className="ni-interpretation-title">{interpretation.title}</h3>
        {meta.persona_name && (
          <p className="ni-persona-text">
            {t.completeBy} <strong>{meta.persona_name}</strong>
          </p>
        )}
        <p className="ni-summary">{interpretation.summary}</p>
      </div>

      <div>
        <p className="ni-section-label">{t.highlightsTitle}</p>
        <HighlightsChips highlights={highlights} />
      </div>

      <SectionAccordion sections={sections} sectionsMap={t.sectionsMap} lang={lang} isLockedFree={isLockedFree} />

      <div className="ni-content-card ni-content-card--advice ni-advice-block">
        <p className="ni-section-label ni-section-label--card">{t.adviceTitle}</p>
        <h4 className="ni-advice-title">{t.adviceTitle}</h4>
        {isLockedFree ? (
          <LockedSection
            cta={<UpgradeCTA featureCode="natal_chart_long" variant="button" to="/settings/subscription" />}
          >
            <AdviceLockedContent bullets={t.lockedAdviceBullets} body={t.lockedAdviceBody} />
          </LockedSection>
        ) : (
          <AdviceList advice={advice} />
        )}
      </div>

      <EvidenceTags evidence={evidence} title={t.evidenceTitle} t={t} />

      <AstrologyProjectionsPanel projectionState={projectionState} />

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

function AstrologyProjectionsPanel({
  projectionState,
}: {
  projectionState?: AstrologyProjectionPanelState
}) {
  if (!projectionState) {
    return null
  }

  return (
    <section className="ni-projections" aria-label="Projections astrologiques">
      <div className="ni-content-card ni-projections__card">
        <p className="ni-section-label ni-section-label--card">Projections B2C</p>
        <h3 className="ni-projections__title">Synthèse publique du thème</h3>

        {projectionState.isLoading ? (
          <p className="ni-projections__state">Chargement des projections astrologiques...</p>
        ) : projectionState.isEntitlementError ? (
          <p className="ni-projections__state ni-projections__state--locked" role="alert">
            Votre abonnement actuel ne permet pas cette profondeur d'interprétation.
          </p>
        ) : projectionState.isApiError ? (
          <div className="ni-projections__state ni-projections__state--error" role="alert">
            <p>Les projections ne sont pas disponibles pour le moment.</p>
            <button
              type="button"
              className="ni-action-btn ni-action-btn--primary"
              onClick={projectionState.refetchAll}
            >
              Réessayer
            </button>
          </div>
        ) : projectionState.projections.length === 0 ? (
          <p className="ni-projections__state">Aucune projection publique n'est disponible pour ce thème.</p>
        ) : (
          <div className="ni-projections__grid">
            {projectionState.projections.map((projection) => (
              <ProjectionCard key={projection.projection_type} projection={projection} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

function ProjectionCard({ projection }: { projection: AstrologyProjectionViewData }) {
  const state = readString(projection.payload.state)
  const title = projection.projection_type === "beginner_summary_v1"
    ? "Résumé débutant"
    : "Interprétation client"
  const messages = readDisplayMessages(projection.payload.display_messages)
  const sections = readSections(projection.payload.sections)
  const summaryItems = readSummaryItems(projection.payload.summary_items)
  const supportElements = readSupportElements(projection.payload.support_elements)
  const errorMessage = readProjectionErrorMessage(projection.payload.error)
  const isEmpty = state === "empty" || (sections.length === 0 && summaryItems.length === 0 && supportElements.length === 0)

  return (
    <article className="ni-projection-card">
      <div className="ni-projection-card__header">
        <h4 className="ni-projection-card__title">{title}</h4>
        <span className="ni-projection-card__version">{projection.projection_version}</span>
      </div>

      {state === "degraded" && (
        <p className="ni-projections__state ni-projections__state--degraded">
          Projection partielle: données de naissance incomplètes.
        </p>
      )}

      {errorMessage && (
        <p className="ni-projections__state ni-projections__state--locked">{errorMessage}</p>
      )}

      {messages.length > 0 && (
        <ul className="ni-projection-list">
          {messages.map((message) => (
            <li key={message}>{message}</li>
          ))}
        </ul>
      )}

      {summaryItems.length > 0 && (
        <ul className="ni-projection-list">
          {summaryItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}

      {sections.length > 0 && (
        <div className="ni-projection-sections">
          {sections.map((section) => (
            <section key={section.code} className="ni-projection-section">
              <h5>{section.title}</h5>
              <p>{section.text}</p>
            </section>
          ))}
        </div>
      )}

      {supportElements.length > 0 && (
        <ul className="ni-projection-list ni-projection-list--support">
          {supportElements.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}

      {isEmpty && !errorMessage && (
        <p className="ni-projections__state">Aucun contenu affichable pour cette projection.</p>
      )}
    </article>
  )
}

function readString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null
}

function readDisplayMessages(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.flatMap((item) => {
    if (typeof item === "string") return [item]
    if (item && typeof item === "object" && "message" in item) {
      const message = readString((item as { message?: unknown }).message)
      return message ? [message] : []
    }
    return []
  })
}

function readSummaryItems(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.flatMap((item) => {
    if (typeof item === "string") return [item]
    if (item && typeof item === "object") {
      const record = item as Record<string, unknown>
      return [readString(record.label) ?? readString(record.value) ?? readString(record.code)].filter(Boolean) as string[]
    }
    return []
  })
}

function readSections(value: unknown): Array<{ code: string; title: string; text: string }> {
  if (!Array.isArray(value)) return []
  return value.flatMap((item, index) => {
    if (!item || typeof item !== "object") return []
    const record = item as Record<string, unknown>
    const code = readString(record.code) ?? `section-${index}`
    const title = readString(record.title) ?? readString(record.heading) ?? code
    const text = readString(record.text) ?? readString(record.content) ?? readString(record.summary)
    return text ? [{ code, title, text }] : []
  })
}

function readSupportElements(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.flatMap((item) => {
    if (typeof item === "string") return [item]
    if (!item || typeof item !== "object") return []
    const record = item as Record<string, unknown>
    return [readString(record.label) ?? readString(record.text) ?? readString(record.code)].filter(Boolean) as string[]
  })
}

function readProjectionErrorMessage(value: unknown): string | null {
  if (!value || typeof value !== "object") return null
  return readString((value as { message?: unknown }).message)
}

function HighlightsChips({ highlights }: { highlights: string[] }) {
  return (
    <div className="ni-highlights">
      {highlights.map((highlight, index) => (
        <div key={index} className="ni-highlight-chip">
          <div className="ni-highlight-icon">
            <Sparkles size={16} className="ni-highlight-star" />
          </div>
          <p className="ni-highlight-text">{stripLeadingNumbering(highlight)}</p>
        </div>
      ))}
    </div>
  )
}

function SectionAccordion({
  sections,
  sectionsMap,
  lang,
  isLockedFree,
}: {
  sections: NatalInterpretationSectionView[]
  sectionsMap: Record<string, string>
  lang: NatalInterpretationLocale
  isLockedFree?: boolean
}) {
  const [openIds, setOpenIds] = useState<string[]>(sections[0] ? [`${sections[0].key}-0`] : [])

  const toggleSection = (sectionId: string) => {
    setOpenIds((previous) =>
      previous.includes(sectionId)
        ? previous.filter((id) => id !== sectionId)
        : [...previous, sectionId],
    )
  }

  return (
    <div className="ni-accordion">
      {sections.map((section, index) => {
        const sectionId = `${section.key}-${index}`
        const isOpen = openIds.includes(sectionId)
        const sectionTitle = section.heading?.trim() || sectionsMap[section.key] || section.key

        if (isLockedFree) {
          return (
            <div key={sectionId} className="ni-accordion-item">
              <div className="ni-accordion-header ni-accordion-header--locked">
                <span className="ni-accordion-title">{sectionTitle}</span>
              </div>
              <LockedSection
                cta={<UpgradeCTA featureCode="natal_chart_long" variant="button" to="/settings/subscription" />}
              >
                <div className="teaser-placeholder">
                  <p className="teaser-placeholder__lead">{getNatalSectionTeaser(section.key, lang)}</p>
                  <p className="teaser-placeholder__body">{getNatalLockedSectionCopy(section.key, lang)}</p>
                </div>
              </LockedSection>
            </div>
          )
        }

        return (
          <div key={sectionId} className="ni-accordion-item">
            <button type="button" onClick={() => toggleSection(sectionId)} className="ni-accordion-header">
              <span className="ni-accordion-title">{sectionTitle}</span>
              {isOpen
                ? <ChevronUp size={20} className="ni-accordion-icon ni-accordion-icon--open" />
                : <ChevronDown size={20} className="ni-accordion-icon ni-accordion-icon--closed" />}
            </button>
            {isOpen && (
              <div className="ni-accordion-body">
                <p className="ni-accordion-text">{section.content}</p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function AdviceList({ advice }: { advice: string[] }) {
  return (
    <div className="ni-advice-list">
      {advice.map((item, index) => (
        <div key={index} className="ni-advice-item">
          <div className="ni-advice-icon">
            <Sparkles size={12} className="ni-advice-star" />
          </div>
          <p className="ni-advice-text">{stripLeadingNumber(item)}</p>
        </div>
      ))}
    </div>
  )
}

function AdviceLockedContent({ bullets, body }: { bullets: string[]; body: string }) {
  return (
    <div className="ni-advice-list ni-advice-list--locked">
      {bullets.map((item, index) => (
        <div key={index} className="ni-advice-item">
          <div className="ni-advice-icon">
            <Sparkles size={12} className="ni-advice-star" />
          </div>
          <p className="ni-advice-text">{item}</p>
        </div>
      ))}
      <p className="ni-advice-text ni-advice-text--locked">{body}</p>
    </div>
  )
}
