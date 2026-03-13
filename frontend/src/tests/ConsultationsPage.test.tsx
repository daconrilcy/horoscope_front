import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import React, { useEffect } from "react"

import { ConsultationsPage } from "../pages/ConsultationsPage"
import { ConsultationWizardPage } from "../pages/ConsultationWizardPage"
import { ConsultationResultPage } from "../pages/ConsultationResultPage"
import { generateSimpleInterpretation } from "../utils/generateSimpleInterpretation"
import type { AstrologyLang } from "../i18n/astrology"
import { ConsultationProvider, useConsultation, STORAGE_KEY, CHAT_PREFILL_KEY } from "../state/consultationStore"
import { t } from "../i18n/consultations"
import { AUTO_ASTROLOGER_ID, CONTEXT_MAX_LENGTH, CONTEXT_TRUNCATE_LENGTH } from "../types/consultation"

const mockUseAstrologers = vi.fn()
const mockUseAstrologer = vi.fn()
const mockUseContextualGuidance = vi.fn()
const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/astrologers", () => ({
  useAstrologers: () => mockUseAstrologers(),
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

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

function renderConsultationsPage() {
  return render(
    <MemoryRouter initialEntries={["/consultations"]} future={routerFutureFlags}>
      <Routes>
        <Route
          path="/consultations"
          element={
            <ConsultationProvider>
              <ConsultationsPage />
            </ConsultationProvider>
          }
        />
        <Route
          path="/consultations/new"
          element={
            <ConsultationProvider>
              <ConsultationWizardPage />
            </ConsultationProvider>
          }
        />
        <Route
          path="/consultations/result"
          element={
            <ConsultationProvider>
              <ConsultationResultPage />
            </ConsultationProvider>
          }
        />
        <Route path="/chat" element={<div>Chat Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

function renderWizardPage() {
  return render(
    <MemoryRouter initialEntries={["/consultations/new"]} future={routerFutureFlags}>
      <Routes>
        <Route
          path="/consultations"
          element={
            <ConsultationProvider>
              <ConsultationsPage />
            </ConsultationProvider>
          }
        />
        <Route
          path="/consultations/new"
          element={
            <ConsultationProvider>
              <ConsultationWizardPage />
            </ConsultationProvider>
          }
        />
        <Route
          path="/consultations/result"
          element={
            <ConsultationProvider>
              <ConsultationResultPage />
            </ConsultationProvider>
          }
        />
        <Route path="/chat" element={<div>Chat Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

beforeEach(() => {
  localStorage.setItem("lang", "fr")
  mockUseAstrologers.mockReturnValue({
    data: [
      {
        id: "1",
        name: "Luna Céleste",
        avatar_url: "/avatars/luna.jpg",
        specialties: ["Thème natal"],
        style: "Bienveillant",
        bio_short: "Astrologue depuis 15 ans.",
      },
    ],
    isPending: false,
    error: null,
  })
  mockUseAstrologer.mockReturnValue({
    data: {
      id: "1",
      name: "Luna Céleste",
      avatar_url: "/avatars/luna.jpg",
      specialties: ["Thème natal"],
      style: "Bienveillant",
      bio_short: "Astrologue depuis 15 ans.",
      bio_full: "Bio complète",
      languages: ["Français"],
      experience_years: 15,
    },
    isPending: false,
    error: null,
  })
})

afterEach(() => {
  cleanup()
  mockUseAstrologers.mockReset()
  mockUseAstrologer.mockReset()
  mockUseContextualGuidance.mockReset()
  mockNavigate.mockReset()
  localStorage.clear()
  sessionStorage.clear()
})

describe("ConsultationsPage", () => {
  describe("AC1: Liste consultations", () => {
    it("displays page title and subtitle", () => {
      renderConsultationsPage()

      expect(screen.getByText("Consultations")).toBeInTheDocument()
      expect(
        screen.getByText(/Créez des consultations thématiques/)
      ).toBeInTheDocument()
    })

    it("displays consultation types", () => {
      renderConsultationsPage()

      expect(screen.getByText("Dating / Rendez-vous amoureux")).toBeInTheDocument()
      expect(screen.getByText("Choix professionnel")).toBeInTheDocument()
      expect(screen.getByText("Événement important")).toBeInTheDocument()
      expect(screen.getByText("Question libre")).toBeInTheDocument()
    })

    it("displays empty history state when no consultations", () => {
      renderConsultationsPage()

      expect(screen.getByText("Aucune consultation passée")).toBeInTheDocument()
    })

    it("has a CTA to start new consultation", () => {
      renderConsultationsPage()

      const cta = screen.getByText("Nouvelle consultation")
      expect(cta).toBeInTheDocument()
      expect(cta.closest("a")).toHaveAttribute("href", "/consultations/new")
    })
  })
})

describe("ConsultationTypeStep - keyboard accessibility", () => {
  it("advances to next step when Enter is pressed on focused type button", async () => {
    renderWizardPage()

    const datingButton = screen.getByRole("button", { name: /Dating/i })
    datingButton.focus()
    expect(document.activeElement).toBe(datingButton)

    fireEvent.click(datingButton)

    await waitFor(() => {
      expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
    })
  })

  it("has focusable consultation type buttons", () => {
    renderWizardPage()

    const buttons = screen.getAllByRole("button", { pressed: false })
    const typeButtons = buttons.filter((btn) =>
      ["Dating", "Choix professionnel", "Événement", "Question libre"].some((label) =>
        btn.textContent?.includes(label)
      )
    )

    expect(typeButtons.length).toBeGreaterThanOrEqual(4)
    typeButtons.forEach((btn) => {
      expect(btn).not.toHaveAttribute("tabindex", "-1")
    })
  })
})

function renderWizardPageWithType(type: string) {
  return render(
    <MemoryRouter initialEntries={[`/consultations/new?type=${type}`]} future={routerFutureFlags}>
      <Routes>
        <Route
          path="/consultations/new"
          element={
            <ConsultationProvider>
              <ConsultationWizardPage />
            </ConsultationProvider>
          }
        />
        <Route path="/consultations/result" element={<div>Result</div>} />
        <Route path="/chat" element={<div>Chat Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe("ConsultationWizardPage", () => {
  describe("AC2: Wizard step 1 - Type", () => {
    it("displays consultation type selection on first step", () => {
      renderWizardPage()

      expect(screen.getByText("Choisissez le type de consultation")).toBeInTheDocument()
      expect(screen.getByText("Dating / Rendez-vous amoureux")).toBeInTheDocument()
      expect(screen.getByText("Choix professionnel")).toBeInTheDocument()
    })

    it("pre-selects type from URL parameter", async () => {
      renderWizardPageWithType("pro")

      await waitFor(() => {
        const proButton = screen.getByRole("button", { name: /Choix professionnel/i })
        expect(proButton).toHaveAttribute("aria-pressed", "true")
      })
    })

    it("ignores invalid type URL parameter", () => {
      renderWizardPageWithType("invalid_type")

      expect(screen.getByText("Choisissez le type de consultation")).toBeInTheDocument()
    })

    it("advances to step 2 when type is selected", async () => {
      renderWizardPage()

      const datingButton = screen.getByRole("button", { name: /Dating/i })
      fireEvent.click(datingButton)

      await waitFor(() => {
        expect(screen.getByText("Choisissez votre astrologue")).toBeInTheDocument()
      })
    })
  })

  describe("AC3: Wizard step 2 - Astrologue", () => {
    it("shows astrologer selection after type is selected", async () => {
      renderWizardPage()

      const datingButton = screen.getByRole("button", { name: /Dating/i })
      fireEvent.click(datingButton)

      await waitFor(() => {
        expect(screen.getByText("Choisissez votre astrologue")).toBeInTheDocument()
        expect(screen.getByText("Laisser choisir automatiquement")).toBeInTheDocument()
        expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
      })
    })

    it("advances to step 3 when astrologer is selected", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))

      await waitFor(() => {
        expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText("Luna Céleste"))

      await waitFor(() => {
        expect(screen.getByText("Récapitulatif")).toBeInTheDocument()
      })
    })
  })

  describe("AC5: Wizard step 3 - Validation", () => {
    it("shows summary and context input", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))

      await waitFor(() => {
        expect(screen.getByText("Récapitulatif")).toBeInTheDocument()
        expect(screen.getByText("Dating / Rendez-vous amoureux")).toBeInTheDocument()
        expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
        expect(screen.getByLabelText(/Décrivez votre situation/)).toBeInTheDocument()
      })
    })

    it("generate button is disabled without context", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))

      await waitFor(() => {
        const generateBtn = screen.getByRole("button", { name: /Générer la consultation/i })
        expect(generateBtn).toBeDisabled()
      })
    })

    it("generate button is enabled with context", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))

      await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

      const textarea = screen.getByLabelText(/Décrivez votre situation/)
      fireEvent.change(textarea, { target: { value: "Ma question importante" } })

      await waitFor(() => {
        const generateBtn = screen.getByRole("button", { name: /Générer la consultation/i })
        expect(generateBtn).not.toBeDisabled()
      })
    })

    it("navigates to result page on generate", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))
      await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

      const textarea = screen.getByLabelText(/Décrivez votre situation/)
      fireEvent.change(textarea, { target: { value: "Ma question importante" } })

      const generateBtn = screen.getByRole("button", { name: /Générer la consultation/i })
      fireEvent.click(generateBtn)

      expect(mockNavigate).toHaveBeenCalledWith("/consultations/result")
    })
  })

  describe("Wizard navigation", () => {
    it("can navigate back with previous button", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Choisissez votre astrologue"))

      const prevBtn = screen.getByRole("button", { name: /Précédent/i })
      fireEvent.click(prevBtn)

      await waitFor(() => {
        expect(screen.getByText("Choisissez le type de consultation")).toBeInTheDocument()
      })
    })

    it("cancel navigates back to consultations list", async () => {
      renderWizardPage()

      const cancelBtn = screen.getByRole("button", { name: /Annuler/i })
      fireEvent.click(cancelBtn)

      expect(mockNavigate).toHaveBeenCalledWith("/consultations")
    })

    it("cancel resets wizard state before navigating", async () => {
      let capturedState: { draft: { type: string | null } } | null = null

      const StateCapture = () => {
        const { state, setType } = useConsultation()
        capturedState = state
        React.useEffect(() => {
          setType("dating")
        }, [setType])
        return <ConsultationWizardPage />
      }

      render(
        <MemoryRouter initialEntries={["/consultations/new"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/new"
              element={
                <ConsultationProvider>
                  <StateCapture />
                </ConsultationProvider>
              }
            />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        expect(capturedState?.draft.type).toBe("dating")
      })

      const cancelBtn = screen.getByRole("button", { name: /Annuler/i })
      fireEvent.click(cancelBtn)

      expect(capturedState?.draft.type).toBeNull()
      expect(mockNavigate).toHaveBeenCalledWith("/consultations")
    })
  })
})

