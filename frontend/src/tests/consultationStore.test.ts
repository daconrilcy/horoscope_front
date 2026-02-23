import { describe, expect, it } from "vitest"
import { renderHook } from "@testing-library/react"
import {
  consultationReducer,
  isValidConsultationResult,
  useConsultation,
  INITIAL_DRAFT,
  STORAGE_KEY,
  CHAT_PREFILL_KEY,
  type ConsultationState,
  type ConsultationAction,
} from "../state/consultationStore"
import {
  AUTO_ASTROLOGER_ID,
  getConsultationTypeConfig,
  getDrawingOptionConfig,
  HISTORY_MAX_LENGTH,
  WIZARD_LAST_STEP_INDEX,
  WIZARD_STEPS,
  WIZARD_STEP_LABELS,
  type ConsultationResult,
} from "../types/consultation"

const createInitialState = (): ConsultationState => ({
  draft: { ...INITIAL_DRAFT },
  step: 0,
  result: null,
  history: [],
})

const createMockResult = (overrides?: Partial<ConsultationResult>): ConsultationResult => ({
  id: "test-123",
  type: "dating",
  astrologerId: "1",
  drawingOption: "none",
  context: "Test context",
  interpretation: "Test interpretation",
  createdAt: new Date().toISOString(),
  ...overrides,
})

describe("consultationReducer", () => {
  describe("SET_TYPE", () => {
    it("sets the consultation type", () => {
      const state = createInitialState()
      const action: ConsultationAction = { type: "SET_TYPE", payload: "pro" }
      const result = consultationReducer(state, action)
      expect(result.draft.type).toBe("pro")
    })
  })

  describe("SET_ASTROLOGER", () => {
    it("sets the astrologer ID", () => {
      const state = createInitialState()
      const action: ConsultationAction = { type: "SET_ASTROLOGER", payload: "astro-42" }
      const result = consultationReducer(state, action)
      expect(result.draft.astrologerId).toBe("astro-42")
    })
  })

  describe("SET_DRAWING_OPTION", () => {
    it("sets the drawing option", () => {
      const state = createInitialState()
      const action: ConsultationAction = { type: "SET_DRAWING_OPTION", payload: "tarot" }
      const result = consultationReducer(state, action)
      expect(result.draft.drawingOption).toBe("tarot")
    })
  })

  describe("SET_CONTEXT", () => {
    it("sets the context", () => {
      const state = createInitialState()
      const action: ConsultationAction = { type: "SET_CONTEXT", payload: "My question" }
      const result = consultationReducer(state, action)
      expect(result.draft.context).toBe("My question")
    })
  })

  describe("NEXT_STEP", () => {
    it("increments step by 1", () => {
      const state = createInitialState()
      const result = consultationReducer(state, { type: "NEXT_STEP" })
      expect(result.step).toBe(1)
    })

    it("does not exceed WIZARD_LAST_STEP_INDEX", () => {
      const state = { ...createInitialState(), step: WIZARD_LAST_STEP_INDEX }
      const result = consultationReducer(state, { type: "NEXT_STEP" })
      expect(result.step).toBe(WIZARD_LAST_STEP_INDEX)
    })
  })

  describe("PREV_STEP", () => {
    it("decrements step by 1", () => {
      const state = { ...createInitialState(), step: 2 }
      const result = consultationReducer(state, { type: "PREV_STEP" })
      expect(result.step).toBe(1)
    })

    it("does not go below 0", () => {
      const state = createInitialState()
      const result = consultationReducer(state, { type: "PREV_STEP" })
      expect(result.step).toBe(0)
    })
  })

  describe("GO_TO_STEP", () => {
    it("goes to specified step", () => {
      const state = createInitialState()
      const result = consultationReducer(state, { type: "GO_TO_STEP", payload: 2 })
      expect(result.step).toBe(2)
    })

    it("clamps to valid range (0 to WIZARD_LAST_STEP_INDEX)", () => {
      const state = createInitialState()
      expect(consultationReducer(state, { type: "GO_TO_STEP", payload: -1 }).step).toBe(0)
      expect(consultationReducer(state, { type: "GO_TO_STEP", payload: 5 }).step).toBe(WIZARD_LAST_STEP_INDEX)
    })
  })

  describe("SET_RESULT", () => {
    it("sets the result", () => {
      const state = createInitialState()
      const mockResult = createMockResult()
      const result = consultationReducer(state, { type: "SET_RESULT", payload: mockResult })
      expect(result.result).toEqual(mockResult)
    })
  })

  describe("SAVE_TO_HISTORY", () => {
    it("adds result to history at the beginning", () => {
      const state = createInitialState()
      const mockResult = createMockResult()
      const result = consultationReducer(state, { type: "SAVE_TO_HISTORY", payload: mockResult })
      expect(result.history[0]).toEqual(mockResult)
    })

    it("does not add duplicate entries", () => {
      const mockResult = createMockResult()
      const state = { ...createInitialState(), history: [mockResult] }
      const result = consultationReducer(state, { type: "SAVE_TO_HISTORY", payload: mockResult })
      expect(result.history.length).toBe(1)
    })

    it("limits history to HISTORY_MAX_LENGTH entries", () => {
      const existingHistory = Array.from({ length: HISTORY_MAX_LENGTH }, (_, i) =>
        createMockResult({ id: `existing-${i}` })
      )
      const state = { ...createInitialState(), history: existingHistory }
      const newResult = createMockResult({ id: "new-result" })
      const result = consultationReducer(state, { type: "SAVE_TO_HISTORY", payload: newResult })
      expect(result.history.length).toBe(HISTORY_MAX_LENGTH)
      expect(result.history[0].id).toBe("new-result")
      expect(result.history[HISTORY_MAX_LENGTH - 1].id).toBe(`existing-${HISTORY_MAX_LENGTH - 2}`)
    })
  })

  describe("RESET", () => {
    it("resets draft, step, and result but keeps history", () => {
      const mockResult = createMockResult()
      const state: ConsultationState = {
        draft: { type: "pro", astrologerId: "1", drawingOption: "tarot", context: "test" },
        step: WIZARD_LAST_STEP_INDEX,
        result: mockResult,
        history: [mockResult],
      }
      const result = consultationReducer(state, { type: "RESET" })
      expect(result.draft).toEqual(INITIAL_DRAFT)
      expect(result.step).toBe(0)
      expect(result.result).toBeNull()
      expect(result.history).toHaveLength(1)
    })
  })

  describe("LOAD_HISTORY", () => {
    it("replaces history with payload", () => {
      const state = createInitialState()
      const history = [createMockResult({ id: "h1" }), createMockResult({ id: "h2" })]
      const result = consultationReducer(state, { type: "LOAD_HISTORY", payload: history })
      expect(result.history).toEqual(history)
    })
  })
})

