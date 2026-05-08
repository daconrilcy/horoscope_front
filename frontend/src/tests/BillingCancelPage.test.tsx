import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { BrowserRouter } from "react-router-dom"

import BillingCancelPage from "../pages/billing/BillingCancelPage"

const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../i18n", () => ({
  useTranslation: () => ({
    cancel: {
      title: "Paiement annule",
      message: "Votre paiement a ete annule.",
      backToSettings: "Retour aux parametres",
      tryAgain: "Reessayer",
    },
  }),
}))

describe("BillingCancelPage", () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  it("renvoie l'utilisateur vers la page abonnement pour reessayer", async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <BillingCancelPage />
      </BrowserRouter>,
    )

    await user.click(screen.getByRole("button", { name: "Reessayer" }))

    expect(mockNavigate).toHaveBeenCalledWith("/settings/subscription")
  })

  it("renvoie l'utilisateur vers la page abonnement depuis le retour aux parametres", async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter>
        <BillingCancelPage />
      </BrowserRouter>,
    )

    await user.click(
      screen.getByRole("button", { name: "Retour aux parametres" }),
    )

    expect(mockNavigate).toHaveBeenCalledWith("/settings/subscription")
  })
})
