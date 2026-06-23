// Vérifie que la page thème natal ne boucle pas après un échec Astral.
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { NatalChartPage } from "../pages/NatalChartPage"

const mockSubmitAstralJob = vi.fn()
const mockUseEntitlementsSnapshot = vi.fn()
const mockUseAccessTokenSnapshot = vi.fn()
const mockUseAstralJobStatus = vi.fn()
const mockUseAstralJobEvents = vi.fn()
let capturedAstralEventHandler: ((event: unknown) => void) | null = null

vi.mock("../api/astral", async () => {
  const actual = await vi.importActual<typeof import("../api/astral")>("../api/astral")
  return {
    ...actual,
    useSubmitAstralJob: (accessToken: string | null) => {
      if (!accessToken) {
        throw new Error("Le token est requis dans ce test.")
      }
      return useMutation({
        mutationFn: mockSubmitAstralJob,
      })
    },
    useAstralJobStatus: () => mockUseAstralJobStatus(),
    useAstralJobEvents: (...args: unknown[]) => {
      mockUseAstralJobEvents(...args)
      capturedAstralEventHandler = typeof args[2] === "function" ? args[2] as (event: unknown) => void : null
    },
  }
})

vi.mock("../hooks/useEntitlementSnapshot", () => ({
  useEntitlementsSnapshot: () => mockUseEntitlementsSnapshot(),
}))

vi.mock("../utils/authToken", () => ({
  useAccessTokenSnapshot: () => mockUseAccessTokenSnapshot(),
  getSubjectFromAccessToken: () => null,
  hasUsableAccessToken: (token: string | null) => Boolean(token),
}))

let queryClient: QueryClient

function renderNatalChartPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NatalChartPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })
  mockSubmitAstralJob.mockReset()
  mockUseEntitlementsSnapshot.mockReturnValue({
    data: {
      plan_code: "basic",
      billing_status: "active",
      features: [
        {
          feature_code: "horoscope_daily",
          granted: true,
          reason_code: "granted",
          access_mode: "quota",
          variant_code: "basic_short",
          usage_states: [],
        },
      ],
      upgrade_hints: [],
    },
    isPending: false,
    isError: false,
  })
  mockUseAccessTokenSnapshot.mockReturnValue("access-token")
  mockUseAstralJobStatus.mockReturnValue({
    data: undefined,
    isError: false,
    isPending: false,
  })
  mockUseAstralJobEvents.mockReset()
  capturedAstralEventHandler = null
})

afterEach(() => {
  cleanup()
  queryClient.clear()
})