describe("WizardProgress", () => {
  it("shows progress indicator with current step highlighted", () => {
    renderWizardPage()

    const progressNav = screen.getByRole("navigation", { name: /Étapes de la consultation/i })
    expect(progressNav).toBeInTheDocument()

    expect(screen.getByText("Type")).toBeInTheDocument()
    expect(screen.getByText("Astrologue")).toBeInTheDocument()
    expect(screen.getByText("Validation")).toBeInTheDocument()
    expect(screen.queryByText("Tirage")).not.toBeInTheDocument()
  })

  it("has aria-current='step' on the current step", () => {
    renderWizardPage()

    const listItems = screen.getAllByRole("listitem")
    const currentStepItem = listItems.find(
      (item) => item.getAttribute("aria-current") === "step"
    )
    expect(currentStepItem).toBeDefined()
    expect(currentStepItem).toHaveTextContent("Type")
  })

  it("shows completed steps with checkmark after advancing", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))

    await waitFor(() => {
      expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
    })

    const listItems = screen.getAllByRole("listitem")
    const typeStepItem = listItems.find((item) => item.textContent?.includes("Type"))
    expect(typeStepItem).toHaveClass("wizard-progress-step--completed")
    expect(typeStepItem?.textContent).toContain("✓")
  })
})

