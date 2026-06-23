// Vérifie que la page thème natal ne boucle pas après un échec Astral.
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query"
import { cleanup, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { NatalChartPage } from "../pages/NatalChartPage"

const mockSubmitAstralJob = vi.fn()
const mockUseEntitlementsSnapshot = vi.fn()
const mockUseAccessTokenSnapshot = vi.fn()
const mockUseAstralJobStatus = vi.fn()
const mockUseAstralJobEvents = vi.fn()

vi.mock("../api/astral", async () => {
  const actual = await vi.importActual<typeof import("../api/astral")>("../api/astral")
  return {
    ...actual,
    useSubmitAstralJob: (accessToken: string | null) => {
      if (!accessToken) {
        throw new Error("Le token est requis dans ce test.")
      }
      return useMutation({
        mutationFn: mockSubmitAstralJob,
      })
    },
    useAstralJobStatus: () => mockUseAstralJobStatus(),
    useAstralJobEvents: (...args: unknown[]) => {
      mockUseAstralJobEvents(...args)
    },
  }
})

vi.mock("../hooks/useEntitlementSnapshot", () => ({
  useEntitlementsSnapshot: () => mockUseEntitlementsSnapshot(),
}))

vi.mock("../utils/authToken", () => ({
  useAccessTokenSnapshot: () => mockUseAccessTokenSnapshot(),
  getSubjectFromAccessToken: () => null,
  hasUsableAccessToken: (token: string | null) => Boolean(token),
}))

let queryClient: QueryClient

function renderNatalChartPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NatalChartPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })
  mockSubmitAstralJob.mockReset()
  mockUseEntitlementsSnapshot.mockReturnValue({
    data: {
      plan_code: "basic",
      billing_status: "active",
      features: [
        {
          feature_code: "horoscope_daily",
          granted: true,
          reason_code: "granted",
          access_mode: "quota",
          variant_code: "basic_short",
          usage_states: [],
        },
      ],
      upgrade_hints: [],
    },
    isPending: false,
    isError: false,
  })
  mockUseAccessTokenSnapshot.mockReturnValue("access-token")
  mockUseAstralJobStatus.mockReturnValue({
    data: undefined,
    isError: false,
    isPending: false,
  })
  mockUseAstralJobEvents.mockReset()
})

afterEach(() => {
  cleanup()
  queryClient.clear()
})

describe("NatalChartPage", () => {
  it("ne soumet pas automatiquement un job Astral au montage", async () => {
    renderNatalChartPage()

    expect(await screen.findByRole("button", { name: "Lancer le theme natal" })).toBeEnabled()
    expect(mockSubmitAstralJob).not.toHaveBeenCalled()
  })
})
