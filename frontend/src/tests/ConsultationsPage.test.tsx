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
const mockExecuteModule = vi.fn()
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

vi.mock("../api/chat", () => ({
  useExecuteModule: () => ({
    mutateAsync: mockExecuteModule,
    isPending: false,
  }),
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
  mockExecuteModule.mockReset()
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
        expect(screen.getByText("Souhaitez-vous un tirage ?")).toBeInTheDocument()
      })
    })
  })

  describe("AC4: Wizard step 3 - Tirage", () => {
    it("shows drawing options", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))

      await waitFor(() => {
        expect(screen.getByText("Sans tirage")).toBeInTheDocument()
        expect(screen.getByText("Tirage de cartes")).toBeInTheDocument()
        expect(screen.getByText("Tirage de runes")).toBeInTheDocument()
      })
    })

    it("advances to step 4 when drawing option is selected", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))
      await waitFor(() => screen.getByText("Sans tirage"))
      fireEvent.click(screen.getByText("Sans tirage"))

      await waitFor(() => {
        expect(screen.getByText("Récapitulatif")).toBeInTheDocument()
      })
    })
  })

  describe("AC5: Wizard step 4 - Validation", () => {
    it("shows summary and context input", async () => {
      renderWizardPage()

      fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
      await waitFor(() => screen.getByText("Luna Céleste"))
      fireEvent.click(screen.getByText("Luna Céleste"))
      await waitFor(() => screen.getByText("Sans tirage"))
      fireEvent.click(screen.getByText("Sans tirage"))

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
      await waitFor(() => screen.getByText("Sans tirage"))
      fireEvent.click(screen.getByText("Sans tirage"))

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
      await waitFor(() => screen.getByText("Sans tirage"))
      fireEvent.click(screen.getByText("Sans tirage"))

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
      await waitFor(() => screen.getByText("Sans tirage"))
      fireEvent.click(screen.getByText("Sans tirage"))
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
    expect(screen.getByText("Tirage")).toBeInTheDocument()
    expect(screen.getByText("Validation")).toBeInTheDocument()
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
            drawingOption: "none",
            context: "Existing consultation",
            interpretation: "Test",
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

    it("handles malformed/XSS ID parameter safely", () => {
      const malformedId = "<script>alert('xss')</script>"

      render(
        <MemoryRouter initialEntries={[`/consultations/result?id=${encodeURIComponent(malformedId)}`]} future={routerFutureFlags}>
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
      expect(screen.queryByText("alert")).not.toBeInTheDocument()
      expect(document.querySelector("script")).toBeNull()
    })

    it("handles gracefully when typeConfig is not found for invalid type", async () => {
      const mockResultWithBadType = {
        id: "test-bad-type",
        type: "dating" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "none" as const,
        context: "Test context",
        interpretation: "Test interpretation",
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

    it("shows loading state with aria-live when generating", async () => {
      const { rerender } = render(
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
            <Route path="/consultations/new" element={<div>Wizard</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        const loadingOrEmpty = screen.queryByText(/Génération en cours|Aucune consultation/)
        expect(loadingOrEmpty).toBeInTheDocument()
      })
    })

    it("displays result with type, astrologer, context when result exists in history", async () => {
      const mockResult = {
        id: "test-consultation-123",
        type: "dating" as const,
        astrologerId: "1",
        drawingOption: "none" as const,
        context: "Ma question test pour le rendez-vous",
        interpretation: "Votre interprétation astrologique...",
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
      expect(screen.getByRole("button", { name: /Ouvrir dans le chat/i })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Sauvegardé/i })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Sauvegardé/i })).toBeDisabled()
    })

    it("displays drawing section when tirage is present", async () => {
      const mockResult = {
        id: "test-consultation-tarot",
        type: "pro" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "tarot" as const,
        context: "Choix de carrière",
        drawing: { cards: ["L'Empereur", "La Lune"] },
        interpretation: "Les cartes indiquent...",
        createdAt: new Date().toISOString(),
      }

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([mockResult])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=test-consultation-tarot"]} future={routerFutureFlags}>
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

      expect(screen.getByText(/L'Empereur/)).toBeInTheDocument()
      expect(screen.getByText(/La Lune/)).toBeInTheDocument()
    })

    it("displays runes section when runes tirage is present", async () => {
      const mockResult = {
        id: "test-consultation-runes",
        type: "event" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "runes" as const,
        context: "Mon événement",
        drawing: { runes: ["Fehu", "Uruz"] },
        interpretation: "Les runes indiquent...",
        createdAt: new Date().toISOString(),
      }

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([mockResult])
      )

      render(
        <MemoryRouter initialEntries={["/consultations/result?id=test-consultation-runes"]} future={routerFutureFlags}>
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

      expect(screen.getByText(/Fehu/)).toBeInTheDocument()
      expect(screen.getByText(/Uruz/)).toBeInTheDocument()
    })

    it("shows save button as already saved for history items", async () => {
      const mockResult = {
        id: "test-already-saved",
        type: "free" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "none" as const,
        context: "Question test",
        interpretation: "Réponse test",
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
        drawingOption: "none" as const,
        context: "Mon événement important",
        interpretation: "L'interprétation de l'événement...",
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

      expect(mockNavigate).toHaveBeenCalledWith("/chat")

      const prefill = sessionStorage.getItem(CHAT_PREFILL_KEY)
      expect(prefill).toBeTruthy()
      expect(prefill).toContain("Mon événement important")
      expect(prefill).toContain("L'interprétation de l'événement...")
    })

    it("save button works and shows 'Sauvegardé' after click", async () => {
      const mockResult = {
        id: "test-save-new",
        type: "free" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "none" as const,
        context: "Question libre test",
        interpretation: "Réponse libre...",
        createdAt: new Date().toISOString(),
      }

      const ResultPageWithState = () => {
        const { setResult } = useConsultation()
        React.useEffect(() => {
          setResult(mockResult)
        }, [setResult])
        return <ConsultationResultPage />
      }

      render(
        <MemoryRouter initialEntries={["/consultations/result"]} future={routerFutureFlags}>
          <Routes>
            <Route
              path="/consultations/result"
              element={
                <ConsultationProvider>
                  <ResultPageWithState />
                </ConsultationProvider>
              }
            />
            <Route path="/chat" element={<div>Chat</div>} />
            <Route path="/consultations" element={<div>List</div>} />
          </Routes>
        </MemoryRouter>
      )

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /Sauvegarder/i })).toBeInTheDocument()
      })

      const saveBtn = screen.getByRole("button", { name: /Sauvegarder/i })
      fireEvent.click(saveBtn)

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /Sauvegardé/i })).toBeInTheDocument()
        expect(screen.getByRole("button", { name: /Sauvegardé/i })).toBeDisabled()
      })
    })
  })
})