describe("NatalChartPage", () => {
  it("ne soumet pas automatiquement un job Astral au montage", async () => {
    renderNatalChartPage()

    expect(await screen.findByRole("button", { name: "Lancer le theme natal" })).toBeEnabled()
    expect(mockSubmitAstralJob).not.toHaveBeenCalled()
  })

  it("soumet le theme natal full au backend pour laisser la facade choisir le service Astral", async () => {
    const user = userEvent.setup()
    mockSubmitAstralJob.mockResolvedValue({
      run_id: "run-natal-1",
      status: "queued",
      service_code: "natal_basic",
    })

    renderNatalChartPage()

    await user.click(await screen.findByRole("button", { name: "Lancer le theme natal" }))

    await waitFor(() => {
      expect(mockSubmitAstralJob).toHaveBeenCalledWith(
        expect.objectContaining({
          product: "natal_full",
          plan: "basic",
          target_language_code: "fr",
          audience_level: "beginner",
        }),
        expect.anything(),
      )
    })
  })

  it("rend une lecture Astral structuree et la precision reduite si le job revient en simplifie", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-2",
        status: "completed",
        service_code: "natal_simplified",
        result: {
          reading: {
            status: "success",
            run_id: "generation-run-1",
            reading: {
              schema_version: "natal_reading_v1",
              reading_type: "natal",
              language: "fr",
              summary: {
                title: "Lecture natale publique",
                short_text: "Une synthese claire du theme.",
              },
              chapters: [
                {
                  code: "identity",
                  title: "Identite",
                  body: "Votre lecture met l'accent sur une dynamique personnelle stable.",
                  confidence: "medium",
                  astro_basis: ["Soleil en Cancer", "Lune en Balance"],
                },
              ],
              legal: {
                disclaimer: "Lecture symbolique et non medicale.",
              },
              quality: {
                astro_contract_version: "natal_simplified_structured_v1",
                fallback_used: false,
                generation_mode: "single_pass",
                prompt_family: "natal_simplified",
                prompt_version: "v1",
                used_model: "fake",
                used_provider: "fake",
              },
            },
          },
        },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage()

    expect(await screen.findByRole("heading", { name: "Lecture natale publique" })).toBeVisible()
    expect(screen.getByText("Une synthese claire du theme.")).toBeVisible()
    expect(screen.getByRole("heading", { name: "Identite" })).toBeVisible()
    expect(screen.getByText(/dynamique personnelle stable/i)).toBeVisible()
    expect(screen.getByText("Confiance moyenne")).toBeVisible()
    expect(screen.getByText("Soleil en Cancer")).toBeVisible()
    expect(screen.getByText("Lune en Balance")).toBeVisible()
    expect(screen.getByText(/Lecture indicative : sans heure de naissance fiable/i)).toBeVisible()
    expect(screen.queryByLabelText("Resultat Astral")).not.toBeInTheDocument()
  })

  it("conserve le resultat de polling quand un evenement SSE completed est minimal", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-3",
        status: "completed",
        service_code: "natal_basic",
        result: {
          reading: {
            status: "success",
            run_id: "generation-run-3",
            reading: {
              schema_version: "natal_reading_v1",
              reading_type: "natal",
              language: "fr",
              summary: {
                title: "Lecture conservee",
                short_text: "Le polling garde le texte public.",
              },
              chapters: [],
              legal: { disclaimer: "Lecture symbolique." },
              quality: {
                astro_contract_version: "astro_engine_response_v1",
                fallback_used: false,
                generation_mode: "chapter_orchestrated",
                prompt_family: "natal_prompter",
                prompt_version: "v1",
                used_model: "fake",
                used_provider: "fake",
              },
            },
          },
        },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage()
    capturedAstralEventHandler?.({ run_id: "run-natal-3", status: "completed" })

    expect(await screen.findByRole("heading", { name: "Lecture conservee" })).toBeVisible()
    expect(screen.getByText("Le polling garde le texte public.")).toBeVisible()
  })

  it("traite safety_rejected comme un statut terminal explicite", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-4",
        status: "safety_rejected",
        service_code: "natal_basic",
        error: { code: "SAFETY_REJECTED", message: "Rejected" },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage()

    expect(await screen.findByRole("alert")).toHaveTextContent("safety_rejected")
    expect(screen.queryByRole("button", { name: "Lancer le theme natal" })).not.toBeInTheDocument()
  })

  it("rend un rejet de securite interne sans exposer le payload technique", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-5",
        status: "completed",
        service_code: "natal_basic",
        result: {
          debug: { llm_request: { prompt: "secret prompt" } },
          interpretation_request: { hidden: "internal" },
          reading: {
            status: "safety_rejected",
            error: {
              code: "SAFETY_REJECTED",
              message: "La lecture a ete refusee par les controles de securite.",
              rule_id: "medical_claim",
            },
          },
        },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage()

    expect(await screen.findByRole("alert")).toHaveTextContent("La lecture a ete refusee")
    expect(screen.getByText("Lecture Astral non generee.")).toBeVisible()
    expect(screen.queryByText("Resultat Astral pret.")).not.toBeInTheDocument()
    expect(screen.getByText("Code: SAFETY_REJECTED")).toBeVisible()
    expect(screen.getByText("Regle: medical_claim")).toBeVisible()
    expect(screen.queryByText(/secret prompt/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/internal/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText("Resultat Astral")).not.toBeInTheDocument()
  })

  it("affiche une enveloppe gateway V2 premium sans fuite debug", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-6",
        status: "completed",
        result: {
          metadata: {
            product_code: "natal_full_premium",
            tier: "premium",
            variant: "full",
          },
          quality: {
            reading_completeness: "completed",
          },
          debug: { run_id: "debug-run", llm_request: { prompt: "hidden gateway" } },
          reading: {
            status: "success",
            reading: {
              schema_version: "natal_reading_v1",
              reading_type: "natal",
              language: "fr",
              summary: {
                title: "Lecture premium Astral",
                short_text: "Une lecture approfondie du theme.",
              },
              chapters: [
                {
                  code: "career",
                  title: "Vocation",
                  body: "Votre dynamique professionnelle s'appuie sur des ressources visibles.",
                  confidence: "high",
                  astro_basis: [
                    {
                      fact_id: "signal:mc:taurus",
                      label: "Milieu du Ciel en Taureau",
                      interpretive_role: "core",
                    },
                  ],
                },
              ],
              legal: { disclaimer: "Lecture symbolique." },
            },
          },
        },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage()

    expect(await screen.findByRole("heading", { name: "Lecture premium Astral" })).toBeVisible()
    expect(screen.getByText("Lecture approfondie")).toBeVisible()
    expect(screen.getByText("Milieu du Ciel en Taureau (central)")).toBeVisible()
    expect(screen.queryByText(/signal:mc:taurus/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/hidden gateway/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText("Resultat Astral")).not.toBeInTheDocument()
  })
})
