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

const mockUseFeatureAccess = vi.fn()
const mockUseUpgradeHint = vi.fn()

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
      const isRelation = payload.consultation_type === "relation" || payload.consultation_type === "relationship"
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
  useConsultationCatalogue: () => ({
    data: {
      items: [
        {
          key: "period",
          icon_ref: "📅",
          title: "Period Title",
          subtitle: "Period Subtitle",
          description: "Period Desc",
          metadata_config: { tags: ["Tag1"] },
          sort_order: 1,
        },
        {
          key: "career",
          icon_ref: "💼",
          title: "Career Title",
          subtitle: "Career Subtitle",
          description: "Career Desc",
          metadata_config: { tags: ["Tag2"] },
          sort_order: 2,
        },
      ],
      meta: { total: 2 },
    },
    isLoading: false,
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

vi.mock("../hooks/useEntitlementSnapshot", () => ({
  useFeatureAccess: (...args: unknown[]) => mockUseFeatureAccess(...args),
  useUpgradeHint: (...args: unknown[]) => mockUseUpgradeHint(...args),
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
    mockUseFeatureAccess.mockReturnValue({ feature_code: "thematic_consultation", granted: true })
    mockUseUpgradeHint.mockReturnValue({
      feature_code: "thematic_consultation",
      current_plan_code: "free",
      target_plan_code: "basic",
      benefit_key: "upgrade.thematic_consultation.unlock",
      cta_variant: "inline",
      priority: 3,
    })
  })

  afterEach(() => {
    cleanup()
  })

  describe("AC1: Liste consultations", () => {
    it("displays page title and subtitle", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByText("Choose your consultation")).toBeInTheDocument()
      expect(screen.getByText(/Which area would you like guidance on/i)).toBeInTheDocument()
    })

    it("displays consultation types from catalogue", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByText("Period Title")).toBeInTheDocument()
      expect(screen.getByText("Career Title")).toBeInTheDocument()
    })

    it("renders upgrade CTAs to Basic instead of consultation actions for free users", () => {
      mockUseFeatureAccess.mockReturnValue({
        feature_code: "thematic_consultation",
        granted: false,
        reason_code: "access_denied",
      })

      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      const ctaLinks = screen.getAllByRole("link", {
        name: /Upgrade to Basic for thematic consultations/i,
      })

      expect(ctaLinks).toHaveLength(3)
      ctaLinks.forEach((link) => {
        expect(link).toHaveAttribute("href", "/settings/subscription")
      })
      expect(screen.queryByText("Choose")).not.toBeInTheDocument()
      expect(screen.queryByText("Start")).not.toBeInTheDocument()
    })

    it("keeps consultation navigation actions for entitled users", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByRole("link", { name: /Period Title/i })).toHaveAttribute(
        "href",
        "/consultations/new?type=period",
      )
      expect(screen.getAllByText("Choose")).toHaveLength(2)
      expect(screen.getByText("Start")).toBeInTheDocument()
    })
  })
})

