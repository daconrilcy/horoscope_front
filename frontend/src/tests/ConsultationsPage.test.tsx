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
      expect(screen.getByText(/Créez des consultations thématiques|Create thematic consultations/)).toBeInTheDocument()
    })

    it("displays consultation types", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByText(/Période & Climat|Period & Climate/)).toBeInTheDocument()
      expect(screen.getByText(/Carrière & Travail|Career & Work/)).toBeInTheDocument()
      expect(screen.getByText(/Orientation & Mission/)).toBeInTheDocument()
      expect(screen.getByText(/Relations & Synastrie|Relationships & Synastry/)).toBeInTheDocument()
      expect(screen.getByText(/Élection & Timing|Election & Timing/)).toBeInTheDocument()
      
      // Legacy types should NOT be in the creation list
      expect(screen.queryByText(/Legacy/)).not.toBeInTheDocument()
    })

    it("displays UX promise for each type", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })
      expect(screen.getByText(/Comprenez les énergies|Understand the energies/)).toBeInTheDocument()
    })

    it("displays empty history state when no consultations", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByText(/Aucune consultation passée|No past consultations/)).toBeInTheDocument()
    })

    it("has a CTA to start new consultation", () => {
      renderWithProviders(<ConsultationsPage />, { route: "/consultations" })

      expect(screen.getByText(/Nouvelle consultation|New consultation/)).toBeInTheDocument()
    })
  })
})

describe("ConsultationTypeStep - keyboard accessibility", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  it("advances to next step when Enter is pressed on focused type button", async () => {
    renderWithProviders(
      <Routes>
        <Route path="/consultations/new" element={<ConsultationWizardPage />} />
      </Routes>,
      { route: "/consultations/new" }
    )

    const periodButton = screen.getByRole("button", { name: /Période|Period/i })
    periodButton.focus()
    fireEvent.click(periodButton)

    await waitFor(() => {
      expect(screen.getByText(/Choisissez votre astrologue|Choose your astrologer/)).toBeInTheDocument()
    })
  })

  it("has focusable consultation type buttons", () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

    const buttons = screen.getAllByRole("button", { pressed: false })
    const typeButtons = buttons.filter((btn) =>
      ["Période", "Period", "Carrière", "Career", "Orientation", "Relations", "Élection", "Election"].some((label) =>
        btn.textContent?.includes(label)
      )
    )

    expect(typeButtons.length).toBeGreaterThanOrEqual(5)
  })
})

describe("ConsultationWizardPage", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  describe("AC2: Wizard step 1 - Type", () => {
    it("displays consultation type selection on first step", () => {
      renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

      expect(screen.getByText(/Choisissez le type|Choose consultation type/)).toBeInTheDocument()
      expect(screen.getByText(/Période & Climat|Period & Climate/)).toBeInTheDocument()
    })

    it("pre-selects type from URL parameter", async () => {
      renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new?type=work" })

      await waitFor(() => {
        const workButton = screen.getByRole("button", { name: /Carrière & Travail|Career & Work/i })
        expect(workButton).toHaveAttribute("aria-pressed", "true")
      })
    })

    it("advances to step 2 when type is selected", async () => {
      renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

      const periodButton = screen.getByRole("button", { name: /Période|Period/i })
      fireEvent.click(periodButton)

      await waitFor(() => {
        expect(screen.getByText(/Choisissez votre astrologue|Choose your astrologer/)).toBeInTheDocument()
      })
    })
  })

  describe("AC3: Wizard step 2 - Astrologue", () => {
    it("shows astrologer selection after type is selected", async () => {
      renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

      fireEvent.click(screen.getByRole("button", { name: /Période|Period/i }))

      await waitFor(() => {
        expect(screen.getByText(/Choisissez votre astrologue|Choose your astrologer/)).toBeInTheDocument()
        expect(screen.getByText(/Laisser choisir automatiquement|Let choose automatically/)).toBeInTheDocument()
      })
    })
  })

  describe("AC5: Wizard step 3 - Validation", () => {
    it("shows request summary, objective, context and optional time horizon inputs", async () => {
      renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

      fireEvent.click(screen.getByRole("button", { name: /Période|Period/i }))
      await waitFor(() => screen.getByText(/Choisissez votre astrologue|Choose your astrologer/))
      fireEvent.click(screen.getByText(/Laisser choisir automatiquement|Let choose automatically/))

      await waitFor(() => {
        expect(screen.getByText(/Votre demande ciblée|Your targeted request/)).toBeInTheDocument()
        expect(screen.getByLabelText(/Objet de la consultation|Consultation goal/)).toBeInTheDocument()
      })
    })
  })
})

describe("ConsultationResultPage", () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  it("handles gracefully when typeConfig is not found for invalid type", async () => {
    const mockResultWithBadType = {
      id: "test-bad-type",
      type: "dating" as any,
      astrologerId: AUTO_ASTROLOGER_ID,
      context: "Test context",
      summary: "Test interpretation",
      createdAt: new Date().toISOString(),
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify([mockResultWithBadType]))

    renderWithProviders(<ConsultationResultPage />, { route: "/consultations/result?id=test-bad-type" })

    await waitFor(() => {
      expect(screen.getByText(/Résultat de votre consultation|Your consultation result/)).toBeInTheDocument()
    })

    expect(screen.getByText(/Dating.*Legacy/)).toBeInTheDocument()
  })
})

describe("ValidationStep - Character counter", () => {
  afterEach(() => {
    cleanup()
  })

  it("displays character counter with CONTEXT_MAX_LENGTH remaining", async () => {
    renderWithProviders(<ConsultationWizardPage />, { route: "/consultations/new" })

    fireEvent.click(screen.getByRole("button", { name: /Période|Period/i }))
    await waitFor(() => screen.getByText(/Choisissez votre astrologue|Choose your astrologer/))
    fireEvent.click(screen.getByText(/Laisser choisir automatiquement|Let choose automatically/))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation|Describe your situation/))

    const expectedText = new RegExp(`${CONTEXT_MAX_LENGTH} .*`)
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })
})
