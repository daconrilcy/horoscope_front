import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { UsageSettings } from "../pages/settings/UsageSettings"

const mockUseChatEntitlementUsage = vi.fn()
const mockUseChatEntitlementFeature = vi.fn()

vi.mock("@api/billing", async (importActual) => {
  const actual = await importActual<typeof import("@api/billing")>()
  return {
    ...actual,
    useChatEntitlementUsage: () => mockUseChatEntitlementUsage(),
    useChatEntitlementFeature: () => mockUseChatEntitlementFeature(),
  }
})

afterEach(() => {
  cleanup()
  mockUseChatEntitlementUsage.mockReset()
  mockUseChatEntitlementFeature.mockReset()
})

describe("UsageSettings", () => {
  it("affiche des lignes jour semaine mois avec un detail formate en tokens", () => {
    mockUseChatEntitlementUsage.mockReturnValue({
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
      data: {
        quota_date: "2026-04-01",
        quota_key: "tokens",
        limit: 50000,
        consumed: 12450,
        remaining: 37550,
        reset_at: "2026-05-01T00:00:00Z",
        blocked: false,
      },
    })
    mockUseChatEntitlementFeature.mockReturnValue({
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
      data: {
        feature_code: "astrologer_chat",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        quota_limit: 50000,
        quota_remaining: 37550,
        variant_code: null,
        usage_states: [
          {
            quota_key: "tokens",
            quota_limit: 1667,
            used: 980,
            remaining: 687,
            exhausted: false,
            period_unit: "day",
            period_value: 1,
            reset_mode: "calendar",
            window_start: "2026-04-17T10:00:00Z",
            window_end: "2026-04-18T10:00:00Z",
          },
          {
            quota_key: "tokens",
            quota_limit: 12500,
            used: 4200,
            remaining: 8300,
            exhausted: false,
            period_unit: "week",
            period_value: 1,
            reset_mode: "calendar",
            window_start: "2026-04-17T10:00:00Z",
            window_end: "2026-04-24T10:00:00Z",
          },
          {
            quota_key: "tokens",
            quota_limit: 50000,
            used: 12450,
            remaining: 37550,
            exhausted: false,
            period_unit: "month",
            period_value: 1,
            reset_mode: "calendar",
            window_start: "2026-04-17T10:00:00Z",
            window_end: "2026-05-17T10:00:00Z",
          },
        ],
      },
    })

    render(<UsageSettings />)

    expect(screen.getByText("Usage du jour")).toBeInTheDocument()
    expect(screen.getByText("Usage de la semaine")).toBeInTheDocument()
    expect(screen.getByText("Usage du mois")).toBeInTheDocument()
    expect(screen.getByText("980 tokens / 1 667 tokens au total")).toBeInTheDocument()
    expect(screen.getByText("4 200 tokens / 12 500 tokens au total")).toBeInTheDocument()
    expect(screen.getByText("12 450 tokens / 50 000 tokens au total")).toBeInTheDocument()
    expect(screen.getAllByText(/Réinitialisation/)).toHaveLength(3)
  })
})
