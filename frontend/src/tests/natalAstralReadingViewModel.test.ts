// Vérifie la normalisation publique des contrats Astral natals.
import { describe, expect, it } from "vitest"

import type { AstralJobResponse } from "../api/astral"
import { buildNatalInterpretationViewModel } from "../features/natal-chart/natalAstralReadingViewModel"

const completeExplanations = {
  status: "complete",
  language_code: "fr",
  items: [
    {
      fact_id: "placement:sun:capricorn:house:2",
      kind_code: "placement",
      title: "Soleil en Capricorne maison 2",
      explanation: "Explication Astral du Soleil fournie par le moteur externe.",
      expression_primary: "Maison 2",
      source: "generated",
    },
    {
      fact_id: "placement:moon:pisces:house:4",
      kind_code: "placement",
      title: "Lune en Poissons maison 4",
      explanation: "Explication Astral de la Lune fournie par le moteur externe.",
      expression_primary: "Maison 4",
      source: "generated",
    },
    {
      fact_id: "placement:ascendant:scorpio:house:1",
      kind_code: "angle",
      title: "Ascendant en Scorpion maison 1",
      explanation: "Explication Astral de l'Ascendant fournie par le moteur externe.",
      expression_primary: "Maison 1",
      source: "generated",
    },
    {
      fact_id: "house_axis:self_relationship",
      kind_code: "house_axis",
      title: "Axe maison : soi et relation",
      explanation: "Explication Astral de l'axe relationnel fournie par le moteur externe.",
      source: "generated",
    },
    {
      fact_id: "house_emphasis:house:2",
      kind_code: "house_emphasis",
      title: "Emphase maison ressources",
      explanation: "Explication Astral du domaine dominant fournie par le moteur externe.",
      expression_primary: "resources",
      source: "generated",
    },
    {
      fact_id: "placement:mercury:capricorn:house:3",
      kind_code: "placement",
      title: "Mercure en Capricorne maison 3",
      explanation: "Explication Astral de Mercure fournie par le moteur externe.",
      expression_primary: "Maison 3",
      source: "generated",
    },
    {
      fact_id: "placement:venus:taurus:house:10",
      kind_code: "placement",
      title: "Vénus en Taureau maison 10",
      explanation: "Explication Astral de Vénus fournie par le moteur externe.",
      expression_primary: "Maison 10",
      source: "generated",
    },
    {
      fact_id: "placement:mars:aquarius:house:8",
      kind_code: "placement",
      title: "Mars en Verseau maison 8",
      explanation: "Explication Astral de Mars fournie par le moteur externe.",
      expression_primary: "Maison 8",
      source: "generated",
    },
    {
      fact_id: "aspect:mars:trine:uranus",
      kind_code: "aspect",
      title: "Mars en harmonie avec Uranus",
      explanation: "Explication Astral de l'aspect Mars Uranus fournie par le moteur externe.",
      expression_primary: "Fluidité",
      source: "generated",
    },
  ],
}

