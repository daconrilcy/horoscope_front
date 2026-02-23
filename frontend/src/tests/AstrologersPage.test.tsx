import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"

import { AstrologersPage } from "../pages/AstrologersPage"
import { AstrologerProfilePage } from "../pages/AstrologerProfilePage"

const mockUseAstrologers = vi.fn()
const mockUseAstrologer = vi.fn()
const mockNavigate = vi.fn()

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
    useAstrologers: () => mockUseAstrologers(),
    useAstrologer: (id: string | undefined) => mockUseAstrologer(id),
    isValidAstrologerId: actual.isValidAstrologerId,
  }
})

beforeEach(() => {
  localStorage.setItem("lang", "fr")
})

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

function renderAstrologersPage() {
  return render(
    <MemoryRouter initialEntries={["/astrologers"]} future={routerFutureFlags}>
      <Routes>
        <Route path="/astrologers" element={<AstrologersPage />} />
        <Route path="/astrologers/:id" element={<AstrologerProfilePage />} />
        <Route path="/chat" element={<div>Chat Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

function renderProfilePage(id: string) {
  return render(
    <MemoryRouter initialEntries={[`/astrologers/${id}`]} future={routerFutureFlags}>
      <Routes>
        <Route path="/astrologers" element={<AstrologersPage />} />
        <Route path="/astrologers/:id" element={<AstrologerProfilePage />} />
        <Route path="/chat" element={<div>Chat Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

afterEach(() => {
  cleanup()
  mockUseAstrologers.mockReset()
  mockUseAstrologer.mockReset()
  mockNavigate.mockReset()
  localStorage.clear()
})

describe("AstrologersPage", () => {
  const mockAstrologersList = [
    {
      id: "1",
      name: "Luna Céleste",
      avatar_url: "/avatars/luna.jpg",
      specialties: ["Thème natal", "Transits", "Relations"],
      style: "Bienveillant et direct",
      bio_short: "Astrologue depuis 15 ans.",
    },
    {
      id: "2",
      name: "Orion Mystique",
      avatar_url: "/avatars/orion.jpg",
      specialties: ["Carrière", "Événements"],
      style: "Analytique et précis",
      bio_short: "Expert en astrologie prévisionnelle.",
    },
  ]

  describe("AC1: Catalogue astrologues - Grille de vignettes", () => {
    it("renders grid of astrologer cards when data is loaded", () => {
      mockUseAstrologers.mockReturnValue({
        data: mockAstrologersList,
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByText("Nos Astrologues")).toBeInTheDocument()
      expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
      expect(screen.getByText("Orion Mystique")).toBeInTheDocument()
    })

    it("displays avatar, name, specialties, and style for each card", () => {
      mockUseAstrologers.mockReturnValue({
        data: mockAstrologersList,
        isPending: false,
        error: null,
      })

      renderAstrologersPage()

      expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
      expect(screen.getByText("Bienveillant et direct")).toBeInTheDocument()
      expect(screen.getByText("Thème natal")).toBeInTheDocument()
      expect(screen.getByText("Transits")).toBeInTheDocument()
      expect(screen.getByText("Relations")).toBeInTheDocument()
      expect(screen.getByAltText("Avatar de Luna Céleste")).toBeInTheDocument()
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

      const lunaCard = screen.getByRole("button", { name: /Voir le profil de Luna Céleste/i })
      fireEvent.click(lunaCard)

      expect(mockNavigate).toHaveBeenCalledWith(`/astrologers/${encodeURIComponent("1")}`)
    })

    it("uses encodeURIComponent for profile navigation with valid ID formats", () => {
      const validId = "astro_expert-42"
      const astrologerValid = {
        id: validId,
        name: "Astro Expert",
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
    avatar_url: "/avatars/luna.jpg",
    specialties: ["Thème natal", "Transits", "Relations"],
    style: "Bienveillant et direct",
    bio_short: "Astrologue depuis 15 ans.",
    bio_full: "Passionnée par les étoiles depuis mon enfance, j'ai consacré 15 années à l'étude.",
    languages: ["Français", "Anglais", "Espagnol"],
    experience_years: 15,
  }

  describe("AC3: Profil astrologue", () => {
    it("displays complete profile with avatar, bio, specialties, languages, style", () => {
      mockUseAstrologer.mockReturnValue({
        data: mockProfile,
        isPending: false,
        error: null,
      })

      renderProfilePage("1")

      expect(screen.getByText("Luna Céleste")).toBeInTheDocument()
      expect(screen.getByText("Bienveillant et direct")).toBeInTheDocument()
      expect(screen.getByText("15 ans d'expérience")).toBeInTheDocument()
      expect(screen.getByText("Thème natal")).toBeInTheDocument()
      expect(screen.getByText("Français, Anglais, Espagnol")).toBeInTheDocument()
      expect(screen.getByText(/Passionnée par les étoiles/)).toBeInTheDocument()
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
      })

      renderProfilePage("1")

      expect(screen.getByText("Erreur lors du chargement des astrologues.")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Retour au catalogue" })).toBeInTheDocument()
    })
  })

  describe("AC4: Démarrer conversation", () => {
    it("navigates to chat with astrologer when clicking CTA", () => {
      mockUseAstrologer.mockReturnValue({
        data: mockProfile,
        isPending: false,
        error: null,
      })

      renderProfilePage("1")

      const ctaButton = screen.getByRole("button", { name: /Démarrer une conversation|Start a conversation/i })
      fireEvent.click(ctaButton)

      expect(mockNavigate).toHaveBeenCalledWith(`/chat?astrologerId=${encodeURIComponent("1")}`)
    })

    it("navigates to chat with correct astrologerId param for different astrologer", () => {
      const otherProfile = {
        ...mockProfile,
        id: "42",
        name: "Autre Astrologue",
      }
      mockUseAstrologer.mockReturnValue({
        data: otherProfile,
        isPending: false,
        error: null,
      })

      renderProfilePage("42")

      const ctaButton = screen.getByRole("button", { name: /Démarrer une conversation|Start a conversation/i })
      fireEvent.click(ctaButton)

      expect(mockNavigate).toHaveBeenCalledWith(`/chat?astrologerId=${encodeURIComponent("42")}`)
    })

    it("properly encodes astrologer id with underscore for chat navigation", () => {
      const idWithUnderscore = "astro_expert_42"
      const astrologerWithUnderscore = {
        ...mockProfile,
        id: idWithUnderscore,
        name: "Astro Expert",
      }
      mockUseAstrologer.mockReturnValue({
        data: astrologerWithUnderscore,
        isPending: false,
        error: null,
      })

      renderProfilePage(idWithUnderscore)

      const ctaButton = screen.getByRole("button", { name: /Démarrer une conversation|Start a conversation/i })
      fireEvent.click(ctaButton)

      expect(mockNavigate).toHaveBeenCalledWith(`/chat?astrologerId=${encodeURIComponent(idWithUnderscore)}`)
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
})
