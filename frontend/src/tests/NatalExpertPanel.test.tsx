// Tests du panneau expert natal: verifie l'affichage strict des faits API sans derivation locale.
import { render, screen, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { NatalExpertPanel } from "../features/natal-chart/NatalExpertPanel"
import type { LatestNatalChart } from "../api/natalChart"

const BASE_CHART = {
  chart_id: "chart-202",
  created_at: "2026-05-20T08:00:00Z",
  metadata: {
    reference_version: "v1.2",
    ruleset_version: "traditional-standard",
    engine: "natal",
    house_system: "placidus",
    degraded_mode: null,
  },
  astro_profile: {
    sun_sign_code: "TAURUS",
    ascendant_sign_code: "CAPRICORN",
    missing_birth_time: false,
  },
  result: {
    reference_version: "v1.2",
    ruleset_version: "traditional-standard",
    prepared_input: {
      birth_datetime_local: "1990-01-15T10:30:00",
      birth_datetime_utc: "1990-01-15T09:30:00Z",
      timestamp_utc: 632400600,
      julian_day: 2447907.896,
      birth_timezone: "Europe/Paris",
      jd_ut: 2447907.896,
      timezone_used: "Europe/Paris",
    },
    planet_positions: [],
    houses: [],
    aspects: [],
  },
} satisfies LatestNatalChart

function buildExpertChart(): LatestNatalChart {
  return {
    ...BASE_CHART,
    result: {
      ...BASE_CHART.result,
      dignities: {
        score_profile: "traditional_standard",
        tradition: "traditional",
        reference_version: "v1.2",
        sect: {
          chart_sect: "day",
          sun_horizon_position: "above_horizon",
          sun_above_horizon: true,
          calculation_basis: "fixture_horizon_rule",
          reference_system: "traditional",
        },
        planets: {
          alpha: {
            sect_condition: {
              planet_code: "alpha",
              chart_sect: "day",
              intrinsic_sect: "custom",
              planet_sect_condition: "in_sect",
              is_in_sect: true,
              is_out_of_sect: false,
              calculation_basis: "fixture_explicit_flags",
              reference_system: "traditional",
            },
            essential_score: 5,
            accidental_score: 4,
            total_score: 9,
            functional_strength_score: 1.9,
            expression_quality_score: 1.5,
            intensity_score: 1.5,
            essential_breakdown: [{ type: "domicile", score_value: 5, reason: "backend fact" }],
            accidental_breakdown: [{ type: "angular_house", score_value: 4, reason: "backend fact" }],
          },
          beta: {
            sect_condition: {
              planet_code: "beta",
              chart_sect: "day",
              intrinsic_sect: "custom",
              planet_sect_condition: "out_of_sect",
              is_in_sect: false,
              is_out_of_sect: true,
              calculation_basis: "fixture_explicit_flags",
              reference_system: "traditional",
            },
            total_score: -2,
          },
          gamma: {
            sect_condition: {
              planet_code: "gamma",
              chart_sect: "day",
              intrinsic_sect: "neutral",
              planet_sect_condition: "neutral_to_sect",
              is_in_sect: false,
              is_out_of_sect: false,
              calculation_basis: "fixture_explicit_flags",
              reference_system: "traditional",
            },
            total_score: 0,
          },
        },
      },
      planet_condition_profiles: {
        alpha: {
          planet_code: "alpha",
          condition_level: "strong",
          ranking_score: 5.7,
          functional_strength: 1.9,
          visibility: 1,
          stability: 0.8,
          intensity: 1.5,
          coherence: 0.6,
          support: 0.4,
          constraint: 0,
        },
      },
      planet_condition_signals: {
        alpha: [
          {
            code: "visibility_high",
            label: "Visibility high",
            axis: "visibility",
            level: "high",
            axis_value: 1,
            interpretation_use: "surface_condition_axis",
            priority_weight: 30,
          },
        ],
      },
      advanced_conditions: [
        {
          planet_code: "alpha",
          condition_code: "hayz",
          condition_type: "hayz",
          score_effect: 1.5,
          axis_weights: { functional_strength: 0.3, visibility: 0.2 },
          evidence: ["alpha matches backend condition."],
        },
        {
          planet_code: "beta",
          condition_code: "out_of_sect",
          condition_type: "sect",
          score_effect: -1,
          axis_weights: { constraint: 0.4 },
          evidence: ["beta is flagged by backend."],
        },
      ],
      traditional_conditions: {
        alpha: {
          planet_code: "alpha",
          hayz: {
            planet_code: "alpha",
            is_hayz: true,
            sect_match: true,
            hemisphere_match: true,
            sign_gender_match: true,
            chart_sect: "day",
            intrinsic_sect: "diurnal",
            planet_sect_condition: "in_sect",
            planet_horizon_position: "above_horizon",
            sign_gender: "masculine",
            calculation_basis: "sect_hemisphere_sign_gender",
            reference_system: "traditional",
            evidence: ["alpha matches backend condition."],
          },
          rejoicing: {
            planet_code: "alpha",
            is_rejoicing: false,
            current_house: 10,
            rejoicing_house: null,
            calculation_basis: "planetary_joy_house",
            reference_system: "traditional",
            evidence: [],
          },
        },
        beta: {
          planet_code: "beta",
          hayz: {
            planet_code: "beta",
            is_hayz: false,
            sect_match: false,
            hemisphere_match: null,
            sign_gender_match: null,
            chart_sect: "night",
            intrinsic_sect: "diurnal",
            planet_sect_condition: "out_of_sect",
            planet_horizon_position: "unknown",
            sign_gender: "unknown",
            calculation_basis: "sect_hemisphere_sign_gender",
            reference_system: "traditional",
            evidence: [],
          },
          rejoicing: {
            planet_code: "beta",
            is_rejoicing: true,
            current_house: 6,
            rejoicing_house: 6,
            calculation_basis: "planetary_joy_house",
            reference_system: "traditional",
            evidence: ["beta rejoices."],
          },
        },
      },
      dominant_planets: {
        top_planet_code: "alpha",
        chart_ruler_code: "gamma",
        most_elevated_planet_code: "beta",
        planets: [
          {
            planet_code: "alpha",
            rank: 1,
            score: 0.75,
            factors: [
              {
                factor_code: "chart_ruler",
                raw_value: 1,
                normalized_value: 1,
                weight: 1.4,
                weighted_score: 1.4,
                reason: "backend dominance factor",
              },
            ],
          },
        ],
      },
      interpretation_adapter: {
        signals: [
          {
            signal: "dominant_alpha_signature",
            theme: "drive_assertion_action",
            source_type: "dominant_planet",
            source_code: "alpha",
            priority: "critical",
            priority_rank: 10,
            weight: 1,
            semantic_category: "planetary_signature",
          },
        ],
        activated_themes: [
          {
            theme: "drive_assertion_action",
            theme_category: "behavioral",
            activation_score: 1,
            priority: "critical",
            priority_rank: 10,
            contributing_signals: ["dominant_alpha_signature"],
          },
        ],
        dominant_topics: ["drive"],
        dominant_axes: ["action"],
        tension_patterns: ["constraint_on_action"],
        support_patterns: ["visibility_support"],
        critical_patterns: ["dominant_alpha_signature"],
        narrative_priorities: ["technical_priority_1"],
      },
    },
  }
}

describe("NatalExpertPanel", () => {
  it("rend les blocs experts du payload public sans calcul local", () => {
    render(<NatalExpertPanel chart={buildExpertChart()} />)

    expect(screen.getByRole("heading", { name: "Panneau expert natal" })).toBeInTheDocument()

    const sectSection = screen.getByRole("region", { name: "Secte du theme" })
    expect(within(sectSection).getByText("chart_sect")).toBeInTheDocument()
    expect(within(sectSection).getByText("day")).toBeInTheDocument()
    expect(within(sectSection).getByText("sun_horizon_position")).toBeInTheDocument()
    expect(within(sectSection).getByText("above_horizon")).toBeInTheDocument()

    const advancedSection = screen.getByRole("region", { name: "Conditions avancees" })
    expect(within(advancedSection).getByText(/alpha \/ hayz/)).toBeInTheDocument()
    expect(within(advancedSection).getByText(/beta \/ out_of_sect/)).toBeInTheDocument()

    const traditionalSection = screen.getByRole("region", { name: "Contrats traditionnels" })
    expect(within(traditionalSection).getAllByText("hayz.is_hayz").length).toBeGreaterThan(0)
    expect(within(traditionalSection).getAllByText("hayz.hemisphere_match").length).toBeGreaterThan(0)
    expect(within(traditionalSection).getAllByText("hayz.chart_sect").length).toBeGreaterThan(0)
    expect(
      within(traditionalSection).getAllByText("hayz.planet_horizon_position").length,
    ).toBeGreaterThan(0)
    expect(within(traditionalSection).getAllByText("rejoicing.rejoicing_house").length).toBeGreaterThan(0)

    expect(screen.getAllByText("essential_score").length).toBeGreaterThan(0)
    expect(screen.getAllByText("total_score").length).toBeGreaterThan(0)
    expect(screen.getByText("condition_level")).toBeInTheDocument()
    expect(screen.getByText("visibility_high")).toBeInTheDocument()
    expect(screen.getByText("top_planet_code")).toBeInTheDocument()
    expect(screen.getAllByText("dominant_alpha_signature").length).toBeGreaterThan(0)
    expect(screen.getByText("critical_patterns")).toBeInTheDocument()
  })

  it("groupe les conditions de secte uniquement depuis les booleens et codes explicites", () => {
    render(<NatalExpertPanel chart={buildExpertChart()} />)

    const conditionSection = screen.getByRole("region", { name: "Condition de secte par planete" })
    const inGroup = within(conditionSection).getByRole("heading", { name: "Dans la secte" }).closest("article")
    const outGroup = within(conditionSection).getByRole("heading", { name: "Hors secte" }).closest("article")
    const neutralGroup = within(conditionSection)
      .getByRole("heading", { name: "Neutre / variable / inconnu" })
      .closest("article")

    expect(inGroup).not.toBeNull()
    expect(outGroup).not.toBeNull()
    expect(neutralGroup).not.toBeNull()
    expect(within(inGroup as HTMLElement).getByText("alpha")).toBeInTheDocument()
    expect(within(outGroup as HTMLElement).getByText("beta")).toBeInTheDocument()
    expect(within(neutralGroup as HTMLElement).getByText("gamma")).toBeInTheDocument()
  })

  it("distingue les payloads anciens, vides et sans heure fiable", () => {
    const legacyChart = { ...BASE_CHART }
    const emptyExpertChart: LatestNatalChart = {
      ...BASE_CHART,
      result: {
        ...BASE_CHART.result,
        dignities: { sect: null, planets: {} },
        planet_condition_profiles: {},
        planet_condition_signals: {},
        advanced_conditions: [],
        traditional_conditions: null,
        dominant_planets: null,
        interpretation_adapter: null,
      },
    }
    const noTimeChart: LatestNatalChart = {
      ...emptyExpertChart,
      metadata: { ...emptyExpertChart.metadata, degraded_mode: "no_time" },
      astro_profile: { ...emptyExpertChart.astro_profile!, missing_birth_time: true },
    }

    const { rerender } = render(<NatalExpertPanel chart={legacyChart} />)
    expect(screen.getByText(/Ancien payload ou projection partielle/i)).toBeInTheDocument()

    rerender(<NatalExpertPanel chart={emptyExpertChart} />)
    expect(screen.getAllByText(/Bloc absent ou vide dans le payload public/i).length).toBeGreaterThan(0)
    expect(screen.getByText(/Dominantes indisponibles dans ce payload/i)).toBeInTheDocument()
    expect(screen.getByText(/Adaptateur indisponible dans ce payload/i)).toBeInTheDocument()

    rerender(<NatalExpertPanel chart={noTimeChart} />)
    expect(screen.getByText(/Mode sans heure fiable/i)).toBeInTheDocument()
    expect(
      within(screen.getByRole("region", { name: "Contrats traditionnels" })).getByText(
        /Bloc absent ou vide dans le payload public/i,
      ),
    ).toBeInTheDocument()
  })

  it("rend les etats loading, error et absence de chart", () => {
    const { rerender } = render(<NatalExpertPanel isLoading />)
    expect(screen.getByText(/Chargement des faits techniques/i)).toBeInTheDocument()

    rerender(<NatalExpertPanel errorMessage="Erreur API natal expert" />)
    expect(screen.getByRole("alert")).toHaveTextContent("Erreur API natal expert")

    rerender(<NatalExpertPanel chart={null} />)
    expect(screen.getByText(/Aucun theme natal charge/i)).toBeInTheDocument()
  })
})
