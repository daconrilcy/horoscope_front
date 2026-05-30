import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { NatalNarrativeReading } from "../features/natal-chart/NatalNarrativeReading"
import { NatalReadingSources } from "../features/natal-chart/NatalReadingSources"

const READING = {
  contract_version: "narrative_natal_reading_v1" as const,
  editorial_profile: "premium" as const,
  chapters: [
    {
      key: "personality" as const,
      title: "Votre personnalite",
      narrative:
        "Paragraphe narratif suffisamment long pour le test de rendu public sans fuite technique.",
      key_points: [],
    },
    {
      key: "emotional_world" as const,
      title: "Votre monde emotionnel",
      narrative: "Deuxieme chapitre narratif lisible pour l utilisateur final.",
      key_points: [],
    },
    {
      key: "relationships" as const,
      title: "Vos relations",
      narrative: "Troisieme chapitre narratif lisible pour l utilisateur final.",
      key_points: [],
    },
    {
      key: "vocation" as const,
      title: "Votre vocation",
      narrative: "Quatrieme chapitre narratif lisible pour l utilisateur final.",
      key_points: [],
    },
    {
      key: "evolution_path" as const,
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
}

describe("NatalNarrativeReading", () => {
  it("affiche les cinq chapitres sans identifiants techniques", () => {
    const { container } = render(<NatalNarrativeReading reading={READING} lang="fr" />)
    expect(screen.getByRole("heading", { name: "Votre personnalite" })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Votre chemin d evolution" })).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/visibility_expression|audit_input|condition_axis:/i)
  })
})

describe("NatalReadingSources", () => {
  it("n expose pas de raw evidence id dans le DOM", () => {
    const { container } = render(
      <NatalReadingSources elements={READING.used_astrological_elements} lang="fr" />,
    )
    expect(screen.getByRole("button", { name: /Ce que nous avons utilise/i })).toHaveAttribute(
      "aria-expanded",
      "false",
    )
    expect(container.textContent).not.toMatch(/SUN_TAURUS|interpretive_signal/i)
  })

  it("bascule le panneau sources au clic clavier", () => {
    render(<NatalReadingSources elements={READING.used_astrological_elements} lang="fr" />)
    const toggle = screen.getByRole("button", { name: /Ce que nous avons utilise/i })
    expect(toggle).toHaveAttribute("aria-expanded", "false")
    fireEvent.click(toggle)
    expect(toggle).toHaveAttribute("aria-expanded", "true")
    expect(screen.getByText("Soleil en Taureau")).toBeVisible()
  })
})
