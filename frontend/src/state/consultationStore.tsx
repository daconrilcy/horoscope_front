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
  VALID_DRAWING_OPTIONS,
  WIZARD_LAST_STEP_INDEX,
  WIZARD_STEPS,
  type ConsultationType,
  type DrawingOption,
  type ConsultationDraft,
  type ConsultationResult,
  type WizardStep,
} from "../types/consultation"

const INITIAL_DRAFT: ConsultationDraft = {
  type: null,
  astrologerId: null,
  drawingOption: "none",
  context: "",
}

export type ConsultationState = {
  draft: ConsultationDraft
  step: number
  result: ConsultationResult | null
  history: ConsultationResult[]
}

export type ConsultationAction =
  | { type: "SET_TYPE"; payload: ConsultationType }
  | { type: "SET_ASTROLOGER"; payload: string }
  | { type: "SET_DRAWING_OPTION"; payload: DrawingOption }
  | { type: "SET_CONTEXT"; payload: string }
  | { type: "NEXT_STEP" }
  | { type: "PREV_STEP" }
  | { type: "GO_TO_STEP"; payload: number }
  | { type: "SET_RESULT"; payload: ConsultationResult }
  | { type: "SAVE_TO_HISTORY"; payload: ConsultationResult }
  | { type: "RESET" }
  | { type: "LOAD_HISTORY"; payload: ConsultationResult[] }

export function consultationReducer(
  state: ConsultationState,
  action: ConsultationAction
): ConsultationState {
  switch (action.type) {
    case "SET_TYPE":
      return {
        ...state,
        draft: { ...state.draft, type: action.payload },
      }
    case "SET_ASTROLOGER":
      return {
        ...state,
        draft: { ...state.draft, astrologerId: action.payload },
      }
    case "SET_DRAWING_OPTION":
      return {
        ...state,
        draft: { ...state.draft, drawingOption: action.payload },
      }
    case "SET_CONTEXT":
      return {
        ...state,
        draft: { ...state.draft, context: action.payload },
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
    case "RESET":
      return {
        ...state,
        draft: INITIAL_DRAFT,
        step: 0,
        result: null,
      }
    default:
      return state
  }
}

export const STORAGE_KEY = "horoscope_consultations_history"
export const CHAT_PREFILL_KEY = "chat_prefill"

function isValidDrawing(drawing: unknown): boolean {
  if (drawing === undefined) return true
  if (typeof drawing !== "object" || drawing === null) return false
  const d = drawing as Record<string, unknown>
  if (d.cards !== undefined && !Array.isArray(d.cards)) return false
  if (d.runes !== undefined && !Array.isArray(d.runes)) return false
  if (d.cards !== undefined && !d.cards.every((c: unknown) => typeof c === "string")) return false
  if (d.runes !== undefined && !d.runes.every((r: unknown) => typeof r === "string")) return false
  return true
}

function isValidISODate(dateStr: unknown): boolean {
  if (typeof dateStr !== "string") return false
  if (dateStr.length === 0) return false
  const isoRegex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z|[+-]\d{2}:\d{2})?)?$/
  if (!isoRegex.test(dateStr)) return false
  const date = new Date(dateStr)
  return !isNaN(date.getTime())
}

export function isValidConsultationResult(item: unknown): item is ConsultationResult {
  if (typeof item !== "object" || item === null) return false
  const obj = item as Record<string, unknown>
  return (
    typeof obj.id === "string" &&
    typeof obj.type === "string" &&
    VALID_CONSULTATION_TYPES.includes(obj.type as ConsultationType) &&
    typeof obj.astrologerId === "string" &&
    typeof obj.drawingOption === "string" &&
    VALID_DRAWING_OPTIONS.includes(obj.drawingOption as DrawingOption) &&
    typeof obj.context === "string" &&
    typeof obj.interpretation === "string" &&
    isValidISODate(obj.createdAt) &&
    isValidDrawing(obj.drawing)
  )
}

function loadHistoryFromStorage(): ConsultationResult[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    const parsed: unknown = JSON.parse(stored)
    if (!Array.isArray(parsed)) return []
    return parsed.filter(isValidConsultationResult)
  } catch (e) {
    if (import.meta.env.DEV) {
      console.warn("[consultationStore] localStorage load failed:", e)
    }
    return []
  }
}

function saveHistoryToStorage(history: ConsultationResult[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
  } catch (e) {
    if (import.meta.env.DEV) {
      console.warn("[consultationStore] localStorage save failed:", e)
    }
  }
}

type ConsultationContextValue = {
  state: ConsultationState
  setType: (type: ConsultationType) => void
  setAstrologer: (id: string) => void
  setDrawingOption: (option: DrawingOption) => void
  setContext: (context: string) => void
  nextStep: () => void
  prevStep: () => void
  goToStep: (step: number) => void
  setResult: (result: ConsultationResult) => void
  saveToHistory: (result: ConsultationResult) => void
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
  })

  const setType = useCallback((type: ConsultationType) => {
    dispatch({ type: "SET_TYPE", payload: type })
  }, [])

  const setAstrologer = useCallback((id: string) => {
    dispatch({ type: "SET_ASTROLOGER", payload: id })
  }, [])

  const setDrawingOption = useCallback((option: DrawingOption) => {
    dispatch({ type: "SET_DRAWING_OPTION", payload: option })
  }, [])

  const setContext = useCallback((context: string) => {
    dispatch({ type: "SET_CONTEXT", payload: context })
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

  const reset = useCallback(() => {
    dispatch({ type: "RESET" })
  }, [])

  const currentStepName = WIZARD_STEPS[state.step]

  const canProceed = useMemo(() => {
    switch (currentStepName) {
      case "type":
        return state.draft.type !== null
      case "astrologer":
        return state.draft.astrologerId !== null
      case "drawing":
        return true
      case "validation":
        return state.draft.context.trim().length > 0
      default:
        return false
    }
  }, [currentStepName, state.draft.type, state.draft.astrologerId, state.draft.context])

  const contextValue = useMemo(
    () => ({
      state,
      setType,
      setAstrologer,
      setDrawingOption,
      setContext,
      nextStep,
      prevStep,
      goToStep,
      setResult,
      saveToHistory,
      reset,
      currentStepName,
      canProceed,
    }),
    [
      state,
      setType,
      setAstrologer,
      setDrawingOption,
      setContext,
      nextStep,
      prevStep,
      goToStep,
      setResult,
      saveToHistory,
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
