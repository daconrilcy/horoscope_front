// Rendu presentational du contenu d'une interpretation natale (lecture narrative uniquement).
import { AlertCircle } from "lucide-react"

import { natalChartTranslations } from "../../i18n/natalChart"
import { NatalNarrativeReading } from "../../features/natal-chart/NatalNarrativeReading"
import { NatalReadingSources } from "../../features/natal-chart/NatalReadingSources"
import type { NatalInterpretationLocale, NatalInterpretationViewData } from "./NatalInterpretationTypes"

export function InterpretationContent({
  data,
  lang,
}: {
  data: NatalInterpretationViewData
  lang: NatalInterpretationLocale
}) {
  const t = natalChartTranslations[lang].interpretation
  const { interpretation, meta, degraded_mode, narrative_natal_reading_v1: narrativeReading } = data
  const isCompleteLevel = meta.level === "complete"
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

      {narrativeReading ? (
        <>
          <NatalNarrativeReading reading={narrativeReading} lang={lang} />
          <NatalReadingSources elements={narrativeReading.used_astrological_elements} lang={lang} />
        </>
      ) : isCompleteLevel ? (
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
