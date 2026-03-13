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

describe("ConsultationWizardPage - Story 47.3 Flow", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  it("advances from Type to Framing", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

    const periodButton = screen.getByRole("button", { name: /Period/i })
    fireEvent.click(periodButton)

    await waitFor(() => {
      expect(screen.getByText(/Frame your request/i)).toBeInTheDocument()
    })
  })

  it("advances from Framing to Collection with valid context", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

    // Step 1: Type
    const periodButton = screen.getByRole("button", { name: /Period/i })
    fireEvent.click(periodButton)

    // Step 2: Frame
    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    
    const textarea = screen.getByLabelText(/Describe your situation/i)
    fireEvent.change(textarea, { target: { value: "Ma question test sur mon futur." } })
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    await waitFor(() => expect(nextBtn).not.toBeDisabled())
    fireEvent.click(nextBtn)

    // Step 3: Collection
    await waitFor(() => {
      expect(screen.getByText(/Additional information/i)).toBeInTheDocument()
    })
  })

  it("shows other person form in Collection step for Relation type", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

    // Step 1: Type (Relation)
    const relationBtn = screen.getByRole("button", { name: /Relation/i })
    fireEvent.click(relationBtn)

    // Step 2: Frame
    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Relation avec mon conjoint" } 
    })
    
    const nextBtn = screen.getByRole("button", { name: /Next/i })
    await waitFor(() => expect(nextBtn).not.toBeDisabled())
    fireEvent.click(nextBtn)

    // Step 3: Collection
    await waitFor(() => {
      expect(screen.getByText(/Information about the other person/i)).toBeInTheDocument()
    })
    
    expect(screen.getByLabelText(/Birth date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Birth place/i)).toBeInTheDocument()
  })

  it("advances to Summary step and allows generation without choosing an astrologer", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

    // Step 1: Type
    fireEvent.click(screen.getByRole("button", { name: /Period/i }))

    // Step 2: Frame
    await waitFor(() => expect(screen.getByText(/Frame your request/i)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Describe your situation/i), { 
      target: { value: "Test context" } 
    })
    
    const nextBtn1 = screen.getByRole("button", { name: /Next/i })
    await waitFor(() => expect(nextBtn1).not.toBeDisabled())
    fireEvent.click(nextBtn1)

    // Step 3: Collection
    await waitFor(() => expect(screen.getByText(/Additional information/i)).toBeInTheDocument())
    
    const nextBtn2 = screen.getByRole("button", { name: /Next/i })
    await waitFor(() => expect(nextBtn2).not.toBeDisabled())
    fireEvent.click(nextBtn2)

    // Step 4: Summary
    await waitFor(() => {
      expect(screen.getByText(/Final verification/i)).toBeInTheDocument()
    })

    const generateBtn = screen.getByRole("button", { name: /Generate consultation/i })
    expect(generateBtn).not.toBeDisabled()
  })
})
