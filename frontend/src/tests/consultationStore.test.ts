import { describe, expect, it } from "vitest"
import { renderHook } from "@testing-library/react"

import {
  consultationReducer,
  normalizeConsultationResult,
  useConsultation,
  INITIAL_DRAFT,
  STORAGE_KEY,
  CHAT_PREFILL_KEY,
  type ConsultationAction,
  type ConsultationState,
} from "../state/consultationStore"
import {
  AUTO_ASTROLOGER_ID,
  HISTORY_MAX_LENGTH,
  WIZARD_LAST_STEP_INDEX,
  WIZARD_STEPS,
  WIZARD_STEP_LABELS,
  getConsultationTypeConfig,
  type ConsultationResult,
} from "../types/consultation"

const createInitialState = (): ConsultationState => ({
  draft: { ...INITIAL_DRAFT },
  step: 0,
  result: null,
  history: [],
  precheck: null,
})

const createMockResult = (overrides?: Partial<ConsultationResult>): ConsultationResult => ({
  id: "test-123",
  type: "dating",
  astrologerId: "1",
  context: "Test context",
  objective: "relation/amour",
  timeHorizon: "cette semaine",
  summary: "Test summary",
  keyPoints: ["Point 1"],
  actionableAdvice: ["Conseil 1"],
  disclaimer: "Test disclaimer",
  createdAt: new Date().toISOString(),
  ...overrides,
})

describe("consultationReducer", () => {
  it("sets type, astrologer, context, objective and time horizon", () => {
    let state = createInitialState()
    const actions: ConsultationAction[] = [
      { type: "SET_TYPE", payload: "pro" },
      { type: "SET_ASTROLOGER", payload: "astro-42" },
      { type: "SET_CONTEXT", payload: "Mon entretien arrive" },
      { type: "SET_OBJECTIVE", payload: "clarifier la dynamique de l'entretien" },
      { type: "SET_TIME_HORIZON", payload: "avant vendredi" },
    ]

    for (const action of actions) {
      state = consultationReducer(state, action)
    }

    expect(state.draft).toEqual({
      type: "pro",
      astrologerId: "astro-42",
      context: "Mon entretien arrive",
      objective: "clarifier la dynamique de l'entretien",
      timeHorizon: "avant vendredi",
      isInteraction: false,
      otherPerson: null,
      saveThirdParty: false,
      thirdPartyNickname: "",
      selectedThirdPartyExternalId: null,
    })
  })

  it("clamps navigation between 0 and last step", () => {
    const initial = createInitialState()
    expect(consultationReducer(initial, { type: "PREV_STEP" }).step).toBe(0)
    expect(consultationReducer(initial, { type: "GO_TO_STEP", payload: 42 }).step).toBe(
      WIZARD_LAST_STEP_INDEX
    )
  })

  it("stores current result", () => {
    const mockResult = createMockResult()
    const result = consultationReducer(createInitialState(), {
      type: "SET_RESULT",
      payload: mockResult,
    })
    expect(result.result).toEqual(mockResult)
  })

  it("prepends history without duplicates and keeps max length", () => {
    const existingHistory = Array.from({ length: HISTORY_MAX_LENGTH }, (_, index) =>
      createMockResult({ id: `existing-${index}` })
    )
    const state = { ...createInitialState(), history: existingHistory }
    const newResult = createMockResult({ id: "new-result" })

    const updated = consultationReducer(state, { type: "SAVE_TO_HISTORY", payload: newResult })
    const duplicated = consultationReducer(updated, { type: "SAVE_TO_HISTORY", payload: newResult })

    expect(updated.history).toHaveLength(HISTORY_MAX_LENGTH)
    expect(updated.history[0].id).toBe("new-result")
    expect(updated.history.at(-1)?.id).toBe(`existing-${HISTORY_MAX_LENGTH - 2}`)
    expect(duplicated.history).toEqual(updated.history)
  })

  it("resets draft, step and result while keeping history", () => {
    const mockResult = createMockResult()
    const state: ConsultationState = {
      draft: {
        type: "free",
        astrologerId: "1",
        context: "Question libre",
        objective: "aller droit au point",
        timeHorizon: "ce mois-ci",
        saveThirdParty: false,
        thirdPartyNickname: "",
        selectedThirdPartyExternalId: null,
      },
      step: WIZARD_LAST_STEP_INDEX,
      result: mockResult,
      history: [mockResult],
      precheck: null,
    }

    const result = consultationReducer(state, { type: "RESET" })
    expect(result.draft).toEqual(INITIAL_DRAFT)
    expect(result.step).toBe(0)
    expect(result.result).toBeNull()
    expect(result.history).toEqual([mockResult])
  })
})

