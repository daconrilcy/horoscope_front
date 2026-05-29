// Tests du top aspects publics sans affichage d'orbes techniques.
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { NatalMajorAspects } from "../features/natal-chart/NatalMajorAspects"

describe("NatalMajorAspects", () => {
  it("relie le ranking public aux aspects calcules et limite a dix entrees", () => {
    render(
      <NatalMajorAspects
        dominantAspects={Array.from({ length: 12 }, (_, index) => ({
          code: "trine",
          rank: index + 1,
          score: 0.9 - index * 0.01,
        }))}
        aspects={Array.from({ length: 12 }, (_, index) => ({
          aspect_code: "TRINE",
          planet_a: `PLANET_${index}`,
          planet_b: `PLANET_${index + 12}`,
          angle: 120,
          orb: 1,
        }))}
        translatePlanet={(code) => code}
        translateAspect={() => "Trigone"}
      />,
    )

    expect(screen.getAllByRole("heading", { name: /Trigone/ })).toHaveLength(10)
    expect(screen.getAllByText("Impact majeur")).toHaveLength(3)
    expect(screen.queryByText(/0\.9/)).not.toBeInTheDocument()
    expect(screen.queryByText(/orbe/i)).not.toBeInTheDocument()
  })

  it("accepte encore un payload enrichi deja denormalise", () => {
    render(
      <NatalMajorAspects
        dominantAspects={[
          {
            aspect_code: "SQUARE",
            planet_a: "SATURN",
            planet_b: "MOON",
            rank: 1,
          },
        ]}
        aspects={[]}
        translatePlanet={(code) => code}
        translateAspect={() => "Carre"}
      />,
    )

    expect(screen.getByRole("heading", { name: /Carre/ })).toBeInTheDocument()
  })
})