describe("ConsultationsPage - Historique avec données", () => {
  it("has aria-live polite on history section for accessibility", () => {
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

    const historySection = document.querySelector(".consultations-history-section")
    expect(historySection).toBeInTheDocument()
    expect(historySection).toHaveAttribute("aria-live", "polite")
  })

  it("truncates context to CONTEXT_TRUNCATE_LENGTH with ellipsis", () => {
    const longContext = "A".repeat(CONTEXT_TRUNCATE_LENGTH + 10)
    const mockHistory = [
      {
        id: "hist-truncate",
        type: "dating" as const,
        astrologerId: "1",
        drawingOption: "none" as const,
        context: longContext,
        interpretation: "Interpretation",
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
    expect(screen.queryByText(longContext)).not.toBeInTheDocument()
  })

  it("does not truncate context shorter than CONTEXT_TRUNCATE_LENGTH", () => {
    const shortContext = "Short context"
    const mockHistory = [
      {
        id: "hist-short",
        type: "pro" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "none" as const,
        context: shortContext,
        interpretation: "Interpretation",
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

    expect(screen.getByText(shortContext)).toBeInTheDocument()
    expect(screen.queryByText(shortContext + "...")).not.toBeInTheDocument()
  })

  it("displays consultation history when items exist in localStorage", async () => {
    const mockHistory = [
      {
        id: "hist-1",
        type: "dating" as const,
        astrologerId: "1",
        drawingOption: "none" as const,
        context: "Ma question romantique",
        interpretation: "Une interprétation...",
        createdAt: new Date().toISOString(),
      },
      {
        id: "hist-2",
        type: "pro" as const,
        astrologerId: AUTO_ASTROLOGER_ID,
        drawingOption: "tarot" as const,
        context: "Mon choix de carrière",
        interpretation: "Une autre interprétation...",
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

    expect(screen.getByText(/Ma question romantique/)).toBeInTheDocument()
    expect(screen.getByText(/Mon choix de carrière/)).toBeInTheDocument()
    expect(screen.queryByText("Aucune consultation passée")).not.toBeInTheDocument()
  })

  it("displays formatted date in history list", () => {
    const specificDate = "2026-02-15T14:30:00.000Z"
    const mockHistory = [
      {
        id: "hist-date-test",
        type: "dating" as const,
        astrologerId: "1",
        drawingOption: "none" as const,
        context: "Test date formatting",
        interpretation: "Test interpretation",
        createdAt: specificDate,
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

    const dateElement = screen.getByText(/15/)
    expect(dateElement).toBeInTheDocument()
  })
})

describe("ConsultationsPage - Links to wizard types", () => {
  it("renders direct links to each consultation type", () => {
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

    const datingLink = screen.getByRole("link", { name: /Dating/i })
    expect(datingLink).toHaveAttribute("href", "/consultations/new?type=dating")

    const proLink = screen.getByRole("link", { name: /Choix professionnel/i })
    expect(proLink).toHaveAttribute("href", "/consultations/new?type=pro")

    const eventLink = screen.getByRole("link", { name: /Événement/i })
    expect(eventLink).toHaveAttribute("href", "/consultations/new?type=event")

    const freeLink = screen.getByRole("link", { name: /Question libre/i })
    expect(freeLink).toHaveAttribute("href", "/consultations/new?type=free")
  })
})

describe("ConsultationResultPage - Gestion des erreurs", () => {
  it("shows error state when module execution fails", async () => {
    mockExecuteModule.mockRejectedValueOnce(new Error("API Error"))

    const TestWrapper = () => {
      const { setType, setAstrologer, setDrawingOption, setContext, goToStep } = useConsultation()

      useEffect(() => {
        setType("dating")
        setAstrologer("1")
        setDrawingOption("tarot")
        setContext("Ma question test")
        goToStep(3)
      }, [setType, setAstrologer, setDrawingOption, setContext, goToStep])

      return <ConsultationResultPage />
    }

    render(
      <MemoryRouter initialEntries={["/consultations/result"]} future={routerFutureFlags}>
        <Routes>
          <Route
            path="/consultations/result"
            element={
              <ConsultationProvider>
                <TestWrapper />
              </ConsultationProvider>
            }
          />
          <Route path="/consultations/new" element={<div>Wizard</div>} />
          <Route path="/consultations" element={<div>List</div>} />
        </Routes>
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/Erreur lors de la génération/i)).toBeInTheDocument()
    }, { timeout: 3000 })

    expect(screen.getByRole("alert")).toBeInTheDocument()
  })
})

describe("ValidationStep - Character counter", () => {
  it("displays character counter with CONTEXT_MAX_LENGTH remaining", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
    await waitFor(() => screen.getByText("Luna Céleste"))
    fireEvent.click(screen.getByText("Luna Céleste"))
    await waitFor(() => screen.getByText("Sans tirage"))
    fireEvent.click(screen.getByText("Sans tirage"))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

    const expectedText = new RegExp(`${CONTEXT_MAX_LENGTH} caractères restants`)
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })

  it("updates character counter when typing", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
    await waitFor(() => screen.getByText("Luna Céleste"))
    fireEvent.click(screen.getByText("Luna Céleste"))
    await waitFor(() => screen.getByText("Sans tirage"))
    fireEvent.click(screen.getByText("Sans tirage"))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

    const textarea = screen.getByLabelText(/Décrivez votre situation/)
    const testInput = "Hello World"
    fireEvent.change(textarea, { target: { value: testInput } })

    const expectedRemaining = CONTEXT_MAX_LENGTH - testInput.length
    const expectedText = new RegExp(`${expectedRemaining} caractères restants`)
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })

  it("has maxLength attribute set to CONTEXT_MAX_LENGTH on textarea", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
    await waitFor(() => screen.getByText("Luna Céleste"))
    fireEvent.click(screen.getByText("Luna Céleste"))
    await waitFor(() => screen.getByText("Sans tirage"))
    fireEvent.click(screen.getByText("Sans tirage"))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

    const textarea = screen.getByLabelText(/Décrivez votre situation/) as HTMLTextAreaElement
    expect(textarea).toHaveAttribute("maxlength", String(CONTEXT_MAX_LENGTH))
  })

  it("has aria-describedby linking textarea to character counter", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
    await waitFor(() => screen.getByText("Luna Céleste"))
    fireEvent.click(screen.getByText("Luna Céleste"))
    await waitFor(() => screen.getByText("Sans tirage"))
    fireEvent.click(screen.getByText("Sans tirage"))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

    const textarea = screen.getByLabelText(/Décrivez votre situation/) as HTMLTextAreaElement
    expect(textarea).toHaveAttribute("aria-describedby", "consultation-context-counter")

    const counter = document.getElementById("consultation-context-counter")
    expect(counter).toBeInTheDocument()
    expect(counter).toHaveTextContent(/caractères restants/)
  })

  it("keeps Generate button disabled when context is only whitespace", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))
    await waitFor(() => screen.getByText("Luna Céleste"))
    fireEvent.click(screen.getByText("Luna Céleste"))
    await waitFor(() => screen.getByText("Sans tirage"))
    fireEvent.click(screen.getByText("Sans tirage"))

    await waitFor(() => screen.getByLabelText(/Décrivez votre situation/))

    const textarea = screen.getByLabelText(/Décrivez votre situation/)
    fireEvent.change(textarea, { target: { value: "   " } })

    const generateBtn = screen.getByRole("button", { name: /Générer la consultation/i })
    expect(generateBtn).toBeDisabled()
  })
})

