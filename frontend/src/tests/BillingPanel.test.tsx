import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { BillingPanel } from "../components/BillingPanel"

const mockUseBillingSubscription = vi.fn()
const mockUseCheckoutEntryPlan = vi.fn()
const mockUseRetryCheckout = vi.fn()
const mockUseChangePlan = vi.fn()
const mockUseBillingQuota = vi.fn()

vi.mock("../api/billing", () => ({
  BillingApiError: class extends Error {},
  useBillingSubscription: () => mockUseBillingSubscription(),
  useCheckoutEntryPlan: () => mockUseCheckoutEntryPlan(),
  useRetryCheckout: () => mockUseRetryCheckout(),
  useChangePlan: () => mockUseChangePlan(),
  useBillingQuota: () => mockUseBillingQuota(),
}))

afterEach(() => {
  cleanup()
  mockUseBillingSubscription.mockReset()
  mockUseCheckoutEntryPlan.mockReset()
  mockUseRetryCheckout.mockReset()
  mockUseChangePlan.mockReset()
  mockUseBillingQuota.mockReset()
  vi.restoreAllMocks()
})

describe("BillingPanel", () => {
  it("renders subscription status and triggers checkout", async () => {
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue(
      "11111111-1111-1111-1111-111111111111",
    )
    const refetch = vi.fn()
    const mutateAsync = vi.fn().mockResolvedValue({
      payment_status: "succeeded",
      subscription: { status: "active", failure_reason: null },
    })

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
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
      mutateAsync,
    })
    mockUseRetryCheckout.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseChangePlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue({
      refetch: vi.fn(),
    })

    render(<BillingPanel />)
    expect(screen.getByText("Statut: inactif")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Souscrire au plan Basic (5 EUR/mois)" }))

    await waitFor(() =>
      expect(mutateAsync).toHaveBeenCalledWith({
        plan_code: "basic-entry",
        payment_method_token: "pm_card_ok",
        idempotency_key: "11111111-1111-1111-1111-111111111111",
      }),
    )
  })

  it("shows failure reason and allows retry", async () => {
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue(
      "22222222-2222-2222-2222-222222222222",
    )
    const refetch = vi.fn()
    const checkoutMutateAsync = vi.fn().mockResolvedValue({
      payment_status: "failed",
      subscription: { status: "inactive", failure_reason: "payment provider declined the payment method" },
    })
    const retryMutateAsync = vi.fn().mockResolvedValue({
      payment_status: "succeeded",
      subscription: { status: "active", failure_reason: null },
    })

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
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
      mutateAsync: checkoutMutateAsync,
    })
    mockUseRetryCheckout.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: retryMutateAsync,
    })
    mockUseChangePlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue({
      refetch: vi.fn(),
    })

    render(<BillingPanel />)
    fireEvent.change(screen.getByLabelText("Simulation paiement"), { target: { value: "pm_fail" } })
    fireEvent.click(screen.getByRole("button", { name: "Souscrire au plan Basic (5 EUR/mois)" }))
    await waitFor(() => expect(checkoutMutateAsync).toHaveBeenCalled())

    const retryButton = await screen.findByRole("button", { name: "Reessayer le paiement" })
    expect(retryButton).toBeInTheDocument()
    expect(screen.getByText(/Motif echec paiement:/)).toBeInTheDocument()

    fireEvent.click(retryButton)
    await waitFor(() => expect(retryMutateAsync).toHaveBeenCalled())

    expect(retryMutateAsync).toHaveBeenCalledWith({
      plan_code: "basic-entry",
      payment_method_token: "pm_card_ok",
      idempotency_key: "22222222-2222-2222-2222-222222222222-retry",
    })
  })

  it("changes active subscription plan and shows quota impact", async () => {
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue(
      "33333333-3333-3333-3333-333333333333",
    )
    const refetch = vi.fn()
    const changePlanMutateAsync = vi.fn().mockResolvedValue({
      previous_plan_code: "basic-entry",
      target_plan_code: "premium-unlimited",
      plan_change_status: "succeeded",
      subscription: {
        status: "active",
        plan: {
          code: "premium-unlimited",
          display_name: "Premium 20 EUR/mois",
          monthly_price_cents: 2000,
          currency: "EUR",
          daily_message_limit: 1000,
          is_active: true,
        },
        failure_reason: null,
        updated_at: null,
      },
    })

    mockUseBillingSubscription.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        status: "active",
        plan: {
          code: "basic-entry",
          display_name: "Basic 5 EUR/mois",
          monthly_price_cents: 500,
          currency: "EUR",
          daily_message_limit: 5,
          is_active: true,
        },
        failure_reason: null,
        updated_at: null,
      },
      refetch,
    })
    mockUseCheckoutEntryPlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRetryCheckout.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseChangePlan.mockReturnValue({
      isPending: false,
      data: null,
      error: null,
      mutateAsync: changePlanMutateAsync,
    })
    const refetchQuota = vi.fn()
    mockUseBillingQuota.mockReturnValue({
      refetch: refetchQuota,
    })

    render(<BillingPanel />)
    expect(screen.getByText(/Impact quota cible: 1000 messages\/jour/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Changer de plan" }))

    await waitFor(() =>
      expect(changePlanMutateAsync).toHaveBeenCalledWith({
        target_plan_code: "premium-unlimited",
        idempotency_key: "33333333-3333-3333-3333-333333333333",
      }),
    )
    expect(refetchQuota).toHaveBeenCalled()
    expect(screen.getByText(/Plan mis a jour: basic-entry -> premium-unlimited/)).toBeInTheDocument()
  })
})
