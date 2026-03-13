import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import React from "react"

import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { ConsultationProvider, useConsultation, STORAGE_KEY, CHAT_PREFILL_KEY } from "../state/consultationStore"

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

vi.mock("../api/guidance", () => ({
  useContextualGuidance: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}))

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

describe("Consultation Migration (Story 46.3)", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr")
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  it("AC1 & AC2: normalizes legacy history items on load", async () => {
    const legacyHistory = [
      {
        id: "legacy-1",
        type: "dating",
        astrologerId: "1",
        drawingOption: "tarot",
        drawing: { cards: ["L'Amoureux"] },
        context: "Ma question legacy",
        interpretation: "Une interprétation ancienne",
        createdAt: new Date().toISOString(),
      },
    ]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(legacyHistory))

    render(
      <MemoryRouter initialEntries={["/consultations/result?id=legacy-1"]} future={routerFutureFlags}>
        <ConsultationProvider>
          <ConsultationResultPage />
        </ConsultationProvider>
      </MemoryRouter>
    )

    await waitFor(() => {
      // Should display the interpretation normalized to 'summary'
      expect(screen.getByText("Une interprétation ancienne")).toBeInTheDocument()
      expect(screen.getByText("relation/amour")).toBeInTheDocument()
    })

    // Verify drawing section is NOT present (AC2 & AC5 of Story 46.2 reinforced here)
    expect(screen.queryByText(/L'Amoureux/i)).not.toBeInTheDocument()
  })

  it("AC3: saves new items in V2 format", async () => {
    const newResult = {
      id: "new-v2",
      type: "pro" as const,
      astrologerId: "1",
      context: "Ma question pro",
      objective: "objectif pro",
      timeHorizon: "ce trimestre",
      summary: "Résumé pro",
      keyPoints: ["Point 1"],
      actionableAdvice: ["Conseil 1"],
      createdAt: new Date().toISOString(),
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
      <ConsultationProvider>
        <TestWrapper />
      </ConsultationProvider>
    )

    fireEvent.click(screen.getByText("Save"))

    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]")
    expect(stored[0]).toEqual(newResult)
    expect(stored[0]).not.toHaveProperty("drawingOption")
    expect(stored[0]).not.toHaveProperty("interpretation")
  })

  it("AC5: Ouvrir dans le chat uses normalized summary and no drawing info", async () => {
    const legacyHistory = [
      {
        id: "legacy-chat",
        type: "event",
        astrologerId: "1",
        drawingOption: "runes",
        context: "Mon événement legacy",
        interpretation: "Interprétation runes",
        createdAt: new Date().toISOString(),
      },
    ]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(legacyHistory))

    render(
      <MemoryRouter initialEntries={["/consultations/result?id=legacy-chat"]} future={routerFutureFlags}>
        <ConsultationProvider>
          <ConsultationResultPage />
        </ConsultationProvider>
      </MemoryRouter>
    )

    await waitFor(() => screen.getByRole("button", { name: /Ouvrir dans le chat/i }))
    fireEvent.click(screen.getByRole("button", { name: /Ouvrir dans le chat/i }))

    const prefill = sessionStorage.getItem(CHAT_PREFILL_KEY)
    expect(prefill).toContain("Mon événement legacy")
    expect(prefill).toContain("Objectif: événement spécifique")
    expect(prefill).toContain("Interprétation runes")
    // Should NOT contain legacy headers related to drawing
    expect(prefill).not.toContain("Tirage")
    expect(prefill).not.toContain("Cartes")
  })
})
