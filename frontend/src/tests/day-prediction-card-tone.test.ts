// Verifie le fallback de classe CSS des tonalites de prediction.
import { describe, expect, it } from "vitest"
import { getDayPredictionToneClassKey } from "../components/prediction/DayPredictionCard"

describe("DayPredictionCard tone class", () => {
  it("normalise les tonalites connues vers leur classe CSS", () => {
    expect(getDayPredictionToneClassKey("positive")).toBe("positive")
    expect(getDayPredictionToneClassKey("careful")).toBe("careful")
  })

  it("retombe sur neutral pour les tonalites inconnues ou absentes", () => {
    expect(getDayPredictionToneClassKey("backend-new-tone")).toBe("neutral")
    expect(getDayPredictionToneClassKey(null)).toBe("neutral")
    expect(getDayPredictionToneClassKey(undefined)).toBe("neutral")
  })
})
