// Types de rendu locaux pour isoler les enfants presentational de l'API natale.
import type { NarrativeNatalReadingV1 } from "../../api/natal-chart"
import type { AstrologyLang } from "../../i18n/astrology"
import type { natalChartTranslations } from "../../i18n/natalChart"

export type InterpretationTranslations = typeof natalChartTranslations["fr"]["interpretation"]

export type NatalInterpretationSectionView = {
  key: string
  heading?: string | null
  content: string
}

export type NatalInterpretationViewData = {
  degraded_mode?: string | null
  narrative_natal_reading_v1?: NarrativeNatalReadingV1 | null
  meta: {
    id?: number | null
    level?: "short" | "complete"
    persona_name?: string | null
    persisted_at?: string | null
  }
  interpretation: {
    title: string
    summary: string
    highlights?: string[] | null
    sections?: NatalInterpretationSectionView[] | null
    advice?: string[] | null
    evidence?: string[] | null
  }
}

export type NatalInterpretationHistoryItemView = {
  id: number
  created_at: string
  level: "short" | "complete"
  persona_name?: string | null
}

export type NatalInterpretationLocale = AstrologyLang
