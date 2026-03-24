import {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useMemo,
  type ReactNode,
} from "react"

import {
  HISTORY_MAX_LENGTH,
  VALID_CONSULTATION_TYPES,
  WIZARD_LAST_STEP_INDEX,
  WIZARD_STEPS,
  getConsultationTypeConfig,
  getObjectiveForType,
  type ConsultationType,
  type ConsultationDraft,
  type ConsultationResult,
  type WizardStep,
  type OtherPersonDraft,
} from "../types/consultation"
import { type ConsultationPrecheckData } from "../api/consultations"

const INITIAL_DRAFT: ConsultationDraft = {
  type: null,
  astrologerId: "auto",
  context: "",
  saveThirdParty: false,
  thirdPartyNickname: "",
  selectedThirdPartyExternalId: null,
}

export type ConsultationState = {
  draft: ConsultationDraft
  step: number
  result: ConsultationResult | null
  history: ConsultationResult[]
  precheck: ConsultationPrecheckData | null
}

export type ConsultationAction =
  | { type: "SET_TYPE"; payload: ConsultationType }
  | { type: "SET_ASTROLOGER"; payload: string }
  | { type: "SET_CONTEXT"; payload: string }
  | { type: "SET_OBJECTIVE"; payload: string }
  | { type: "SET_TIME_HORIZON"; payload: string | null }
  | { type: "SET_OTHER_PERSON"; payload: OtherPersonDraft | null }
  | { type: "SET_IS_INTERACTION"; payload: boolean }
  | { type: "SET_SAVE_THIRD_PARTY"; payload: boolean }
  | { type: "SET_THIRD_PARTY_NICKNAME"; payload: string }
  | { type: "SET_SELECTED_THIRD_PARTY_EXTERNAL_ID"; payload: string | null }
  | { type: "NEXT_STEP" }
  | { type: "PREV_STEP" }
  | { type: "GO_TO_STEP"; payload: number }
  | { type: "SET_RESULT"; payload: ConsultationResult }
  | { type: "SAVE_TO_HISTORY"; payload: ConsultationResult }
  | { type: "RESET" }
  | { type: "LOAD_HISTORY"; payload: ConsultationResult[] }
  | { type: "SET_PRECHECK"; payload: ConsultationPrecheckData | null }

export function consultationReducer(
  state: ConsultationState,
  action: ConsultationAction
): ConsultationState {
  switch (action.type) {
    case "SET_TYPE":
      const config = getConsultationTypeConfig(action.payload)
      return {
        ...state,
        draft: { 
          ...state.draft, 
          type: action.payload,
          isInteraction: config?.defaultInteraction ?? false,
          otherPerson: null,
          saveThirdParty: false,
          thirdPartyNickname: "",
          selectedThirdPartyExternalId: null,
        },
      }
    case "SET_ASTROLOGER":
      return {
        ...state,
        draft: { ...state.draft, astrologerId: action.payload },
      }
    case "SET_CONTEXT":
      return {
        ...state,
        draft: { ...state.draft, context: action.payload },
      }
    case "SET_OBJECTIVE":
      return {
        ...state,
        draft: { ...state.draft, objective: action.payload },
      }
    case "SET_TIME_HORIZON":
      return {
        ...state,
        draft: { ...state.draft, timeHorizon: action.payload },
      }
    case "SET_OTHER_PERSON":
      return {
        ...state,
        draft: { ...state.draft, otherPerson: action.payload },
      }
    case "SET_IS_INTERACTION":
      return {
        ...state,
        draft: {
          ...state.draft,
          isInteraction: action.payload,
          otherPerson: action.payload ? state.draft.otherPerson : null,
          saveThirdParty: action.payload ? state.draft.saveThirdParty : false,
          thirdPartyNickname: action.payload ? state.draft.thirdPartyNickname : "",
          selectedThirdPartyExternalId: action.payload
            ? state.draft.selectedThirdPartyExternalId
            : null,
        },
      }
    case "SET_SAVE_THIRD_PARTY":
      return {
        ...state,
        draft: {
          ...state.draft,
          saveThirdParty: action.payload,
          thirdPartyNickname: action.payload ? state.draft.thirdPartyNickname : "",
        },
      }
    case "SET_THIRD_PARTY_NICKNAME":
      return {
        ...state,
        draft: { ...state.draft, thirdPartyNickname: action.payload },
      }
    case "SET_SELECTED_THIRD_PARTY_EXTERNAL_ID":
      return {
        ...state,
        draft: { ...state.draft, selectedThirdPartyExternalId: action.payload },
      }
    case "NEXT_STEP":
      return {
        ...state,
        step: Math.min(state.step + 1, WIZARD_LAST_STEP_INDEX),
      }
    case "PREV_STEP":
      return {
        ...state,
        step: Math.max(state.step - 1, 0),
      }
    case "GO_TO_STEP":
      return {
        ...state,
        step: Math.max(0, Math.min(action.payload, WIZARD_LAST_STEP_INDEX)),
      }
    case "SET_RESULT":
      return {
        ...state,
        result: action.payload,
      }
    case "SAVE_TO_HISTORY": {
      const existing = state.history.find((h) => h.id === action.payload.id)
      if (existing) return state
      const newHistory = [action.payload, ...state.history].slice(0, HISTORY_MAX_LENGTH)
      saveHistoryToStorage(newHistory)
      return {
        ...state,
        history: newHistory,
      }
    }
    case "LOAD_HISTORY":
      return {
        ...state,
        history: action.payload,
      }
    case "SET_PRECHECK":
      return {
        ...state,
        precheck: action.payload,
      }
    case "RESET":
      return {
        ...state,
        draft: INITIAL_DRAFT,
        step: 0,
        result: null,
        precheck: null,
      }
    default:
      return state
  }
}

