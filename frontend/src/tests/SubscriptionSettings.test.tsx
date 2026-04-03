import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { BillingApiError } from "../api/billing"
import { SubscriptionSettings } from "../pages/settings/SubscriptionSettings"

const mockUseBillingSubscription = vi.fn()
const mockUseBillingPlans = vi.fn()
const mockUseStripeCheckoutSession = vi.fn()
const mockUseStripePortalSession = vi.fn()
const mockUseStripePortalSubscriptionCancelSession = vi.fn()
const mockUseStripePortalSubscriptionUpdateSession = vi.fn()
const mockUseStripeSubscriptionReactivate = vi.fn()
const mockUseStripeSubscriptionUpgrade = vi.fn()

vi.mock("@api/billing", async (importActual) => {
  const actual = await importActual<typeof import("@api/billing")>()
  return {
    ...actual,
    useBillingSubscription: () => mockUseBillingSubscription(),
    useBillingPlans: () => mockUseBillingPlans(),
    useStripeCheckoutSession: () => mockUseStripeCheckoutSession(),
    useStripePortalSession: () => mockUseStripePortalSession(),
    useStripePortalSubscriptionCancelSession: () => mockUseStripePortalSubscriptionCancelSession(),
    useStripePortalSubscriptionUpdateSession: () => mockUseStripePortalSubscriptionUpdateSession(),
    useStripeSubscriptionReactivate: () => mockUseStripeSubscriptionReactivate(),
    useStripeSubscriptionUpgrade: () =>
      mockUseStripeSubscriptionUpgrade() ?? { isPending: false, mutate: vi.fn() },
  }
})

afterEach(() => {
  cleanup()
  mockUseBillingSubscription.mockReset()
  mockUseBillingPlans.mockReset()
  mockUseStripeCheckoutSession.mockReset()
  mockUseStripePortalSession.mockReset()
  mockUseStripePortalSubscriptionCancelSession.mockReset()
  mockUseStripePortalSubscriptionUpdateSession.mockReset()
  mockUseStripeSubscriptionReactivate.mockReset()
  mockUseStripeSubscriptionUpgrade.mockReset()
  localStorage.clear()
  vi.restoreAllMocks()
})

function getPlanCard(label: "Basic" | "Premium") {
  const cards = screen.getAllByRole("button").filter((element) =>
    element.className.includes("subscription-plan-card"),
  )
  const card = cards.find((element) => element.textContent?.includes(label))
  if (!card) {
    throw new Error(`Plan card not found for ${label}`)
  }
  return card
}

