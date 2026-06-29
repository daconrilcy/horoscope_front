// Vérifie que la page thème natal ne boucle pas après un échec Astral.
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  buildNatalAstralJobRequest,
  resolveNatalAstralPlan,
} from "../features/natal-chart/natalAstralJobConfig"
import { resolveNatalJobViewState } from "../features/natal-chart/natalJobViewState"
import { mergeCurrentAstralJobState } from "../features/natal-chart/useNatalAstralJob"
import { NatalChartPage } from "../pages/NatalChartPage"

const mockSubmitAstralJob = vi.fn()
const mockUseEntitlementsSnapshot = vi.fn()
const mockUseAccessTokenSnapshot = vi.fn()
const mockUseAstralJobStatus = vi.fn()
const mockUseAstralJobEvents = vi.fn()
let capturedAstralEventHandler: ((event: unknown) => void) | null = null
let restoreScrollIntoView: (() => void) | null = null
let restoreGetBoundingClientRect: (() => void) | null = null

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

function mockScrollIntoView() {
  const originalScrollIntoView = Element.prototype.scrollIntoView
  const scrollIntoViewMock = vi.fn()
  Element.prototype.scrollIntoView = scrollIntoViewMock
  restoreScrollIntoView = () => {
    Element.prototype.scrollIntoView = originalScrollIntoView
    restoreScrollIntoView = null
  }
  return scrollIntoViewMock
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
  restoreScrollIntoView?.()
  restoreGetBoundingClientRect?.()
  cleanup()
  queryClient.clear()
})

