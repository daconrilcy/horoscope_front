// Tests des helpers purs d'evidence de l'interpretation natale.
import { describe, expect, it } from "vitest"

import { categorizeEvidence, formatEvidenceId } from "../components/natal-interpretation/NatalInterpretationEvidence"

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
})
