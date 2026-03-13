import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import React from "react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { ConsultationProvider, useConsultation } from "../state/consultationStore"

const mockGenerate = vi.fn()
const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/astrologers", () => ({
  useAstrologer: () => ({
    data: { id: "1", name: "Luna Céleste" },
    isPending: false,
  }),
}))

vi.mock("../api/consultations", () => ({
  useConsultationGenerate: () => ({
    mutateAsync: mockGenerate,
    isPending: false,
  }),
}))

const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
}

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  })

function renderResultPage(
  ui: React.ReactElement,
  route = "/consultations/result",
) {
  return render(
    <QueryClientProvider client={createTestQueryClient()}>
      <MemoryRouter initialEntries={[route]} future={routerFutureFlags}>
        <ConsultationProvider>
          <Routes>
            <Route path="/consultations/result" element={ui} />
            <Route path="/consultations/new" element={<div>New</div>} />
          </Routes>
        </ConsultationProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe("Consultation Reconnection", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    mockGenerate.mockReset()
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    localStorage.clear()
  })

  it("génère une consultation via le contrat consultations dédié", async () => {
    mockGenerate.mockResolvedValueOnce({
      data: {
        consultation_id: "consult-1",
        consultation_type: "dating",
        status: "nominal",
        precision_level: "high",
        fallback_mode: null,
        safeguard_issue: null,
        route_key: "dating_full",
        summary: "Ceci est une guidance amoureuse contextuelle.",
        sections: [
          { id: "key_points", title: "Points clés", content: "Point 1\nPoint 2" },
          { id: "advice", title: "Conseils", content: "Conseil 1" },
        ],
        chat_prefill: "prefill",
        metadata: {},
      },
      meta: {
        request_id: "req-1",
        contract_version: "consultation-generate.v1",
      },
    })

    const TestWrapper = () => {
      const { setType, setAstrologer, setContext, setObjective, setTimeHorizon } =
        useConsultation()

      React.useEffect(() => {
        setType("dating")
        setAstrologer("1")
        setContext("Je vais à un premier rendez-vous.")
        setObjective("comprendre la dynamique de ce rendez-vous")
        setTimeHorizon("ce soir")
      }, [setType, setAstrologer, setContext, setObjective, setTimeHorizon])

      return <ConsultationResultPage />
    }

    renderResultPage(<TestWrapper />)

    await waitFor(() => {
      expect(
        screen.getByText("Ceci est une guidance amoureuse contextuelle.")
      ).toBeInTheDocument()
    })

    expect(mockGenerate).toHaveBeenCalledWith({
      consultation_type: "dating",
      question: "Je vais à un premier rendez-vous.",
      horizon: "ce soir",
      astrologer_id: "1",
      other_person: undefined,
    })
  })

  it("affiche une erreur backend de génération", async () => {
    mockGenerate.mockRejectedValueOnce(new Error("Service Unavailable"))

    const TestWrapper = () => {
      const { setType, setAstrologer, setContext } = useConsultation()

      React.useEffect(() => {
        setType("dating")
        setAstrologer("1")
        setContext("Test context")
      }, [setType, setAstrologer, setContext])

      return <ConsultationResultPage />
    }

    renderResultPage(<TestWrapper />)

    await waitFor(() => {
      expect(screen.getByText("Service Unavailable")).toBeInTheDocument()
    })
  })

  it("recharge un résultat existant depuis l'historique avec ?id=", async () => {
    const mockHistory = [
      {
        id: "hist-123",
        type: "pro",
        astrologerId: "1",
        context: "Ma question pro",
        objective: "préparer ma prochaine décision pro",
        summary: "Guidance sauvegardée",
        createdAt: new Date().toISOString(),
        keyPoints: [],
        actionableAdvice: [],
      },
    ]
    localStorage.setItem("horoscope_consultations_history", JSON.stringify(mockHistory))

    renderResultPage(<ConsultationResultPage />, "/consultations/result?id=hist-123")

    await waitFor(() => {
      expect(screen.getByText("Guidance sauvegardée")).toBeInTheDocument()
    })

    expect(mockGenerate).not.toHaveBeenCalled()
  })
})
