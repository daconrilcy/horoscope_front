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

describe("Consultation Migration (Epic 47)", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  it("normalizes legacy 46.x history items on load", async () => {
    const legacyHistory = [
      {
        id: "legacy-1",
        type: "dating",
        astrologerId: "1",
        context: "Ma question legacy",
        summary: "Une interprétation 46.x",
        createdAt: new Date().toISOString(),
      },
    ]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(legacyHistory))

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/consultations/result?id=legacy-1"]} future={routerFutureFlags}>
          <ConsultationProvider>
            <ConsultationResultPage />
          </ConsultationProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText("Une interprétation 46.x")).toBeInTheDocument()
      expect(screen.getByText("relation/amour")).toBeInTheDocument()
    })
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

  it("exposes canonical consultation labels without legacy vocabulary", () => {
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
    expect(consultationLabelsSource).not.toMatch(/legacy/i)
  })
})
