import { describe, expect, it } from 'vitest'

import type { DailyPredictionResponse } from '../types/dailyPrediction'
import { buildDailyAdviceCardModel } from './dailyAdviceCardMapper'

function makePrediction(overrides: Partial<DailyPredictionResponse> = {}): DailyPredictionResponse {
  return {
    meta: {
      date_local: '2026-03-21',
      timezone: 'Europe/Paris',
      computed_at: '2026-03-21T08:00:00',
      reference_version: '1.0.0',
      ruleset_version: '1.0.0',
      was_reused: false,
      house_system_effective: 'placidus',
      is_provisional_calibration: false,
      calibration_label: null,
    },
    summary: {
      overall_tone: 'mixed',
      overall_summary: 'Journee mobile.',
      top_categories: [],
      bottom_categories: [],
      best_window: null,
      main_turning_point: null,
    },
    day_climate: {
      label: 'Journee contrastée',
      tone: 'mixed',
      intensity: 7,
      stability: 5,
      summary: 'Une alternance d elan et de reajustement.',
      top_domains: ['relations_echanges'],
      watchout: 'energie_bienetre',
      best_window_ref: '10:00–12:00',
    },
    has_llm_narrative: false,
    categories: [],
    timeline: [],
    turning_points: [],
    best_window: {
      time_range: '10:00–12:00',
      label: 'Votre meilleur créneau',
      why: 'La dynamique se fluidifie.',
      recommended_actions: ['clarifier'],
      is_pivot: false,
    },
    ...overrides,
  }
}

describe('dailyAdviceCardMapper', () => {
  it('uses llm advice when available', () => {
    const model = buildDailyAdviceCardModel(
      makePrediction({
        daily_advice: {
          advice: 'Prenez l initiative sur le matin avant que le rythme ne se fragmente.',
          emphasis: 'Le timing fait la difference.',
        },
      }),
      'fr',
    )

    expect(model.advice).toContain('Prenez l initiative')
    expect(model.emphasis).toBe('Le timing fait la difference.')
  })

  it('builds a contextual fallback from the prediction when llm advice is absent', () => {
    const model = buildDailyAdviceCardModel(makePrediction(), 'fr')

    expect(model.advice).toContain('10:00–12:00')
    expect(model.advice.toLowerCase()).toContain('relations')
    expect(model.emphasis).toContain('10:00–12:00')
  })
})
