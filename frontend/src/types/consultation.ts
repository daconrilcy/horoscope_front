export type ConsultationType =
  | "period"
  | "career"
  | "orientation"
  | "relationship"
  | "timing"
  | "work" // Legacy, mapped to career
  | "relation" // Legacy, mapped to relationship
  | "dating"
  | "pro"
  | "event"
  | "free"

export type OtherPersonDraft = {
  birthDate: string
  birthTime?: string | null
  birthTimeKnown: boolean
  birthPlace: string
  birthCity: string
  birthCountry: string
  placeResolvedId: number | null
  birthLat?: number | null
  birthLon?: number | null
}

export type ConsultationDraft = {
  type: ConsultationType | null
  astrologerId: string
  context: string
  objective: string
  timeHorizon: string | null
  isInteraction: boolean
  otherPerson: OtherPersonDraft | null
  saveThirdParty: boolean
  thirdPartyNickname: string | null
  selectedThirdPartyExternalId: string | null
}

export type ConsultationTypeConfig = {
  id: ConsultationType
  icon: string
  labelKey: string
  uxPromiseKey: string
  objectiveKey: string
  isLegacy?: boolean
}

export const CONSULTATION_TYPES: ConsultationTypeConfig[] = [
  {
    id: "period",
    icon: "📅",
    labelKey: "type_period_label",
    uxPromiseKey: "type_period_promise",
    objectiveKey: "objective_period",
  },
  {
    id: "career",
    icon: "💼",
    labelKey: "type_work_label",
    uxPromiseKey: "type_work_promise",
    objectiveKey: "objective_work",
  },
  {
    id: "orientation",
    icon: "🗺️",
    labelKey: "type_orientation_label",
    uxPromiseKey: "type_orientation_promise",
    objectiveKey: "objective_orientation",
  },
  {
    id: "relationship",
    icon: "🤝",
    labelKey: "type_relation_label",
    uxPromiseKey: "type_relation_promise",
    objectiveKey: "objective_relation",
  },
  {
    id: "timing",
    icon: "⏱️",
    labelKey: "type_timing_label",
    uxPromiseKey: "type_timing_promise",
    objectiveKey: "objective_timing",
  },
  // Legacy mappings for breadcrumbs/history labels if needed
  {
    id: "work",
    icon: "💼",
    labelKey: "type_work_label",
    uxPromiseKey: "type_work_promise",
    objectiveKey: "objective_work",
    isLegacy: true,
  },
  {
    id: "relation",
    icon: "🤝",
    labelKey: "type_relation_label",
    uxPromiseKey: "type_relation_promise",
    objectiveKey: "objective_relation",
    isLegacy: true,
  },
]

export const VALID_CREATABLE_TYPES: ConsultationType[] = [
  "period",
  "career",
  "orientation",
  "relationship",
  "timing",
  "work", // Allowed for redirect
  "relation", // Allowed for redirect
]

export const VALID_CONSULTATION_TYPES: ConsultationType[] = [
  ...VALID_CREATABLE_TYPES,
  "dating",
  "pro",
  "event",
  "free",
]

export const INTERACTION_ELIGIBLE_TYPES: ConsultationType[] = ["career", "work", "relationship", "relation"]

export const WIZARD_LAST_STEP_INDEX = 3
export const HISTORY_MAX_LENGTH = 50

export const WIZARD_STEPS = ["type", "frame", "collection", "summary"] as const
export type WizardStep = (typeof WIZARD_STEPS)[number]

export const WIZARD_STEP_LABELS: Record<WizardStep, string> = {
  type: "select_type",
  frame: "frame_request",
  collection: "additional_info",
  summary: "final_verification",
}

export const CONTEXT_MAX_LENGTH = 2000
export const CONTEXT_TRUNCATE_LENGTH = 120

export function getConsultationTypeConfig(
  type: ConsultationType | string
): ConsultationTypeConfig | undefined {
  return CONSULTATION_TYPES.find((t) => t.id === type)
}

export function getObjectiveForType(type: ConsultationType): string {
  const config = getConsultationTypeConfig(type)
  if (config) return config.objectiveKey

  // Fallbacks for unknown types
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
  return `objective_${type}`
}

/**
 * Mappe les anciennes clés vers les nouvelles clés canoniques.
 * AC2: work -> career, relation -> relationship
 */
export function mapLegacyConsultationKey(key: string): ConsultationType {
  const mapping: Record<string, ConsultationType> = {
    work: "career",
    relation: "relationship",
  }
  return mapping[key] || (key as ConsultationType)
}
