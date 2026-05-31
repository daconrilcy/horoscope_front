// Types de rendu locaux pour isoler les enfants presentational de l'API natale.
import type { AstrologyLang } from "../../i18n/astrology"
import type { natalChartTranslations } from "../../i18n/natalChart"

export type InterpretationTranslations = typeof natalChartTranslations["fr"]["interpretation"]

export type NatalInterpretationSectionView = {
  key: string
  heading?: string | null
  content: string
}

export type NatalNarrativeReadingChapterView = {
  key: "personality" | "emotional_world" | "relationships" | "vocation" | "evolution_path"
  title: string
  narrative: string
  key_points: string[]
}

export type UsedAstrologicalElementView = {
  astrological_label: string
  consequence: string
}

export type NatalNarrativeReadingView = {
  contract_version: "narrative_natal_reading_v1"
  editorial_profile: "free" | "basic" | "premium"
  chapters: NatalNarrativeReadingChapterView[]
  used_astrological_elements: UsedAstrologicalElementView[]
}

export type BasicNatalPublicEvidenceView = {
  source_id?: string | null
  source_type?: string | null
  label: string
  meaning: string
  theme?: string
  used_in_sections?: string[] | null
}

export type BasicNatalPublicThemeView = {
  title: string
  narrative: string
  public_evidence: BasicNatalPublicEvidenceView[]
}

export type BasicNatalInterpretationView = {
  locale: string
  level: "basic"
  engine_version: "basic-natal-reading-v1"
  schema_version: "basic_natal_interpretation_v2"
  taxonomy_version: "basic-natal-theme-taxonomy-v1"
  salience_version: "basic-natal-salience-v1"
  prompt_version: "basic-natal-draft-prompt-v1"
  validator_version: "basic-natal-validator-v1"
  interpretation: {
    title: string
    introduction: string
    themes: BasicNatalPublicThemeView[]
    conclusion: string
    public_evidence: BasicNatalPublicEvidenceView[]
  }
  limitations: string[]
  disclaimers: string[]
  public_evidence: BasicNatalPublicEvidenceView[]
}

export type NatalInterpretationViewData = {
  chart_id?: string
  degraded_mode?: string | null
  narrative_natal_reading_v1?: NatalNarrativeReadingView | null
  basic_natal_interpretation_v2?: BasicNatalInterpretationView | null
  meta: {
    id?: number | null
    level?: "short" | "complete"
    use_case?: string | null
    persona_name?: string | null
    persisted_at?: string | null
  }
  use_case?: string | null
  interpretation: {
    title: string
    summary: string
    highlights?: string[] | null
    sections?: NatalInterpretationSectionView[] | null
    advice?: string[] | null
    evidence?: string[] | null
    disclaimers?: string[] | null
  }
}

export type NatalInterpretationHistoryItemView = {
  id: number
  created_at: string
  level: "short" | "complete"
  persona_name?: string | null
}

export type NatalInterpretationLocale = AstrologyLang