describe("Consultation Taxonomy Consistency", () => {
  it("contains career and relationship", () => {
    expect(INTERACTION_ELIGIBLE_TYPES).toContain("career")
    expect(INTERACTION_ELIGIBLE_TYPES).toContain("relationship")
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
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=career&astrologerId=auto" })

    await waitFor(() => {
      expect(screen.getByText(/Career Title/i)).toBeInTheDocument()
    })

    expect(screen.getByText(/This consultation also concerns another person/i)).toBeInTheDocument()
  })

  it("advances from Form to Result without extra data if interaction is NOT checked", async () => {
    // Note: Wizard is now 2 steps: astrologer -> form. Result is a separate page.
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=career&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Career Title/i)).toBeInTheDocument())
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Mon évolution pro" } 
    })
    
    const generateBtn = screen.getByRole("button", { name: /Generate consultation/i })
    expect(generateBtn).not.toBeDisabled()
    fireEvent.click(generateBtn)

    expect(mockNavigate).toHaveBeenCalledWith("/consultations/result")
  })

  it("requires extra data in Form step if interaction IS checked", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=career&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Career Title/i)).toBeInTheDocument())
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Entretien avec un recruteur" } 
    })
    
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))
    
    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
    
    const generateBtn = screen.getByRole("button", { name: /Generate consultation/i })
    expect(generateBtn).toBeDisabled()
  })

  it("keeps Generate enabled on form when a direct type link is still running its initial precheck", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=period&astrologerId=auto" })
    
    await waitFor(() => expect(screen.getByText(/Period Title/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Test precheck state" } 
    })
    
    const generateBtn = screen.getByRole("button", { name: /Generate consultation/i })
    expect(generateBtn).not.toBeDisabled()
  })

  it("uses natal geocoding protocol for third-party birth place and propagates resolved coordinates", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relationship&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Formulate your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    
    // Relation type in story 47.8 shows the form automatically or via toggle
    // In the new wizard, we added a toggle for all types.
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))

    await waitFor(() => expect(screen.getByLabelText(/Birth city/i)).toBeInTheDocument())
    
    fireEvent.change(screen.getByLabelText(/Birth date/i), { target: { value: "1995-01-01" } })
    fireEvent.change(screen.getByLabelText(/Birth city/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Birth country/i), { target: { value: "France" } })
    
    fireEvent.blur(screen.getByLabelText(/Birth city/i))

    await waitFor(() => expect(screen.getByDisplayValue(/Paris, France/i)).toBeInTheDocument())
    
    const generateBtn = screen.getByRole("button", { name: /Generate consultation/i })
    expect(generateBtn).not.toBeDisabled()
  })

  it("restarts the wizard when clicking Cancel", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=career&astrologerId=auto" })
    await waitFor(() => expect(screen.getByText(/Career Title/i)).toBeInTheDocument())
    
    fireEvent.click(screen.getByRole("button", { name: /Cancel/i }))
    expect(mockNavigate).toHaveBeenCalledWith("/consultations")
  })

  it("allows toggling other person form", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relationship&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Formulate your request/i)).toBeInTheDocument())
    expect(screen.getByLabelText(/This consultation also concerns another person/i)).toBeInTheDocument()
    
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Ma relation" } 
    })
    
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))

    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
  })

  it("allows selecting an existing third-party contact", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relationship&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Formulate your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Retrouvailles" } })
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))

    await waitFor(() => expect(screen.getByLabelText(/Use an existing contact/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Use an existing contact/i), { target: { value: "tp-1" } })

    await waitFor(() => {
      expect(screen.getByDisplayValue("1990-01-01")).toBeInTheDocument()
      expect(screen.getByDisplayValue("Paris")).toBeInTheDocument()
    })
  })

  it("AC3: shows save-to-contacts checkbox on other person form", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relationship&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Formulate your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))

    await waitFor(() => expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument())
    expect(screen.getByLabelText(/Save to my contacts/i)).toBeInTheDocument()
  })

  it("AC4: shows nickname field and privacy warning when save-to-contacts is checked", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relationship&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Formulate your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))

    await waitFor(() => expect(screen.getByLabelText(/Save to my contacts/i)).toBeInTheDocument())
    fireEvent.click(screen.getByLabelText(/Save to my contacts/i))

    await waitFor(() => {
      expect(screen.getByLabelText(/Nickname/i)).toBeInTheDocument()
      expect(screen.getByText(/do not use full names/i)).toBeInTheDocument()
    })
  })

  it("AC4: Generate is blocked if save-to-contacts is checked but nickname is empty", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=relationship&astrologerId=auto" })

    await waitFor(() => expect(screen.getByText(/Formulate your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { target: { value: "Synastrie" } })
    fireEvent.click(screen.getByLabelText(/This consultation also concerns another person/i))

    await waitFor(() => expect(screen.getByLabelText(/Birth city/i)).toBeInTheDocument())

    fireEvent.change(screen.getByLabelText(/Birth date/i), { target: { value: "1990-01-01" } })
    fireEvent.change(screen.getByLabelText(/Birth city/i), { target: { value: "Paris" } })
    fireEvent.change(screen.getByLabelText(/Birth country/i), { target: { value: "France" } })

    fireEvent.click(screen.getByLabelText(/Save to my contacts/i))

    await waitFor(() => expect(screen.getByLabelText(/Nickname/i)).toBeInTheDocument())

    const generateBtn = screen.getByRole("button", { name: /Generate consultation/i })
    expect(generateBtn).toBeDisabled()
  })
})