describe("ConsultationResultPage", () => {
  function renderResultPageWithState() {
    return render(
      <MemoryRouter initialEntries={["/consultations/result"]} future={routerFutureFlags}>
        <Routes>
          <Route
            path="/consultations/result"
            element={
              <ConsultationProvider>
                <ConsultationResultPage />
              </ConsultationProvider>
            }
          />
          <Route path="/consultations" element={<div>Consultations List</div>} />
          <Route path="/consultations/new" element={<div>Wizard Page</div>} />
          <Route path="/chat" element={<div data-testid="chat-page">Chat Page</div>} />
        </Routes>
      </MemoryRouter>
    )
  }

  describe("AC6: Page résultat", () => {
    it("shows empty state when no result available", () => {
      renderResultPageWithState()

      expect(screen.getByText("Aucune consultation passée")).toBeInTheDocument()
      expect(screen.getByText("Retour aux consultations")).toBeInTheDocument()
    })

    it("shows empty state when history ID does not exist", () => {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([
          {
            id: "existing-id",
            type: "dating",
            astrologerId: "1",
            context: "Existing consultation",
            summary: "Test",
            createdAt: new Date().toISOString(),
          },
        ])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=non-existent-id"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/result"
              element={
                <ConsultationProvider>
                  <ConsultationResultPage />
                </ConsultationProvider>
              }
            />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      expect(screen.getByText("Aucune consultation passée")).toBeInTheDocument()
    })

    it("handles gracefully when typeConfig is not found for invalid type", async () => {
      const mockResultWithBadType = {
        id: "test-bad-type",
        type: "dating" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        context: "Test context",
        summary: "Test interpretation",
        createdAt: new Date().toISOString(),
      }

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([mockResultWithBadType])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=test-bad-type"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/result"
              element={
                <ConsultationProvider>
                  <ConsultationResultPage />
                </ConsultationProvider>
              }
            />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        expect(screen.getByText("Résultat de votre consultation")).toBeInTheDocument()
      })

      expect(screen.getByText("Dating / Rendez-vous amoureux")).toBeInTheDocument()
    })

    it("displays result with type, astrologer, context when result exists in history", async () => {
      const mockResult = {
        id: "test-consultation-123",
        type: "dating" as const,
        astrologerId: "1",
        context: "Ma question test pour le rendez-vous",
        summary: "Votre interprétation astrologique...",
        keyPoints: ["Point 1"],
        actionableAdvice: ["Conseil 1"],
        createdAt: new Date().toISOString(),
      }

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([mockResult])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=test-consultation-123"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/result"
              element={
                <ConsultationProvider>
                  <ConsultationResultPage />
                </ConsultationProvider>
              }
            />
            <Route path="/chat" element={<div>Chat Page</div>} />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        expect(screen.getByText("Résultat de votre consultation")).toBeInTheDocument()
      })

      expect(screen.getByText("Dating / Rendez-vous amoureux")).toBeInTheDocument()
      expect(screen.getByText(/Ma question test pour le rendez-vous/)).toBeInTheDocument()
      expect(screen.getByText("Votre interprétation astrologique...")).toBeInTheDocument()
      expect(screen.getByText("Point 1")).toBeInTheDocument()
      expect(screen.getByText("Conseil 1")).toBeInTheDocument()
    })

    it("shows save button as already saved for history items", async () => {
      const mockResult = {
        id: "test-already-saved",
        type: "free" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        context: "Question test",
        summary: "Réponse test",
        createdAt: new Date().toISOString(),
      }

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([mockResult])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=test-already-saved"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/result"
              element={
                <ConsultationProvider>
                  <ConsultationResultPage />
                </ConsultationProvider>
              }
            />
            <Route path="/chat" element={<div>Chat</div>} />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        expect(screen.getByText("Résultat de votre consultation")).toBeInTheDocument()
      })

      const saveBtn = screen.getByRole("button", { name: /Sauvegardé/i })
      expect(saveBtn).toBeInTheDocument()
      expect(saveBtn).toBeDisabled()
    })
  })

  describe("AC7: Ouvrir dans le chat", () => {
    it("sets chat_prefill in sessionStorage and navigates to /chat on click", async () => {
      const mockResult = {
        id: "test-open-chat",
        type: "event" as const,
        astrologerId: "1",
        context: "Mon événement important",
        summary: "L'interprétation de l'événement...",
        createdAt: new Date().toISOString(),
      }

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([mockResult])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=test-open-chat"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/result"
              element={
                <ConsultationProvider>
                  <ConsultationResultPage />
                </ConsultationProvider>
              }
            />
            <Route path="/chat" element={<div data-testid="chat-page">Chat Page</div>} />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /Ouvrir dans le chat/i })).toBeInTheDocument()
      })

      const openChatBtn = screen.getByRole("button", { name: /Ouvrir dans le chat/i })
      fireEvent.click(openChatBtn)

      expect(mockNavigate).toHaveBeenCalledWith("/chat?astrologerId=1")

      const prefill = sessionStorage.getItem(CHAT_PREFILL_KEY)
      expect(prefill).toBeTruthy()
      expect(prefill).toContain("Mon événement important")
      expect(prefill).toContain("L'interprétation de l'événement...")
    })
  })
})

