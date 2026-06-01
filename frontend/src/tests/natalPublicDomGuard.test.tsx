// Garde DOM: la lecture narrative publique /natal n'expose pas de surfaces techniques interdites.
import { render, screen, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { InterpretationContent } from "../components/natal-interpretation/NatalInterpretationContent"
import type { NatalInterpretationViewData } from "../components/natal-interpretation/NatalInterpretationTypes"
import { NatalNarrativeReading } from "../features/natal-chart/NatalNarrativeReading"
import { NatalReadingSources } from "../features/natal-chart/NatalReadingSources"

const FORBIDDEN_DOM_PATTERN =
  /visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node/i

const FORBIDDEN_BASIC_PUBLIC_LABEL_PATTERN =
  /\b(moon|sun|saturn|north node|south node|Synthese|theme|themes|repere|planetaire|a integrer)\b/i

const FORBIDDEN_PUBLIC_CONTROL_PATTERN =
  /shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh|natal_interpretation_short|natal_long_free|fallback_default/i

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
    const { container } = render(
      <InterpretationContent
        data={NARRATIVE_DATA}
        lang="fr"
        renderNarrativeReading={(reading, lang) => <NatalNarrativeReading reading={reading} lang={lang} />}
        renderReadingSources={(elements, lang) => <NatalReadingSources elements={elements} lang={lang} />}
      />,
    )

    expect(screen.getByRole("heading", { name: "Votre personnalite" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Ce que nous avons utilise/i })).toBeInTheDocument()
    expect(container.textContent).not.toMatch(FORBIDDEN_DOM_PATTERN)
    expect(container.textContent).not.toMatch(FORBIDDEN_PUBLIC_CONTROL_PATTERN)
    expect(container.innerHTML).not.toMatch(/SUN_TAURUS|ASPECT_|_H\d/i)
  })

  it("test_theme_natal_contract_is_only_public_generation_path", () => {
    const publicPreviewData: NatalInterpretationViewData = {
      ...NARRATIVE_DATA,
      schema_version: "theme_natal.preview.v1",
      use_case: "theme_natal_preview",
      narrative_natal_reading_v1: null,
      meta: { level: "short", use_case: "theme_natal_preview", persona_name: null },
      interpretation: {
        title: "Portrait astrologique",
        summary: "Resume public visible.",
        highlights: ["Point public preview"],
        sections: [
          {
            key: "theme-natal-preview-section",
            heading: "Section publique preview",
            content: "Contenu public theme natal visible.",
          },
        ],
        advice: [],
        evidence: [],
      },
    }

    const { container } = render(<InterpretationContent data={publicPreviewData} lang="fr" />)

    expect(screen.getByText("Resume public visible.")).toBeInTheDocument()
    expect(screen.getByText("Section publique preview")).toBeInTheDocument()
    expect(screen.getByText("Contenu public theme natal visible.")).toBeInTheDocument()
    expect(container.querySelector(".ni-evidence-tags")).toBeNull()
    expect(screen.queryByText(/Lecture complète à régénérer/i)).not.toBeInTheDocument()
  })

  it("affiche le resume public preview sans message de regeneration obsolete", () => {
    const publicPreviewData: NatalInterpretationViewData = {
      ...NARRATIVE_DATA,
      schema_version: "theme_natal.preview.v1",
      use_case: "theme_natal_preview",
      narrative_natal_reading_v1: null,
      meta: { level: "short", use_case: "theme_natal_preview", persona_name: null },
      interpretation: {
        title: "Portrait astrologique",
        summary: "Resume preview visible.",
        highlights: [],
        sections: [],
        advice: [],
        evidence: [],
      },
    }

    render(<InterpretationContent data={publicPreviewData} lang="fr" />)

    expect(screen.getByText("Resume preview visible.")).toBeInTheDocument()
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

  it("affiche les preuves Basic V2 sans identifiants ni champs techniques", () => {
    const basicData: NatalInterpretationViewData = {
      ...NARRATIVE_DATA,
      narrative_natal_reading_v1: null,
      meta: { level: "complete", use_case: "natal_interpretation", persona_name: null },
      interpretation: {
        title: "Ancien titre",
        summary: "Ancien resume masque par Basic V2.",
        highlights: [],
        sections: [],
        advice: [],
        evidence: ["SUN_TAURUS_H10"],
      },
      basic_natal_interpretation_v2: {
        locale: "fr-FR",
        level: "basic",
        engine_version: "basic-natal-reading-v1",
        schema_version: "basic_natal_interpretation_v2",
        taxonomy_version: "basic-natal-theme-taxonomy-v1",
        salience_version: "basic-natal-salience-v1",
        prompt_version: "basic-natal-draft-prompt-v1",
        validator_version: "basic-natal-validator-v1",
        interpretation: {
          title: "Lecture Basic publique",
          introduction: "Introduction publique sans trace technique.",
          themes: [
            {
              title: "Vie intérieure",
              narrative: "Narration publique centrée sur la cohérence personnelle.",
              public_evidence: [
                {
                  source_id: "moon-cancer",
                  label: "Lune en Cancer",
                  meaning: "Votre sensibilite soutient les liens.",
                },
              ],
            },
            {
              title: "Vie relationnelle",
              narrative: "Narration publique centrée sur les liens.",
              public_evidence: [
                {
                  source_id: "moon-cancer",
                  label: "Lune en Cancer",
                  meaning: "Votre sensibilite soutient les liens.",
                },
              ],
            },
          ],
          conclusion: "Conclusion publique sans score ni identifiant brut.",
          public_evidence: [
            { label: "Soleil en Taureau", meaning: "Votre expression cherche la stabilite." },
          ],
        },
        public_evidence: [
          { label: "Ascendant Balance", meaning: "Votre presence cherche l'equilibre." },
          {
            source_id: "moon-cancer",
            label: "Lune en Cancer",
            meaning: "Votre sensibilite soutient les liens.",
          },
        ],
        limitations: ["Lecture symbolique."],
        disclaimers: [
          "Contenu de reflexion personnelle.",
          "Lecture symbolique.",
          "Cette interprétation astrologique est un contenu de réflexion personnelle, non scientifique et non prédictif.",
        ],
      },
    }

    const { container } = render(<InterpretationContent data={basicData} lang="fr" />)

    expect(screen.getByText("Lecture Basic publique")).toBeInTheDocument()
    expect(screen.getAllByText("Lune en Cancer")).toHaveLength(1)
    expect(screen.getByText("Votre sensibilite soutient les liens.")).toBeInTheDocument()
    expect(screen.getByText("Soleil en Taureau")).toBeInTheDocument()
    expect(screen.getByText("Votre expression cherche la stabilite.")).toBeInTheDocument()
    expect(screen.getByText("Ascendant Balance")).toBeInTheDocument()
    expect(screen.getByText("Votre presence cherche l'equilibre.")).toBeInTheDocument()
    expect(screen.getAllByText(/Ce que j’ai utilisé pour écrire cette interprétation/i)).toHaveLength(1)
    expect(screen.getAllByText(/Mentions légales/i)).toHaveLength(1)
    expect(screen.getAllByText("Lecture symbolique.")).toHaveLength(1)
    expect(within(container.querySelector(".ni-basic-theme-list")!).queryByText("Lune en Cancer")).not.toBeInTheDocument()
    expect(container.textContent).not.toMatch(FORBIDDEN_DOM_PATTERN)
    expect(container.textContent).not.toMatch(FORBIDDEN_BASIC_PUBLIC_LABEL_PATTERN)
    expect(container.textContent).not.toMatch(FORBIDDEN_PUBLIC_CONTROL_PATTERN)
    expect(container.innerHTML).not.toMatch(/SUN_TAURUS|ASPECT_|_H\d|ranking_score|weighted_score/i)
  })
})
