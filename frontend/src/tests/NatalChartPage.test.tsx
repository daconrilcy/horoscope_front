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

function renderNatalChartPage(initialEntries = ["/natal"]) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
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

  it("reprend un job Astral transmis depuis le profil sans appeler l'ancien endpoint natal", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-from-profile",
        status: "queued",
        service_code: "natal_basic",
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage(["/natal?runId=run-from-profile"])

    expect(await screen.findByRole("status")).toHaveTextContent("Statut: queued")
    expect(mockSubmitAstralJob).not.toHaveBeenCalled()
    expect(mockUseAstralJobEvents).toHaveBeenCalledWith(
      "access-token",
      "run-from-profile",
      expect.any(Function),
    )
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
          calculation: {
            core_identity: {
              sun: {
                placement: {
                  object: "Sun",
                  sign: "Capricorn",
                  house: { number: 2, theme: "Resources" },
                  longitude_deg: 281.4543,
                },
              },
              moon: {
                placement: {
                  object: "Moon",
                  sign: "Pisces",
                  house: { number: 4, theme: "Home" },
                  longitude_deg: 341.7641,
                },
              },
            },
            angles: {
              ascendant: { sign: "Scorpio", house: 1 },
              descendant: { sign: "Taurus", house: 7 },
            },
            placements: {
              supporting: [
                {
                  object: "Mercury",
                  sign: "Capricorn",
                  house: { number: 3, theme: "Communication" },
                  longitude_deg: 295.4488,
                  motion: "Retrograde motion",
                },
              ],
            },
            dominant_themes: {
              houses: [{ number: 2, theme: "Resources", importance: "Very high" }],
            },
            dynamics: {
              major_aspects: [
                {
                  aspect: "Jupiter opposition Uranus",
                  objects: ["Jupiter", "Uranus"],
                  orb_degrees: 0.76,
                  quality: "Tension",
                },
              ],
            },
          },
          explanations: {
            status: "complete",
            language_code: "fr",
            items: [
              {
                fact_id: "placement:sun:capricorn:house:2",
                kind_code: "placement",
                title: "Soleil en Capricorne maison 2",
                explanation: "Explication externe du Soleil.",
                expression_primary: "Maison 2",
                source: "generated",
              },
              {
                fact_id: "placement:moon:pisces:house:4",
                kind_code: "placement",
                title: "Lune en Poissons maison 4",
                explanation: "Explication externe de la Lune.",
                expression_primary: "Maison 4",
                source: "generated",
              },
              {
                fact_id: "placement:ascendant:scorpio:house:1",
                kind_code: "angle",
                title: "Ascendant en Scorpion maison 1",
                explanation: "Explication externe de l'Ascendant.",
                expression_primary: "Maison 1",
                source: "generated",
              },
              {
                fact_id: "house_axis:self_relationship",
                kind_code: "house_axis",
                title: "Axe maison : soi et relation",
                explanation: "Explication externe de l'axe relationnel.",
                source: "generated",
              },
              {
                fact_id: "house_emphasis:house:2",
                kind_code: "house_emphasis",
                title: "Emphase maison ressources",
                explanation: "Explication externe du domaine dominant.",
                expression_primary: "resources",
                source: "generated",
              },
              {
                fact_id: "placement:mercury:capricorn:house:3",
                kind_code: "placement",
                title: "Mercure en Capricorne maison 3",
                explanation: "Explication externe de Mercure.",
                expression_primary: "Maison 3",
                source: "generated",
              },
              {
                fact_id: "aspect:jupiter:opposition:uranus",
                kind_code: "aspect",
                title: "Jupiter en tension avec Uranus",
                explanation: "Explication externe de l'aspect Jupiter Uranus.",
                expression_primary: "Tension",
                source: "generated",
              },
            ],
          },
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
    expect(screen.getByRole("heading", { name: "Ce qui ressort globalement" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Les 3 reperes essentiels" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Les grands equilibres du theme" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Le domaine de vie dominant" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Forces complementaires" })).toBeVisible()
    expect(screen.getByRole("heading", { name: "Dynamique principale" })).toBeVisible()
    expect(screen.getByText("Details techniques du calcul")).toBeVisible()
    expect(screen.queryByText("Données de calcul Astral")).not.toBeInTheDocument()
    const renderedText = document.body.textContent ?? ""
    expect(renderedText.indexOf("Ce qui ressort globalement")).toBeLessThan(
      renderedText.indexOf("Lecture natale publique"),
    )
    expect(screen.queryByRole("heading", { name: "Vos 3 grands piliers astrologiques" })).not.toBeInTheDocument()
    expect(screen.queryByRole("heading", { name: "Les grands axes de votre vie" })).not.toBeInTheDocument()
    expect(screen.queryByRole("heading", { name: "Domaines de vie les plus marques" })).not.toBeInTheDocument()
    expect(screen.queryByRole("heading", { name: "Autres forces importantes du theme" })).not.toBeInTheDocument()
    expect(screen.queryByRole("heading", { name: "Dynamiques fortes entre les planetes" })).not.toBeInTheDocument()
    expect(screen.getByRole("region", { name: "Les 3 reperes essentiels" })).toHaveTextContent("Soleil")
    expect(screen.getByRole("region", { name: "Les 3 reperes essentiels" })).toHaveTextContent("Ascendant")
    expect(screen.getByRole("region", { name: "Les 3 reperes essentiels" })).toHaveTextContent(
      "Explication externe du Soleil.",
    )
    expect(screen.getByRole("region", { name: "Les grands equilibres du theme" })).toHaveTextContent(
      "Axe maison : soi et relation",
    )
    expect(screen.getByRole("region", { name: "Les grands equilibres du theme" })).not.toHaveTextContent(
      "Ascendant en Scorpion",
    )
    expect(screen.getByRole("region", { name: "Le domaine de vie dominant" })).toHaveTextContent(
      "Emphase maison ressources",
    )
    expect(screen.getByRole("region", { name: "Le domaine de vie dominant" })).toHaveTextContent("Domaine dominant")
    expect(screen.getByRole("region", { name: "Le domaine de vie dominant" })).not.toHaveTextContent("resources")
    expect(screen.getByRole("region", { name: "Le domaine de vie dominant" })).not.toHaveTextContent(
      "Soleil en Maison II",
    )
    expect(screen.getByRole("region", { name: "Forces complementaires" })).toHaveTextContent("Mercure")
    expect(screen.getByRole("region", { name: "Dynamique principale" })).toHaveTextContent(
      "Jupiter en tension avec Uranus",
    )
    expect(screen.getByRole("region", { name: "Dynamique principale" })).toHaveTextContent(
      "Explication externe de l'aspect Jupiter Uranus.",
    )
    expect(renderedText).not.toContain("Ce repere decrit")
    expect(renderedText).not.toContain("Ce repere nuance")
    expect(renderedText).not.toContain("Ce theme met en avant")
    expect(renderedText).not.toContain("cooperation entre les planetes")
    expect(renderedText).not.toContain("Very high")
    expect(renderedText).not.toContain("placement:sun")
    expect(renderedText).not.toContain("generated")
    expect(screen.getByText("Une synthese claire du theme.")).toBeVisible()
    expect(screen.getByText("basic")).toBeVisible()
    expect(screen.getByRole("heading", { name: "Identite" })).toBeVisible()
    expect(screen.getByText(/dynamique personnelle stable/i)).toBeVisible()
    expect(screen.getByText("Confiance moyenne")).toBeVisible()
    expect(screen.getByText("Soleil en Cancer")).toBeVisible()
    expect(screen.getByText("Lune en Balance")).toBeVisible()
    expect(screen.getByRole("alert")).toHaveTextContent(/Theme partiel : certaines donnees de naissance/i)
    expect(screen.queryByText(/completude partielle/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText("Resultat Astral")).not.toBeInTheDocument()
    expect(renderedText.indexOf("Details techniques du calcul")).toBeGreaterThan(
      renderedText.indexOf("Lecture symbolique et non medicale."),
    )
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

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Le service Astral n'a pas pu produire votre theme natal",
    )
    expect(screen.queryByText(/safety_rejected/i)).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Lancer le theme natal" })).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Relancer le theme natal" })).toBeEnabled()
  })

  it("permet de relancer un theme natal depuis un ancien run failed", async () => {
    const user = userEvent.setup()
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "old-failed-run",
        status: "failed",
        service_code: "natal_basic",
        error: { code: "astral_external_service_error", message: "Erreur publique" },
      },
      isError: false,
      isPending: false,
    })
    mockSubmitAstralJob.mockResolvedValue({
      run_id: "new-run",
      status: "queued",
      service_code: "natal_basic",
    })

    renderNatalChartPage(["/natal?runId=old-failed-run"])

    await user.click(await screen.findByRole("button", { name: "Relancer le theme natal" }))

    await waitFor(() => {
      expect(mockSubmitAstralJob).toHaveBeenCalledWith(
        expect.objectContaining({
          product: "natal_full",
          plan: "basic",
          audience_level: "beginner",
        }),
        expect.anything(),
      )
    })
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

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "La lecture Astral n'a pas pu etre generee",
    )
    expect(screen.queryByText("Resultat Astral pret.")).not.toBeInTheDocument()
    expect(screen.queryByText("Code: SAFETY_REJECTED")).not.toBeInTheDocument()
    expect(screen.queryByText("Regle: medical_claim")).not.toBeInTheDocument()
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
    expect(screen.getByText("premium")).toBeVisible()
    expect(screen.getByText("Milieu du Ciel en Taureau (central)")).toBeVisible()
    expect(screen.queryByText(/signal:mc:taurus/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/hidden gateway/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText("Resultat Astral")).not.toBeInTheDocument()
  })
})
