import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"

import { ChatPage } from "../pages/ChatPage"

const mockUseSendChatMessage = vi.fn()
const mockUseChatConversations = vi.fn()
const mockUseChatConversationHistory = vi.fn()
const mockUseChatEntitlementUsage = vi.fn()
const mockUseCreateConversationByPersona = vi.fn()
const mockUseAstrologers = vi.fn()
const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock("../api/chat", () => ({
  ChatApiError: class extends Error {
    code: string
    status: number
    details: Record<string, string>

    constructor(code: string, message: string, status: number, details: Record<string, string> = {}) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
    }
  },
  useSendChatMessage: () => mockUseSendChatMessage(),
  useChatConversations: (limit?: number, offset?: number) => mockUseChatConversations(limit, offset),
  useChatConversationHistory: (id: number | null) => mockUseChatConversationHistory(id),
  useCreateConversationByPersona: () => mockUseCreateConversationByPersona(),
}))

vi.mock("../api/billing", () => ({
  BillingApiError: class extends Error {
    code: string
    status: number
    details: Record<string, string>

    constructor(code: string, message: string, status: number, details: Record<string, string> = {}) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
    }
  },
  useChatEntitlementUsage: () => mockUseChatEntitlementUsage(),
}))

vi.mock("../hooks/useEntitlementSnapshot", () => ({
  useUpgradeHint: vi.fn().mockReturnValue(undefined),
  useEntitlementsSnapshot: vi.fn().mockReturnValue({ data: null }),
  useFeatureAccess: vi.fn().mockReturnValue(undefined),
}))

vi.mock("../api/astrologers", () => ({
  useAstrologer: () => ({
    data: null,
    isPending: false,
    error: null,
  }),
  useAstrologers: () => mockUseAstrologers(),
}))

const routerFutureFlags = { v7_startTransition: true, v7_relativeSplatPath: true }

