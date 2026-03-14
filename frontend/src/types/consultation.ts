export type ConsultationType =
  | "period"
  | "work"
  | "orientation"
  | "relation"
  | "timing"
  | "dating"
  | "pro"
  | "event"
  | "free"

export type OtherPersonDraft = {
  birthDate: string
  birthTime: string | null
  birthTimeKnown: boolean
  birthPlace: string
  birthCity: string
  birthCountry: string
  placeResolvedId?: number | null
  birthLat?: number | null
  birthLon?: number | null
}

export type ConsultationDraft = {
  type: ConsultationType | null
  astrologerId: string | null
  context: string
  objective?: string
  timeHorizon?: string | null
  otherPerson?: OtherPersonDraft | null
  isInteraction?: boolean
}

export type ConsultationSection = {
  id: string
  title: string
  content: string
  blocks?: ConsultationBlock[]
}

export type ConsultationBlock = {
  kind: "paragraph" | "title" | "subtitle" | "bullet_list"
  text?: string | null
  items?: string[]
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
  fallbackMode?: string | null
  precisionLevel?: string | null
  sections?: ConsultationSection[]
  routeKey?: string | null
  saveThirdParty?: boolean
  thirdPartyNickname?: string
}

export type ConsultationTypeConfig = {
  id: ConsultationType
  labelKey: string
  uxPromiseKey: string
  icon: string
  isLegacy?: boolean
  requiredData?: ("birth_profile" | "location" | "current_time")[]
  fallbackAllowed?: boolean
  interactionEligible?: boolean
  defaultInteraction?: boolean
}

export const CONSULTATION_TYPES: ConsultationTypeConfig[] = [
  {
    id: "period",
    labelKey: "type_period_label",
    uxPromiseKey: "type_period_promise",
    icon: "📅",
    requiredData: ["birth_profile"],
    fallbackAllowed: true,
  },
  {
    id: "work",
    labelKey: "type_work_label",
    uxPromiseKey: "type_work_promise",
    icon: "💼",
    requiredData: ["birth_profile"],
    fallbackAllowed: true,
    interactionEligible: true,
  },
  {
    id: "orientation",
    labelKey: "type_orientation_label",
    uxPromiseKey: "type_orientation_promise",
    icon: "🗺️",
    requiredData: ["birth_profile"],
    fallbackAllowed: false,
  },
  {
    id: "relation",
    labelKey: "type_relation_label",
    uxPromiseKey: "type_relation_promise",
    icon: "🤝",
    requiredData: ["birth_profile"],
    fallbackAllowed: true,
    interactionEligible: true,
    defaultInteraction: true,
  },
  {
    id: "timing",
    labelKey: "type_timing_label",
    uxPromiseKey: "type_timing_promise",
    icon: "⏱️",
    requiredData: ["birth_profile", "location"],
    fallbackAllowed: false,
  },
  // Legacy types (hidden from creation but kept for history rendering)
  {
    id: "dating",
    labelKey: "type_dating",
    uxPromiseKey: "type_dating",
    icon: "💕",
    isLegacy: true,
  },
  {
    id: "pro",
    labelKey: "type_pro",
    uxPromiseKey: "type_pro",
    icon: "💼",
    isLegacy: true,
  },
  {
    id: "event",
    labelKey: "type_event",
    uxPromiseKey: "type_event",
    icon: "📅",
    isLegacy: true,
  },
  {
    id: "free",
    labelKey: "type_free",
    uxPromiseKey: "type_free",
    icon: "❓",
    isLegacy: true,
  },
]

export const VALID_CREATABLE_TYPES: ConsultationType[] = CONSULTATION_TYPES.filter(
  (c) => !c.isLegacy
).map((c) => c.id)

export const INTERACTION_ELIGIBLE_TYPES: ConsultationType[] = CONSULTATION_TYPES.filter(
  (c) => c.interactionEligible
).map((c) => c.id)


export const WIZARD_STEPS = ["type", "frame", "collection", "summary"] as const
export type WizardStep = (typeof WIZARD_STEPS)[number]
export const WIZARD_LAST_STEP_INDEX = WIZARD_STEPS.length - 1

export const WIZARD_STEP_LABELS: Record<WizardStep, string> = {
  type: "step_type",
  frame: "step_frame",
  collection: "step_collection",
  summary: "step_summary",
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
  const config = getConsultationTypeConfig(type)
  if (config?.isLegacy) {
    switch (type) {
      case "dating":
        return "objective_dating"
      case "pro":
        return "objective_pro"
      case "event":
        return "objective_event"
      case "free":
        return "objective_free"
    }
  }
  return `objective_${type}`
}
