import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import React from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { readFileSync } from "node:fs"
import { resolve } from "node:path"

import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { ConsultationProvider, useConsultation, STORAGE_KEY, CHAT_PREFILL_KEY } from "../state/consultationStore"
import { tConsultations } from "../i18n/consultations"

const mockNavigate = vi.fn()
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/astrologers", () => ({
  useAstrologer: () => ({ data: { name: "Luna Céleste" }, isPending: false }),
}))

vi.mock("../api/consultations", () => ({
  useConsultationGenerate: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }
const consultationLabelsPath = resolve(process.cwd(), "src/i18n/consultations.ts")

describe("Consultation contract guards", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  it("renders canonical history items with structured sections", async () => {
    const history = [
      {
        id: "canonical-1",
        type: "dating",
        astrologerId: "1",
        context: "Ma question",
        objective: "relation/amour",
        summary: "Une interprétation structurée",
        sections: [
          {
            id: "consultation_basis",
            title: "Base technique",
            content: "",
            blocks: [{ kind: "paragraph", text: "Base technique masquée." }],
          },
          {
            id: "overview",
            title: "Vue d'ensemble",
            content: "",
            blocks: [{ kind: "paragraph", text: "Bloc canonique rendu." }],
          },
        ],
        createdAt: new Date().toISOString(),
      },
    ]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history))

    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/consultations/result?id=canonical-1"]} future={routerFutureFlags}>
          <ConsultationProvider>
            <ConsultationResultPage />
          </ConsultationProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText("Une interprétation structurée")).toBeInTheDocument()
      expect(screen.getByText("Bloc canonique rendu.")).toBeInTheDocument()
      expect(screen.getByText("relation/amour")).toBeInTheDocument()
      expect(screen.queryByText("Base technique masquée.")).not.toBeInTheDocument()
      expect(container.querySelector(".is-consultation-result-page")).not.toBeNull()
      expect(container.querySelector(".result-astrologer-pill")).not.toBeNull()
    })
  })

  it("conserve les contrats runtime CSS et query key de la page résultat", () => {
    const source = readFileSync(resolve(process.cwd(), "src/pages/ConsultationResultPage.tsx"), "utf8")

    expect(source).toContain('queryKey: ["consultation-third-parties"]')
    expect(source).toContain('s.id !== "consultation_basis"')
    expect(source).toContain('className="is-consultation-result-page"')
    expect(source).toContain('className="result-astrologer-pill"')
    expect(source).not.toContain("session-third-parties")
    expect(source).not.toContain("activity-third-parties")
    expect(source).not.toContain("session_basis")
    expect(source).not.toContain("result-person-pill")
  })

  it("saves new 47.x items with sections and metadata", async () => {
    const newResult = {
      id: "new-47",
      type: "period" as const,
      astrologerId: "1",
      context: "Ma question 47",
      objective: "objectif 47",
      summary: "Résumé 47",
      keyPoints: ["Point 1"],
      actionableAdvice: ["Conseil 1"],
      createdAt: new Date().toISOString(),
      sections: [{ id: "test", title: "Titre Test", content: "Contenu Test" }],
      fallbackMode: "user_no_birth_time",
      precisionLevel: "medium"
    }

    const TestWrapper = () => {
      const { setResult, saveToHistory } = useConsultation()
      React.useEffect(() => {
        setResult(newResult)
      }, [setResult])
      return (
        <button onClick={() => saveToHistory(newResult)}>Save</button>
      )
    }

    render(
      <QueryClientProvider client={queryClient}>
        <ConsultationProvider>
          <TestWrapper />
        </ConsultationProvider>
      </QueryClientProvider>
    )

    fireEvent.click(screen.getByText("Save"))

    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]")
    expect(stored[0].id).toBe("new-47")
    expect(stored[0].sections).toBeDefined()
    expect(stored[0].fallbackMode).toBe("user_no_birth_time")
  })

  it("exposes canonical consultation labels without retired vocabulary", () => {
    expect({
      fr: tConsultations("type_dating", "fr"),
      en: tConsultations("type_dating", "en"),
      es: tConsultations("type_dating", "es"),
    }).toEqual({
      fr: "Dating / Rendez-vous amoureux",
      en: "Dating / Romantic meetup",
      es: "Cita / Encuentro romántico",
    })

    expect({
      fr: tConsultations("type_pro", "fr"),
      en: tConsultations("type_pro", "en"),
      es: tConsultations("type_pro", "es"),
    }).toEqual({
      fr: "Choix professionnel",
      en: "Professional choice",
      es: "Elección profesional",
    })

    expect({
      fr: tConsultations("type_event", "fr"),
      en: tConsultations("type_event", "en"),
      es: tConsultations("type_event", "es"),
    }).toEqual({
      fr: "Événement important",
      en: "Important event",
      es: "Evento importante",
    })

    expect({
      fr: tConsultations("type_free", "fr"),
      en: tConsultations("type_free", "en"),
      es: tConsultations("type_free", "es"),
    }).toEqual({
      fr: "Question libre",
      en: "Free question",
      es: "Pregunta libre",
    })

    const consultationLabelsSource = readFileSync(consultationLabelsPath, "utf8")
    expect(consultationLabelsSource).not.toMatch(/retired-api-vocabulary/i)
  })
})
