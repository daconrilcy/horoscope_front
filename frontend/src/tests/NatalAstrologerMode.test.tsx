// Tests du toggle mode astrologue et de son gate d'acces.
import { fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import { NatalAstrologerMode } from "../features/natal-chart/NatalAstrologerMode"
import type { FeatureEntitlementResponse } from "../api/billing"

function access(variantCode: string, granted = true): FeatureEntitlementResponse {
  return {
    feature_code: "natal_chart_long",
    granted,
    reason_code: granted ? "granted" : "upgrade_required",
    access_mode: "quota",
    variant_code: variantCode,
    usage_states: [],
  }
}

describe("NatalAstrologerMode", () => {
  it("masque le contenu technique par defaut puis l'affiche pour un acces premium", () => {
    render(
      <MemoryRouter>
        <NatalAstrologerMode access={access("multi_astrologer")}>
          <p>Panneau expert natal</p>
        </NatalAstrologerMode>
      </MemoryRouter>,
    )

    const toggle = screen.getByRole("button", { name: "Afficher les details techniques" })
    expect(toggle).toHaveAttribute("aria-expanded", "false")
    expect(screen.queryByText("Panneau expert natal")).not.toBeInTheDocument()

    fireEvent.click(toggle)

    expect(screen.getByRole("button", { name: "Masquer les details techniques" })).toHaveAttribute("aria-expanded", "true")
    expect(screen.getByText("Panneau expert natal")).toBeInTheDocument()
  })

  it("affiche un CTA upgrade sans fuite technique pour un acces free", () => {
    render(
      <MemoryRouter>
        <NatalAstrologerMode access={access("free_short")}>
          <p>Panneau expert natal</p>
        </NatalAstrologerMode>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Afficher les details techniques" }))

    expect(screen.getByText("Mode astrologue reserve")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Voir les offres" })).toHaveAttribute("href", "/settings/subscription")
    expect(screen.queryByText("Panneau expert natal")).not.toBeInTheDocument()
  })

  it("bloque le contenu technique quand l'acces est inconnu ou refuse", () => {
    const { rerender } = render(
      <MemoryRouter>
        <NatalAstrologerMode access={undefined}>
          <p>Panneau expert natal</p>
        </NatalAstrologerMode>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole("button", { name: "Afficher les details techniques" }))
    expect(screen.getByText("Mode astrologue reserve")).toBeInTheDocument()
    expect(screen.queryByText("Panneau expert natal")).not.toBeInTheDocument()

    rerender(
      <MemoryRouter>
        <NatalAstrologerMode access={access("multi_astrologer", false)}>
          <p>Panneau expert natal</p>
        </NatalAstrologerMode>
      </MemoryRouter>,
    )

    expect(screen.queryByText("Panneau expert natal")).not.toBeInTheDocument()
  })
})
