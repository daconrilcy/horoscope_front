import { describe, expect, it } from "vitest"

import { getDailyEditorialSummary } from "../utils/dailySummaryHelper"
import type { DailyPredictionResponse } from "../types/dailyPrediction"

function makePrediction(overrides: Partial<DailyPredictionResponse>): DailyPredictionResponse {
  return {
    meta: {
      date_local: "2026-03-12",
      timezone: "Europe/Paris",
      computed_at: "2026-03-12T06:00:00Z",
      reference_version: "2026.03",
      ruleset_version: "1.0.0",
      was_reused: false,
      house_system_effective: "placidus",
      is_provisional_calibration: null,
      calibration_label: null,
    },
    summary: {
      overall_tone: "open",
      top_categories: ["love"],
      bottom_categories: [],
      best_window: null,
      main_turning_point: null,
    },
    categories: [],
    timeline: [],
    turning_points: [],
    has_llm_narrative: false,
    ...overrides,
  }
}

describe("getDailyEditorialSummary", () => {
  it("retourne daily_synthesis quand il est fourni", () => {
    expect(
      getDailyEditorialSummary(
        makePrediction({
          daily_synthesis: "Synthèse éditoriale prioritaire.",
          day_climate: {
            label: "Climat",
            tone: "open",
            intensity: 7,
            stability: 6,
            summary: "Résumé climat.",
            top_domains: ["love"],
            watchout: null,
            best_window_ref: null,
          },
        }),
      ),
    ).toBe("Synthèse éditoriale prioritaire.")
  })

  it("retourne day_climate.summary quand daily_synthesis est absent", () => {
    expect(
      getDailyEditorialSummary(
        makePrediction({
          daily_synthesis: null,
          day_climate: {
            label: "Climat",
            tone: "open",
            intensity: 7,
            stability: 6,
            summary: "Résumé climat canonique.",
            top_domains: ["love"],
            watchout: null,
            best_window_ref: null,
          },
        }),
      ),
    ).toBe("Résumé climat canonique.")
  })

  it("retourne une chaine vide sans source éditoriale canonique", () => {
    expect(getDailyEditorialSummary(makePrediction({ daily_synthesis: null }))).toBe("")
  })
})
