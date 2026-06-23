// Verifie la normalisation publique des contrats Astral natals.
import { describe, expect, it } from "vitest"

import { buildNatalInterpretationViewModel } from "../features/natal-chart/natalAstralReadingViewModel"
import type { AstralJobResponse } from "../api/astral"

describe("buildNatalInterpretationViewModel", () => {
  it("normalise une enveloppe async V1 complete", () => {
    const job: AstralJobResponse = {
      run_id: "run-async",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: {
              title: "Lecture basic",
              short_text: "Synthese publique.",
            },
            chapters: [
              {
                code: "identity",
                title: "Identite",
                body: "Premier paragraphe.\n\nSecond paragraphe.",
                confidence: "high",
                astro_basis: [
                  "Soleil en Lion",
                  {
                    fact_id: "signal:moon:balance",
                    label: "Lune en Balance",
                    interpretive_role: "supporting",
                  },
                ],
              },
            ],
            legal: { disclaimer: "Lecture symbolique." },
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.status).toBe("success")
    expect(viewModel?.label).toBe("basic")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual(["Premier paragraphe.", "Second paragraphe."])
    expect(viewModel?.chapters[0]?.confidenceLabel).toBe("Confiance elevee")
    expect(viewModel?.chapters[0]?.astroBasis).toEqual(["Soleil en Lion", "Lune en Balance (appui)"])
    expect(viewModel?.disclaimer).toBe("Lecture symbolique.")
    expect(JSON.stringify(viewModel)).not.toContain("signal:moon:balance")
  })

  it("normalise une enveloppe gateway V2 premium", () => {
    const job: AstralJobResponse = {
      run_id: "run-v2",
      status: "completed",
      result: {
        metadata: {
          product_code: "natal_full_premium",
          tier: "premium",
          variant: "full",
        },
        quality: {
          reading_completeness: "completed",
        },
        calculation: {
          core_identity: {
            sun: {
              placement: {
                object: "Sun",
                sign: "Capricorn",
                house: { number: 2, theme: "Resources" },
                longitude_deg: 281.4543,
              },
            },
            moon: {
              placement: {
                object: "Moon",
                sign: "Pisces",
                house: { number: 4, theme: "Home" },
                longitude_deg: 341.7641,
              },
            },
          },
          angles: {
            ascendant: { sign: "Scorpio", house: 1 },
            descendant: { sign: "Taurus", house: 7 },
          },
          dominant_themes: {
            houses: [{ number: 2, theme: "Resources", importance: "Very high" }],
          },
          dynamics: {
            major_aspects: [
              {
                aspect: "Jupiter opposition Uranus",
                objects: ["Jupiter", "Uranus"],
                orb_degrees: 0.76,
                quality: "Tension",
              },
            ],
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: {
              title: "Lecture premium",
              short_text: "Lecture approfondie.",
            },
            chapters: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job)

    expect(viewModel?.tier).toBe("premium")
    expect(viewModel?.variant).toBe("full")
    expect(viewModel?.label).toBe("premium")
    expect(viewModel?.isPartial).toBe(false)
    expect(viewModel?.calculationFacts?.groups.map((group) => group.title)).toEqual([
      "Repères principaux",
      "Maisons",
      "Aspects notables",
    ])
    expect(viewModel?.calculationFacts?.groups[0]?.items).toEqual([
      { label: "Soleil", value: "Capricorne", detail: "Maison II - Valeurs - 281.45°" },
      { label: "Lune", value: "Poissons", detail: "Maison IV - Foyer - 341.76°" },
      { label: "Ascendant", value: "Scorpion", detail: "Maison I - Identité" },
      { label: "Descendant", value: "Taureau", detail: "Maison VII - Relations" },
    ])
  })

  it("lit les faits natals depuis calculation.llm_payload quand le calcul Astral est enveloppe", () => {
    const job: AstralJobResponse = {
      run_id: "run-real-shape",
      status: "completed",
      service_code: "natal_basic",
      result: {
        calculation: {
          response_contract_version: "astro_engine_response_v1",
          calculation_result: {
            status: "completed",
            chart_calculation_id: "chart-1",
          },
          llm_payload: {
            core_identity: {
              sun: {
                placement: {
                  object: "Sun",
                  sign: "Capricorn",
                  house: { number: 2, theme: "Resources" },
                },
              },
              moon: {
                placement: {
                  object: "Moon",
                  sign: "Pisces",
                  house: { number: 4, theme: "Home" },
                },
              },
              ascendant: {
                sign: "Scorpio",
              },
            },
            angles: {
              descendant: { sign: "Taurus", house: 7 },
              midheaven: { sign: "Leo", house: 10 },
            },
            placements: {
              supporting: [
                {
                  object: "Mercury",
                  sign: "Capricorn",
                  house: { number: 3, theme: "Communication" },
                },
              ],
            },
            dominant_themes: {
              houses: [{ number: 2, theme: "Resources", importance: "Very high" }],
            },
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture basic" },
            chapters: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.calculationFacts?.groups[0]?.items).toEqual([
      { label: "Soleil", value: "Capricorne", detail: "Maison II - Valeurs" },
      { label: "Lune", value: "Poissons", detail: "Maison IV - Foyer" },
      { label: "Ascendant", value: "Scorpion", detail: null },
      { label: "Descendant", value: "Taureau", detail: "Maison VII - Relations" },
      { label: "Milieu du Ciel", value: "Lion", detail: "Maison X - Carrière" },
    ])
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]).toEqual({
      label: "Mercure",
      value: "Capricorne",
      detail: "Maison III - Communication",
    })
  })

  it("marque une lecture simplifiee sans heure comme partielle", () => {
    const job: AstralJobResponse = {
      run_id: "run-simplified",
      status: "completed",
      service_code: "natal_simplified",
      result: {
        quality: { reading_completeness: "partial" },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture indicative" },
            chapters: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.variant).toBe("simplified")
    expect(viewModel?.completeness).toBe("partial")
    expect(viewModel?.label).toBe("basic")
    expect(viewModel?.isPartial).toBe(true)
  })

  it("remonte une erreur interne failed proprement", () => {
    const job: AstralJobResponse = {
      run_id: "run-failed",
      status: "completed",
      result: {
        reading: {
          status: "failed",
          error: {
            code: "PROVIDER_ERROR",
            message: "Provider indisponible.",
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job)

    expect(viewModel?.status).toBe("failed")
    expect(viewModel?.error?.code).toBe("PROVIDER_ERROR")
    expect(viewModel?.error?.message).toBe("Provider indisponible.")
  })

  it("remonte un rejet safety avec code et regle", () => {
    const job: AstralJobResponse = {
      run_id: "run-safety",
      status: "completed",
      result: {
        reading: {
          status: "safety_rejected",
          error: {
            code: "SAFETY_REJECTED",
            message: "Contenu refuse.",
            rule_id: "medical_claim",
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job)

    expect(viewModel?.status).toBe("safety_rejected")
    expect(viewModel?.error?.code).toBe("SAFETY_REJECTED")
    expect(viewModel?.error?.ruleId).toBe("medical_claim")
  })

  it("ne fuite pas le payload technique quand la forme est inconnue", () => {
    const job: AstralJobResponse = {
      run_id: "run-unknown",
      status: "completed",
      result: {
        debug: { llm_request: { secret: "hidden" } },
        interpretation_request: { prompt: "hidden" },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job)

    expect(viewModel?.status).toBe("empty")
    expect(viewModel?.label).toBe("unknown")
    expect(viewModel?.shortText).toContain("forme publique")
    expect(JSON.stringify(viewModel)).not.toContain("hidden")
  })
})
