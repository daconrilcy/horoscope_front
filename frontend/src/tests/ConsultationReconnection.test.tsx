import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import React from "react"

import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { ConsultationProvider, useConsultation } from "../state/consultationStore"

const mockUseContextualGuidance = vi.fn()
const mockUseAstrologer = vi.fn()
const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/astrologers", () => ({
  useAstrologer: (id: string | undefined) => mockUseAstrologer(id),
}))

vi.mock("../api/guidance", () => ({
  useContextualGuidance: () => ({
    mutateAsync: mockUseContextualGuidance,
    isPending: false,
  }),
  GuidanceApiError: class extends Error {
    code: string
    status: number
    constructor(code: string, message: string, status: number) {
      super(message)
      this.code = code
      this.status = status
    }
  }
}))

// Mock useExecuteModule from api/chat to ensure it's NOT called
const mockExecuteModule = vi.fn()
vi.mock("../api/chat", () => ({
  useExecuteModule: () => ({
    mutateAsync: mockExecuteModule,
    isPending: false,
  }),
}))

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

describe("Consultation Reconnection (Story 46.1)", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    mockUseAstrologer.mockReturnValue({
      data: { id: "1", name: "Luna Céleste" },
      isPending: false,
    })
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    localStorage.clear()
  })

  it("AC1 & AC7: generates a dating consultation using contextual guidance and NOT useExecuteModule", async () => {
    mockUseContextualGuidance.mockResolvedValueOnce({
      summary: "Ceci est une guidance amoureuse contextuelle.",
    })

    const TestWrapper = () => {
      const { setType, setAstrologer, setDrawingOption, setContext } = useConsultation()
      React.useEffect(() => {
        setType("dating")
        setAstrologer("1")
        setDrawingOption("none")
        setContext("Je vais à un premier rendez-vous.")
      }, [setType, setAstrologer, setDrawingOption, setContext])
      return <ConsultationResultPage />
    }

    render(
      <MemoryRouter initialEntries={["/consultations/result"]} future={routerFutureFlags}>
        <ConsultationProvider>
          <Routes>
            <Route path="/consultations/result" element={<TestWrapper />} />
            <Route path="/consultations/new" element={<div>New</div>} />
          </Routes>
        </ConsultationProvider>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText("Ceci est une guidance amoureuse contextuelle.")).toBeInTheDocument()
    })

    // Verify AC1 & AC2: correct API called with right payload
    expect(mockUseContextualGuidance).toHaveBeenCalledWith({
      situation: "Je vais à un premier rendez-vous.",
      objective: "relation/amour",
    })

    // Verify AC1: useExecuteModule was NOT called
    expect(mockExecuteModule).not.toHaveBeenCalled()
  })

  it("AC5: handles backend error from contextual guidance", async () => {
    mockUseContextualGuidance.mockRejectedValueOnce(new Error("Service Unavailable"))

    const TestWrapper = () => {
      const { setType, setAstrologer, setDrawingOption, setContext } = useConsultation()
      React.useEffect(() => {
        setType("dating")
        setAstrologer("1")
        setDrawingOption("none")
        setContext("Test context")
      }, [setType, setAstrologer, setDrawingOption, setContext])
      return <ConsultationResultPage />
    }

    render(
      <MemoryRouter initialEntries={["/consultations/result"]} future={routerFutureFlags}>
        <ConsultationProvider>
          <Routes>
            <Route path="/consultations/result" element={<TestWrapper />} />
            <Route path="/consultations/new" element={<div>New</div>} />
          </Routes>
        </ConsultationProvider>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/Erreur lors de la génération/i)).toBeInTheDocument()
    })
  })

  it("AC6: supports loading existing result from history (?id=...)", async () => {
    const mockHistory = [
      {
        id: "hist-123",
        type: "pro",
        astrologerId: "1",
        drawingOption: "none",
        context: "Ma question pro",
        interpretation: "Guidance sauvegardée",
        createdAt: new Date().toISOString(),
      },
    ]
    localStorage.setItem("horoscope_consultations_history", JSON.stringify(mockHistory))

    render(
      <MemoryRouter initialEntries={["/consultations/result?id=hist-123"]} future={routerFutureFlags}>
        <ConsultationProvider>
          <Routes>
            <Route path="/consultations/result" element={<ConsultationResultPage />} />
          </Routes>
        </ConsultationProvider>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText("Guidance sauvegardée")).toBeInTheDocument()
    })
    
    // Should NOT trigger a new generation
    expect(mockUseContextualGuidance).not.toHaveBeenCalled()
  })
})
