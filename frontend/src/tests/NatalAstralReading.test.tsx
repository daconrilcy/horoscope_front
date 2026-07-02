// Vérifie le rendu public de la lecture natale Astral et la préservation de la prose.
import { describe, expect, it } from "vitest"

import { NatalAstralReading } from "../features/natal-chart/NatalAstralReading"
import type { NatalInterpretationViewModel } from "../features/natal-chart/natalAstralReadingViewModel"
import { renderWithRouter } from "./test-utils"

function buildReadingViewModel(paragraphs: string[]): NatalInterpretationViewModel {
  return {
    status: "success",
    title: "Lecture natale",
    shortText: "Synthèse publique.",
    tier: "basic",
    variant: "full",
    label: "Essentielle",
    completeness: "completed",
    isPartial: false,
    chapters: [
      {
        code: "identity",
        title: "Identité",
        summarySentence: "Résumé du chapitre.",
        paragraphs,
        confidenceLabel: null,
        astroBasis: [],
        safetyFlags: [],
      },
    ],
    explanations: [],
    calculationFacts: null,
    highlightFacts: [],
    disclaimer: null,
    error: null,
  }
}

describe("NatalAstralReading", () => {
  it("ne coupe pas la prose longue sur les virgules", () => {
    const longParagraph =
      "Première clause très détaillée pour vérifier que le texte reste continu et lisible, " +
      "deuxième clause tout aussi développée pour occuper le flux narratif sans créer de coupure artificielle, " +
      "troisième clause finale pour atteindre une longueur suffisante et garder une lecture naturelle."

    const reading = buildReadingViewModel([longParagraph])

    const { container } = renderWithRouter(<NatalAstralReading reading={reading} />)
    const body = container.querySelector(".natal-reading__chapter-body")

    expect(body).not.toBeNull()
    const renderedParagraphs = Array.from(body?.querySelectorAll(".natal-reading__prose-paragraph") ?? [])

    expect(renderedParagraphs).toHaveLength(1)
    expect(renderedParagraphs[0]).toHaveTextContent("deuxième clause")
    expect(renderedParagraphs[0]).toHaveTextContent("troisième clause")
  })
})