describe("SubscriptionSettings", () => {
  const setupCatalogMock = () => {
    mockUseBillingPlans.mockReturnValue({
      isLoading: false,
      data: [
        { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
        { code: "premium", display_name: "Premium", monthly_price_cents: 2900, currency: "EUR", daily_message_limit: 1000, is_active: true },
      ],
    })
  }

  it("appelle useStripeCheckoutSession avec le code canonique pour un utilisateur sans abonnement Stripe", () => {
    setupCatalogMock()
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: { status: "inactive", subscription_status: null, plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    // Sélectionner le plan "Basic" (UI code: basic)
    const basicCard = getPlanCard("Basic")
    fireEvent.click(basicCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(mutate).toHaveBeenCalledWith(
      "basic", // code canonique Stripe
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  it("affiche un résumé de statut avec plan actif, expérience, renouvellement et prochaine échéance", () => {
    setupCatalogMock()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "active",
        subscription_status: "active",
        plan: {
          code: "premium",
          display_name: "Premium",
          monthly_price_cents: 2900,
          currency: "EUR",
          daily_message_limit: 1000,
          is_active: true,
        },
        current_period_end: "2026-04-30T22:00:00Z",
        failure_reason: null,
      },
      refetch: vi.fn(),
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    expect(screen.getByText(/Résumé de l'abonnement|Subscription snapshot/i)).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Premium", level: 3 })).toBeInTheDocument()
    expect(screen.getAllByText(/Pour une expérience complète|For a complete experience/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Consultations thématiques incluses|Thematic consultations included/i).length).toBeGreaterThan(0)
    expect(screen.getByText(/Renouvellement automatique|Auto-renew enabled/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Voir les formules|Browse plans/i })).toBeInTheDocument()
    expect(screen.queryByText(/tokens/i)).not.toBeInTheDocument()
  })

  it("n'envoie jamais basic-entry ou premium-unlimited à useStripeCheckoutSession — uniquement les codes canoniques", () => {
    setupCatalogMock()
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: { status: "inactive", subscription_status: null, plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    const premiumCard = getPlanCard("Premium")
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    const calledWith = mutate.mock.calls[0]?.[0]
    expect(calledWith).not.toBe("premium-unlimited")
    expect(calledWith).not.toBe("basic-entry")
    expect(["basic", "premium"]).toContain(calledWith)
  })

  it("repasse par un nouveau Checkout quand l'ancien abonnement Stripe est canceled et qu'aucun plan n'est actif", () => {
    setupCatalogMock()
    const checkoutMutate = vi.fn()
    const portalMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "inactive",
        subscription_status: "canceled",
        plan: null,
        failure_reason: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: checkoutMutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: portalMutate })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    const basicCard = getPlanCard("Basic")
    fireEvent.click(basicCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(checkoutMutate).toHaveBeenCalledWith(
      "basic",
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
    expect(portalMutate).not.toHaveBeenCalled()
  })

  it("utilise le flow d'upgrade immédiat quand l'abonnement actif passe de basic à premium", () => {
    setupCatalogMock()
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
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionUpgrade.mockReturnValue({ isPending: false, mutate })

    render(<SubscriptionSettings />)

    const premiumCard = getPlanCard("Premium")
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)
    fireEvent.click(screen.getByRole("button", { name: /continuer vers stripe|continue to stripe/i }))

    expect(mutate).toHaveBeenCalledWith(
      "premium",
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  it("affiche un retour visible et bloque la double soumission quand l'upgrade est payé automatiquement", () => {
    setupCatalogMock()
    const refetch = vi.fn()
    const mutate = vi.fn((_plan, options) => {
      options?.onSuccess?.({
        checkout_url: null,
        invoice_status: "paid",
        amount_due_cents: 2000,
        currency: "eur",
      })
    })

    let subscriptionData = {
      status: "active",
      subscription_status: "active",
      plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
      failure_reason: null,
      current_quota: null,
    }

    mockUseBillingSubscription.mockImplementation(() => ({
      isLoading: false,
      data: subscriptionData,
      refetch,
    }))
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionUpgrade.mockReturnValue({ isPending: false, mutate })

    const { rerender } = render(<SubscriptionSettings />)

    const premiumCard = getPlanCard("Premium")
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)
    expect(
      screen.getByText(/facturation intermédiaire|intermediate charge/i),
    ).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: /continuer vers stripe|continue to stripe/i }))

    expect(mutate).toHaveBeenCalledTimes(1)
    expect(refetch).toHaveBeenCalled()
    expect(
      screen.getByText(/Paiement accepté\. Activation du plan Premium en cours|Payment accepted\. Activating the Premium plan/i),
    ).toBeInTheDocument()
    expect(validateButton).toBeDisabled()

    fireEvent.click(validateButton)
    expect(mutate).toHaveBeenCalledTimes(1)

    subscriptionData = {
      ...subscriptionData,
      plan: { code: "premium", display_name: "Premium", monthly_price_cents: 2900, currency: "EUR", daily_message_limit: 1000, is_active: true },
    }

    rerender(<SubscriptionSettings />)

    expect(
      screen.getByText(/Le plan Premium est maintenant actif|The Premium plan is now active/i),
    ).toBeInTheDocument()
  })

  it("redirige vers Checkout Stripe hébergé quand un paiement additionnel est requis", () => {
    setupCatalogMock()
    const mutate = vi.fn((_plan, options) => {
      options?.onSuccess?.({
        checkout_url: "https://checkout.stripe.com/pay/cs_123",
        invoice_status: "open",
        amount_due_cents: 1934,
        currency: "eur",
      })
    })

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
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionUpgrade.mockReturnValue({ isPending: false, mutate })

    render(<SubscriptionSettings />)

    const premiumCard = getPlanCard("Premium")
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)
    fireEvent.click(screen.getByRole("button", { name: /continuer vers stripe|continue to stripe/i }))

    expect(mutate).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem("billing_upgrade_pending_payment")).toBeNull()
  })

  it("conserve le portail subscription_update pour un downgrade actif premium vers basic", () => {
    setupCatalogMock()
    const updateMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "active",
        subscription_status: "active",
        plan: { code: "premium", display_name: "Premium", monthly_price_cents: 2900, currency: "EUR", daily_message_limit: 1000, is_active: true },
        failure_reason: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: updateMutate })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    const basicCard = getPlanCard("Basic")
    fireEvent.click(basicCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(updateMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  it("affiche correctement la carte Basic comme plan courant quand l'API renvoie le code canonique 'basic'", () => {
    setupCatalogMock()
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
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    // La carte "Basic" doit être sélectionnée (aria-pressed=true) — elle est le plan courant
    const basicCard = getPlanCard("Basic")
    expect(basicCard).toHaveAttribute("aria-pressed", "true")

    // Le bouton "Valider" doit être désactivé (aucun changement de plan)
    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    expect(validateButton).toBeDisabled()
  })

  it("appelle useStripePortalSession pour un utilisateur past_due (pas de nouveau Checkout)", () => {
    setupCatalogMock()
    const portalMutate = vi.fn()
    const checkoutMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "inactive",
        subscription_status: "past_due",
        plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
        failure_reason: "card_declined",
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: checkoutMutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: portalMutate })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    // L'utilisateur sélectionne Premium (changement de plan)
    const premiumCard = getPlanCard("Premium")
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

  it("fallback vers le portal générique si subscription_update est désactivé dans Stripe Portal", () => {
    setupCatalogMock()
    const portalMutate = vi.fn()
    const updateMutate = vi.fn((_payload, options) => {
      options?.onError?.(
        new BillingApiError(
          "stripe_portal_subscription_update_disabled",
          "subscription update disabled",
          422,
          {},
        ),
      )
    })

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "active",
        subscription_status: "active",
        plan: { code: "premium", display_name: "Premium", monthly_price_cents: 2900, currency: "EUR", daily_message_limit: 1000, is_active: true },
        failure_reason: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: portalMutate })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: updateMutate })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    const basicCard = getPlanCard("Basic")
    fireEvent.click(basicCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(updateMutate).toHaveBeenCalled()
    expect(portalMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  it("bloque l'upgrade Premium pendant un trial Basic et n'appelle aucun endpoint Stripe", () => {
    setupCatalogMock()
    const portalMutate = vi.fn()
    const cancelMutate = vi.fn()
    const updateMutate = vi.fn()
    const checkoutMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: {
        status: "active",
        subscription_status: "trialing",
        plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
        failure_reason: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: checkoutMutate })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: portalMutate })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: cancelMutate,
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: updateMutate })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    expect(screen.getAllByText(/Votre essai correspond au plan Basic/i).length).toBeGreaterThan(0)

    const premiumCard = getPlanCard("Premium")
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    expect(validateButton).toBeDisabled()
    fireEvent.click(validateButton)

    expect(updateMutate).not.toHaveBeenCalled()
    expect(portalMutate).not.toHaveBeenCalled()
    expect(cancelMutate).not.toHaveBeenCalled()
    expect(checkoutMutate).not.toHaveBeenCalled()
  })

  it("affiche un bouton dédié de résiliation quand un abonné a un plan actif", () => {
    setupCatalogMock()
    const cancelMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      refetch: vi.fn(),
      data: {
        status: "active",
        subscription_status: "active",
        plan: {
          code: "basic",
          display_name: "Basic",
          monthly_price_cents: 900,
          currency: "EUR",
          daily_message_limit: 50,
          is_active: true,
        },
        failure_reason: null,
        current_quota: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: cancelMutate,
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    const cancelButton = screen.getByRole("button", { name: /résilier l'abonnement|cancel subscription/i })
    fireEvent.click(cancelButton)

    expect(cancelMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })

  it("déclenche une resynchronisation après retour portail tant que l'annulation n'est pas visible", () => {
    setupCatalogMock()
    const refetch = vi.fn()
    localStorage.setItem(
      "billing_portal_pending_action",
      JSON.stringify({ action: "cancel", createdAt: Date.now() }),
    )

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      refetch,
      data: {
        status: "active",
        subscription_status: "active",
        plan: {
          code: "basic",
          display_name: "Basic",
          monthly_price_cents: 900,
          currency: "EUR",
          daily_message_limit: 50,
          is_active: true,
        },
        cancel_at_period_end: false,
        current_period_end: null,
        failure_reason: null,
        current_quota: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    expect(refetch).toHaveBeenCalled()
    expect(
      screen.getByText(/Synchronisation de l'abonnement en cours/i),
    ).toBeInTheDocument()
  })

  it("affiche immédiatement la date de résiliation après retour portail quand l'échéance est connue", () => {
    setupCatalogMock()
    const refetch = vi.fn()
    localStorage.setItem(
      "billing_portal_pending_action",
      JSON.stringify({
        action: "cancel",
        createdAt: Date.now(),
        currentPeriodEnd: "2026-04-30T22:00:00Z",
      }),
    )

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      refetch,
      data: {
        status: "active",
        subscription_status: "active",
        plan: {
          code: "basic",
          display_name: "Basic",
          monthly_price_cents: 900,
          currency: "EUR",
          daily_message_limit: 50,
          is_active: true,
        },
        cancel_at_period_end: false,
        current_period_end: null,
        failure_reason: null,
        current_quota: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    expect(screen.queryByText(/Synchronisation de l'abonnement en cours/i)).not.toBeInTheDocument()
    expect(
      screen.getByText(/Abonnement actif jusqu'au|Current subscription remains active until/i),
    ).toBeInTheDocument()
  })

  it("bascule automatiquement en mode résiliation programmée quand le webhook met à jour l'abonnement", () => {
    setupCatalogMock()
    const refetch = vi.fn()
    localStorage.setItem(
      "billing_portal_pending_action",
      JSON.stringify({ action: "cancel", createdAt: Date.now() }),
    )

    let subscriptionData = {
      status: "active",
      subscription_status: "active",
      plan: {
        code: "basic",
        display_name: "Basic",
        monthly_price_cents: 900,
        currency: "EUR",
        daily_message_limit: 50,
        is_active: true,
      },
      cancel_at_period_end: false,
      current_period_end: null,
      failure_reason: null,
      current_quota: null,
    }

    mockUseBillingSubscription.mockImplementation(() => ({
      isLoading: false,
      refetch,
      data: subscriptionData,
    }))
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    const { rerender } = render(<SubscriptionSettings />)

    expect(
      screen.getByText(/Synchronisation de l'abonnement en cours/i),
    ).toBeInTheDocument()

    subscriptionData = {
      ...subscriptionData,
      cancel_at_period_end: true,
      current_period_end: "2026-04-30T22:00:00Z",
    }

    rerender(<SubscriptionSettings />)

    const basicCard = getPlanCard("Basic")

    expect(screen.queryByText(/Synchronisation de l'abonnement en cours/i)).not.toBeInTheDocument()
    expect(basicCard).toHaveAttribute("aria-pressed", "true")
    expect(basicCard).toHaveTextContent(/Abonnement actif jusqu'au|Current subscription remains active until/i)
  })

  it("passe en mode réactivation quand cancel_at_period_end est déjà vrai", () => {
    setupCatalogMock()
    const cancelMutate = vi.fn()
    const updateMutate = vi.fn()
    const reactivateMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      refetch: vi.fn(),
      data: {
        status: "active",
        subscription_status: "active",
        plan: {
          code: "basic",
          display_name: "Basic",
          monthly_price_cents: 900,
          currency: "EUR",
          daily_message_limit: 50,
          is_active: true,
        },
        cancel_at_period_end: true,
        current_period_end: "2026-04-30T22:00:00Z",
        failure_reason: null,
        current_quota: null,
      },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: cancelMutate,
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({
      isPending: false,
      mutate: updateMutate,
    })
    mockUseStripeSubscriptionReactivate.mockReturnValue({
      isPending: false,
      mutate: reactivateMutate,
    })

    render(<SubscriptionSettings />)

    expect(
      screen.getByText(/Réactiver en prenant Basic|Reactivate with Basic/i),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Réactiver en prenant Premium|Reactivate with Premium/i),
    ).toBeInTheDocument()

    const reactivateButton = screen.getByRole("button", { name: /réactiver l'abonnement|reactivate subscription/i })
    expect(reactivateButton).toBeEnabled()

    expect(
      screen.getByText(/Abonnement actif jusqu'au|Current subscription remains active until/i),
    ).toBeInTheDocument()
    const basicCard = getPlanCard("Basic")
    expect(basicCard).toHaveTextContent(/Abonnement actif jusqu'au|Current subscription remains active until/i)
    expect(cancelMutate).not.toHaveBeenCalled()

    fireEvent.click(reactivateButton)

    expect(reactivateMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
    expect(updateMutate).not.toHaveBeenCalled()

    const premiumCard = getPlanCard("Premium")
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    expect(validateButton).toBeEnabled()
    fireEvent.click(validateButton)

    expect(updateMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
    expect(cancelMutate).not.toHaveBeenCalled()
  })

  it("masque la carte Gratuit et affiche un sous-titre quand aucun abonnement n'est actif", () => {
    setupCatalogMock()
    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      data: { status: "inactive", subscription_status: null, plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripePortalSubscriptionCancelSession.mockReturnValue({
      isPending: false,
      mutate: vi.fn(),
    })
    mockUseStripePortalSubscriptionUpdateSession.mockReturnValue({ isPending: false, mutate: vi.fn() })
    mockUseStripeSubscriptionReactivate.mockReturnValue({ isPending: false, mutate: vi.fn() })

    render(<SubscriptionSettings />)

    expect(screen.queryByRole("button", { name: /^gratuit$|^free$/i })).not.toBeInTheDocument()
    expect(
      screen.queryByText(/Aucun abonnement actif pour le moment|You do not have an active subscription/i),
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(/mode gratuit avec des fonctionnalités limitées|free tier with limited features/i),
    ).toBeInTheDocument()
  })
})
