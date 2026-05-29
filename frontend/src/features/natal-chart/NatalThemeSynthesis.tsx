// Section de synthese IA: elle repositionne le flux d'interpretation existant sans le dupliquer.
import type { FeatureEntitlementResponse } from "../../api/billing"
import type { AstrologyLang } from "../../i18n/astrology"
import { NatalInterpretationSection } from "./NatalInterpretation"

type HeaderActionRequest = {
  kind: "upgrade" | "switch_persona"
  nonce: number
} | null

type ActiveInterpretation = {
  level: "short" | "complete"
  personaName: string | null
  canSwitchPersona: boolean
  isBasicCompleteLimitReached: boolean
}

type NatalThemeSynthesisProps = {
  chartId: string
  lang: AstrologyLang
  fallbackEvidence: string[]
  initialPersonaId: string | null
  initialInterpretationId: number | null
  isLockedFree: boolean
  longFeatureAccess: FeatureEntitlementResponse | undefined
  actionRequest: HeaderActionRequest
  onActiveInterpretationChange: (state: ActiveInterpretation) => void
}

/** Rend la synthese narrative comme premiere lecture utile du theme natal. */
export function NatalThemeSynthesis({
  chartId,
  lang,
  fallbackEvidence,
  initialPersonaId,
  initialInterpretationId,
  isLockedFree,
  longFeatureAccess,
  actionRequest,
  onActiveInterpretationChange,
}: NatalThemeSynthesisProps) {
  return (
    <section className="natal-theme-synthesis" aria-labelledby="natal-theme-synthesis-title">
      <div className="natal-section-heading">
        <span className="natal-section-eyebrow">Synthese IA</span>
        <h2 id="natal-theme-synthesis-title">Ce que votre theme raconte</h2>
      </div>
      <NatalInterpretationSection
        chartLoaded
        chartId={chartId}
        lang={lang}
        fallbackEvidence={fallbackEvidence}
        initialPersonaId={initialPersonaId}
        initialInterpretationId={initialInterpretationId}
        isLockedFree={isLockedFree}
        longFeatureAccess={longFeatureAccess}
        onActiveInterpretationChange={onActiveInterpretationChange}
        actionRequest={actionRequest}
      />
    </section>
  )
}
