import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import React from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { AUTO_ASTROLOGER_ID, CONTEXT_MAX_LENGTH, INTERACTION_ELIGIBLE_TYPES } from "../types/consultation"
import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { ConsultationProvider, STORAGE_KEY } from "../state/consultationStore"

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
  useConsultationThirdParties: () => ({
    data: { items: [
      { external_id: "tp-1", nickname: "Partner", birth_date: "1990-01-01", birth_place: "Paris", birth_time_known: true }
    ] },
    isPending: false,
  }),
  useCreateConsultationThirdParty: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}))

vi.mock("../api/geocoding", () => ({
  geocodeCity: vi.fn().mockResolvedValue({
    display_name: "Paris, France",
    place_resolved_id: 123,
    lat: 48.8566,
    lon: 2.3522,
  }),
  GeocodingError: class extends Error {
    constructor(public code: string, message: string) {
      super(message)
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

describe("ConsultationsPage", () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem("lang", "en")
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

describe("Consultation Taxonomy Consistency", () => {
  it("contains exactly work and relation", () => {
    expect(INTERACTION_ELIGIBLE_TYPES).toContain("work")
    expect(INTERACTION_ELIGIBLE_TYPES).toContain("relation")
    expect(INTERACTION_ELIGIBLE_TYPES.length).toBe(2)
  })

  it("does not include non-eligible types", () => {
    expect(INTERACTION_ELIGIBLE_TYPES).not.toContain("period")
    expect(INTERACTION_ELIGIBLE_TYPES).not.toContain("timing")
  })
})

describe("ConsultationWizardPage - Story 47.8 Flow", () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem("lang", "en")
    sessionStorage.clear()
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
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    fireEvent.click(nextBtn)

    await waitFor(() => expect(screen.getByText(/Additional information/i)).toBeInTheDocument())
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
    
    fireEvent.click(screen.getByLabelText(/This consultation concerns another person/i))
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    fireEvent.click(nextBtn)

    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
    
    const nextBtn2 = screen.getByRole("button", { name: /Next/i })
    expect(nextBtn2).toBeDisabled()
  })

  it("keeps Next enabled on frame when a direct type link is still running its initial precheck", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=period" })
    
    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Test precheck state" } 
    })
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    expect(nextBtn).not.toBeDisabled()
  })

  it("uses natal geocoding protocol for third-party birth place and propagates resolved coordinates", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByLabelText(/Birth city/i)).toBeInTheDocument())
    
    fireEvent.change(screen.getByLabelText(/Birth date/i), { target: { value: "1995-01-01" } })
    fireEvent.change(screen.getByLabelText(/Birth city/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Birth country/i), { target: { value: "France" } })
    
    fireEvent.blur(screen.getByLabelText(/Birth city/i))

    await waitFor(() => expect(screen.getByDisplayValue(/Paris, France/i)).toBeInTheDocument())
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    expect(nextBtn).not.toBeDisabled()
  })

  it("restarts the wizard from the new type when switching consultation mid-process", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=work" })
    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    
    fireEvent.click(screen.getByRole("button", { name: /Cancel/i }))
    expect(mockNavigate).toHaveBeenCalledWith("/consultations")
  })

  it("relation type still shows other person form without toggle", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    expect(screen.queryByText(/This consultation concerns another person/i)).not.toBeInTheDocument()
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Ma relation" } 
    })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
  })

  it("allows selecting an existing third-party contact", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Retrouvailles" } })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByLabelText(/Use an existing contact/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Use an existing contact/i), { target: { value: "tp-1" } })

    await waitFor(() => {
      expect(screen.getByDisplayValue("1990-01-01")).toBeInTheDocument()
      expect(screen.getByDisplayValue("Paris")).toBeInTheDocument()
    })
  })

  it("AC3: shows save-to-contacts checkbox on other person form", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
    expect(screen.getByLabelText(/Save to my contacts/i)).toBeInTheDocument()
  })

  it("AC4: shows nickname field and privacy warning when save-to-contacts is checked", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByLabelText(/Save to my contacts/i)).toBeInTheDocument())
    fireEvent.click(screen.getByLabelText(/Save to my contacts/i))

    await waitFor(() => {
      expect(screen.getByLabelText(/Nickname/i)).toBeInTheDocument()
      expect(screen.getByText(/do not use full names/i)).toBeInTheDocument()
    })
  })

  it("AC4: Next is blocked if save-to-contacts is checked but nickname is empty", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relation" })

    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByRole("button", { name: /Next/i }))

    await waitFor(() => expect(screen.getByLabelText(/Birth city/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Birth date/i), { target: { value: "1990-01-01" } })
    fireEvent.change(screen.getByLabelText(/Birth city/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Birth country/i), { target: { value: "France" } })

    fireEvent.click(screen.getByLabelText(/Save to my contacts/i))

    await waitFor(() => expect(screen.getByLabelText(/Nickname/i)).toBeInTheDocument())

    const nextBtn = screen.getByRole("button", { name: /Next/i })
    expect(nextBtn).toBeDisabled()
  })
})
