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
  vi.restoreAllMocks()
})

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

    render(<SubscriptionSettings />)

    // Sélectionner le plan "Basic" (UI code: basic)
    const basicCard = screen.getByText("Basic").closest('[role="button"]')!
    fireEvent.click(basicCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(mutate).toHaveBeenCalledWith(
      "basic", // code canonique Stripe
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
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

    render(<SubscriptionSettings />)

    // La carte "Basic" doit être sélectionnée (aria-pressed=true) — elle est le plan courant
    const basicCard = screen.getByText("Basic").closest('[role="button"]')!
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
        plan: { code: "basic", display_name: "Basic", monthly_price_cents: 900, currency: "EUR", daily_message_limit: 50, is_active: true },
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

    render(<SubscriptionSettings />)

    const premiumCard = screen.getByText("Premium").closest('[role="button"]')!
    fireEvent.click(premiumCard)

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

    render(<SubscriptionSettings />)

    expect(
      screen.getByText(/Votre essai correspond au plan Basic/i),
    ).toBeInTheDocument()

    const premiumCard = screen.getByText("Premium").closest('[role="button"]')!
    fireEvent.click(premiumCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    expect(validateButton).toBeDisabled()
    fireEvent.click(validateButton)

    expect(updateMutate).not.toHaveBeenCalled()
    expect(portalMutate).not.toHaveBeenCalled()
    expect(cancelMutate).not.toHaveBeenCalled()
    expect(checkoutMutate).not.toHaveBeenCalled()
  })

  it("appelle le flow de résiliation dédié quand un abonné actif sélectionne le plan Gratuit", () => {
    setupCatalogMock()
    const cancelMutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
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

    render(<SubscriptionSettings />)

    const freeCard = screen.getByText(/gratuit|free/i).closest('[role="button"]')!
    fireEvent.click(freeCard)

    const validateButton = screen.getByRole("button", { name: /valider|validate/i })
    fireEvent.click(validateButton)

    expect(cancelMutate).toHaveBeenCalledWith(
      undefined,
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
  })
})