export const STORAGE_KEY = "horoscope_consultations_history"
export const CHAT_PREFILL_KEY = "chat_prefill"

function isValidISODate(dateStr: unknown): boolean {
  if (typeof dateStr !== "string") return false
  if (dateStr.length === 0) return false
  const isoRegex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z|[+-]\d{2}:\d{2})?)?$/
  if (!isoRegex.test(dateStr)) return false
  const date = new Date(dateStr)
  return !isNaN(date.getTime())
}

function normalizeStringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return []
  }
  return value.filter((item): item is string => typeof item === "string" && item.trim().length > 0)
}

export function normalizeConsultationResult(item: unknown): ConsultationResult | null {
  if (typeof item !== "object" || item === null) return null
  const obj = item as Record<string, unknown>

  if (
    typeof obj.id !== "string" ||
    typeof obj.type !== "string" ||
    !VALID_CONSULTATION_TYPES.includes(obj.type as ConsultationType) ||
    typeof obj.astrologerId !== "string" ||
    typeof obj.context !== "string" ||
    !isValidISODate(obj.createdAt)
  ) {
    return null
  }

  return {
    id: obj.id as string,
    type: obj.type as ConsultationType,
    astrologerId: obj.astrologerId as string,
    context: obj.context as string,
    objective:
      typeof obj.objective === "string" && obj.objective.trim().length > 0
        ? obj.objective
        : getObjectiveForType(obj.type as ConsultationType),
    timeHorizon:
      typeof obj.timeHorizon === "string"
        ? obj.timeHorizon
        : typeof obj.time_horizon === "string"
          ? obj.time_horizon
          : null,
    summary:
      typeof obj.summary === "string"
        ? obj.summary
        : typeof obj.interpretation === "string"
          ? obj.interpretation
          : "",
    keyPoints: normalizeStringList(obj.keyPoints),
    actionableAdvice: normalizeStringList(obj.actionableAdvice),
    disclaimer: typeof obj.disclaimer === "string" ? obj.disclaimer : "",
    createdAt: obj.createdAt as string,
    fallbackMode: typeof obj.fallbackMode === "string" ? obj.fallbackMode : null,
    precisionLevel: typeof obj.precisionLevel === "string" ? obj.precisionLevel : null,
    sections: Array.isArray(obj.sections) ? (obj.sections as any) : undefined,
    routeKey: typeof obj.routeKey === "string" ? obj.routeKey : null,
    saveThirdParty: typeof obj.saveThirdParty === "boolean" ? obj.saveThirdParty : undefined,
    thirdPartyNickname: typeof obj.thirdPartyNickname === "string" ? obj.thirdPartyNickname : undefined,
  }
}

function loadHistoryFromStorage(): ConsultationResult[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    const parsed: unknown = JSON.parse(stored)
    if (!Array.isArray(parsed)) return []
    
    return parsed
      .map(normalizeConsultationResult)
      .filter((item): item is ConsultationResult => item !== null)
  } catch (e) {
    if (import.meta.env.DEV && import.meta.env.MODE !== "test") {
      console.warn("[consultationStore] localStorage load failed:", e)
    }
    return []
  }
}

function saveHistoryToStorage(history: ConsultationResult[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
  } catch (e) {
    if (import.meta.env.DEV && import.meta.env.MODE !== "test") {
      console.warn("[consultationStore] localStorage save failed:", e)
    }
  }
}

type ConsultationContextValue = {
  state: ConsultationState
  setType: (type: ConsultationType) => void
  setAstrologer: (id: string) => void
  setContext: (context: string) => void
  setObjective: (objective: string) => void
  setTimeHorizon: (horizon: string | null) => void
  setOtherPerson: (data: OtherPersonDraft | null) => void
  setIsInteraction: (isInteraction: boolean) => void
  setSaveThirdParty: (save: boolean) => void
  setThirdPartyNickname: (nickname: string) => void
  setSelectedThirdPartyExternalId: (externalId: string | null) => void
  nextStep: () => void
  prevStep: () => void
  goToStep: (step: number) => void
  setResult: (result: ConsultationResult) => void
  saveToHistory: (result: ConsultationResult) => void
  setPrecheck: (precheck: ConsultationPrecheckData | null) => void
  reset: () => void
  currentStepName: WizardStep
  canProceed: boolean
}

