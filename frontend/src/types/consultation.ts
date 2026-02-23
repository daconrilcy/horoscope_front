export type ConsultationType = "dating" | "pro" | "event" | "free"

export type DrawingOption = "none" | "tarot" | "runes"

export type ConsultationDraft = {
  type: ConsultationType | null
  astrologerId: string | null
  drawingOption: DrawingOption
  context: string
}

export type DrawingResult = {
  cards?: string[]
  runes?: string[]
}

export type ConsultationResult = {
  id: string
  type: ConsultationType
  astrologerId: string
  drawingOption: DrawingOption
  context: string
  drawing?: DrawingResult
  interpretation: string
  createdAt: string
}

export type ConsultationTypeConfig = {
  id: ConsultationType
  labelKey: string
  icon: string
}

export const CONSULTATION_TYPES: ConsultationTypeConfig[] = [
  { id: "dating", labelKey: "type_dating", icon: "💕" },
  { id: "pro", labelKey: "type_pro", icon: "💼" },
  { id: "event", labelKey: "type_event", icon: "📅" },
  { id: "free", labelKey: "type_free", icon: "❓" },
]

export type DrawingOptionConfig = {
  id: DrawingOption
  labelKey: string
  icon: string
}

export const DRAWING_OPTIONS: DrawingOptionConfig[] = [
  { id: "none", labelKey: "drawing_none", icon: "🚫" },
  { id: "tarot", labelKey: "drawing_tarot", icon: "🃏" },
  { id: "runes", labelKey: "drawing_runes", icon: "ᚱ" },
]

export const WIZARD_STEPS = ["type", "astrologer", "drawing", "validation"] as const
export type WizardStep = (typeof WIZARD_STEPS)[number]
export const WIZARD_LAST_STEP_INDEX = WIZARD_STEPS.length - 1

export const WIZARD_STEP_LABELS: Record<WizardStep, string> = {
  type: "step_type",
  astrologer: "step_astrologer",
  drawing: "step_drawing",
  validation: "step_validation",
}

export const CONTEXT_TRUNCATE_LENGTH = 50
export const CONTEXT_MAX_LENGTH = 2000
export const HISTORY_MAX_LENGTH = 20
export const AUTO_ASTROLOGER_ID = "auto"

export const VALID_CONSULTATION_TYPES: ConsultationType[] = CONSULTATION_TYPES.map((c) => c.id)
export const VALID_DRAWING_OPTIONS: DrawingOption[] = DRAWING_OPTIONS.map((d) => d.id)

export function getConsultationTypeConfig(type: ConsultationType): ConsultationTypeConfig | undefined {
  return CONSULTATION_TYPES.find((ct) => ct.id === type)
}

export function getDrawingOptionConfig(option: DrawingOption): DrawingOptionConfig | undefined {
  return DRAWING_OPTIONS.find((d) => d.id === option)
}
