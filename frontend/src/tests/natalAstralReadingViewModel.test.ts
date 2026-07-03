// Verifie la normalisation publique des contrats Astral natals.
import { describe, expect, it } from "vitest"

import { buildNatalInterpretationViewModel } from "../features/natal-chart/natalAstralReadingViewModel"
import type { AstralJobResponse } from "../api/astral"
import type { BirthProfileData } from "../api/birthProfile"

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
                summary_sentence: "Résumé public du chapitre.",
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
    expect(viewModel?.title).toBe("Lecture basic")
    expect(viewModel?.label).toBe("Essentielle")
    expect(viewModel?.chapters[0]?.summarySentence).toBe("Résumé public du chapitre.")
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
            calculation_reference: {
              version: "1.2.3",
              zodiacal_reference_system: "tropical",
              coordinate_reference_system: "geocentric",
              house_system: "placidus",
              ephemeris_reference: "Swiss Ephemeris 2.10",
              precision: "arc-second",
            },
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
      "Maisons dominantes",
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
    expect(viewModel?.calculationFacts?.calculationReferenceMethods).toEqual([
      { label: "Version", value: "1.2.3", detail: null },
      { label: "Système zodiacal", value: "tropical", detail: null },
      { label: "Coordonnées", value: "geocentric", detail: null },
      { label: "Maisons", value: "placidus", detail: null },
      { label: "Éphémérides", value: "Swiss Ephemeris 2.10", detail: null },
    ])
    expect(viewModel?.calculationFacts?.groups[1]?.items[0]).toEqual({
      label: "Maison II - Valeurs",
      value: "Resources",
      detail: "Very high",
    })
    expect(viewModel?.calculationFacts?.groups[2]?.items[0]).toEqual({
      label: "Sun square Moon",
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

  it("affiche toutes les maisons dominantes transmises par dominant_themes.houses", () => {
    const job: AstralJobResponse = {
      run_id: "run-dominant-houses",
      status: "completed",
      result: {
        calculation: {
          dominant_themes: {
            houses: [
              { number: 2, theme: "Resources", importance: "Very high" },
              { number: 10, theme: "Career", importance: "High" },
              { number: 4, theme: "Home", importance: "Medium" },
            ],
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec maisons dominantes" },
            chapters: [],
          },
        },
      },
    }

    const dominantHousesGroup = buildNatalInterpretationViewModel(job, "basic")?.calculationFacts?.groups.find(
      (group) => group.title === "Maisons dominantes",
    )

    expect(dominantHousesGroup?.items).toEqual([
      { label: "Maison II - Valeurs", value: "Resources", detail: "Very high" },
      { label: "Maison X - Carrière", value: "Career", detail: "High" },
      { label: "Maison IV - Foyer", value: "Home", detail: "Medium" },
    ])
  })

  it("accepte dominant_houses et dedoublonne sans masquer les maisons distinctes", () => {
    const job: AstralJobResponse = {
      run_id: "run-dominant-houses-v2",
      status: "completed",
      result: {
        calculation: {
          dominant_houses: [
            { house_number: 7, theme: "Relations", importance: "High" },
            { house_number: 7, theme: "Relations", importance: "High" },
          ],
          dominance: {
            dominant_houses: [
              { house: 7, theme: "Partnerships", importance: "High" },
              { house: 11, theme: "Community", importance: "Medium" },
            ],
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec nouveau contrat" },
            chapters: [],
          },
        },
      },
    }

    const dominantHousesGroup = buildNatalInterpretationViewModel(job, "basic")?.calculationFacts?.groups.find(
      (group) => group.title === "Maisons dominantes",
    )

    expect(dominantHousesGroup?.items).toEqual([
      { label: "Maison VII - Relations", value: "Relations", detail: "High" },
      { label: "Maison VII - Relations", value: "Partnerships", detail: "High" },
      { label: "Maison XI - Communauté", value: "Community", detail: "Medium" },
    ])
  })

  it("lit les maisons dominantes numerotees par code depuis chart_balance", () => {
    const job: AstralJobResponse = {
      run_id: "run-chart-balance-dominant-houses",
      status: "completed",
      result: {
        chart_balance: {
          dominant_houses: [
            { code: "10", score: 0.82, rank: 1, source: "house_strength" },
            { code: "11", score: 0.76, rank: 2, source: "house_strength" },
            { code: "4", score: 0.52, rank: 3, source: "house_strength" },
            { code: "13", score: 0.4, rank: 4, source: "house_strength" },
            { code: "10.5", score: 0.3, rank: 5, source: "house_strength" },
          ],
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec chart balance" },
            chapters: [],
          },
        },
      },
    }

    const dominantHousesGroup = buildNatalInterpretationViewModel(job, "basic")?.calculationFacts?.groups.find(
      (group) => group.title === "Maisons dominantes",
    )

    expect(dominantHousesGroup?.items).toEqual([
      { label: "Maison X - Carrière", value: "Maison dominante", detail: "Rang 1", details: ["Score 0.82", "house_strength"] },
      { label: "Maison XI - Communauté", value: "Maison dominante", detail: "Rang 2", details: ["Score 0.76", "house_strength"] },
      { label: "Maison IV - Foyer", value: "Maison dominante", detail: "Rang 3", details: ["Score 0.52", "house_strength"] },
    ])
  })

  it("complete les maisons dominantes depuis chart_emphasis sans traduire le contenu source", () => {
    const job: AstralJobResponse = {
      run_id: "run-audit-dominant-houses",
      status: "completed",
      result: {
        calculation: {
          llm_payload: {
            dominant_themes: {
              houses: [
                {
                  importance: "Very high",
                  number: 10,
                  supporting_factors: ["Midheaven in house", "Sun in house"],
                  theme: "Career",
                },
              ],
            },
          },
          audit_payload: {
            payload: {
              chart_emphasis: {
                dominant_houses: [
                  {
                    house_number: 10,
                    score: 0.8587,
                    reason_details: [
                      { reason_code: "object_in_house", object_code: "mc" },
                      { reason_code: "object_in_house", object_code: "sun" },
                    ],
                  },
                  { house_number: 6, score: 0.3152 },
                  { house_number: 1, score: 0.2174 },
                ],
              },
            },
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec audit" },
            chapters: [],
          },
        },
      },
    }

    const dominantHousesGroup = buildNatalInterpretationViewModel(job, "basic")?.calculationFacts?.groups.find(
      (group) => group.title === "Maisons dominantes",
    )

    expect(dominantHousesGroup?.items).toEqual([
      {
        label: "Maison X - Carrière",
        value: "Career",
        detail: "Very high",
        details: ["Midheaven in house", "Sun in house", "Score 0.8587", "object_in_house - mc", "object_in_house - sun"],
      },
      { label: "Maison VI - Routines / hygiène de vie", value: "Maison dominante", detail: "Score 0.3152" },
      { label: "Maison I - Identité", value: "Maison dominante", detail: "Score 0.2174" },
    ])
  })

  it("preserve le texte source sans normalisation intrusive", () => {
    const job: AstralJobResponse = {
      run_id: "run-source-text-preserved",
      status: "completed",
      result: {
        reading: {
          status: "success",
          reading: {
            summary: { title: "Career — public" },
            chapters: [{ title: "Sun — Taurus", paragraphs: ["Alpha — beta"] }],
          },
        },
      },
    }

    const viewModel = buildNatalInterpretationViewModel(job, "basic")

    expect(viewModel?.title).toBe("Career — public")
    expect(viewModel?.chapters[0]?.title).toBe("Sun — Taurus")
    expect(viewModel?.chapters[0]?.paragraphs[0]).toBe("Alpha — beta")
  })

  it("expose les axes de maisons depuis house_axis_emphasis", () => {
    const job: AstralJobResponse = {
      run_id: "run-house-axis-emphasis",
      status: "completed",
      result: {
        calculation: {
          audit_payload: {
            payload: {
              house_axis_emphasis: [
                {
                  axis_code: "private_public",
                  houses: [4, 10],
                  primary_house: 10,
                  house_scores: [
                    { house_number: 4, score: 0.505 },
                    { house_number: 10, score: 1 },
                  ],
                },
                {
                  axis_code: "control_surrender",
                  houses: [6, 12],
                  primary_house: 6,
                  house_scores: [{ house_number: 6, score: 0.8946 }],
                },
                {
                  axis_code: "self_relationship",
                  houses: [1, 7],
                  primary_house: 1,
                  house_scores: [
                    { house_number: 1, score: 0.5252 },
                    { house_number: 7, score: 0.428 },
                  ],
                },
              ],
            },
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec axes" },
            chapters: [],
          },
        },
      },
    }

    const axesGroup = buildNatalInterpretationViewModel(job, "basic")?.calculationFacts?.groups.find(
      (group) => group.title === "Axes de maisons",
    )

    expect(axesGroup?.items).toEqual([
      {
        label: "Axe",
        value: "private_public",
        detail: "Maison IV - Foyer / Maison X - Carrière - Maison primaire Maison X - Carrière",
        details: ["Maison IV - Foyer: Score 0.505", "Maison X - Carrière: Score 1"],
      },
      {
        label: "Axe",
        value: "control_surrender",
        detail: "Maison VI - Routines / hygiène de vie / Maison XII - Inconscient - Maison primaire Maison VI - Routines / hygiène de vie",
        details: ["Maison VI - Routines / hygiène de vie: Score 0.8946"],
      },
      {
        label: "Axe",
        value: "self_relationship",
        detail: "Maison I - Identité / Maison VII - Relations - Maison primaire Maison I - Identité",
        details: ["Maison I - Identité: Score 0.5252", "Maison VII - Relations: Score 0.428"],
      },
    ])
  })

  it("conserve les maisons techniques separees des maisons dominantes", () => {
    const job: AstralJobResponse = {
      run_id: "run-dominant-and-technical-houses",
      status: "completed",
      result: {
        calculation: {
          dominant_themes: {
            houses: [{ number: 10, theme: "Career", importance: "High" }],
          },
          houses: [
            { number: 1, sign: "Scorpio", cusp_longitude: 215.1 },
            { number: 2, sign: "Sagittarius", cusp_longitude: 243.2 },
          ],
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec maisons separees" },
            chapters: [],
          },
        },
      },
    }

    const groups = buildNatalInterpretationViewModel(job, "basic")?.calculationFacts?.groups

    expect(groups?.map((group) => group.title)).toEqual(["Maisons dominantes", "Maisons"])
    expect(groups?.[0]?.items).toEqual([
      { label: "Maison X - Carrière", value: "Career", detail: "High" },
    ])
    expect(groups?.[1]?.items).toEqual([
      { label: "Maison I - Identité", value: "Scorpion", detail: "215.10°" },
      { label: "Maison II - Valeurs", value: "Sagittaire", detail: "243.20°" },
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
            engine_version: "0.1.0",
            ephemeris_version: "se-2026a",
            raw_payload_contract_version: "natal_structured_v14",
          },
          llm_payload: {
            chart: {
              calculation: {
                zodiac: "Tropical",
                coordinates: "Geocentric",
                house_system: "Placidus",
              },
            },
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
          audit_payload: {
            contract_version: "natal_structured_v14",
            payload: {
              chart_context: {
                calculation_reliability: {
                  birth_time_precision_required: true,
                  house_system_sensitive: true,
                },
                payload_contract: {
                  contract_version: "natal_structured_v14",
                },
              },
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
    expect(viewModel?.calculationFacts?.calculationReferenceMethods).toEqual([
      { label: "Version", value: "0.1.0", detail: null },
      { label: "Système zodiacal", value: "Tropical", detail: null },
      { label: "Coordonnées", value: "Geocentric", detail: null },
      { label: "Maisons", value: "Placidus", detail: null },
      { label: "Éphémérides", value: "se-2026a", detail: null },
    ])
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

    expect(viewModel?.title).toBe("How to read your natal chart")
    expect(viewModel?.shortText).toBe("Résumé issu du moteur externe.")
    expect(viewModel?.chapters.map((chapter) => chapter.paragraphs[0])).toEqual([
      "Explication top-level fournie par result.explanations.items.",
      "Deuxième explication top-level conservée.",
    ])
    expect(viewModel?.chapters.map((chapter) => chapter.title)).toEqual([
      "sun_in_taurus_house_10",
      "Moon en capricorn maison 6",
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
    expect(viewModel?.explanations.map((chapter) => chapter.title)).toEqual(["Sun en taurus maison 10"])
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
    expect(viewModel?.title).toBe("Lecture Basic publique")
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

    expect(viewModel?.title).toBe("Lecture Basic imbriquée")
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

    expect(viewModel?.title).toBe("Lecture Basic publique")
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

    expect(viewModel?.title).toBe("Lecture Basic complète")
    expect(viewModel?.chapters[0]?.paragraphs).toEqual([
      "Explication complète fournie par le moteur externe.",
    ])
  })

  it("dedoublonne le fuseau horaire et ordonne les coordonnees du profil", () => {
    const job: AstralJobResponse = {
      run_id: "run-birth-profile-methods",
      status: "completed",
      result: {
        calculation: {
          prepared_input: {
            birth_timezone: "Europe/Paris",
            timezone_used: "Europe/Paris",
          },
        },
        reading: {
          status: "success",
          reading: {
            summary: { title: "Lecture avec profil" },
            chapters: [],
          },
        },
      },
    }
    const birthProfile = {
      birth_date: "1988-04-12",
      birth_place: "Grenoble, France",
      birth_time: "23:17",
      birth_timezone: "Europe/Paris",
      birth_lat: 45.1885,
      birth_lon: 5.7245,
    } as BirthProfileData

    const viewModel = buildNatalInterpretationViewModel(job, "basic", birthProfile)

    expect(viewModel?.calculationFacts?.methods).toEqual([
      { label: "Fuseau horaire", value: "Europe/Paris", detail: null },
      { label: "Coordonnées", value: "5.7245° E\n45.1885° N", detail: null },
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
