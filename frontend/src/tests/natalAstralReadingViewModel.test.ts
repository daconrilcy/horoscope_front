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
    expect(viewModel?.calculationReading?.summary?.highlights).toEqual([
      "Soleil en Capricorne",
      "Lune en Poissons",
      "Ascendant en Scorpion",
      "Maison II - Valeurs tres marque",
    ])
    expect(viewModel?.calculationReading?.summary?.text).toBe(
      "Ce theme met en avant une dynamique structuree, responsable et exigeante, avec un accent net sur Maison II - Valeurs.",
    )
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Ce repere decrit")
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Ce repere nuance")
    expect(viewModel?.calculationReading?.lifeAreas[0]).toMatchObject({
      rank: "Tres marque",
      title: "Maison II - Valeurs",
    })
    expect(viewModel?.calculationReading?.aspects[0]).toMatchObject({
      badge: "Tension",
      title: "Jupiter en tension avec Uranus",
    })
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Very high")
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Resources")
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
                  motion: "Retrograde motion",
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
      detail: "Maison III - Communication - retrograde apparent",
    })
    expect(viewModel?.calculationReading?.axes.map((axis) => axis.title)).toEqual(["Scorpion / Taureau"])
    expect(JSON.stringify(viewModel?.calculationReading?.axes)).not.toContain("Ascendant en Scorpion")
    expect(viewModel?.calculationReading?.otherForces[0]).toMatchObject({
      title: "Mercure en Capricorne",
      functionLabel: "Communication",
      lifeArea: "Maison III",
    })
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]?.detail).not.toContain("Retrograde motion")
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]?.detail).toContain("retrograde apparent")
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

  it("rend un aspect textuel brut avec vocabulaire public lisible", () => {
    const job: AstralJobResponse = {
      run_id: "run-text-aspect",
      status: "completed",
      result: {
        calculation: {
          dynamics: {
            major_aspects: [
              {
                aspect: "Mars trine Uranus",
                orb_degrees: 0.2,
                quality: "Flow",
                phase: "Separating",
              },
            ],
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture aspect" },
            chapters: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.calculationReading?.aspects[0]).toMatchObject({
      badge: "Fluidite",
      title: "Mars en harmonie avec Uranus",
      details: [
        { label: "Aspect", value: "Trigone" },
        { label: "Planetes", value: "Mars et Uranus" },
        { label: "Orbe", value: "0.20°" },
        { label: "Phase", value: "Separant" },
      ],
    })
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Mars trine Uranus")
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Flow")
    expect(JSON.stringify(viewModel?.calculationReading)).not.toContain("Separating")
  })

  it("deduit aussi les luminaires depuis un aspect textuel brut", () => {
    const job: AstralJobResponse = {
      run_id: "run-luminary-aspect",
      status: "completed",
      result: {
        calculation: {
          dynamics: {
            major_aspects: [{ aspect: "Sun trine Moon", quality: "Flow" }],
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture luminaires" },
            chapters: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.calculationReading?.aspects[0]).toMatchObject({
      badge: "Fluidite",
      title: "Soleil en harmonie avec Lune",
    })
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
