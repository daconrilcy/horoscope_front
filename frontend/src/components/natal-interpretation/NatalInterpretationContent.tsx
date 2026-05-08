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

export function InterpretationContent({
  data,
  lang,
  fallbackEvidence,
  isLockedFree,
}: {
  data: NatalInterpretationViewData
  lang: NatalInterpretationLocale
  fallbackEvidence?: string[]
  isLockedFree?: boolean
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
