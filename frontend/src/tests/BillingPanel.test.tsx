import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { BillingPanel } from "../components/BillingPanel"

const mockUseBillingSubscription = vi.fn()
const mockUseCheckoutEntryPlan = vi.fn()
const mockUseRetryPayment = vi.fn()
const mockUseChangePlan = vi.fn()
const mockUseBillingQuota = vi.fn()

vi.mock("@api", () => ({
  BillingApiError: class extends Error {},
  useBillingSubscription: () => mockUseBillingSubscription(),
  useCheckoutEntryPlan: () => mockUseCheckoutEntryPlan(),
  useRetryPayment: () => mockUseRetryPayment(),
  useChangePlan: () => mockUseChangePlan(),
  useBillingQuota: () => mockUseBillingQuota(),
}))

afterEach(() => {
  cleanup()
  mockUseBillingSubscription.mockReset()
  mockUseCheckoutEntryPlan.mockReset()
  mockUseRetryPayment.mockReset()
  mockUseChangePlan.mockReset()
  mockUseBillingQuota.mockReset()
  vi.restoreAllMocks()
})

describe("BillingPanel", () => {
  it("renders subscription status and triggers checkout", async () => {
    const refetch = vi.fn()
    const mutateAsync = vi.fn()

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        is_active: false,
        status: "inactive",
        plan: null,
        failure_reason: null,
      },
      refetch,
    })
    mockUseCheckoutEntryPlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: mutateAsync,
    })
    mockUseRetryPayment.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: vi.fn(),
    })
    mockUseChangePlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue({
      refetch: vi.fn(),
    })

    render(<BillingPanel />)
    
    const subscribeButton = screen.getByRole("button", { name: /Subscribe Basic/i })
    expect(subscribeButton).toBeInTheDocument()

    fireEvent.click(subscribeButton)

    expect(mutateAsync).toHaveBeenCalledWith({
      plan_code: "basic-entry",
      payment_method_token: "pm_card_ok",
    })
  })

  it("shows failure reason and allows retry", async () => {
    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        is_active: false,
        status: "inactive",
        plan: null,
        failure_reason: null,
        last_failed_checkout_id: 123
      },
    })
    mockUseCheckoutEntryPlan.mockReturnValue({
      isPending: false,
      data: { payment_status: "failed", payment_failure_reason: "card declined", checkout_id: 123 },
      error: null,
      mutate: vi.fn(),
    })
    const mutateRetry = vi.fn()
    mockUseRetryPayment.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: mutateRetry,
    })
    mockUseChangePlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutate: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue({
      refetch: vi.fn(),
    })

    render(<BillingPanel />)
    
    expect(screen.getByText(/Motif échec paiement: card declined/i)).toBeInTheDocument()
    const retryButton = screen.getByRole("button", { name: /Retry Payment/i })
    
    fireEvent.click(retryButton)
    expect(mutateRetry).toHaveBeenCalledWith({
      checkoutId: 123,
      paymentMethodToken: "pm_card_ok",
    })
  })
})
