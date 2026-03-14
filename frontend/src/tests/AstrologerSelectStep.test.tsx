import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { AstrologerSelectStep } from "../features/consultations/components/AstrologerSelectStep"

const mockUseAstrologers = vi.fn()

vi.mock("../api/astrologers", () => ({
  useAstrologers: () => mockUseAstrologers(),
}))

describe("AstrologerSelectStep", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    mockUseAstrologers.mockReset()
  })

  afterEach(() => {
    cleanup()
    localStorage.clear()
  })

  it("affiche les astrologues quand la liste est disponible", () => {
    mockUseAstrologers.mockReturnValue({
      data: [
        {
          id: "astro-1",
          name: "Luna",
          avatar_url: null,
          specialties: ["Relations"],
          style: "Douce",
          bio_short: "Bio",
        },
      ],
      isPending: false,
      error: null,
      refetch: vi.fn(),
      isFetching: false,
    })

    render(<AstrologerSelectStep selectedId="auto" onSelect={vi.fn()} />)

    expect(screen.getByText("Luna")).toBeInTheDocument()
    expect(screen.queryByText("Réessayer")).not.toBeInTheDocument()
  })

  it("propose un retry quand le chargement échoue et qu'aucune liste n'est disponible", () => {
    const refetch = vi.fn()
    mockUseAstrologers.mockReturnValue({
      data: [],
      isPending: false,
      error: new Error("network"),
      refetch,
      isFetching: false,
    })

    render(<AstrologerSelectStep selectedId="auto" onSelect={vi.fn()} />)

    expect(screen.getByText("Impossible de charger les astrologues.")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Réessayer" }))
    expect(refetch).toHaveBeenCalled()
  })
})
