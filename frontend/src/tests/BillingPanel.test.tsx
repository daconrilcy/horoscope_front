import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { BillingPanel } from "../components/BillingPanel"

const mockUseBillingSubscription = vi.fn()
const mockUseStripeCheckoutSession = vi.fn()
const mockUseStripePortalSession = vi.fn()
const mockUseChatEntitlementUsage = vi.fn()

vi.mock("@api", () => ({
  BillingApiError: class extends Error {
    code: string
    status: number
    details: Record<string, string>
    constructor(code: string, message: string, status: number, details: Record<string, string> = {}) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
    }
  },
  useBillingSubscription: () => mockUseBillingSubscription(),
  useStripeCheckoutSession: () => mockUseStripeCheckoutSession(),
  useStripePortalSession: () => mockUseStripePortalSession(),
  useChatEntitlementUsage: () => mockUseChatEntitlementUsage(),
}))

afterEach(() => {
  cleanup()
  mockUseBillingSubscription.mockReset()
  mockUseStripeCheckoutSession.mockReset()
  mockUseStripePortalSession.mockReset()
  mockUseChatEntitlementUsage.mockReset()
  vi.restoreAllMocks()
})

describe("BillingPanel", () => {
  it("shows checkout button when subscription is inactive and triggers checkout session", () => {
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { status: "inactive", plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate,
    })
    mockUseStripePortalSession.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: vi.fn(),
    })
    mockUseChatEntitlementUsage.mockReturnValue({ data: null })

    render(<BillingPanel />)

    const checkoutButton = screen.getByRole("button", { name: /créer session checkout/i })
    expect(checkoutButton).toBeInTheDocument()

    fireEvent.click(checkoutButton)

    expect(mutate).toHaveBeenCalledWith("basic", expect.objectContaining({ onSuccess: expect.any(Function) }))
  })

  it("shows portal button and triggers portal session", () => {
    const mutate = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { status: "active", plan: { code: "basic" }, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: vi.fn(),
    })
    mockUseStripePortalSession.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate,
    })
    mockUseChatEntitlementUsage.mockReturnValue({ data: null })

    render(<BillingPanel />)

    const portalButton = screen.getByRole("button", { name: /ouvrir le portail stripe/i })
    expect(portalButton).toBeInTheDocument()

    fireEvent.click(portalButton)

    expect(mutate).toHaveBeenCalledWith(undefined, expect.objectContaining({ onSuccess: expect.any(Function) }))
  })

  it("does not show paymentToken selector", () => {
    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { status: "inactive", plan: null, failure_reason: null },
    })
    mockUseStripeCheckoutSession.mockReturnValue({ isPending: false, data: null, error: null, mutate: vi.fn() })
    mockUseStripePortalSession.mockReturnValue({ isPending: false, data: null, error: null, mutate: vi.fn() })
    mockUseChatEntitlementUsage.mockReturnValue({ data: null })

    render(<BillingPanel />)

    expect(screen.queryByLabelText(/simulation paiement/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/pm_card_ok/i)).not.toBeInTheDocument()
  })
})
