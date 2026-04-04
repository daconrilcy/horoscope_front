import { renderHook, waitFor } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useEntitlementsSnapshot, useUpgradeHint, useFeatureAccess } from "../hooks/useEntitlementSnapshot"
import * as billingApi from "../api/billing"
import * as authUtils from "../utils/authToken"
import React from "react"

vi.mock("../api/billing")
vi.mock("../utils/authToken")

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
)

describe("useEntitlementSnapshot hooks", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("useEntitlementsSnapshot fetches data when token is present", async () => {
    vi.mocked(authUtils.useAccessTokenSnapshot).mockReturnValue("mock-token")
    const mockData: billingApi.EntitlementsSnapshot = {
      plan_code: "free",
      billing_status: "active",
      features: [],
      upgrade_hints: []
    }
    vi.mocked(billingApi.fetchEntitlementsSnapshot).mockResolvedValue(mockData)

    const { result } = renderHook(() => useEntitlementsSnapshot(), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual(mockData)
  })

  it("useUpgradeHint returns the correct hint", async () => {
    vi.mocked(authUtils.useAccessTokenSnapshot).mockReturnValue("mock-token")
    const hint: billingApi.UpgradeHint = {
      feature_code: "horoscope_daily",
      current_plan_code: "free",
      target_plan_code: "basic",
      benefit_key: "unlock",
      cta_variant: "inline",
      priority: 1
    }
    const mockData: billingApi.EntitlementsSnapshot = {
      plan_code: "free",
      billing_status: "active",
      features: [],
      upgrade_hints: [hint]
    }
    vi.mocked(billingApi.fetchEntitlementsSnapshot).mockResolvedValue(mockData)

    const { result } = renderHook(() => useUpgradeHint("horoscope_daily"), { wrapper })

    await waitFor(() => expect(result.current).toEqual(hint))
  })

  it("useFeatureAccess returns the correct access", async () => {
    vi.mocked(authUtils.useAccessTokenSnapshot).mockReturnValue("mock-token")
    const feature: billingApi.FeatureEntitlementResponse = {
      feature_code: "natal_chart_long",
      granted: true,
      reason_code: "granted",
      access_mode: "unlimited",
      variant_code: "free_short",
      usage_states: []
    }
    const mockData: billingApi.EntitlementsSnapshot = {
      plan_code: "free",
      billing_status: "active",
      features: [feature],
      upgrade_hints: []
    }
    vi.mocked(billingApi.fetchEntitlementsSnapshot).mockResolvedValue(mockData)

    const { result } = renderHook(() => useFeatureAccess("natal_chart_long"), { wrapper })

    await waitFor(() => expect(result.current).toEqual(feature))
  })
})