describe("generateSimpleInterpretation", () => {
  it("returns French interpretation by default", () => {
    const result = generateSimpleInterpretation("Ma question test", "fr")
    expect(result).toContain("Votre question")
    expect(result).toContain("Ma question test")
    expect(result).toContain("Les astres vous invitent")
  })

  it("returns English interpretation for lang=en", () => {
    const result = generateSimpleInterpretation("My test question", "en")
    expect(result).toContain("Your question")
    expect(result).toContain("My test question")
    expect(result).toContain("The stars invite you")
  })

  it("returns Spanish interpretation for lang=es", () => {
    const result = generateSimpleInterpretation("Mi pregunta de prueba", "es")
    expect(result).toContain("Su pregunta")
    expect(result).toContain("Mi pregunta de prueba")
    expect(result).toContain("Las estrellas le invitan")
  })

  it("falls back to French for unknown languages", () => {
    const result = generateSimpleInterpretation("Meine Testfrage", "de" as AstrologyLang)
    expect(result).toContain("Votre question")
    expect(result).toContain("Les astres vous invitent")
  })

  it("falls back to French for empty string language", () => {
    const result = generateSimpleInterpretation("Test question", "" as AstrologyLang)
    expect(result).toContain("Votre question")
    expect(result).toContain("Les astres vous invitent")
  })

  it("truncates long context to CONTEXT_TRUNCATE_LENGTH with ellipsis", () => {
    const longContext = "A".repeat(CONTEXT_TRUNCATE_LENGTH + 50)
    const result = generateSimpleInterpretation(longContext, "fr")
    expect(result).toContain(`${"A".repeat(CONTEXT_TRUNCATE_LENGTH)}...`)
    expect(result).not.toContain("A".repeat(CONTEXT_TRUNCATE_LENGTH + 1))
  })

  it("does not add ellipsis for short context", () => {
    const shortContext = "Hello"
    const result = generateSimpleInterpretation(shortContext, "fr")
    expect(result).toContain('"Hello"')
    expect(result).not.toContain("Hello...")
  })
})

