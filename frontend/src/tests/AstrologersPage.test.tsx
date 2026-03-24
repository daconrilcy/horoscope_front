import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { AstrologersPage } from "../pages/AstrologersPage"
import { AstrologerProfilePage } from "../pages/AstrologerProfilePage"

const mockUseAstrologers = vi.fn()
const mockUseAstrologer = vi.fn()
const mockUseUserSettings = vi.fn()
const mockUseUpdateUserSettings = vi.fn()
const mockNavigate = vi.fn()
const mockRateAstrologer = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/astrologers", async () => {
  const actual = await vi.importActual<typeof import("../api/astrologers")>("../api/astrologers")
  return {
    ...actual,
    useAstrologers: () => mockUseAstrologers(),
    useAstrologer: (id: string | undefined) => mockUseAstrologer(id),
    rateAstrologer: (...args: unknown[]) => mockRateAstrologer(...args),
    isValidAstrologerId: actual.isValidAstrologerId,
  }
})

vi.mock("@api/userSettings", () => ({
  useUserSettings: () => mockUseUserSettings(),
  useUpdateUserSettings: () => mockUseUpdateUserSettings(),
}))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

beforeEach(() => {
  localStorage.setItem("lang", "fr")
  mockUseUserSettings.mockReturnValue({ data: { default_astrologer_id: null }, isLoading: false })
  mockUseUpdateUserSettings.mockReturnValue({ mutate: vi.fn(), isPending: false })
})

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

function renderAstrologersPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/astrologers"]} future={routerFutureFlags}>
        <Routes>
          <Route path="/astrologers" element={<AstrologersPage />} />
          <Route path="/astrologers/:id" element={<AstrologerProfilePage />} />
          <Route path="/chat" element={<div>Chat Page</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

function renderProfilePage(id: string) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/astrologers/${id}`]} future={routerFutureFlags}>
        <Routes>
          <Route path="/astrologers" element={<AstrologersPage />} />
          <Route path="/astrologers/:id" element={<AstrologerProfilePage />} />
          <Route path="/chat" element={<div>Chat Page</div>} />
          <Route path="/chat/:conversationId" element={<div>Chat Conversation</div>} />
          <Route path="/natal" element={<div>Natal Page</div>} />
          <Route path="/consultations/new" element={<div>Consultation Wizard</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

afterEach(() => {
  cleanup()
  mockUseAstrologers.mockReset()
  mockUseAstrologer.mockReset()
  mockNavigate.mockReset()
  mockRateAstrologer.mockReset()
  localStorage.clear()
})

describe("AstrologersPage", () => {
  const mockAstrologersList = [
    {
      id: "1",
      name: "Luna Céleste",
      first_name: "Luna",
      last_name: "Caron",
      avatar_url: "/avatars/luna.jpg",
      provider_type: "ia",
      specialties: ["Thème natal", "Transits", "Relations"],
      style: "Bienveillant et direct",
      bio_short: "Astrologue depuis 15 ans.",
    },
    {
      id: "2",
      name: "Orion Mystique",
      first_name: "Orion",
      last_name: "Vasseur",
      avatar_url: "/avatars/orion.jpg",
      provider_type: "real",
      specialties: ["Carrière", "Événements"],
      style: "Analytique et précis",
      bio_short: "Expert en astrologie prévisionnelle.",
    },
  ]

  describe("AC1: Catalogue astrologues - Grille de vignettes", () => {
    it("alternates the first displayed astrologer between visits", () => {
      mockUseAstrologers.mockReturnValue({
        data: [
          {
            id: "guide",
            name: "Guide Psychologique",
            first_name: "Étienne",
            last_name: "Garnier",
            avatar_url: "/avatars/etienne.jpg",
            provider_type: "ia",
            specialties: ["Débutants"],
            style: "Pédagogique",
            bio_short: "Profil onboarding.",
          },
          ...mockAstrologersList,
        ],
        isPending: false,
        error: null,
      })

      const firstRender = renderAstrologersPage()
      const firstButtons = screen.getAllByRole("button", { name: /Voir le profil de/i })
      expect(firstButtons[0]).toHaveAccessibleName("Voir le profil de Étienne Garnier")
      firstRender.unmount()

      const secondRender = renderAstrologersPage()
      const secondButtons = screen.getAllByRole("button", { name: /Voir le profil de/i })
      expect(secondButtons[0]).toHaveAccessibleName("Voir le profil de Luna Caron")
      secondRender.unmount()
    })

    it("renders premium hierarchy and highlights the onboarding astrologer", () => {
      mockUseAstrologers.mockReturnValue({
        data: [
          {
            id: "guide",
            name: "Guide Psychologique",
            first_name: "Étienne",
            last_name: "Garnier",
            avatar_url: "/avatars/etienne.jpg",
            provider_type: "ia",
            specialties: ["Débutants", "Bases", "Onboarding"],
            style: "Pédagogique",
            bio_short: "Astrologue d'entrée pour les débutants.",
          },
          ...mockAstrologersList,
        ],
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByRole("heading", { name: "Nos Astrologues" })).toBeInTheDocument()
      expect(screen.getByText("Étienne Garnier")).toBeInTheDocument()
    })

    it("renders grid of astrologer cards when data is loaded", () => {
      mockUseAstrologers.mockReturnValue({
        data: mockAstrologersList,
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByText("Nos Astrologues")).toBeInTheDocument()
      expect(screen.getByText("Luna Caron")).toBeInTheDocument()
      expect(screen.getByText("Orion Vasseur")).toBeInTheDocument()
    })

    it("displays avatar, name, specialties, and style for each card", () => {
      mockUseAstrologers.mockReturnValue({
        data: mockAstrologersList,
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByText("Luna Caron")).toBeInTheDocument()
      expect(screen.getByText("Bienveillant et direct")).toBeInTheDocument()
      expect(screen.getByText("Astrologue IA")).toBeInTheDocument()
      expect(screen.getByText("Astrologue réel")).toBeInTheDocument()
      expect(screen.getByText("Thème natal")).toBeInTheDocument()
      expect(screen.getByText("Transits")).toBeInTheDocument()
      expect(screen.getByText("Relations")).toBeInTheDocument()
      expect(screen.getByAltText("Avatar de Luna Caron")).toBeInTheDocument()
    })

    it("shows loading state while fetching", () => {
      mockUseAstrologers.mockReturnValue({
        data: undefined,
        isPending: true,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByText("Chargement...")).toBeInTheDocument()
    })

    it("shows error state when fetch fails", () => {
      mockUseAstrologers.mockReturnValue({
        data: undefined,
        isPending: false,
        error: new Error("Network error"),
      })

      renderAstrologersPage()

      expect(screen.getByText("Erreur lors du chargement des astrologues.")).toBeInTheDocument()
    })
  })

  describe("AC2: Navigation vers profil", () => {
    it("navigates to profile page when clicking astrologer card", () => {
      mockUseAstrologers.mockReturnValue({
        data: mockAstrologersList,
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      const lunaCard = screen.getByRole("button", { name: /Voir le profil de Luna Caron/i })
      fireEvent.click(lunaCard)

      expect(mockNavigate).toHaveBeenCalledWith(`/astrologers/${encodeURIComponent("1")}`)
    })

    it("uses encodeURIComponent for profile navigation with valid ID formats", () => {
      const validId = "astro_expert-42"
      const astrologerValid = {
        id: validId,
        name: "Astro Expert",
        first_name: "Astro",
        last_name: "Expert",
        avatar_url: "/avatars/expert.jpg",
        specialties: ["Test"],
        style: "Test style",
        bio_short: "Test bio.",
      }
      mockUseAstrologers.mockReturnValue({
        data: [astrologerValid],
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      const card = screen.getByRole("button", { name: /Voir le profil de Astro Expert/i })
      fireEvent.click(card)

      expect(mockNavigate).toHaveBeenCalledWith(`/astrologers/${encodeURIComponent(validId)}`)
    })
  })

  describe("AC5: Empty state", () => {
    it("shows empty state when no astrologers available", () => {
      mockUseAstrologers.mockReturnValue({
        data: [],
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByText("Aucun astrologue disponible")).toBeInTheDocument()
    })
  })
})

describe("AstrologerProfilePage", () => {
  const mockProfile = {
    id: "1",
    name: "Luna Céleste",
    first_name: "Luna",
    last_name: "Caron",
    avatar_url: "/avatars/luna.jpg",
    specialties: ["Thème natal", "Transits", "Relations"],
    style: "Bienveillant et direct",
    bio_short: "Astrologue depuis 15 ans.",
    bio_full: "Luna propose une astrologie centrée sur les émotions, les relations et l’équilibre intérieur.",
    gender: "female" as const,
    age: 36,
    location: "Paris, France",
    quote: "Je vous aide à relire votre thème avec douceur.",
    mission_statement: "Se comprendre pour mieux se relier.",
    ideal_for: "Idéal pour relations",
    metrics: {
      total_experience_years: 5,
      experience_years: 7,
      consultations_count: 2400,
      average_rating: 4.8,
    },
    specialties_details: [
      { title: "Thème natal", description: "Lecture simple et émotionnelle." },
      { title: "Transits", description: "Comprendre les cycles actuels." },
    ],
    professional_background: [
      "5 ans en accompagnement psychologique (non-clinique)",
      "7 ans astrologue relationnelle",
    ],
    key_skills: ["Relations", "Transits"],
    behavioral_style: ["Douceur", "Clarté"],
    reviews: [
      {
        id: "review-1",
        user_name: "Marie",
        rating: 5,
        comment: "Très éclairante.",
        tags: ["Débutante"],
        created_at: "2026-03-01T10:00:00Z",
      },
    ],
    review_summary: {
      average_rating: 4.8,
      review_count: 127,
    },
    user_rating: 4,
    user_review: {
      id: "my-review",
      user_name: "marie.lou",
      rating: 4,
      comment: "",
      tags: [],
      created_at: "2026-03-02T10:00:00Z",
    },
    action_state: {
      has_chat: false,
      has_natal_interpretation: false,
    },
  }

  describe("AC3: Profil astrologue", () => {
    it("displays complete profile with hero, metrics, specialties and reviews", () => {
      mockUseAstrologer.mockReturnValue({
        data: mockProfile,
        isPending: false,
        error: null,
      })

      renderProfilePage("1")

      expect(screen.getByText("Luna Caron")).toBeInTheDocument()
      expect(screen.getByText("Astrologue IA")).toBeInTheDocument()
      expect(screen.getByText(/Astrologue .*Chaleureuse/)).toBeInTheDocument()
      expect(screen.getByText("Paris, France")).toBeInTheDocument()
      expect(screen.getByText("7 ans d'expérience")).toBeInTheDocument()
      expect(screen.getByText("Thème natal")).toBeInTheDocument()
      expect(screen.getByText(/Luna propose une astrologie centrée sur les émotions/)).toBeInTheDocument()
      expect(screen.getByText("Je vous aide à relire votre thème avec douceur.")).toBeInTheDocument()
      expect(screen.getByText("Personnes accompagnées")).toBeInTheDocument()
      expect(screen.getByText(/Marie/)).toBeInTheDocument()
      expect(screen.getByRole("heading", { name: "Avis" })).toBeInTheDocument()
      expect(screen.getByText(/\(127 avis\)/)).toBeInTheDocument()
    })

    it("shows loading state", () => {
      mockUseAstrologer.mockReturnValue({
        data: undefined,
        isPending: true,
        error: null,
      })

      renderProfilePage("1")

      expect(screen.getByText("Chargement...")).toBeInTheDocument()
    })

    it("shows not found state for unknown astrologer", () => {
      mockUseAstrologer.mockReturnValue({
        data: null,
        isPending: false,
        error: null,
      })

      renderProfilePage("999")

      expect(screen.getByText("Astrologue introuvable")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Retour au catalogue" })).toBeInTheDocument()
    })

    it("shows error state when useAstrologer returns an error", () => {
      mockUseAstrologer.mockReturnValue({
        data: undefined,
        isPending: false,
        error: new Error("Server error"),
        refetch: vi.fn(),
      })

      renderProfilePage("1")

      expect(screen.getByText("Erreur lors du chargement des astrologues.")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument()
    })
  })

  describe("AC4: Démarrer conversation", () => {
    it("creates or resumes chat from the profile CTA", () => {
      mockUseAstrologer.mockReturnValue({
        data: mockProfile,
        isPending: false,
        error: null,
        refetch: vi.fn(),
      })

      renderProfilePage("1")

      const ctaButton = screen.getByRole("button", { name: /Démarrer un chat|Start a chat/i })
      fireEvent.click(ctaButton)

      expect(mockNavigate).toHaveBeenCalledWith(`/chat?personaId=${encodeURIComponent("1")}`)
    })

    it("resumes the existing conversation when one already exists", () => {
      const otherProfile = {
        ...mockProfile,
        id: "42",
        name: "Autre Astrologue",
        action_state: {
          has_chat: true,
          last_chat_id: "902",
          has_natal_interpretation: false,
        },
      }
      mockUseAstrologer.mockReturnValue({
        data: otherProfile,
        isPending: false,
        error: null,
        refetch: vi.fn(),
      })

      renderProfilePage("42")

      const ctaButton = screen.getByRole("button", { name: /Reprendre le chat|Resume chat/i })
      fireEvent.click(ctaButton)

      expect(mockNavigate).toHaveBeenCalledWith(`/chat/${encodeURIComponent("902")}`)
    })

    it("routes natal and consultation CTAs to supported pages", () => {
      const astrologerWithActions = {
        ...mockProfile,
        id: "astro_expert_42",
        action_state: {
          has_chat: false,
          has_natal_interpretation: true,
          last_natal_interpretation_id: "321",
        },
      }
      mockUseAstrologer.mockReturnValue({
        data: astrologerWithActions,
        isPending: false,
        error: null,
        refetch: vi.fn(),
      })

      renderProfilePage("astro_expert_42")

      fireEvent.click(screen.getByRole("button", { name: /Voir mon interprétation|View my interpretation/i }))
      expect(mockNavigate).toHaveBeenCalledWith("/natal?interpretationId=321")

      fireEvent.click(screen.getByRole("button", { name: /Lancer une consultation|Start a consultation/i }))
      expect(mockNavigate).toHaveBeenCalledWith(
        `/consultations/new?astrologerId=${encodeURIComponent("astro_expert_42")}`
      )
    })
  })

  describe("Navigation", () => {
    it("can navigate back to catalogue", () => {
      mockUseAstrologer.mockReturnValue({
        data: mockProfile,
        isPending: false,
        error: null,
      })

      renderProfilePage("1")

      const backButton = screen.getByRole("button", { name: /Retour au catalogue/i })
      fireEvent.click(backButton)

      expect(mockNavigate).toHaveBeenCalledWith("/astrologers")
    })
  })

  describe("Reviews flow", () => {
    it("opens the review composer when selecting a rating for the first time", () => {
      const unratedProfile = {
        ...mockProfile,
        user_rating: undefined,
        user_review: undefined,
      }
      mockUseAstrologer.mockReturnValue({
        data: unratedProfile,
        isPending: false,
        error: null,
        refetch: vi.fn(),
      })

      renderProfilePage("1")

      fireEvent.click(screen.getByRole("button", { name: "Votre note 5/5" }))

      expect(screen.getByRole("dialog")).toBeInTheDocument()
      expect(
        screen.getByPlaceholderText("Décrivez votre expérience avec cet astrologue...")
      ).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Publier l'avis" })).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Fermer" })).toBeInTheDocument()
    })

    it("shows a validation message when the review is shorter than 10 characters", () => {
      const unratedProfile = {
        ...mockProfile,
        user_rating: undefined,
        user_review: undefined,
      }
      mockUseAstrologer.mockReturnValue({
        data: unratedProfile,
        isPending: false,
        error: null,
        refetch: vi.fn(),
      })

      renderProfilePage("1")

      fireEvent.click(screen.getByRole("button", { name: "Votre note 5/5" }))
      fireEvent.change(
        screen.getByPlaceholderText("Décrivez votre expérience avec cet astrologue..."),
        { target: { value: "court" } }
      )
      fireEvent.click(screen.getByRole("button", { name: "Publier l'avis" }))

      expect(
        screen.getByText("Merci d'écrire au moins 10 caractères pour publier un avis.")
      ).toBeInTheDocument()
    })

    it("shows a button to add a written review after a rating-only submission", () => {
      mockUseAstrologer.mockReturnValue({
        data: mockProfile,
        isPending: false,
        error: null,
        refetch: vi.fn(),
      })

      renderProfilePage("1")

      expect(screen.getByRole("button", { name: "Rédiger un avis" })).toBeInTheDocument()
    })
  })
})