describe("normalizeConsultationResult", () => {
  it("normalizes the epic 46 schema and preserves time horizon", () => {
    const normalized = normalizeConsultationResult(
      createMockResult({ timeHorizon: "dans 3 semaines" })
    )

    expect(normalized).toMatchObject({
      objective: "relation/amour",
      timeHorizon: "dans 3 semaines",
      summary: "Test summary",
    })
  })

  it("normalizes legacy history entries without drawing semantics", () => {
    const normalized = normalizeConsultationResult({
      id: "legacy-1",
      type: "dating",
      astrologerId: "1",
      drawingOption: "tarot",
      drawing: { cards: ["L'Amoureux"] },
      context: "Mon premier rendez-vous",
      interpretation: "Une ancienne interprétation",
      createdAt: "2026-02-22T12:00:00.000Z",
    })

    expect(normalized).toMatchObject({
      id: "legacy-1",
      type: "dating",
      summary: "Une ancienne interprétation",
      objective: "objective_dating",
      keyPoints: [],
      actionableAdvice: [],
      timeHorizon: null,
    })
  })

  it("reads snake_case time_horizon from backend-shaped payloads", () => {
    const normalized = normalizeConsultationResult({
      id: "api-1",
      type: "event",
      astrologerId: "1",
      context: "Mon lancement produit",
      objective: "préparer le bon moment",
      time_horizon: "avant la fin du trimestre",
      summary: "Résumé",
      keyPoints: ["k1"],
      actionableAdvice: ["a1"],
      disclaimer: "d1",
      createdAt: "2026-03-01T09:15:00.000Z",
    })

    expect(normalized?.timeHorizon).toBe("avant la fin du trimestre")
  })

  it("rejects invalid payloads", () => {
    expect(normalizeConsultationResult(null)).toBeNull()
    expect(normalizeConsultationResult("invalid")).toBeNull()
    expect(normalizeConsultationResult({ id: "1", type: "invalid" })).toBeNull()
    expect(
      normalizeConsultationResult({
        id: "1",
        type: "dating",
        astrologerId: "1",
        context: "Question",
        createdAt: "not-a-date",
      })
    ).toBeNull()
  })
})

describe("type exports", () => {
  it("returns consultation config for supported types", () => {
    expect(getConsultationTypeConfig("period")?.icon).toBe("📅")
    expect(getConsultationTypeConfig("career")?.labelKey).toBe("type_work_label")
  })

  it("exposes wizard steps and labels without drawing step", () => {
    expect(WIZARD_STEPS).toEqual(["type", "frame", "collection", "summary"])
    expect(WIZARD_STEP_LABELS).toEqual({
      type: "select_type",
      frame: "frame_request",
      collection: "additional_info",
      summary: "final_verification",
    })
  })

  it("clears third-party state when interaction is disabled", () => {
    const state: ConsultationState = {
      ...createInitialState(),
      draft: {
        ...INITIAL_DRAFT,
        type: "work",
        isInteraction: true,
        otherPerson: {
          birthDate: "1990-01-01",
          birthTime: "12:00",
          birthTimeKnown: true,
          birthPlace: "Paris, France",
          birthCity: "Paris",
          birthCountry: "France",
        },
        saveThirdParty: true,
        thirdPartyNickname: "Collegue",
        selectedThirdPartyExternalId: "tp_123",
      },
    }

    const result = consultationReducer(state, {
      type: "SET_IS_INTERACTION",
      payload: false,
    })

    expect(result.draft.otherPerson).toBeNull()
    expect(result.draft.saveThirdParty).toBe(false)
    expect(result.draft.thirdPartyNickname).toBe("")
    expect(result.draft.selectedThirdPartyExternalId).toBeNull()
  })
})

describe("hook guards and constants", () => {
  it("throws when useConsultation is used outside provider", () => {
    expect(() => renderHook(() => useConsultation())).toThrow(
      "useConsultation must be used within a ConsultationProvider"
    )
  })

  it("exports stable storage constants", () => {
    expect(STORAGE_KEY).toBe("horoscope_consultations_history")
    expect(CHAT_PREFILL_KEY).toBe("chat_prefill")
    expect(AUTO_ASTROLOGER_ID).toBe("auto")
  })
})
