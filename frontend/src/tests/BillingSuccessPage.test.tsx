import { render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
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
      title: "Paiement réussi !",
      message: "Votre paiement est en cours de traitement.",
      trialTitle: "Essai gratuit activé !",
      trialMessage: "Votre période d'essai vient de commencer.",
      trialStarted: "Essai gratuit démarré",
      activationPending: "Activation en cours de confirmation",
      subscriptionActive: "Abonnement activé",
      backToDashboard: "Retour au tableau de bord",
      viewSubscription: "Voir mon abonnement",
      waitingForWebhook: "Paiement en cours de confirmation...",
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
  })

  it("renders trial success message when status is trialing", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { subscription_status: "trialing" },
      isLoading: false,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Essai gratuit activé !")).toBeInTheDocument()
    expect(screen.getByText("Votre période d'essai vient de commencer.")).toBeInTheDocument()
  })

  it("renders active success message when status is active", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { subscription_status: "active" },
      isLoading: false,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Abonnement activé")).toBeInTheDocument()
  })

  it("renders pending message when status is incomplete", () => {
    mockUseBillingSubscription.mockReturnValue({
      data: { subscription_status: "incomplete" },
      isLoading: false,
      refetch: mockRefetch,
    })
    
    render(
      <BrowserRouter>
        <BillingSuccessPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText("Activation en cours de confirmation")).toBeInTheDocument()
  })
})
