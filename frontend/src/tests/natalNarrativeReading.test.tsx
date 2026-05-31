// Garde de lecture narrative: les chapitres publics restent des accordeons accessibles.
import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
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
        "Paragraphe narratif suffisamment long pour le test de rendu public sans fuite technique. Il contient une suite de phrases qui ne doit pas etre dupliquee dans l apercu replie.",
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
    const chapterToggles = screen.getAllByRole("button").filter((button) =>
      button.classList.contains("natal-narrative-reading__toggle"),
    )

    expect(chapterToggles).toHaveLength(5)
    expect(screen.getByRole("button", { name: /Votre personnalite/i })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Votre chemin d evolution/i })).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/visibility_expression|audit_input|condition_axis:/i)
  })

  it("ouvre le premier chapitre par defaut et replie les autres", () => {
    render(<NatalNarrativeReading reading={READING} lang="fr" />)
    const firstToggle = screen.getByRole("button", { name: /Votre personnalite/i })
    const secondToggle = screen.getByRole("button", { name: /Votre monde emotionnel/i })
    expect(firstToggle).toHaveAttribute("aria-expanded", "true")
    expect(secondToggle).toHaveAttribute("aria-expanded", "false")
    expect(screen.getByText(READING.chapters[0].narrative)).toBeVisible()
  })

  it("bascule un chapitre au clic et expose aria-controls", () => {
    render(<NatalNarrativeReading reading={READING} lang="fr" />)
    const secondToggle = screen.getByRole("button", { name: /Votre monde emotionnel/i })
    const panelId = secondToggle.getAttribute("aria-controls")
    expect(panelId).toBeTruthy()
    expect(document.getElementById(panelId!)).toHaveAttribute("aria-labelledby", secondToggle.id)
    fireEvent.click(secondToggle)
    expect(secondToggle).toHaveAttribute("aria-expanded", "true")
    expect(document.getElementById(panelId!)).toBeVisible()
  })

  it("bascule un chapitre au clavier comme un bouton natif", async () => {
    const user = userEvent.setup()
    render(<NatalNarrativeReading reading={READING} lang="fr" />)
    const secondToggle = screen.getByRole("button", { name: /Votre monde emotionnel/i })

    secondToggle.focus()
    await user.keyboard("{Enter}")
    expect(secondToggle).toHaveAttribute("aria-expanded", "true")

    await user.keyboard(" ")
    expect(secondToggle).toHaveAttribute("aria-expanded", "false")
  })

  it("affiche un apercu court et unique seulement pour les chapitres replies", () => {
    render(<NatalNarrativeReading reading={READING} lang="fr" />)
    const firstToggle = screen.getByRole("button", { name: /Votre personnalite/i })
    const secondToggle = screen.getByRole("button", { name: /Votre monde emotionnel/i })

    expect(firstToggle).not.toHaveTextContent("ne doit pas etre dupliquee")
    expect(secondToggle).toHaveTextContent("Deuxieme chapitre narratif lisible")
    expect(secondToggle).not.toHaveTextContent(READING.chapters[0].narrative)
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
