export type ConsultationType = "dating" | "pro" | "event" | "free"

export type ConsultationDraft = {
  type: ConsultationType | null
  astrologerId: string | null
  context: string
  objective?: string
  timeHorizon?: string | null
}

export type ConsultationResult = {
  id: string
  type: ConsultationType
  astrologerId: string
  context: string
  objective: string
  timeHorizon?: string | null
  summary: string
  keyPoints: string[]
  actionableAdvice: string[]
  disclaimer?: string
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

export const WIZARD_STEPS = ["type", "astrologer", "validation"] as const
export type WizardStep = (typeof WIZARD_STEPS)[number]
export const WIZARD_LAST_STEP_INDEX = WIZARD_STEPS.length - 1

export const WIZARD_STEP_LABELS: Record<WizardStep, string> = {
  type: "step_type",
  astrologer: "step_astrologer",
  validation: "step_validation",
}

export const CONTEXT_TRUNCATE_LENGTH = 50
export const CONTEXT_MAX_LENGTH = 2000
export const HISTORY_MAX_LENGTH = 20
export const AUTO_ASTROLOGER_ID = "auto"

export const VALID_CONSULTATION_TYPES: ConsultationType[] = CONSULTATION_TYPES.map((c) => c.id)

export function getConsultationTypeConfig(type: ConsultationType): ConsultationTypeConfig | undefined {
  return CONSULTATION_TYPES.find((ct) => ct.id === type)
}

export function getObjectiveForType(type: ConsultationType): string {
  switch (type) {
    case "dating":
      return "objective_dating"
    case "pro":
      return "objective_pro"
    case "event":
      return "objective_event"
    case "free":
    default:
      return "objective_free"
  }
}
