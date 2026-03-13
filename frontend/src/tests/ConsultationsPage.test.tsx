import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { Link, MemoryRouter, Route, Routes } from "react-router-dom"
import React from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { AUTO_ASTROLOGER_ID, CONTEXT_MAX_LENGTH, INTERACTION_ELIGIBLE_TYPES } from "../types/consultation"
import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { ConsultationProvider, useConsultation, STORAGE_KEY } from "../state/consultationStore"

const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
}

const mockNavigate = vi.fn()
const mockPrecheckMutate = vi.fn()
const mockGenerateMutateAsync = vi.fn()
const mockGeocodeCity = vi.fn()
let mockIsPrechecking = false
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
        other_person?: {
          birth_time_known?: boolean
          birth_city?: string
          birth_country?: string
          place_resolved_id?: number
          birth_lat?: number
          birth_lon?: number
        }
      },
      options?: { onSuccess?: (response: { data: any }) => void }
    ) => {
      mockPrecheckMutate(payload)
      const hasOtherPerson = !!payload.other_person
      const missingBirthTime = hasOtherPerson && payload.other_person?.birth_time_known === false
      const isRelation = payload.consultation_type === "relation"
      const fallbackMode =
        missingBirthTime
          ? "other_no_birth_time"
          : isRelation && !hasOtherPerson
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
    isPending: mockIsPrechecking,
  }),
  useConsultationGenerate: () => ({
    mutateAsync: mockGenerateMutateAsync,
    isPending: false,
  }),
}))

vi.mock("../api/geocoding", () => ({
  geocodeCity: (...args: unknown[]) => mockGeocodeCity(...args),
  GeocodingError: class GeocodingError extends Error {
    code: string
    constructor(message: string, code = "service_unavailable") {
      super(message)
      this.name = "GeocodingError"
      this.code = code
    }
  },
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

function WizardRouteHarness() {
  return (
    <>
      <nav>
        <Link to="/consultations">Consultations hub</Link>
        <Link to="/consultations/new?type=relation">Switch to relation</Link>
      </nav>
      <Routes>
        <Route path="/consultations" element={<ConsultationsPage />} />
        <Route path="/consultations/new" element={<ConsultationWizardPage />} />
      </Routes>
    </>
  )
}

describe("ConsultationsPage", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    vi.clearAllMocks()
    mockIsPrechecking = false
    mockGeocodeCity.mockResolvedValue({
      place_resolved_id: 777,
      lat: 48.8566,
      lon: 2.3522,
      display_name: "Paris, Ile-de-France, France",
    })
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

describe("INTERACTION_ELIGIBLE_TYPES", () => {
  it("contains exactly work and relation", () => {
    expect(INTERACTION_ELIGIBLE_TYPES).toEqual(expect.arrayContaining(["work", "relation"]))
    expect(INTERACTION_ELIGIBLE_TYPES).toHaveLength(2)
  })

  it("does not include non-eligible types", () => {
    expect(INTERACTION_ELIGIBLE_TYPES).not.toContain("period")
    expect(INTERACTION_ELIGIBLE_TYPES).not.toContain("orientation")
    expect(INTERACTION_ELIGIBLE_TYPES).not.toContain("timing")
  })
})

describe("ConsultationWizardPage - Story 47.8 Flow", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    mockIsPrechecking = false
    mockGeocodeCity.mockResolvedValue({
      place_resolved_id: 777,
      lat: 48.8566,
      lon: 2.3522,
      display_name: "Paris, Ile-de-France, France",
    })
    mockGenerateMutateAsync.mockResolvedValue({
      data: {
        consultation_id: "consult-1",
        consultation_type: "work",
        status: "nominal",
        precision_level: "high",
        fallback_mode: null,
        safeguard_issue: null,
        route_key: "work_full",
        summary: "Resume",
        sections: [],
      },
    })
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
    const toggle = screen.getByLabelText(/This consultation concerns another person/i)
    expect(toggle).not.toBeChecked()
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

  it("keeps Next enabled on frame when a direct type link is still running its initial precheck", async () => {
    mockIsPrechecking = true

    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=orientation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Describe your situation/i), {
      target: { value: "Je veux clarifier ma direction de vie" },
    })

    expect(screen.getByRole("button", { name: /Next/i })).toBeEnabled()
  })

  it("uses natal geocoding protocol for third-party birth place and propagates resolved coordinates", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=work" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Describe your situation/i), {
      target: { value: "Entretien avec un recruteur" },
    })
    fireEvent.click(screen.getByLabelText(/This consultation concerns another person/i))
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() =>
      expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument()
    )

    fireEvent.change(screen.getByLabelText(/^Birth date$/i), {
      target: { value: "1990-01-01" },
    })
    fireEvent.change(screen.getByLabelText(/Birth city/i), {
      target: { value: "Paris" },
    })
    fireEvent.change(screen.getByLabelText(/Birth country/i), {
      target: { value: "France" },
    })
    fireEvent.blur(screen.getByLabelText(/Birth country/i))

    await waitFor(() => {
      expect(mockGeocodeCity).toHaveBeenCalledWith("Paris", "France", expect.any(AbortSignal))
    })
    await waitFor(() => {
      expect(screen.getByDisplayValue("Paris, Ile-de-France, France")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Next/i }))
    await waitFor(() => expect(screen.getByText(/Final verification/i)).toBeInTheDocument())

    expect(mockPrecheckMutate).toHaveBeenLastCalledWith(
      expect.objectContaining({
        other_person: expect.objectContaining({
          birth_place: "Paris, Ile-de-France, France",
          birth_city: "Paris",
          birth_country: "France",
          place_resolved_id: 777,
          birth_lat: 48.8566,
          birth_lon: 2.3522,
        }),
      })
    )
  })

  it("restarts the wizard from the new type when switching consultation mid-process", async () => {
    renderWithProviders(<WizardRouteHarness />, { route: "/consultations/new?type=work" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Describe your situation/i), {
      target: { value: "Mon évolution pro" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))
    await waitFor(() => expect(screen.getByText(/Additional information/i)).toBeInTheDocument())

    fireEvent.click(screen.getByRole("link", { name: /Switch to relation/i }))

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    expect(screen.queryByText(/Additional information/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/This consultation concerns another person/i)).not.toBeInTheDocument()
    expect(screen.getByLabelText(/Describe your situation/i)).toHaveValue("")
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