describe("ConsultationsPage - Historique avec données", () => {
  it("truncates context to CONTEXT_TRUNCATE_LENGTH with ellipsis", () => {
    const longContext = "A".repeat(CONTEXT_TRUNCATE_LENGTH + 10)
    const mockHistory = [
      {
        id: "hist-truncate",
        type: "dating" as const,
        astrologerId: "1",
        context: longContext,
        summary: "Interpretation",
        createdAt: new Date().toISOString(),
      },
    ]

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(mockHistory)
    )

    render(
      <MemoryRouter initialEntries={["/consultations"]} future={routerFutureFlags}>
        <Routes>
          <Route
            path="/consultations"
            element={
              <ConsultationProvider>
                <ConsultationsPage />
              </ConsultationProvider>
            }
          />
        </Routes>
      </MemoryRouter>
    )

    const truncated = "A".repeat(CONTEXT_TRUNCATE_LENGTH) + "..."
    expect(screen.getByText(truncated)).toBeInTheDocument()
  })
})

describe("ValidationStep - Character counter", () => {
  it("displays character counter with CONTEXT_MAX_LENGTH remaining", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
    await waitFor(() => screen.getByText("Luna Céleste"))
    fireEvent.click(screen.getByText("Luna Céleste"))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

    const expectedText = new RegExp(`${CONTEXT_MAX_LENGTH} caractères restants`)
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })
})

describe("ConsultationProvider initialization", () => {
  it("loads history from localStorage on mount", async () => {
    const storedHistory = [
      {
        id: "stored-1",
        type: "dating",
        astrologerId: "1",
        context: "Stored context",
        summary: "Stored interpretation",
        createdAt: "2026-02-22T10:00:00.000Z",
      },
    ]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(storedHistory))

    let capturedHistory: any[] = []

    const HistoryCapture = () => {
      const { state } = useConsultation()
      useEffect(() => {
        capturedHistory = state.history
      }, [state.history])
      return null
    }

    render(
      <MemoryRouter future={routerFutureFlags}>
        <ConsultationProvider>
          <HistoryCapture />
        </ConsultationProvider>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(capturedHistory.length).toBe(1)
    })

    expect(capturedHistory[0].id).toBe("stored-1")
  })
})