const ConsultationContext = createContext<ConsultationContextValue | null>(null)

export function ConsultationProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(consultationReducer, {
    draft: INITIAL_DRAFT,
    step: 0,
    result: null,
    history: loadHistoryFromStorage(),
    precheck: null,
  })

  const setType = useCallback((type: ConsultationType) => {
    dispatch({ type: "SET_TYPE", payload: type })
  }, [])

  const setAstrologer = useCallback((id: string) => {
    dispatch({ type: "SET_ASTROLOGER", payload: id })
  }, [])

  const setContext = useCallback((context: string) => {
    dispatch({ type: "SET_CONTEXT", payload: context })
  }, [])

  const setObjective = useCallback((objective: string) => {
    dispatch({ type: "SET_OBJECTIVE", payload: objective })
  }, [])

  const setTimeHorizon = useCallback((horizon: string | null) => {
    dispatch({ type: "SET_TIME_HORIZON", payload: horizon })
  }, [])

  const setOtherPerson = useCallback((data: OtherPersonDraft | null) => {
    dispatch({ type: "SET_OTHER_PERSON", payload: data })
  }, [])

  const setIsInteraction = useCallback((isInteraction: boolean) => {
    dispatch({ type: "SET_IS_INTERACTION", payload: isInteraction })
  }, [])

  const setSaveThirdParty = useCallback((save: boolean) => {
    dispatch({ type: "SET_SAVE_THIRD_PARTY", payload: save })
  }, [])

  const setThirdPartyNickname = useCallback((nickname: string) => {
    dispatch({ type: "SET_THIRD_PARTY_NICKNAME", payload: nickname })
  }, [])

  const setSelectedThirdPartyExternalId = useCallback((externalId: string | null) => {
    dispatch({ type: "SET_SELECTED_THIRD_PARTY_EXTERNAL_ID", payload: externalId })
  }, [])

  const nextStep = useCallback(() => {
    dispatch({ type: "NEXT_STEP" })
  }, [])

  const prevStep = useCallback(() => {
    dispatch({ type: "PREV_STEP" })
  }, [])

  const goToStep = useCallback((step: number) => {
    dispatch({ type: "GO_TO_STEP", payload: step })
  }, [])

  const setResult = useCallback((result: ConsultationResult) => {
    dispatch({ type: "SET_RESULT", payload: result })
  }, [])

  const saveToHistory = useCallback((result: ConsultationResult) => {
    dispatch({ type: "SAVE_TO_HISTORY", payload: result })
  }, [])

  const setPrecheck = useCallback((precheck: ConsultationPrecheckData | null) => {
    dispatch({ type: "SET_PRECHECK", payload: precheck })
  }, [])

  const reset = useCallback(() => {
    dispatch({ type: "RESET" })
  }, [])

  const currentStepName = WIZARD_STEPS[state.step]

  const canProceed = useMemo(() => {
    switch (currentStepName) {
      case "astrologer":
        return true
      case "form": {
        if (state.draft.type === null) return false
        if (state.draft.context.trim().length === 0) return false
        if ((state.draft.objective ?? "").trim().length === 0) return false
        if (state.draft.isInteraction) {
          if (!state.draft.otherPerson) return false
          if (!state.draft.otherPerson.birthDate || !state.draft.otherPerson.birthCity || !state.draft.otherPerson.birthCountry) return false
          if (state.draft.saveThirdParty && !state.draft.thirdPartyNickname?.trim()) return false
        }
        return true
      }
      default:
        return false
    }
  }, [
    currentStepName,
    state.draft.type,
    state.draft.context,
    state.draft.objective,
    state.draft.otherPerson,
    state.draft.isInteraction,
    state.draft.saveThirdParty,
    state.draft.thirdPartyNickname,
  ])

  const contextValue = useMemo(
    () => ({
      state,
      setType,
      setAstrologer,
      setContext,
      setObjective,
      setTimeHorizon,
      setOtherPerson,
      setIsInteraction,
      setSaveThirdParty,
      setThirdPartyNickname,
      setSelectedThirdPartyExternalId,
      nextStep,
      prevStep,
      goToStep,
      setResult,
      saveToHistory,
      setPrecheck,
      reset,
      currentStepName,
      canProceed,
    }),
    [
      state,
      setType,
      setAstrologer,
      setContext,
      setObjective,
      setTimeHorizon,
      setOtherPerson,
      setIsInteraction,
      setSaveThirdParty,
      setThirdPartyNickname,
      setSelectedThirdPartyExternalId,
      nextStep,
      prevStep,
      goToStep,
      setResult,
      saveToHistory,
      setPrecheck,
      reset,
      currentStepName,
      canProceed,
    ]
  )

  return (
    <ConsultationContext.Provider value={contextValue}>
      {children}
    </ConsultationContext.Provider>
  )
}

export function useConsultation(): ConsultationContextValue {
  const context = useContext(ConsultationContext)
  if (!context) {
    throw new Error("useConsultation must be used within a ConsultationProvider")
  }
  return context
}

export { INITIAL_DRAFT }