function baseSuccessfulJob(result: Record<string, unknown>): AstralJobResponse {
  return {
    run_id: "run-test",
    status: "completed",
    result: {
      reading: {
        status: "success",
        reading: {
          summary: {
            title: "Lecture natale",
            short_text: "Synthese publique.",
          },
          chapters: [],
          legal: { disclaimer: "Lecture symbolique." },
        },
      },
      ...result,
    },
  }
}

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

  it("construit la lecture pedagogique uniquement depuis les explications Astral", () => {
    const job = baseSuccessfulJob({
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
      explanations: completeExplanations,
    })

    const viewModel = buildNatalInterpretationViewModel(job)
    const reading = viewModel?.calculationReading

    expect(viewModel?.tier).toBe("premium")
    expect(viewModel?.variant).toBe("full")
    expect(viewModel?.isPartial).toBe(false)
    expect(reading?.explanationStatus).toBe("complete")
    expect(reading?.explanationLanguageCode).toBe("fr")
    expect(reading?.summary).toEqual({
      text: null,
      highlights: [
        "Soleil en Capricorne maison 2",
        "Lune en Poissons maison 4",
        "Ascendant en Scorpion maison 1",
        "Emphase maison ressources",
      ],
    })
    expect(reading?.pillars.map((pillar) => pillar.description)).toEqual([
      "Explication Astral du Soleil fournie par le moteur externe.",
      "Explication Astral de la Lune fournie par le moteur externe.",
      "Explication Astral de l'Ascendant fournie par le moteur externe.",
    ])
    expect(reading?.axes[0]).toMatchObject({
      code: "axis-0",
      title: "Axe maison : soi et relation",
      description: "Explication Astral de l'axe relationnel fournie par le moteur externe.",
    })
    expect(reading?.lifeAreas[0]).toMatchObject({
      rank: "Domaine dominant",
      title: "Emphase maison ressources",
      description: "Explication Astral du domaine dominant fournie par le moteur externe.",
    })
    expect(reading?.lifeAreas[0]?.details).toEqual([])
    expect(reading?.otherForces.map((force) => force.description)).toEqual([
      "Explication Astral de Mercure fournie par le moteur externe.",
      "Explication Astral de Vénus fournie par le moteur externe.",
      "Explication Astral de Mars fournie par le moteur externe.",
    ])
    expect(reading?.aspects[0]).toMatchObject({
      badge: "Fluidité",
      title: "Mars en harmonie avec Uranus",
      description: "Explication Astral de l'aspect Mars Uranus fournie par le moteur externe.",
    })
    expect(JSON.stringify(reading)).not.toContain("generated")
    expect(JSON.stringify(reading)).not.toContain("placement:sun")
    expect(JSON.stringify(reading)).not.toContain("Ce theme met en avant")
    expect(JSON.stringify(reading)).not.toContain("cooperation entre les planetes")
  })

  it("garde les faits de calcul en details techniques sans creer de lecture pedagogique fallback", () => {
    const job = baseSuccessfulJob({
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
    })

    const viewModel = buildNatalInterpretationViewModel(job, "basic")
    const reading = viewModel?.calculationReading

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
    expect(reading?.summary).toBeNull()
    expect(reading?.pillars).toEqual([])
    expect(reading?.axes).toEqual([])
    expect(reading?.lifeAreas).toEqual([])
    expect(reading?.otherForces).toEqual([])
    expect(reading?.aspects).toEqual([])
    expect(reading?.technicalGroups.length).toBeGreaterThan(0)
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]?.detail).not.toContain("Retrograde motion")
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]?.detail).toContain("retrograde apparent")
  })

  it("rend une lecture partielle avec seulement les explications disponibles", () => {
    const job = baseSuccessfulJob({
      explanations: {
        status: "partial",
        language_code: "fr",
        missing_fact_ids: ["placement:ascendant:unknown"],
        errors: ["missing birth time"],
        items: [
          {
            fact_id: "placement:sun:gemini:house:9",
            kind_code: "placement",
            title: "Soleil en Gémeaux maison 9",
            explanation: "Explication partielle du Soleil.",
            expression_primary: "Maison 9",
          },
        ],
      },
    })

    const viewModel = buildNatalInterpretationViewModel(job, "basic")
    const serialized = JSON.stringify(viewModel?.calculationReading)

    expect(viewModel?.calculationReading?.explanationStatus).toBe("partial")
    expect(viewModel?.calculationReading?.pillars).toEqual([
      {
        code: "sun",
        icon: "☉",
        title: "Soleil en Gémeaux maison 9",
        description: "Explication partielle du Soleil.",
        lifeArea: "Expression principale : Maison 9",
      },
    ])
    expect(viewModel?.calculationReading?.pillars.map((pillar) => pillar.code)).not.toContain("ascendant")
    expect(serialized).not.toContain("placement:ascendant")
    expect(serialized).not.toContain("missing birth time")
  })

  it("ignore les explications indisponibles et n'invente pas de contenu public", () => {
    const job = baseSuccessfulJob({
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
      explanations: {
        status: "unavailable",
        language_code: "fr",
        items: [
          {
            fact_id: "aspect:mars:trine:uranus",
            kind_code: "aspect",
            title: "Mars Uranus",
            explanation: "Cette explication ne doit pas etre rendue.",
          },
        ],
      },
    })

    const viewModel = buildNatalInterpretationViewModel(job, "basic")
    const reading = viewModel?.calculationReading

    expect(reading?.explanationStatus).toBe("unavailable")
    expect(reading?.summary).toBeNull()
    expect(reading?.aspects).toEqual([])
    expect(JSON.stringify(reading)).not.toContain("Cette explication ne doit pas etre rendue")
    expect(JSON.stringify(reading)).not.toContain("action rapide")
    expect(viewModel?.calculationFacts?.groups[0]?.items[0]).toMatchObject({
      label: "Trigone",
      value: "Mars - Uranus",
      detail: "0.20° - Fluidite - Separant",
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