describe("NatalChartPage", () => {
  it("mappe les variantes d'entitlement vers le plan Astral natal temporaire", () => {
    expect(resolveNatalAstralPlan("premium_full")).toBe("premium")
    expect(resolveNatalAstralPlan("basic_short")).toBe("basic")
    expect(resolveNatalAstralPlan("single_astrologer")).toBe("basic")
    expect(resolveNatalAstralPlan("unknown_variant")).toBe("free")
    expect(buildNatalAstralJobRequest({ plan: "premium" })).toEqual(
      expect.objectContaining({
        product: "natal_full",
        plan: "premium",
        target_language_code: "fr",
        audience_level: "expert",
      }),
    )
  })

  it("normalise les statuts Astral en etats d'affichage natal", () => {
    expect(resolveNatalJobViewState({ hasTransportError: false, isWorking: false })).toBe("idle")
    expect(resolveNatalJobViewState({ hasTransportError: true, isWorking: true })).toBe("transport-error")
    expect(resolveNatalJobViewState({ hasTransportError: false, isWorking: true })).toBe("working")
    expect(
      resolveNatalJobViewState({
        hasTransportError: false,
        isWorking: false,
        currentJob: { run_id: "run-1", status: "completed" },
      }),
    ).toBe("completed")
    expect(
      resolveNatalJobViewState({
        hasTransportError: false,
        isWorking: false,
        currentJob: { run_id: "run-2", status: "failed" },
      }),
    ).toBe("terminal-error")
  })

  it("conserve result error et token_usage quand un evenement SSE partiel les omet", () => {
    const mergedJob = mergeCurrentAstralJobState(
      { run_id: "run-merge", status: "completed" },
      {
        run_id: "run-merge",
        status: "running",
        result: { reading: { status: "success" } },
        error: { code: "previous" },
        token_usage: { total: 42 },
      },
      undefined,
    )

    expect(mergedJob).toEqual(
      expect.objectContaining({
        run_id: "run-merge",
        status: "completed",
        result: { reading: { status: "success" } },
        error: { code: "previous" },
        token_usage: { total: 42 },
      }),
    )
  })

  it("ne soumet pas automatiquement un job Astral au montage", async () => {
    renderNatalChartPage()

    expect(screen.getByRole("heading", { name: "Votre thème natal" })).toBeVisible()
    expect(screen.getByText(/Une synthèse structurée de vos marqueurs personnels/i)).toBeVisible()
    expect(screen.getByRole("heading", { name: "Comment lire ton thème natal" })).toBeVisible()
    expect(await screen.findByRole("button", { name: "Lancer le thème natal" })).toBeEnabled()
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

    await user.click(await screen.findByRole("button", { name: "Lancer le thème natal" }))

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

  it("ignore une double action de lancement avant la fin de la premiere soumission", async () => {
    const user = userEvent.setup()
    let resolveSubmit: ((value: { run_id: string; status: string; service_code: string }) => void) | null = null
    mockSubmitAstralJob.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSubmit = resolve
        }),
    )

    renderNatalChartPage()

    await user.dblClick(await screen.findByRole("button", { name: "Lancer le thème natal" }))

    expect(mockSubmitAstralJob).toHaveBeenCalledTimes(1)
    resolveSubmit?.({
      run_id: "run-natal-double",
      status: "queued",
      service_code: "natal_basic",
    })
  })

  it("rend une lecture Astral structuree et la precision reduite si le job revient en simplifie", async () => {
    const user = userEvent.setup()
    const scrollIntoViewMock = mockScrollIntoView()
    const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect
    restoreGetBoundingClientRect = () => {
      Element.prototype.getBoundingClientRect = originalGetBoundingClientRect
      restoreGetBoundingClientRect = null
    }
    Element.prototype.getBoundingClientRect = function getBoundingClientRect(this: Element) {
      if (this instanceof HTMLElement && this.classList.contains("natal-reading__chapter")) {
        const chapterIndex = Number.parseInt(this.id.split("-").at(-1) ?? "0", 10)
        const top = chapterIndex * 720
        return {
          bottom: top + 640,
          height: 640,
          left: 0,
          right: 920,
          toJSON: () => undefined,
          top,
          width: 920,
          x: 0,
          y: top,
        } as DOMRect
      }

      return originalGetBoundingClientRect.call(this)
    }
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
                  body: "Chapitre narratif principal conserve. Suite analytique preservee.",
                  confidence: "medium",
                  astro_basis: ["Soleil en Cancer", "Lune en Balance"],
                },
                {
                  code: "emotions",
                  title: "Emotions",
                  body:
                    "Deuxieme lecture ouverte par defaut avec une phrase volontairement longue pour verifier que le chapeau tronque ne repete pas tout le debut du paragraphe dans le detail. Elle reste accessible sans action initiale, avec une phrase volontairement etendue qui accumule plusieurs nuances successives, plusieurs indications symboliques reliees entre elles, plusieurs appuis de lecture destines a rester dans le texte complet, et plusieurs respirations internes pour verifier que le rendu cree de vrais paragraphes plus courts.",
                },
                {
                  code: "relations",
                  title: "Relations",
                  body: "Troisieme lecture secondaire repliee. Elle devient lisible apres action.",
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
          explanations: {
            items: [
              {
                explanation:
                  "Votre lecture met l'accent sur une dynamique personnelle stable. Ce repere detaille la maniere dont le calcul soutient cette interpretation.",
                expression_primary: "Maison 10",
                fact_id: "placement:sun:taurus:house:10",
                kind_code: "placement",
                source: "cache",
                title: "Sun en taurus maison 10",
              },
            ],
            language_code: "fr",
            status: "complete",
          },
        },
      },
      isError: false,
      isPending: false,
    })

    const { container } = renderNatalChartPage()

    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeVisible()
    const heroLogo = container.querySelector(".natal-reading-hero__symbol .natal-reading-hero__logo")
    expect(heroLogo).toHaveAttribute("src", expect.stringContaining("Natal_Logo"))
    expect(screen.getByRole("heading", { name: "Base du calcul natal" })).toBeVisible()
    expect(screen.getByText("Données de calcul Astral")).toBeVisible()
    const renderedText = document.body.textContent ?? ""
    expect(renderedText.indexOf("Thème natal")).toBeLessThan(
      renderedText.indexOf("Base du calcul natal"),
    )
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Sommaire")
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("0% complété")
    expect(screen.getByLabelText("Marqueurs clés du portrait astral")).toHaveTextContent("Statut")
    await user.click(screen.getByRole("button", { name: "Afficher la base" }))
    expect(screen.getByRole("region", { name: "Repères principaux" })).toHaveTextContent("Soleil")
    expect(screen.getByRole("region", { name: "Repères principaux" })).toHaveTextContent("Ascendant")
    expect(screen.getByRole("region", { name: "Repères principaux" })).toHaveTextContent("Descendant")
    const portrait = screen.getByLabelText("Marqueurs clés du portrait astral")
    expect(portrait).toHaveClass("natal-reading-metrics")
    expect(screen.getByLabelText("Marqueurs clés du portrait astral")).toHaveTextContent("Soleil")
    expect(screen.getByLabelText("Marqueurs clés du portrait astral")).toHaveTextContent("Lune")
    expect(screen.getByLabelText("Marqueurs clés du portrait astral")).toHaveTextContent("Ascendant")
    expect(screen.getByText("Une synthese claire du theme.")).toBeVisible()
    expect(container.querySelector(".natal-reading-facts__group--primary")).toHaveTextContent("Repères principaux")
    expect(screen.getByRole("region", { name: "Maisons" })).toHaveTextContent("Maison II")
    expect(screen.getByRole("region", { name: "Planètes notables" })).toHaveTextContent("Mercure")
    expect(screen.getByRole("region", { name: "Aspects notables" })).toHaveTextContent("Jupiter - Uranus")
    expect(container.querySelector(".natal-badge--astro-sign")).toHaveTextContent("Capricorne")
    expect(container.querySelector(".natal-badge--astro-house")).toHaveTextContent("Valeurs")
    expect(container.querySelector(".natal-badge--astro-aspect")).toHaveTextContent("Jupiter - Uranus")
    expect(container.querySelector(".natal-badge--astro-intensity")).toHaveTextContent("Très élevée")
    expect(screen.getAllByText("Une synthese claire du theme.")).toHaveLength(1)
    expect(container.querySelector(".natal-badge--report-status")).toHaveTextContent("Essentielle")
    expect(screen.getByRole("heading", { name: "Identite" })).toBeVisible()
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Identité")
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Émotions")
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Relations")
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Éléments du calcul")
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Explications du calcul")
    expect(screen.getByLabelText("Sommaire de lecture")).toHaveTextContent("Comment lire ton thème natal")
    const progressBar = container.querySelector(".natal-reading-summary__bar")
    expect(progressBar).toHaveProperty("value", 0)
    const firstProgressLink = screen.getByRole("button", { name: "Identite" })
    expect(firstProgressLink).toHaveAttribute("aria-current", "step")
    await user.click(screen.getByRole("button", { name: "Relations" }))
    expect(screen.getByRole("button", { name: "Relations" })).toHaveAttribute("aria-current", "step")
    await waitFor(() => {
      expect(progressBar).toHaveProperty("value", 100)
    })
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: "smooth", block: "start" })
    const firstChapter = container.querySelector(".natal-reading__chapter")
    expect(firstChapter).not.toBeNull()
    expect(within(firstChapter as HTMLElement).getByText(/Chapitre narratif principal conserve/i).closest(".natal-reading__chapter-excerpt")).not.toBeNull()
    expect(within(firstChapter as HTMLElement).getByText("À retenir")).toBeVisible()
    expect(firstChapter?.querySelector(".natal-reading__chapter-excerpt")).toHaveTextContent(
      /Chapitre narratif principal conserve/i,
    )
    const chapterTitle = container.querySelector(".natal-reading__chapter-title")
    expect(chapterTitle).toHaveTextContent("Identite")
    expect(chapterTitle).not.toHaveTextContent("1. Identite")
    expect((chapterTitle?.textContent ?? "").indexOf("Identite")).toBeLessThan(
      (chapterTitle?.textContent ?? "").indexOf("Lecture guidée"),
    )
    expect(screen.getByText("Suite analytique preservee.")).toBeVisible()
    expect(screen.getByText(/Elle reste accessible sans action initiale/i)).toBeVisible()
    const renderedProseParagraphs = Array.from(container.querySelectorAll(".natal-reading__prose-paragraph"))
    expect(renderedProseParagraphs.length).toBeGreaterThan(3)
    expect(Math.max(...renderedProseParagraphs.map((paragraph) => paragraph.textContent?.length ?? 0))).toBeLessThanOrEqual(
      260,
    )
    expect(renderedProseParagraphs.map((paragraph) => paragraph.textContent).join(" ")).toContain(
      "Suite analytique preservee.",
    )
    const longExcerptStart = "Deuxieme lecture ouverte par defaut avec une phrase volontairement longue"
    const chapterTexts = Array.from(container.querySelectorAll(".natal-reading__chapter"))
      .map((chapter) => chapter.textContent ?? "")
      .join(" ")
    expect((chapterTexts.match(new RegExp(longExcerptStart, "g")) ?? [])).toHaveLength(1)
    expect(screen.getByText("Elle devient lisible apres action.")).not.toBeVisible()
    expect(screen.getAllByRole("button", { name: "Réduire" })).toHaveLength(2)
    const firstChapterToggle = screen.getAllByRole("button", { name: "Réduire" })[0]
    expect(firstChapterToggle).toHaveAttribute("aria-expanded", "true")
    await user.click(firstChapterToggle)
    expect(firstChapterToggle).toHaveAttribute("aria-expanded", "false")
    expect(firstChapterToggle).toHaveTextContent("Lire la suite")
    expect(screen.getByText("Suite analytique preservee.")).not.toBeVisible()
    await user.click(firstChapterToggle)
    expect(firstChapterToggle).toHaveAttribute("aria-expanded", "true")
    expect(firstChapterToggle).toHaveTextContent("Réduire")
    expect(screen.getByText("Suite analytique preservee.")).toBeVisible()
    expect(screen.getByText("Confiance moyenne")).toHaveClass("natal-badge--confidence")
    expect(screen.getByText("Repères & évidences")).toBeVisible()
    expect(screen.getByText("Soleil en Cancer")).toBeVisible()
    expect(screen.getByText("Lune en Balance")).toBeVisible()
    const firstMetaToggle = screen.getAllByRole("button", { name: "Afficher les repères" })[0]
    expect(firstMetaToggle).toHaveAttribute("aria-expanded", "false")
    await user.click(firstMetaToggle)
    expect(firstMetaToggle).toHaveAttribute("aria-expanded", "true")
    expect(firstMetaToggle).toHaveTextContent("Masquer les repères")
    const explanationsSection = screen.getByRole("region", { name: "Explications du moteur Astral" })
    expect(explanationsSection).toHaveTextContent("Soleil en Taureau maison 10")
    expect(screen.queryByText("Very high")).not.toBeInTheDocument()
    expect(screen.queryByText("Resources")).not.toBeInTheDocument()
    expect(explanationsSection).toHaveTextContent(/dynamique personnelle stable/i)
    expect(screen.getAllByRole("button", { name: "Lire la suite" })).toHaveLength(2)
    expect(screen.getAllByRole("button", { name: "Lire la suite" })[0]).toHaveAttribute("aria-expanded", "false")
    expect(screen.queryByText("placement:sun:taurus:house:10")).not.toBeInTheDocument()
    expect(screen.queryByText("cache")).not.toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "Comment lire ton thème natal" })).toBeVisible()
    expect(container.querySelector("#natal-chart-guide")?.closest(".natal-reading__main")).not.toBeNull()
    const guideToggle = screen.getByRole("button", { name: "Lire le guide" })
    expect(guideToggle).toHaveAttribute("aria-expanded", "false")
    expect(screen.getByText(/Ton thème natal est une représentation géométrique/i)).not.toBeVisible()
    await user.click(guideToggle)
    expect(guideToggle).toHaveAttribute("aria-expanded", "true")
    expect(guideToggle).toHaveTextContent("Réduire le guide")
    expect(screen.getByText(/Ton thème natal est une représentation géométrique/i)).toBeVisible()
    await user.click(guideToggle)
    expect(guideToggle).toHaveAttribute("aria-expanded", "false")
    expect(guideToggle).toHaveTextContent("Lire le guide")
    expect(screen.getByText(/Ton thème natal est une représentation géométrique/i)).not.toBeVisible()
    expect(screen.getByRole("alert")).toHaveTextContent(/Thème partiel : certaines données de naissance/i)
    expect(screen.queryByText(/completude partielle/i)).not.toBeInTheDocument()
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

    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeVisible()
    expect(screen.getByText("Le polling garde le texte public.")).toBeVisible()
  })

  it("ignore un evenement SSE qui cible un autre run", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-current",
        status: "completed",
        service_code: "natal_basic",
        result: {
          reading: {
            status: "success",
            reading: {
              summary: {
                title: "Lecture courante",
                short_text: "Le run courant reste affiche.",
              },
              chapters: [],
            },
          },
        },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage(["/natal?runId=run-natal-current"])
    capturedAstralEventHandler?.({ run_id: "run-natal-other", status: "failed" })

    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeVisible()
    expect(screen.queryByText("Le service Astral n'a pas pu produire votre thème natal")).not.toBeInTheDocument()
  })

  it("affiche les explications dediees sans message de chapitres manquants", async () => {
    const user = userEvent.setup()
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-explanations-only",
        status: "completed",
        service_code: "natal_basic",
        result: {
          reading: {
            status: "success",
            reading: {
              summary: {
                title: "Lecture avec repères",
                short_text: "Résumé sans chapitre narratif.",
              },
              chapters: [],
            },
          },
          explanations: {
            items: [
              {
                explanation:
                  "Le Soleil en Taureau en maison 10 indique une orientation stable. Cette explication detaille le repere sans interrompre la lecture principale.",
                title: "Sun en taurus maison 10",
              },
            ],
            language_code: "fr",
            status: "complete",
          },
        },
      },
      isError: false,
      isPending: false,
    })

    renderNatalChartPage()

    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeVisible()
    const explanationsSection = screen.getByRole("region", { name: "Explications du moteur Astral" })
    expect(explanationsSection).toHaveTextContent("Soleil en Taureau maison 10")
    const readMore = screen.getByRole("button", { name: "Lire la suite" })
    expect(readMore).toHaveAttribute("aria-expanded", "false")
    expect(screen.getByText(/Cette explication detaille/i)).not.toBeVisible()
    await user.click(readMore)
    expect(readMore).toHaveAttribute("aria-expanded", "true")
    expect(screen.getByText(/Cette explication detaille/i)).toBeVisible()
    expect(screen.queryByText(/ne contient pas encore de chapitres publics/i)).not.toBeInTheDocument()
  })

  it("replie un chapitre sans meta en une seule colonne", async () => {
    mockUseAstralJobStatus.mockReturnValue({
      data: {
        run_id: "run-natal-no-meta",
        status: "completed",
        service_code: "natal_basic",
        result: {
          reading: {
            status: "success",
            reading: {
              summary: {
                title: "Lecture sans repères",
                short_text: "Résumé minimal.",
              },
              chapters: [
                {
                  code: "minimal",
                  title: "Chapitre minimal",
                  body: "Contenu narratif sans métadonnees.",
                },
              ],
            },
          },
        },
      },
      isError: false,
      isPending: false,
    })

    const { container } = renderNatalChartPage()

    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeVisible()
    const chapter = container.querySelector(".natal-reading__chapter")
    expect(chapter).toHaveClass("natal-reading__chapter--no-meta")
    expect(within(chapter as HTMLElement).getAllByText("Contenu narratif sans métadonnees.")).toHaveLength(1)
    expect(screen.queryByLabelText(/Repères et évidences pour Chapitre minimal/i)).not.toBeInTheDocument()
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
      "Le service Astral n'a pas pu produire votre thème natal",
    )
    expect(screen.queryByText(/safety_rejected/i)).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Lancer le thème natal" })).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Relancer le thème natal" })).toBeEnabled()
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

    await user.click(await screen.findByRole("button", { name: "Relancer le thème natal" }))

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
      "La lecture Astral n'a pas pu être générée",
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
                      label: "Midheaven in Taurus",
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

    expect(await screen.findByRole("heading", { name: "Thème natal" })).toBeVisible()
    expect(screen.getAllByText("Premium").length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText("Milieu du Ciel en Taureau (central)")).toBeVisible()
    expect(screen.queryByText(/signal:mc:taurus/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/hidden gateway/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText("Resultat Astral")).not.toBeInTheDocument()
  })
})