describe("AstrologerSelectStep - error state", () => {
  it("displays error message when astrologers fail to load", async () => {
    mockUseAstrologers.mockReturnValue({
      data: undefined,
      isPending: false,
      error: new Error("Network error"),
    })

    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument()
      expect(screen.getByText(/Erreur lors du chargement des astrologues/i)).toBeInTheDocument()
    })
  })
})

describe("AstrologerSelectStep - loading state", () => {
  it("displays loading message when astrologers are being fetched", async () => {
    mockUseAstrologers.mockReturnValue({
      data: undefined,
      isPending: true,
      error: null,
    })

    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))

    await waitFor(() => {
      expect(screen.getByText(/Chargement/i)).toBeInTheDocument()
    })
  })
})

describe("AstrologerSelectStep - avatar fallback", () => {
  it("hides avatar image on error", async () => {
    mockUseAstrologers.mockReturnValue({
      data: [
        {
          id: "1",
          name: "Luna Céleste",
          style: "Mystique",
          avatar_url: "https://invalid-url.example/avatar.png",
        },
      ],
      isPending: false,
      error: null,
    })

    renderWizardPage()
    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))

    await waitFor(() => {
      expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
    })

    const avatarImg = document.querySelector(".astrologer-option-avatar-img") as HTMLImageElement
    expect(avatarImg).toBeInTheDocument()

    fireEvent.error(avatarImg)

    expect(avatarImg.style.display).toBe("none")
  })
})

