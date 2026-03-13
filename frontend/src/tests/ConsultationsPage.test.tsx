import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import React from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { AUTO_ASTROLOGER_ID, CONTEXT_MAX_LENGTH } from "../types/consultation"
import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { ConsultationProvider, useConsultation, STORAGE_KEY } from "../state/consultationStore"

const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
}

const mockNavigate = vi.fn()
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/consultations", () => ({
  useConsultationPrecheck: () => ({
    mutate: (
      payload: {
        consultation_type: string
        other_person?: { birth_time_known?: boolean }
      },
      options?: { onSuccess?: (response: { data: any }) => void }
    ) => {
      const isRelation = payload.consultation_type === "relation"
      const fallbackMode =
        isRelation && payload.other_person?.birth_time_known === false
          ? "other_no_birth_time"
          : isRelation && !payload.other_person
            ? "relation_user_only"
            : null

      options?.onSuccess?.({
        data: {
          consultation_type: payload.consultation_type,
          user_profile_quality: "complete",
          precision_level: fallbackMode ? "medium" : "high",
          status: fallbackMode ? "degraded" : "nominal",
          missing_fields: [],
          available_modes: [],
          fallback_mode: fallbackMode,
          safeguard_issue: null,
          blocking_reasons: [],
        },
      })
    },
    isPending: false,
  }),
  useConsultationGenerate: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}))

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false, gcTime: 0 },
    mutations: { retry: false },
  },
})

const renderWithProviders = (ui: React.ReactElement, { route = "/", queryClient = createTestQueryClient() } = {}) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]} future={routerFutureFlags}>
        <ConsultationProvider>
          {ui}
        </ConsultationProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe("ConsultationsPage", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  describe("AC1: Liste consultations", () => {
    it("displays page title and subtitle", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByText("Consultations")).toBeInTheDocument()
      expect(screen.getByText(/Create targeted/i)).toBeInTheDocument()
    })

    it("displays consultation types", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getAllByText(/Period/i).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/Career/i).length).toBeGreaterThan(0)
    })
  })
})

describe("ConsultationWizardPage - Story 47.8 Flow", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  it("shows interaction toggle for eligible types like Career", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=work" })

    await waitFor(() => {
      expect(screen.getByText(/Frame your request/i)).toBeInTheDocument()
    })

    expect(screen.getByText(/This consultation concerns another person/i)).toBeInTheDocument()
  })

  it("advances from Framing to Summary without extra data if interaction is NOT checked", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=work" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Mon évolution pro" } 
    })
    
    // interaction toggle is NOT checked by default
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    fireEvent.click(nextBtn)

    // Should go to collection step
    await waitFor(() => expect(screen.getByText(/Additional information/i)).toBeInTheDocument())
    // Should NOT see other person form
    expect(screen.queryByText(/Information about the other person/i)).not.toBeInTheDocument()
    
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))
    await waitFor(() => expect(screen.getByText(/Final verification/i)).toBeInTheDocument())
  })

  it("requires extra data in Collection step if interaction IS checked", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=work" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Entretien avec un recruteur" } 
    })
    
    // CHECK interaction toggle
    fireEvent.click(screen.getByLabelText(/This consultation concerns another person/i))
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    fireEvent.click(nextBtn)

    // Should go to collection step and SEE other person form
    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
    
    // Next should be disabled until form filled (simplified state test)
    const nextBtn2 = screen.getByRole("button", { name: /Next/i })
    expect(nextBtn2).toBeDisabled()
  })

  it("relation type still shows other person form without toggle", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    // Toggle should NOT be present because it's implicit/mandatory for relation
    expect(screen.queryByText(/This consultation concerns another person/i)).not.toBeInTheDocument()
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Ma relation" } 
    })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
  })
})