describe("isValidConsultationResult", () => {
  it("returns true for valid consultation result", () => {
    const valid = createMockResult()
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns false for null", () => {
    expect(isValidConsultationResult(null)).toBe(false)
  })

  it("returns false for non-object", () => {
    expect(isValidConsultationResult("string")).toBe(false)
    expect(isValidConsultationResult(123)).toBe(false)
  })

  it("returns false for missing required fields", () => {
    expect(isValidConsultationResult({ id: "123" })).toBe(false)
    expect(isValidConsultationResult({ id: "123", type: "dating" })).toBe(false)
  })

  it("returns false for invalid type values", () => {
    const invalid = { ...createMockResult(), type: "invalid_type" }
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false for invalid drawingOption values", () => {
    const invalid = { ...createMockResult(), drawingOption: "invalid_option" }
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("validates all consultation types", () => {
    for (const type of ["dating", "pro", "event", "free"]) {
      const valid = createMockResult({ type: type as "dating" | "pro" | "event" | "free" })
      expect(isValidConsultationResult(valid)).toBe(true)
    }
  })

  it("validates all drawing options", () => {
    for (const option of ["none", "tarot", "runes"]) {
      const valid = createMockResult({ drawingOption: option as "none" | "tarot" | "runes" })
      expect(isValidConsultationResult(valid)).toBe(true)
    }
  })

  it("returns true when drawing is undefined", () => {
    const valid = createMockResult()
    delete (valid as Record<string, unknown>).drawing
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns true for valid drawing with cards", () => {
    const valid = createMockResult({ drawing: { cards: ["L'Empereur", "La Lune"] } })
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns true for valid drawing with runes", () => {
    const valid = createMockResult({ drawing: { runes: ["Fehu", "Uruz"] } })
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns false when drawing is not an object", () => {
    const invalid = createMockResult({ drawing: "invalid" as unknown as undefined })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false when drawing.cards is not an array", () => {
    const invalid = createMockResult({ drawing: { cards: "not-array" } as unknown as undefined })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false when drawing.runes is not an array", () => {
    const invalid = createMockResult({ drawing: { runes: 123 } as unknown as undefined })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false when drawing.cards contains non-strings", () => {
    const invalid = createMockResult({ drawing: { cards: [1, 2, 3] } as unknown as undefined })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false when drawing.runes contains non-strings", () => {
    const invalid = createMockResult({ drawing: { runes: [null, undefined] } as unknown as undefined })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns true when drawing has both cards and runes", () => {
    const valid = createMockResult({
      drawing: { cards: ["L'Empereur", "La Lune"], runes: ["Fehu", "Uruz"] },
    })
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns false when drawing has both cards and runes but cards is invalid", () => {
    const invalid = createMockResult({
      drawing: { cards: [123, 456], runes: ["Fehu", "Uruz"] } as unknown as undefined,
    })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false when drawing has both cards and runes but runes is invalid", () => {
    const invalid = createMockResult({
      drawing: { cards: ["L'Empereur"], runes: [null, {}] } as unknown as undefined,
    })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns true for valid ISO date in createdAt", () => {
    const valid = createMockResult({ createdAt: "2026-02-22T12:00:00.000Z" })
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns true for ISO date without time", () => {
    const valid = createMockResult({ createdAt: "2026-02-22" })
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns true for ISO date with timezone offset", () => {
    const valid = createMockResult({ createdAt: "2026-02-22T12:00:00+02:00" })
    expect(isValidConsultationResult(valid)).toBe(true)
  })

  it("returns false for invalid date string in createdAt", () => {
    const invalid = createMockResult({ createdAt: "not-a-date" })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false for empty string in createdAt", () => {
    const invalid = createMockResult({ createdAt: "" })
    expect(isValidConsultationResult(invalid)).toBe(false)
  })

  it("returns false for non-ISO date formats", () => {
    expect(isValidConsultationResult(createMockResult({ createdAt: "2026/02/22" }))).toBe(false)
    expect(isValidConsultationResult(createMockResult({ createdAt: "Feb 22, 2026" }))).toBe(false)
    expect(isValidConsultationResult(createMockResult({ createdAt: "22-02-2026" }))).toBe(false)
  })

  it("returns false for object with __proto__ pollution attempt", () => {
    const polluted = JSON.parse('{"__proto__": {"admin": true}, "id": "123", "type": "dating", "astrologerId": "1", "drawingOption": "none", "context": "test", "interpretation": "test", "createdAt": "2026-02-22T12:00:00.000Z"}')
    expect(isValidConsultationResult(polluted)).toBe(true)
    expect((polluted as Record<string, unknown>).admin).toBeUndefined()
  })

  it("returns false for object with constructor pollution attempt", () => {
    const polluted = {
      constructor: { prototype: { admin: true } },
      id: "123",
      type: "dating",
      astrologerId: "1",
      drawingOption: "none",
      context: "test",
      interpretation: "test",
      createdAt: "2026-02-22T12:00:00.000Z",
    }
    expect(isValidConsultationResult(polluted)).toBe(true)
    expect(Object.prototype.hasOwnProperty.call({}, "admin")).toBe(false)
  })
})

describe("getConsultationTypeConfig", () => {
  it("returns config for valid consultation type", () => {
    const config = getConsultationTypeConfig("dating")
    expect(config).toBeDefined()
    expect(config?.id).toBe("dating")
    expect(config?.labelKey).toBe("type_dating")
    expect(config?.icon).toBe("💕")
  })

  it("returns config for all valid types", () => {
    expect(getConsultationTypeConfig("pro")?.id).toBe("pro")
    expect(getConsultationTypeConfig("event")?.id).toBe("event")
    expect(getConsultationTypeConfig("free")?.id).toBe("free")
  })

  it("returns undefined for invalid type", () => {
    const config = getConsultationTypeConfig("invalid" as "dating")
    expect(config).toBeUndefined()
  })
})

describe("getDrawingOptionConfig", () => {
  it("returns config for valid drawing option", () => {
    const config = getDrawingOptionConfig("tarot")
    expect(config).toBeDefined()
    expect(config?.id).toBe("tarot")
    expect(config?.labelKey).toBe("drawing_tarot")
    expect(config?.icon).toBe("🃏")
  })

  it("returns config for all valid options", () => {
    expect(getDrawingOptionConfig("none")?.id).toBe("none")
    expect(getDrawingOptionConfig("runes")?.id).toBe("runes")
  })

  it("returns undefined for invalid option", () => {
    const config = getDrawingOptionConfig("invalid" as "none")
    expect(config).toBeUndefined()
  })
})

describe("SAVE_TO_HISTORY edge cases", () => {
  it("removes the oldest entry when history exceeds HISTORY_MAX_LENGTH", () => {
    const existingHistory = Array.from({ length: HISTORY_MAX_LENGTH }, (_, i) =>
      createMockResult({ id: `item-${i}` })
    )
    const state = { ...createInitialState(), history: existingHistory }
    const newResult = createMockResult({ id: "new-item" })
    const result = consultationReducer(state, { type: "SAVE_TO_HISTORY", payload: newResult })

    expect(result.history.length).toBe(HISTORY_MAX_LENGTH)
    expect(result.history[0].id).toBe("new-item")
    expect(result.history.map((h) => h.id)).not.toContain(`item-${HISTORY_MAX_LENGTH - 1}`)
    expect(result.history[HISTORY_MAX_LENGTH - 1].id).toBe(`item-${HISTORY_MAX_LENGTH - 2}`)
  })
})

describe("useConsultation hook", () => {
  it("throws error when used outside ConsultationProvider", () => {
    expect(() => {
      renderHook(() => useConsultation())
    }).toThrow("useConsultation must be used within a ConsultationProvider")
  })
})

describe("STORAGE_KEY export", () => {
  it("exports the correct localStorage key", () => {
    expect(STORAGE_KEY).toBe("horoscope_consultations_history")
  })
})

describe("CHAT_PREFILL_KEY export", () => {
  it("exports the correct sessionStorage key", () => {
    expect(CHAT_PREFILL_KEY).toBe("chat_prefill")
  })
})

describe("AUTO_ASTROLOGER_ID export", () => {
  it("exports the correct auto astrologer ID", () => {
    expect(AUTO_ASTROLOGER_ID).toBe("auto")
  })
})

describe("currentStepName derivation", () => {
  it("returns correct step name for each step index", () => {
    WIZARD_STEPS.forEach((expectedName, index) => {
      const state = { ...createInitialState(), step: index }
      const derivedName = WIZARD_STEPS[state.step]
      expect(derivedName).toBe(expectedName)
    })
  })

  it("WIZARD_STEPS has expected step names in order", () => {
    expect(WIZARD_STEPS).toEqual(["type", "astrologer", "drawing", "validation"])
  })
})

describe("WIZARD_STEP_LABELS export", () => {
  it("exports labels for all wizard steps", () => {
    expect(WIZARD_STEP_LABELS).toEqual({
      type: "step_type",
      astrologer: "step_astrologer",
      drawing: "step_drawing",
      validation: "step_validation",
    })
  })

  it("has a label for each step in WIZARD_STEPS", () => {
    WIZARD_STEPS.forEach((step) => {
      expect(WIZARD_STEP_LABELS[step]).toBeDefined()
      expect(typeof WIZARD_STEP_LABELS[step]).toBe("string")
    })
  })
})

describe("INITIAL_DRAFT export", () => {
  it("exports the correct initial draft values", () => {
    expect(INITIAL_DRAFT).toEqual({
      type: null,
      astrologerId: null,
      drawingOption: "none",
      context: "",
    })
  })

  it("has null for type initially", () => {
    expect(INITIAL_DRAFT.type).toBeNull()
  })

  it("has null for astrologerId initially", () => {
    expect(INITIAL_DRAFT.astrologerId).toBeNull()
  })

  it("has 'none' as default drawingOption", () => {
    expect(INITIAL_DRAFT.drawingOption).toBe("none")
  })

  it("has empty string for context initially", () => {
    expect(INITIAL_DRAFT.context).toBe("")
  })
})
