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
    expect(viewModel?.title).toBe("Lecture Essentielle")
    expect(viewModel?.label).toBe("Essentielle")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual(["Premier paragraphe.", "Second paragraphe."])
    expect(viewModel?.chapters[0]?.confidenceLabel).toBe("Confiance élevée")
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
          zodiac: "Tropical",
          house_system: "Placidus",
          reference_version: "astro-ref-2026.06",
          engine: "Astral Engine",
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
            imum_coeli: {
              placement: {
                sign: "Aquarius",
                house: { number: 4, theme: "Home" },
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
                aspect: "Sun square Moon",
                objects: ["Sun", "Moon"],
                orb_degrees: 0.76,
                quality: "Tension",
              },
              { aspect: "Mercury trine Mars", objects: ["Mercury", "Mars"], orb_degrees: 1.12 },
              { aspect: "Venus sextile Jupiter", objects: ["Venus", "Jupiter"], orb_degrees: 2.34 },
              { aspect: "Saturn opposition Uranus", objects: ["Saturn", "Uranus"], orb_degrees: 3.45 },
              { aspect: "Neptune square Pluto", objects: ["Neptune", "Pluto"], orb_degrees: 4.56 },
              { aspect: "Moon trine Venus", objects: ["Moon", "Venus"], orb_degrees: 5.67 },
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
    expect(viewModel?.label).toBe("Premium")
    expect(viewModel?.isPartial).toBe(false)
    expect(viewModel?.calculationFacts?.groups.map((group) => group.title)).toEqual([
      "Repères principaux",
      "Maisons",
      "Aspects majeurs",
    ])
    expect(viewModel?.calculationFacts?.groups[0]?.items).toEqual([
      { label: "Soleil", value: "Capricorne", detail: "Maison II - Valeurs - 281.45°" },
      { label: "Lune", value: "Poissons", detail: "Maison IV - Foyer - 341.76°" },
      { label: "Ascendant", value: "Scorpion", detail: "Maison I - Identité" },
      { label: "Descendant", value: "Taureau", detail: "Maison VII - Relations" },
      { label: "Fond du Ciel", value: "Verseau", detail: "Maison IV - Foyer" },
    ])
    expect(viewModel?.calculationFacts?.methods).toEqual([
      { label: "Système", value: "Tropical", detail: "Placidus" },
      { label: "Référence", value: "astro-ref-2026.06", detail: "Astral Engine" },
    ])
    expect(viewModel?.calculationFacts?.groups[1]?.items[0]).toEqual({
      label: "Maison II - Valeurs",
      value: "Valeurs",
      detail: "Très élevée",
    })
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]).toEqual({
      label: "Soleil Carré Lune",
      value: "Soleil - Lune",
      detail: "0.76° - Tension",
    })
    expect(viewModel?.calculationFacts?.groups[2]?.items).toHaveLength(6)
    expect(viewModel?.highlightFacts).toEqual([
      { label: "Soleil", value: "Capricorne", detail: "Maison II - Valeurs - 281.45°" },
      { label: "Lune", value: "Poissons", detail: "Maison IV - Foyer - 341.76°" },
      { label: "Ascendant", value: "Scorpion", detail: "Maison I - Identité" },
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
    expect(viewModel?.highlightFacts.map((fact) => fact.label)).toEqual(["Soleil", "Lune", "Ascendant"])
  })

  it("conserve les explications Astral quand les chapitres utilisent des champs texte alternatifs", () => {
    const job: AstralJobResponse = {
      run_id: "run-explanations",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture Astral" },
            sections: [
              {
                code: "identity",
                title: "Identité",
                body: "",
                explanation: "Explication fournie par le moteur Astral.",
                confidence: "medium",
                public_evidence: [
                  {
                    label: "Soleil en Balance",
                    meaning: "Expression orientée vers l'équilibre.",
                  },
                ],
              },
              {
                title: "Ressources",
                narrative: "Narratif Astral conservé dans la lecture publique.",
              },
            ],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.chapters.map((chapter) => chapter.paragraphs[0])).toEqual([
      "Explication fournie par le moteur Astral.",
      "Narratif Astral conservé dans la lecture publique.",
    ])
    expect(viewModel?.chapters[0]?.astroBasis).toEqual([
      "Soleil en Balance: Expression orientée vers l'équilibre.",
    ])
  })

  it("lit les sections quand Astral renvoie un tableau chapters vide", () => {
    const job: AstralJobResponse = {
      run_id: "run-sections-after-empty-chapters",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture Astral" },
            chapters: [],
            sections: [
              {
                title: "Section Astral",
                narrative: "Section publique récupérée malgré chapters vide.",
              },
            ],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.chapters[0]?.title).toBe("Section Astral")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual([
      "Section publique récupérée malgré chapters vide.",
    ])
  })

  it("lit les sections quand Astral renvoie un tableau chapters non vide mais sans texte", () => {
    const job: AstralJobResponse = {
      run_id: "run-sections-after-empty-chapter-body",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture Astral" },
            chapters: [{ title: "Chapitre vide", body: "" }],
            sections: [
              {
                title: "Section Astral",
                explanation: "Section publique prioritaire quand chapters est vide de texte.",
              },
            ],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.chapters[0]?.title).toBe("Section Astral")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual([
      "Section publique prioritaire quand chapters est vide de texte.",
    ])
  })

  it("affiche les explications top-level result.explanations du moteur Astral", () => {
    const job: AstralJobResponse = {
      run_id: "run-result-explanations",
      status: "completed",
      service_code: "natal_basic",
      result: {
        summary: {
          title: "How to read your natal chart",
          short_text: "Résumé issu du moteur externe.",
        },
        explanations: {
          items: [
            {
              explanation: "Explication top-level fournie par result.explanations.items.",
              expression_primary: "Maison 10",
              fact_id: "placement:sun:taurus:house:10",
              kind_code: "placement",
              source: "cache",
              title: "sun_in_taurus_house_10",
            },
            {
              explanation: "Deuxième explication top-level conservée.",
              expression_primary: "Maison 6",
              fact_id: "placement:moon:capricorn:house:6",
              kind_code: "placement",
              source: "cache",
              title: "Moon en capricorn maison 6",
            },
          ],
          language_code: "fr",
          status: "complete",
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.title).toBe("Comment lire ton thème natal")
    expect(viewModel?.shortText).toBe("Résumé issu du moteur externe.")
    expect(viewModel?.chapters.map((chapter) => chapter.paragraphs[0])).toEqual([
      "Explication top-level fournie par result.explanations.items.",
      "Deuxième explication top-level conservée.",
    ])
    expect(viewModel?.chapters.map((chapter) => chapter.title)).toEqual([
      "Soleil en Taureau maison 10",
      "Lune en Capricorne maison 6",
    ])
    expect(JSON.stringify(viewModel)).not.toContain("placement:sun:taurus:house:10")
    expect(JSON.stringify(viewModel)).not.toContain("cache")
  })

  it("separe result.explanations quand l'enveloppe reading ne contient qu'un resume", () => {
    const job: AstralJobResponse = {
      run_id: "run-result-explanations-fallback",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: {
              title: "Résumé seul",
              short_text: "Synthèse courte sans chapitre.",
            },
            chapters: [],
          },
        },
        explanations: {
          identity: "Explication de secours depuis result.explanations.",
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.chapters).toEqual([])
    expect(viewModel?.explanations[0]?.title).toBe("identity")
    expect(viewModel?.explanations[0]?.paragraphs).toEqual([
      "Explication de secours depuis result.explanations.",
    ])
  })

  it("separe result.explanations.items des chapitres Astral deja presents", () => {
    const job: AstralJobResponse = {
      run_id: "run-result-explanations-with-chapters",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: {
              title: "Lecture structurée",
              short_text: "Résumé structuré.",
            },
            chapters: [
              {
                code: "identity",
                title: "Identité structurée",
                body: "Chapitre narratif principal.",
                astro_basis: [{ fact_id: "hidden", label: "Ascendant en Cancer" }],
              },
            ],
          },
        },
        explanations: {
          items: [
            {
              explanation: "Le Soleil en Taureau en maison 10 indique une orientation stable.",
              expression_primary: "Maison 10",
              fact_id: "placement:sun:taurus:house:10",
              kind_code: "placement",
              source: "cache",
              title: "Sun en taurus maison 10",
            },
          ],
          language_code: "fr",
          status: "complete",
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.chapters.map((chapter) => chapter.title)).toEqual(["Identité structurée"])
    expect(viewModel?.chapters.map((chapter) => chapter.paragraphs[0])).toEqual(["Chapitre narratif principal."])
    expect(viewModel?.explanations.map((chapter) => chapter.title)).toEqual(["Soleil en Taureau maison 10"])
    expect(viewModel?.explanations.map((chapter) => chapter.paragraphs[0])).toEqual([
      "Le Soleil en Taureau en maison 10 indique une orientation stable.",
    ])
    expect(viewModel?.chapters[0]?.astroBasis).toEqual(["Ascendant en Cancer"])
    expect(JSON.stringify(viewModel)).not.toContain("placement:sun:taurus:house:10")
    expect(JSON.stringify(viewModel)).not.toContain("cache")
  })

  it("normalise l'ancien payload public Basic V2 du moteur Astral", () => {
    const job: AstralJobResponse = {
      run_id: "run-basic-v2",
      status: "completed",
      service_code: "natal_basic",
      result: {
        basic_natal_interpretation_v2: {
          interpretation: {
            title: "Lecture Basic publique",
            summary: "Résumé Basic public.",
            introduction: "Introduction lisible fournie par Astral.",
            themes: [
              {
                title: "Identité relationnelle",
                narrative: "Narratif de thème fourni par Astral.",
                public_evidence: [{ label: "Lune en Taureau" }],
              },
            ],
            conclusion: "Conclusion lisible fournie par Astral.",
          },
          disclaimers: ["Lecture symbolique."],
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.status).toBe("success")
    expect(viewModel?.title).toBe("Lecture Essentielle publique")
    expect(viewModel?.shortText).toBe("Résumé Basic public.")
    expect(viewModel?.chapters.map((chapter) => chapter.title)).toEqual([
      "Introduction",
      "Identité relationnelle",
      "Conclusion",
    ])
    expect(viewModel?.chapters.map((chapter) => chapter.paragraphs[0])).toEqual([
      "Introduction lisible fournie par Astral.",
      "Narratif de thème fourni par Astral.",
      "Conclusion lisible fournie par Astral.",
    ])
    expect(viewModel?.chapters[1]?.astroBasis).toEqual(["Lune en Taureau"])
    expect(viewModel?.disclaimer).toBe("Lecture symbolique.")
  })

  it("retrouve l'ancien payload Basic V2 quand il est imbrique dans reading", () => {
    const job: AstralJobResponse = {
      run_id: "run-basic-v2-nested",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            basic_natal_interpretation_v2: {
              interpretation: {
                title: "Lecture Basic imbriquée",
                introduction: "Introduction Basic imbriquée fournie par Astral.",
                themes: [],
              },
            },
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.title).toBe("Lecture Essentielle imbriquée")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual([
      "Introduction Basic imbriquée fournie par Astral.",
    ])
  })

  it("utilise le payload Basic V2 quand l'enveloppe reading voisine ne contient pas de texte", () => {
    const job: AstralJobResponse = {
      run_id: "run-basic-v2-fallback",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture vide" },
            chapters: [],
          },
        },
        basic_natal_interpretation_v2: {
          interpretation: {
            title: "Lecture Basic publique",
            introduction: "Texte public de secours fourni par Astral.",
            themes: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.title).toBe("Lecture Essentielle publique")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual([
      "Texte public de secours fourni par Astral.",
    ])
  })

  it("utilise le payload Basic V2 quand l'enveloppe reading ne contient qu'un resume", () => {
    const job: AstralJobResponse = {
      run_id: "run-basic-v2-summary-only",
      status: "completed",
      service_code: "natal_basic",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: {
              title: "Résumé seul",
              short_text: "Synthèse courte sans chapitre.",
            },
            chapters: [],
          },
        },
        basic_natal_interpretation_v2: {
          interpretation: {
            title: "Lecture Basic complète",
            introduction: "Explication complète fournie par le moteur externe.",
            themes: [],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.title).toBe("Lecture Essentielle complète")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual([
      "Explication complète fournie par le moteur externe.",
    ])
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
    expect(viewModel?.label).toBe("Essentielle")
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
    expect(viewModel?.label).toBe("Lecture")
    expect(viewModel?.shortText).toContain("forme publique")
    expect(JSON.stringify(viewModel)).not.toContain("hidden")
  })
})
