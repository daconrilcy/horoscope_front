// Tests des helpers et classes canoniques d'evidence de l'interpretation natale.
import { cleanup, render, screen } from "@testing-library/react"
import { createElement } from "react"
import { afterEach, describe, expect, it } from "vitest"

import { ConsultationPrecisionBadge } from "../features/consultations/components/ConsultationPrecisionBadge"
import {
  categorizeEvidence,
  EvidenceTags,
  formatEvidenceId,
} from "../components/natal-interpretation/NatalInterpretationEvidence"

afterEach(() => {
  cleanup()
})

describe("natalInterpretation evidence helpers", () => {
  it("formate les identifiants principaux en libelles lisibles", () => {
    expect(formatEvidenceId("SUN_ARIES_H1")).toBe("Soleil Bélier (M1)")
    expect(formatEvidenceId("HOUSE_7_IN_LIBRA")).toBe("Maison 7 en Balance")
    expect(formatEvidenceId("ASPECT_SUN_MOON_TRINE")).toBe("Aspect Soleil - Lune (trigone)")
  })

  it("classe les preuves par categorie stable", () => {
    expect(categorizeEvidence("ASC_ARIES")).toBe("angles")
    expect(categorizeEvidence("SUN_ARIES")).toBe("personal_planets")
    expect(categorizeEvidence("PLUTO_CAPRICORN")).toBe("slow_planets")
    expect(categorizeEvidence("HOUSE_10_IN_LEO")).toBe("dominant_houses")
    expect(categorizeEvidence("ASPECT_SUN_MOON_TRINE")).toBe("major_aspects")
    expect(categorizeEvidence("UNMAPPED_TOKEN")).toBe("other")
  })

  it("rend les preuves avec les classes canoniques ni-evidence", () => {
    const { container } = render(
      createElement(EvidenceTags, {
        evidence: ["SUN_ARIES", "ASPECT_SUN_MOON_TRINE", "ASC_ARIES"],
        title: "Preuves",
        t: {
          evidenceIntro: "Sources utilisees",
          evidenceEmpty: "Aucune preuve",
          showEvidence: "Afficher",
          hideEvidence: "Masquer",
          dedupedCount: (count: number) => `${count} preuves`,
          evidenceCategories: {
            angles: "Angles",
            personalPlanets: "Personnelles",
            slowPlanets: "Lentes",
            dominantHouses: "Maisons",
            majorAspects: "Aspects",
            other: "Autres",
          },
        },
      }),
    )

    expect(screen.getByText("Soleil Bélier")).toHaveClass("ni-evidence-pill", "ni-evidence-pill--planet")
    expect(screen.getByText("Aspect Soleil - Lune (trigone)")).toHaveClass("ni-evidence-pill", "ni-evidence-pill--aspect")
    expect(screen.getByText("Ascendant Bélier")).toHaveClass("ni-evidence-pill", "ni-evidence-pill--angle")
    expect(container.querySelector(".evidence-pill")).toBeNull()
    expect(container.querySelector(".evidence-tags__list")).toBeNull()
  })

  it("rend le badge de precision avec les classes canoniques consultation", () => {
    const { container } = render(
      createElement(ConsultationPrecisionBadge, { precisionLevel: "high" }, "Precision haute"),
    )

    expect(screen.getByText("Precision haute")).toHaveClass(
      "consultation-precision-badge",
      "consultation-precision-badge--high",
    )
    expect(container.querySelector(".precision-badge")).toBeNull()
  })
})