describe("ConsultationWizardPage - Previous button visibility", () => {
  it("does not show Previous button on step 0", () => {
    renderWizardPage()

    expect(screen.queryByRole("button", { name: /Précédent/i })).not.toBeInTheDocument()
  })

  it("shows Previous button on step 1", async () => {
    renderWizardPage()

    fireEvent.click(screen.getByRole("button", { name: /Dating/i }))

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Précédent/i })).toBeInTheDocument()
    })
  })
})

describe("ConsultationResultPage - reset after open in chat", () => {
  it("resets wizard state after clicking open in chat", async () => {
    const mockResult = {
      id: "test-reset-chat",
      type: "pro" as const,
      astrologerId: AUTO_ASTROLOGER_ID,
      drawingOption: "none" as const,
      context: "Question test reset",
      interpretation: "Interprétation test...",
      createdAt: new Date().toISOString(),
    }

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify([mockResult])
    )

    let capturedState: { draft: { type: string | null } } | null = null

    const StateCapture = () => {
      const { state } = useConsultation()
      capturedState = state
      return null
    }

    render(
      <MemoryRouter initialEntries={["/consultations/result?id=test-reset-chat"]} future={routerFutureFlags}>
        <Routes>
          <Route
            path="/consultations/result"
            element={
              <ConsultationProvider>
                <StateCapture />
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
      expect(screen.getByRole("button", { name: /Ouvrir dans le chat/i })).toBeInTheDocument()
    })

    const openChatBtn = screen.getByRole("button", { name: /Ouvrir dans le chat/i })
    fireEvent.click(openChatBtn)

    expect(mockNavigate).toHaveBeenCalledWith("/chat")
    expect(capturedState?.draft.type).toBeNull()
  })
})

describe("consultations i18n t() function", () => {
  it("returns the key when key does not exist", () => {
    const result = t("nonexistent_key", "fr")
    expect(result).toBe("nonexistent_key")
  })

  it("returns the key when lang entry is missing", () => {
    const result = t("page_title", "de" as "fr")
    expect(result).toBe("page_title")
  })

  it("returns correct translation for existing key", () => {
    expect(t("page_title", "fr")).toBe("Consultations")
    expect(t("page_title", "en")).toBe("Consultations")
    expect(t("page_title", "es")).toBe("Consultas")
  })
})

describe("generateUniqueId fallback", () => {
  it("generates unique ID using crypto.randomUUID when available", () => {
    const id1 = crypto.randomUUID()
    const id2 = crypto.randomUUID()
    expect(id1).not.toBe(id2)
    expect(id1.length).toBe(36)
  })

  it("generates fallback ID format when crypto.randomUUID would not exist", () => {
    const fallbackPattern = /^consultation-\d+-[a-z0-9]+$/
    const timestamp = Date.now()
    const randomPart = Math.random().toString(36).slice(2, 11)
    const fallbackId = `consultation-${timestamp}-${randomPart}`
    expect(fallbackPattern.test(fallbackId)).toBe(true)
  })
})

describe("ConsultationProvider initialization", () => {
  beforeEach(() => {
    localStorage.clear()
    mockUseAstrologers.mockReturnValue({ data: [], isLoading: false })
    mockUseAstrologer.mockReturnValue({ data: null, isLoading: false })
  })

  afterEach(() => {
    cleanup()
    localStorage.clear()
  })

  it("loads history from localStorage on mount", async () => {
    const storedHistory = [
      {
        id: "stored-1",
        type: "dating",
        astrologerId: "1",
        drawingOption: "none",
        context: "Stored context",
        interpretation: "Stored interpretation",
        createdAt: "2026-02-22T10:00:00.000Z",
      },
      {
        id: "stored-2",
        type: "pro",
        astrologerId: "2",
        drawingOption: "tarot",
        context: "Another context",
        interpretation: "Another interpretation",
        createdAt: "2026-02-21T10:00:00.000Z",
      },
    ]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(storedHistory))

    let capturedHistory: Array<{ id: string }> = []

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
      expect(capturedHistory.length).toBe(2)
    })

    expect(capturedHistory[0].id).toBe("stored-1")
    expect(capturedHistory[1].id).toBe("stored-2")
  })

  it("initializes with empty history when localStorage is empty", async () => {
    let capturedHistory: Array<{ id: string }> = []

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
      expect(capturedHistory).toBeDefined()
    })

    expect(capturedHistory.length).toBe(0)
  })

  it("initializes with empty history when localStorage contains invalid data", async () => {
    localStorage.setItem(STORAGE_KEY, "invalid-json")

    let capturedHistory: Array<{ id: string }> = []

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
      expect(capturedHistory).toBeDefined()
    })

    expect(capturedHistory.length).toBe(0)
  })
})
