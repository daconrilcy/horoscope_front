import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { SubscriptionSettings } from "../pages/settings/SubscriptionSettings"

const mockUseBillingSubscription = vi.fn()
const mockUseStripeCheckoutSession = vi.fn()
const mockUseStripePortalSession = vi.fn()
const mockUseStripePortalSubscriptionUpdateSession = vi.fn()

// On utilise importActual pour que toStripePlanCode et fromStripePlanCode
// soient les vraies implémentations (non mockées), ce qui valide leur comportement réel.
vi.mock("@api/billing", async (importActual) => {
  const actual = await importActual<typeof import("@api/billing")>()
  return {
    ...actual,
    useBillingSubscription: () => mockUseBillingSubscription(),
    useStripeCheckoutSession: () => mockUseStripeCheckoutSession(),
    useStripePortalSession: () => mockUseStripePortalSession(),
    useStripePortalSubscriptionUpdateSession: () => mockUseStripePortalSubscriptionUpdateSession(),
  }
})

afterEach(() => {
  cleanup()
  mockUseBillingSubscription.mockReset()
  mockUseStripeCheckoutSession.mockReset()
  mockUseStripePortalSession.mockReset()
  mockUseStripePortalSubscriptionUpdateSession.mockReset()
  vi.restoreAllMocks()
})

describe("SubscriptionSettings", () => {
  it("appelle useStripeCheckoutSession avec le code canonique pour un utilisateur sans abonnement Stripe", () => {
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: { status: "inactive", subscription_status: null, plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    // Sélectionner le plan "Basic" (UI code: basic-entry)
    const basicCard = screen.getByText("Basic").closest('[role="button"]')!
    fireEvent.click(basicCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(mutate).toHaveBeenCalledWith(
      "basic", // code canonique Stripe, jamais "basic-entry"
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  it("n'envoie jamais basic-entry ou premium-unlimited à useStripeCheckoutSession — uniquement les codes canoniques", () => {
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: { status: "inactive", subscription_status: null, plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    const premiumCard = screen.getByText("Premium").closest('[role="button"]')!
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    const calledWith = mutate.mock.calls[0]?.[0]
    expect(calledWith).not.toBe("premium-unlimited")
    expect(calledWith).not.toBe("basic-entry")
    expect(["basic", "premium"]).toContain(calledWith)
  })

  it("appelle useStripePortalSubscriptionUpdateSession quand l'abonnement Stripe est actif et qu'on change de plan", () => {
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "active",
        subscription_status: "active",
        plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
        failure_reason: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate })

    render(<SubscriptionSettings />)

    const premiumCard = screen.getByText("Premium").closest('[role="button"]')!
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(mutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  // Fix HIGH-1 : l'API renvoie plan.code = "basic" (canonique), la carte "Basic" doit afficher le badge "Plan actuel"
  it("affiche correctement la carte Basic comme plan courant quand l'API renvoie le code canonique 'basic'", () => {
    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "active",
        subscription_status: "active",
        plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
        failure_reason: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    // La carte "Basic" doit être sélectionnée (aria-pressed=true) — elle est le plan courant
    const basicCard = screen.getByText("Basic").closest('[role="button"]')!
    expect(basicCard).toHaveAttribute("aria-pressed", "true")

    // Le bouton "Valider" doit être désactivé (aucun changement de plan)
    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    expect(validateButton).toBeDisabled()
  })

  // Fix HIGH-2 : un utilisateur past_due doit aller vers le Customer Portal (pas vers Checkout)
  it("appelle useStripePortalSession pour un utilisateur past_due (pas de nouveau Checkout)", () => {
    const portalMutate = vi.fn()
    const checkoutMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "inactive", // DTO public simplifié — past_due = inactive
        subscription_status: "past_due", // champ Stripe brut — décision réelle
        plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
        failure_reason: "card_declined",
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: checkoutMutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: portalMutate })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    // L'utilisateur sélectionne Premium (changement de plan)
    const premiumCard = screen.getByText("Premium").closest('[role="button"]')!
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    // Doit aller vers le portail (régulariser), pas vers un nouveau Checkout
    expect(portalMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
    expect(checkoutMutate).not.toHaveBeenCalled()
  })
})
