import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import BillingSuccessPage from "../pages/billing/BillingSuccessPage"
import { BrowserRouter } from "react-router-dom"

const mockNavigate = vi.fn()
const mockSearchParams = new URLSearchParams()
const mockRefetch = vi.fn()
const mockUseBillingSubscription = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: () => [mockSearchParams],
  }
})

vi.mock("../i18n", () => ({
  useTranslation: () => ({
    success: {
      trialStarted: "Essai gratuit demarre",
      trialStartedMessage: "Votre essai gratuit a bien demarre.",
      activationPending: "Activation en cours de confirmation",
      activationPendingMessage: "Votre souscription est en attente de confirmation.",
      subscriptionActive: "Abonnement active",
      subscriptionActiveMessage: "Votre abonnement est maintenant actif.",
      backToDashboard: "Retour au tableau de bord",
      viewSubscription: "Voir mon abonnement",
      waitingForWebhook: "Paiement en cours de confirmation...",
      waitingForWebhookMessage: "Nous attendons encore la reconciliation Stripe.",
      billingStateUnavailable: "Verification de l'etat billing impossible",
      billingStateUnavailableMessage:
        "Nous n'avons pas pu recuperer l'etat de votre abonnement pour le moment.",
      retryStatusCheck: "Reessayer",
      pendingStateTitle: "Statut billing en attente de synchronisation",
      pendingStateMessage:
        "Le backend n'a pas encore confirme un etat exploitable. Reessayez dans quelques instants.",
    },
  }),
}))

vi.mock("../api/billing", () => ({
  useBillingSubscription: () => mockUseBillingSubscription(),
}))

describe("BillingSuccessPage", () => {
  beforeEach(() => {
    mockSearchParams.delete("is_trial")
    mockSearchParams.delete("session_id")
    mockNavigate.mockReset()
    mockRefetch.mockReset()
    mockUseBillingSubscription.mockReset()
  })

  it("renders loading state initially", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: null,
      isLoading: true,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Paiement en cours de confirmation...")).toBeInTheDocument()
    expect(screen.getByText("Nous attendons encore la reconciliation Stripe.")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Reessayer" })).not.toBeInTheDocument()
  })

  it("renders an explicit error state and keeps navigation CTAs", async () => {
    const user = userEvent.setup()
    mockUseBillingSubscription.mockReturnValue({
      data: null,
      isLoading: false,
      isError: true,
      error: new Error("backend unavailable"),
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Verification de l'etat billing impossible")).toBeInTheDocument()
    expect(
      screen.getByText("Nous n'avons pas pu recuperer l'etat de votre abonnement pour le moment."),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Retour au tableau de bord" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Voir mon abonnement" })).toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "Reessayer" }))

    expect(mockRefetch).toHaveBeenCalledTimes(1)
  })

  it("renders neutral pending state when API succeeds without usable subscription status", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: null, plan: null },
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Statut billing en attente de synchronisation")).toBeInTheDocument()
    expect(
      screen.getByText("Le backend n'a pas encore confirme un etat exploitable. Reessayez dans quelques instants."),
    ).toBeInTheDocument()
  })

  it("renders neutral pending state when the subscription status is not mapped", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "past_due", plan: null },
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Statut billing en attente de synchronisation")).toBeInTheDocument()
  })

  it("renders trial success message when status is trialing", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "trialing" },
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Essai gratuit demarre")).toBeInTheDocument()
    expect(screen.getByText("Votre essai gratuit a bien demarre.")).toBeInTheDocument()
  })

  it("renders active success message when status is active", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "active", subscription_status: "active" },
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Abonnement active")).toBeInTheDocument()
    expect(screen.getByText("Votre abonnement est maintenant actif.")).toBeInTheDocument()
  })

  it("renders pending activation message when status is incomplete", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "incomplete" },
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Activation en cours de confirmation")).toBeInTheDocument()
    expect(screen.getByText("Votre souscription est en attente de confirmation.")).toBeInTheDocument()
  })

  it("ignores the URL flag and trusts the API status", () => {
    mockSearchParams.set("is_trial", "true")
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "incomplete" },
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>,
    )

    expect(screen.getByText("Activation en cours de confirmation")).toBeInTheDocument()
    expect(screen.queryByText("Essai gratuit demarre")).not.toBeInTheDocument()
  })
})
