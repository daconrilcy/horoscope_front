// Garde DOM: la lecture narrative publique /natal n'expose pas de surfaces techniques interdites.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { InterpretationContent } from "../components/natal-interpretation/NatalInterpretationContent"
import type { NatalInterpretationViewData } from "../components/natal-interpretation/NatalInterpretationTypes"

const FORBIDDEN_DOM_PATTERN =
  /visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version/i

const NARRATIVE_DATA: NatalInterpretationViewData = {
  degraded_mode: null,
  narrative_natal_reading_v1: {
    contract_version: "narrative_natal_reading_v1",
    editorial_profile: "premium",
    chapters: [
      {
        key: "personality",
        title: "Votre personnalite",
        narrative:
          "Paragraphe narratif suffisamment long pour le test de garde DOM public sans fuite technique.",
        key_points: [],
      },
      {
        key: "emotional_world",
        title: "Votre monde emotionnel",
        narrative: "Deuxieme chapitre narratif lisible pour l utilisateur final.",
        key_points: [],
      },
      {
        key: "relationships",
        title: "Vos relations",
        narrative: "Troisieme chapitre narratif lisible pour l utilisateur final.",
        key_points: [],
      },
      {
        key: "vocation",
        title: "Votre vocation",
        narrative: "Quatrieme chapitre narratif lisible pour l utilisateur final.",
        key_points: [],
      },
      {
        key: "evolution_path",
        title: "Votre chemin d evolution",
        narrative: "Cinquieme chapitre narratif lisible pour l utilisateur final.",
        key_points: [],
      },
    ],
    used_astrological_elements: [
      {
        astrological_label: "Soleil en Taureau",
        consequence: "Votre expression personnelle recherche la stabilite.",
      },
    ],
  },
  meta: { level: "complete", persona_name: "Luna" },
  interpretation: {
    title: "Theme",
    summary: "Resume narratif public.",
    highlights: [],
    sections: [],
    advice: [],
    evidence: ["SUN_TAURUS_H10"],
  },
}

describe("natalPublicDomGuard", () => {
  it("n expose pas de motifs techniques dans la branche narrative publique", () => {
    const { container } = render(<InterpretationContent data={NARRATIVE_DATA} lang="fr" />)

    expect(screen.getByRole("heading", { name: "Votre personnalite" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Ce que nous avons utilise/i })).toBeInTheDocument()
    expect(container.textContent).not.toMatch(FORBIDDEN_DOM_PATTERN)
    expect(container.innerHTML).not.toMatch(/SUN_TAURUS|ASPECT_|_H\d/i)
  })

  it("affiche le resume free_long sans message de regeneration obsolete", () => {
    const freeLongData: NatalInterpretationViewData = {
      ...NARRATIVE_DATA,
      use_case: "natal_long_free",
      narrative_natal_reading_v1: null,
      meta: { level: "complete", use_case: "natal_long_free", persona_name: null },
      interpretation: {
        title: "Portrait astrologique",
        summary: "Resume free long visible.",
        highlights: [],
        sections: [],
        advice: [],
        evidence: [],
      },
    }

    render(<InterpretationContent data={freeLongData} lang="fr" />)

    expect(screen.getByText("Resume free long visible.")).toBeInTheDocument()
    expect(screen.queryByText(/Lecture complète à régénérer/i)).not.toBeInTheDocument()
  })

  it("affiche un message de regeneration sans fallback legacy pour une complete obsolete", () => {
    const legacyData: NatalInterpretationViewData = {
      ...NARRATIVE_DATA,
      narrative_natal_reading_v1: null,
      meta: { level: "complete", persona_name: "Luna" },
    }

    const { container } = render(<InterpretationContent data={legacyData} lang="fr" />)

    expect(screen.getByText(/Lecture complète à régénérer/i)).toBeInTheDocument()
    expect(screen.queryByText("Resume narratif public.")).not.toBeInTheDocument()
    expect(container.querySelector(".ni-evidence-tags")).toBeNull()
    expect(container.querySelector(".ni-projections")).toBeNull()
  })

  it("affiche le message de regeneration meme si une complete obsolete garde un corps legacy", () => {
    const legacyBodyData: NatalInterpretationViewData = {
      ...NARRATIVE_DATA,
      narrative_natal_reading_v1: null,
      meta: { level: "complete", persona_name: "Luna" },
      interpretation: {
        title: "Ancienne lecture complete",
        summary: "Resume legacy qui ne doit pas remplacer le message de regeneration.",
        highlights: ["Ancien point fort"],
        sections: [
          {
            key: "legacy-section",
            heading: "Ancienne section legacy",
            content: "Contenu legacy interdit dans la lecture complete publique.",
          },
        ],
        advice: [],
        evidence: [],
      },
    }

    const { container } = render(<InterpretationContent data={legacyBodyData} lang="fr" />)

    expect(screen.getByText(/Lecture complète à régénérer/i)).toBeInTheDocument()
    expect(screen.queryByText("Ancienne section legacy")).not.toBeInTheDocument()
    expect(container.querySelector(".ni-accordion")).toBeNull()
  })
})
