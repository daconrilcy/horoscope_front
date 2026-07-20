// Vérifie le parcours débutant, l'accessibilité et les traductions du guide natal.
import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"

import { NatalChartGuide } from "../components/NatalChartGuide"
import type { AstrologyLang } from "../i18n/astrology"

describe("NatalChartGuide", () => {
  it("reste replie au chargement puis expose le parcours debutant dans le bon ordre", async () => {
    const user = userEvent.setup()
    const { container } = render(<NatalChartGuide lang="fr" partialReading={false} />)
    const toggle = screen.getByRole("button", { name: "Lire le guide" })
    const content = container.querySelector(".natal-chart-guide__content")

    expect(toggle).toHaveAttribute("aria-expanded", "false")
    expect(toggle).toHaveAttribute("aria-controls", content?.id)
    expect(content).not.toBeVisible()

    await user.click(toggle)

    expect(toggle).toHaveAttribute("aria-expanded", "true")
    expect(toggle).toHaveTextContent("Réduire le guide")
    expect(content).toBeVisible()
    expect(screen.getAllByRole("heading", { level: 4 }).slice(0, 4).map((heading) => heading.textContent)).toEqual([
      "La planète",
      "Le signe",
      "La maison",
      "L'aspect",
    ])

    const path = screen.getByRole("heading", { name: "Ton parcours de lecture" }).closest("section")
    expect(path).not.toBeNull()
    expect(within(path!).getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      expect.stringContaining("Lis la synthèse"),
      expect.stringContaining("Repère Soleil, Lune et Ascendant"),
      expect.stringContaining("Choisis un chapitre"),
      expect.stringContaining("Regarde ses bases astrologiques"),
    ])
  })

  it("explique les notions utilisees par les lectures sans presenter les tensions comme negatives", async () => {
    const user = userEvent.setup()
    render(<NatalChartGuide lang="fr" partialReading={false} />)

    await user.click(screen.getByRole("button", { name: "Lire le guide" }))

    expect(screen.getByRole("heading", { name: "Dominantes et axes" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Le maître d'une maison" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Cœur, appui et nuance" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Que veut dire le niveau de confiance ?" })).toBeVisible()
    expect(screen.getByText(/une tension peut devenir une force/i)).toBeVisible()
    expect(screen.getByText(/pas une étiquette ni une prédiction certaine/i)).toBeVisible()
  })

  it("affiche les limites des donnees uniquement pour une lecture partielle", async () => {
    const user = userEvent.setup()
    const { rerender } = render(<NatalChartGuide lang="fr" partialReading={false} />)
    await user.click(screen.getByRole("button", { name: "Lire le guide" }))

    expect(screen.queryByRole("note")).not.toBeInTheDocument()

    rerender(<NatalChartGuide lang="fr" partialReading />)

    expect(screen.getByRole("note")).toHaveTextContent(/l'heure de naissance manque/)
    expect(screen.getByRole("note")).toHaveTextContent(/données sont partielles ou peu précises/)
    expect(screen.getByRole("note")).toHaveTextContent(/Ascendant, les maisons, la Lune et certains aspects/)
  })

  it.each([
    [
      "en",
      "Read the guide",
      "Collapse the guide",
      ["The 4-key formula", "Dominants and axes", "A house ruler", "What does confidence mean?", "Mini glossary"],
      "When the birth time is missing",
    ],
    [
      "es",
      "Leer la guía",
      "Cerrar la guía",
      [
        "La fórmula de las 4 claves",
        "Dominantes y ejes",
        "El regente de una casa",
        "¿Qué significa el nivel de confianza?",
        "Mini glosario",
      ],
      "Cuando falta la hora de nacimiento",
    ],
  ] as const)(
    "traduit tout le parcours et les controles en %s",
    async (lang, openLabel, closeLabel, expectedHeadings, missingTimeCopy) => {
      const user = userEvent.setup()
      render(<NatalChartGuide lang={lang} partialReading />)
      const toggle = screen.getByRole("button", { name: openLabel })

      await user.click(toggle)

      expect(toggle).toHaveTextContent(closeLabel)
      for (const heading of expectedHeadings) {
        expect(screen.getByRole("heading", { name: heading })).toBeVisible()
      }
      expect(screen.getByRole("note")).toHaveTextContent(missingTimeCopy)
      expect(screen.queryByRole("heading", { name: "Le maître d'une maison" })).not.toBeInTheDocument()
    },
  )

  it("utilise le francais comme fallback pour une langue runtime inconnue", () => {
    render(<NatalChartGuide lang={"pt" as AstrologyLang} partialReading={false} />)

    expect(screen.getByRole("heading", { name: "Comment lire ton thème natal" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Lire le guide" })).toBeInTheDocument()
  })
})
