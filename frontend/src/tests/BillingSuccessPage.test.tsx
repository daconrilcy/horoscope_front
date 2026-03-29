import { render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import BillingSuccessPage from "../pages/billing/BillingSuccessPage"
import { BrowserRouter } from "react-router-dom"

// Mock des hooks de react-router-dom
const mockSearchParams = new URLSearchParams()
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useSearchParams: () => [mockSearchParams],
  }
})

// Mock de useTranslation
vi.mock("../i18n", () => ({
  useTranslation: () => ({
    success: {
      trialStarted: "Essai gratuit démarré",
      trialStartedMessage: "Votre essai gratuit a bien démarré.",
      activationPending: "Activation en cours de confirmation",
      activationPendingMessage: "Votre souscription est en attente de confirmation.",
      subscriptionActive: "Abonnement activé",
      subscriptionActiveMessage: "Votre abonnement est maintenant actif.",
      backToDashboard: "Retour au tableau de bord",
      viewSubscription: "Voir mon abonnement",
      waitingForWebhook: "Paiement en cours de confirmation...",
      waitingForWebhookMessage: "Nous attendons encore la réconciliation Stripe.",
    },
  }),
}))

// Mock de useBillingSubscription
const mockRefetch = vi.fn()
const mockUseBillingSubscription = vi.fn()
vi.mock("../api/billing", () => ({
  useBillingSubscription: () => mockUseBillingSubscription(),
}))

describe("BillingSuccessPage", () => {
  beforeEach(() => {
    mockSearchParams.delete("is_trial")
    mockSearchParams.delete("session_id")
    mockRefetch.mockReset()
    mockUseBillingSubscription.mockReset()
  })

  it("renders loading state initially", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: null,
      isLoading: true,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Paiement en cours de confirmation...")).toBeInTheDocument()
    expect(screen.getByText("Nous attendons encore la réconciliation Stripe.")).toBeInTheDocument()
  })

  it("renders trial success message when status is trialing", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "trialing" },
      isLoading: false,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Essai gratuit démarré")).toBeInTheDocument()
    expect(screen.getByText("Votre essai gratuit a bien démarré.")).toBeInTheDocument()
  })

  it("renders active success message when status is active", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "active", subscription_status: "active" },
      isLoading: false,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Abonnement activé")).toBeInTheDocument()
    expect(screen.getByText("Votre abonnement est maintenant actif.")).toBeInTheDocument()
  })

  it("renders pending message when status is incomplete", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "incomplete" },
      isLoading: false,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Activation en cours de confirmation")).toBeInTheDocument()
    expect(screen.getByText("Votre souscription est en attente de confirmation.")).toBeInTheDocument()
  })

  it("ignores the URL flag and trusts the API status", () => {
    mockSearchParams.set("is_trial", "true")
    mockUseBillingSubscription.mockReturnValue({
      data: { status: "inactive", subscription_status: "incomplete" },
      isLoading: false,
      refetch: mockRefetch,
    })

    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )

    expect(screen.getByText("Activation en cours de confirmation")).toBeInTheDocument()
    expect(screen.queryByText("Essai gratuit démarré")).not.toBeInTheDocument()
  })
})