function renderWithRouter(initialRoute = "/chat") {
  return render(
    <MemoryRouter initialEntries={[initialRoute]} future={routerFutureFlags}>
      <Routes>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:conversationId" element={<ChatPage />} />
        <Route path="/astrologers" element={<div>Astrologers Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

afterEach(() => {
  cleanup()
  mockUseSendChatMessage.mockReset()
  mockUseChatConversations.mockReset()
  mockUseChatConversationHistory.mockReset()
  mockUseChatEntitlementUsage.mockReset()
  mockUseCreateConversationByPersona.mockReset()
  mockUseAstrologers.mockReset()
  mockNavigate.mockReset()
})

describe("ChatPage", () => {
  const baseConversationsState = {
    isPending: false,
    error: null,
    data: { conversations: [], total: 0, limit: 20, offset: 0 },
    refetch: vi.fn(),
  }

  const baseHistoryState = {
    isPending: false,
    error: null,
    data: null,
    refetch: vi.fn(),
  }

  const baseQuotaState = {
    isLoading: false,
    error: null,
    data: {
      quota_date: "2026-02-22",
      limit: 5,
      consumed: 0,
      remaining: 5,
      reset_at: "2026-02-23T00:00:00+00:00",
      blocked: false,
    },
    refetch: vi.fn(),
  }

  const baseSendMessageState = {
    isPending: false,
    isError: false,
    error: null,
    mutateAsync: vi.fn(),
  }

  const baseCreateConversationState = {
    isPending: false,
    isError: false,
    error: null,
    mutateAsync: vi.fn(),
  }

  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    mockUseChatEntitlementUsage.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue(baseSendMessageState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseCreateConversationByPersona.mockReturnValue(baseCreateConversationState)
    mockUseAstrologers.mockReturnValue({
      data: [],
      isPending: false,
      error: null,
    })
  })

  describe("Empty State (AC6)", () => {
    it("renders empty state when no conversations exist", () => {
      mockUseChatConversations.mockReturnValue(baseConversationsState)

      renderWithRouter()

      expect(screen.getByText(/Bienvenue dans vos discussions|Welcome to your conversations/)).toBeInTheDocument()
      expect(screen.getByText(/Démarrez une discussion|Start a conversation/)).toBeInTheDocument()
      expect(screen.getByRole("button", { name: /Démarrer ma première discussion|Start my first conversation/ })).toBeInTheDocument()
    })

    it("shows loading state while conversations are loading", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        isPending: true,
        data: null,
      })

      renderWithRouter()

      // Skeleton items are rendered while loading (aria-hidden, no visible text "Chargement...")
      expect(screen.queryByText(/Aucune conversation|No conversation/)).not.toBeInTheDocument()
      expect(screen.queryByText(/Bienvenue dans vos discussions|Welcome/)).not.toBeInTheDocument()
    })
  })

  describe("Conversation List (AC3)", () => {
    it("renders conversation list when conversations exist", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 1, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Message 1" },
            { conversation_id: 2, status: "active", updated_at: "2026-02-21T10:00:00Z", last_message_preview: "Message 2" },
          ],
          total: 2,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter()

      expect(screen.getByText("Message 1")).toBeInTheDocument()
      expect(screen.getByText("Message 2")).toBeInTheDocument()
    })

    it("selects conversation and navigates to /chat/:conversationId", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test message" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter()

      fireEvent.click(screen.getByText("Test message"))

      expect(mockNavigate).toHaveBeenCalledWith("/chat/42")
    })

    it("loads conversation history when conversation is selected", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      mockUseChatConversationHistory.mockImplementation((id) => {
        if (id === 42) {
          return {
            isPending: false,
            error: null,
            data: {
              conversation_id: 42,
              status: "active",
              updated_at: "2026-02-22T10:00:00Z",
              messages: [
                { message_id: 1, role: "user", content: "Question", created_at: "2026-02-22T10:00:00Z" },
                { message_id: 2, role: "assistant", content: "Réponse", created_at: "2026-02-22T10:01:00Z" },
              ],
            },
            refetch: vi.fn(),
          }
        }
        return baseHistoryState
      })

      renderWithRouter("/chat/42")

      expect(screen.getByText("Question")).toBeInTheDocument()
      expect(screen.getByText("Réponse")).toBeInTheDocument()
    })
  })

  describe("Deep Link (AC1)", () => {
    it("loads conversation from URL parameter /chat/123", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 123, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Deep link test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      mockUseChatConversationHistory.mockImplementation((id) => {
        if (id === 123) {
          return {
            isPending: false,
            error: null,
            data: {
              conversation_id: 123,
              status: "active",
              updated_at: "2026-02-22T10:00:00Z",
              messages: [
                { message_id: 1, role: "user", content: "Deep link question", created_at: "2026-02-22T10:00:00Z" },
              ],
            },
            refetch: vi.fn(),
          }
        }
        return baseHistoryState
      })

      renderWithRouter("/chat/123")

      expect(screen.getByText("Deep link question")).toBeInTheDocument()
    })

    it("shows not found state for invalid conversation URL", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 1, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Existing" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/999999")

      expect(screen.getByText(/Conversation introuvable|Conversation not found/)).toBeInTheDocument()
      // 999999 appears in both the error description and the astrologer panel — use getAllByText
      expect(screen.getAllByText(/999999/).length).toBeGreaterThanOrEqual(1)
      expect(screen.getByRole("link", { name: /Retour aux conversations|Back to conversations/ })).toBeInTheDocument()
    })
  })

  describe("Redirection by personaId (AC2)", () => {
    it("calls createConversationByPersona and navigates when ?personaId is present", async () => {
      const mutateAsync = vi.fn().mockResolvedValue({
        conversation_id: 77,
        persona_id: "luna",
        created: true,
      })
      mockUseCreateConversationByPersona.mockReturnValue({
        ...baseCreateConversationState,
        mutateAsync,
      })
      mockUseChatConversations.mockReturnValue(baseConversationsState)

      renderWithRouter("/chat?personaId=luna")

      await waitFor(() => {
        expect(mutateAsync).toHaveBeenCalledWith("luna")
        expect(mockNavigate).toHaveBeenCalledWith("/chat/77", { replace: true })
      })
    })

    it("redirects to /astrologers when personaId is unknown (API error)", async () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
      const mutateAsync = vi.fn().mockRejectedValue(new Error("Not found"))
      mockUseCreateConversationByPersona.mockReturnValue({
        ...baseCreateConversationState,
        mutateAsync,
      })
      mockUseChatConversations.mockReturnValue(baseConversationsState)

      renderWithRouter("/chat?personaId=unknown-persona")

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith("/astrologers", { replace: true })
      })
      consoleErrorSpy.mockRestore()
    })
  })

  describe("Auto-redirect to last conversation (AC3)", () => {
    it("redirects to last conversation when navigating to /chat without ID", async () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 5, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Latest" },
            { conversation_id: 3, status: "active", updated_at: "2026-02-21T10:00:00Z", last_message_preview: "Older" },
          ],
          total: 2,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat")

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith("/chat/5", { replace: true })
      })
    })

    it("does not redirect when conversations are still loading", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        isPending: true,
        data: null,
      })

      renderWithRouter("/chat")

      expect(mockNavigate).not.toHaveBeenCalledWith(
        expect.stringMatching(/^\/chat\/\d+/),
        expect.any(Object)
      )
    })

    it("does not redirect to last conversation if conversationId already in URL", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 5, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Latest" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/5")

      expect(mockNavigate).not.toHaveBeenCalledWith("/chat/5", { replace: true })
    })
  })

  describe("Empty Chat State with Persona (AC5)", () => {
    it("displays persona name in empty conversation state", () => {
      mockUseAstrologers.mockReturnValue({
        data: [
          {
            id: "persona-luna",
            name: "Luna",
            first_name: "Luna",
            last_name: "Caron",
            avatar_url: "/assets/astrologers/luna.png",
            specialties: ["Relations"],
            style: "Douce",
            bio_short: "Astrologue relationnelle",
          },
        ],
        isPending: false,
        error: null,
      })
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            {
              conversation_id: 10,
              persona_id: "persona-luna",
              status: "active",
              updated_at: "2026-02-22T10:00:00Z",
              last_message_preview: "",
              persona_name: "Luna",
              avatar_url: undefined,
            },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })
      mockUseChatConversationHistory.mockReturnValue({
        ...baseHistoryState,
        data: { conversation_id: 10, status: "active", updated_at: "2026-02-22T10:00:00Z", messages: [] },
      })

      renderWithRouter("/chat/10")

      const lunaElements = screen.getAllByText("Luna Caron")
      expect(lunaElements.length).toBeGreaterThanOrEqual(1)
      expect(lunaElements.some((el) => el.className === "astrologer-chip-name")).toBe(true)
      expect(screen.getByAltText("Luna Caron")).toHaveAttribute("src", "/assets/astrologers/luna.png")
      expect(screen.getByText("Bonjour, que puis-je faire pour vous ?")).toBeInTheDocument()
    })
  })

  describe("Send Message (AC4)", () => {
    it("sends message and shows optimistic update", async () => {
      const mutateAsync = vi.fn().mockResolvedValue({
        conversation_id: 42,
        user_message: { message_id: 1, content: "Bonjour", created_at: "2026-02-22T10:00:00Z" },
        assistant_message: { message_id: 2, content: "Salut", created_at: "2026-02-22T10:01:00Z" },
        recovery: { off_scope_detected: false, recovery_applied: false },
      })

      mockUseSendChatMessage.mockReturnValue({
        ...baseSendMessageState,
        mutateAsync,
      })

      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/42")

      const textarea = screen.getByRole("textbox")
      fireEvent.change(textarea, { target: { value: "Bonjour" } })
      fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

      expect(mutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          message: "Bonjour",
          conversation_id: 42,
          client_message_id: expect.any(String),
        })
      )

      await waitFor(() => {
        expect(screen.getByText("Salut")).toBeInTheDocument()
      })
    })

    it("shows typing indicator while message is pending", () => {
      mockUseSendChatMessage.mockReturnValue({
        ...baseSendMessageState,
        isPending: true,
      })

      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/42")

      expect(screen.getByLabelText("L'astrologue écrit...")).toBeInTheDocument()
    })

    it("navigates to new conversation when sending first message", async () => {
      const mutateAsync = vi.fn().mockResolvedValue({
        conversation_id: 99,
        user_message: { message_id: 1, content: "Premier message", created_at: "2026-02-22T10:00:00Z" },
        assistant_message: { message_id: 2, content: "Bienvenue", created_at: "2026-02-22T10:01:00Z" },
        recovery: { off_scope_detected: false, recovery_applied: false },
      })

      mockUseSendChatMessage.mockReturnValue({
        ...baseSendMessageState,
        mutateAsync,
      })

      // Has conversations — so ChatWindow is rendered (not ChatEmptyState)
      // AC3 auto-redirect will call navigate("/chat/1", {replace:true}) but since
      // navigate is mocked it doesn't actually change the URL in MemoryRouter.
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 1, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Existing" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat")

      const textarea = screen.getByRole("textbox")
      fireEvent.change(textarea, { target: { value: "Premier message" } })
      fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith("/chat/99", { replace: true })
      })
    })
  })

  describe("Error Handling", () => {
    it("shows error message when send fails", () => {
      mockUseSendChatMessage.mockReturnValue({
        ...baseSendMessageState,
        isError: true,
        error: {
          code: "llm_unavailable",
          message: "llm provider is unavailable",
          details: {},
        },
      })

      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/42")

      expect(
        screen.getByText(
          "Je suis désolé, je ne peux pas vous répondre pour l'instant. Revenez un peu plus tard."
        )
      ).toBeInTheDocument()
    })

    it("shows quota blocked message", () => {
      mockUseChatEntitlementUsage.mockReturnValue({
        ...baseQuotaState,
        data: { ...baseQuotaState.data, blocked: true },
      })

      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/42")

      expect(screen.getByText(/quota quotidien est épuisé/)).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled()
    })
  })

  describe("3-Column Layout (AC1)", () => {
    it("renders conversation list panel", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 1, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter()

      expect(
        screen.getByRole("heading", { level: 1, name: "Chat astrologique" })
      ).toBeInTheDocument()
      expect(screen.getByText("Discussions")).toBeInTheDocument()
      expect(screen.getByPlaceholderText("Rechercher...")).toBeInTheDocument()
    })

    it("renders chat window panel", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            { conversation_id: 42, status: "active", updated_at: "2026-02-22T10:00:00Z", last_message_preview: "Test" },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/42")

      expect(screen.getByRole("textbox")).toBeInTheDocument()
      expect(screen.getByRole("button", { name: "Envoyer" })).toBeInTheDocument()
    })

    it("renders persona chip in chat header when persona is available", () => {
      mockUseAstrologers.mockReturnValue({
        data: [
          {
            id: "persona-luna",
            name: "Luna",
            first_name: "Luna",
            last_name: "Caron",
            avatar_url: "/assets/astrologers/luna.png",
            specialties: ["Relations"],
            style: "Douce",
            bio_short: "Astrologue relationnelle",
          },
        ],
        isPending: false,
        error: null,
      })
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            {
              conversation_id: 42,
              persona_id: "persona-luna",
              status: "active",
              updated_at: "2026-02-22T10:00:00Z",
              last_message_preview: "Test",
              persona_name: "Luna",
            },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter("/chat/42")

      const lunaElements = screen.getAllByText("Luna Caron")
      expect(lunaElements.some((el) => el.className === "astrologer-chip-name")).toBe(true)
      expect(screen.getByAltText("Luna Caron")).toHaveAttribute("src", "/assets/astrologers/luna.png")
      expect(screen.queryByText("Votre Astrologue")).not.toBeInTheDocument()
    })

    it("uses astrologer photo in conversation list items", () => {
      mockUseAstrologers.mockReturnValue({
        data: [
          {
            id: "persona-luna",
            name: "Luna",
            first_name: "Luna",
            last_name: "Caron",
            avatar_url: "/assets/astrologers/luna.png",
            specialties: ["Relations"],
            style: "Douce",
            bio_short: "Astrologue relationnelle",
          },
        ],
        isPending: false,
        error: null,
      })
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        data: {
          conversations: [
            {
              conversation_id: 1,
              persona_id: "persona-luna",
              persona_name: "Luna",
              avatar_url: "https://api.dicebear.com/legacy.svg",
              status: "active",
              updated_at: "2026-02-22T10:00:00Z",
              last_message_preview: "Test",
            },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      })

      renderWithRouter()

      expect(screen.getByAltText("Avatar de Luna Caron")).toHaveAttribute(
        "src",
        "/assets/astrologers/luna.png"
      )
      expect(screen.getByText("Luna Caron")).toBeInTheDocument()
    })
  })
})
