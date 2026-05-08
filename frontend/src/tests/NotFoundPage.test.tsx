import { cleanup, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it } from "vitest"

import { NotFoundPage } from "../pages/NotFoundPage"

describe("NotFoundPage", () => {
  afterEach(cleanup)

  it("renders the dashboard return action", () => {
    render(
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole("heading", { name: "Page non trouvée" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Retour au tableau de bord" })).toBeInTheDocument()
  })
})
