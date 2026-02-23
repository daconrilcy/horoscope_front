import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { MemoryRouter, Route, Routes } from "react-router-dom"

import { ChatPage } from "../pages/ChatPage"

const mockUseSendChatMessage = vi.fn()
const mockUseChatConversations = vi.fn()
const mockUseChatConversationHistory = vi.fn()
const mockUseBillingQuota = vi.fn()
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
  useBillingQuota: () => mockUseBillingQuota(),
}))

vi.mock("../api/astrologers", () => ({
  useAstrologer: () => ({
    data: null,
    isPending: false,
    error: null,
  }),
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
  mockUseBillingQuota.mockReset()
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

  beforeEach(() => {
    localStorage.setItem("lang", "fr")
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue(baseSendMessageState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
  })

  describe("Empty State (AC6)", () => {
    it("renders empty state when no conversations exist", () => {
      mockUseChatConversations.mockReturnValue(baseConversationsState)

      renderWithRouter()

      expect(screen.getByText(/Aucune conversation|No conversation/)).toBeInTheDocument()
      expect(screen.getByText(/Commencez une nouvelle conversation|Start a new conversation/)).toBeInTheDocument()
      expect(screen.getByRole("link", { name: /Choisir un astrologue|Choose an astrologer/ })).toBeInTheDocument()
    })

    it("shows loading state while conversations are loading", () => {
      mockUseChatConversations.mockReturnValue({
        ...baseConversationsState,
        isPending: true,
        data: null,
      })

      renderWithRouter()

      expect(screen.getByText("Chargement...")).toBeInTheDocument()
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

  describe("Deep Link (AC7)", () => {
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
      expect(screen.getByText(/999999/)).toBeInTheDocument()
      expect(screen.getByRole("link", { name: /Retour aux conversations|Back to conversations/ })).toBeInTheDocument()
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

      expect(mutateAsync).toHaveBeenCalledWith({
        message: "Bonjour",
        conversation_id: 42,
      })

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
          code: "server_error",
          message: "Erreur serveur",
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

      expect(screen.getByText("Erreur: Erreur serveur")).toBeInTheDocument()
    })

    it("shows quota blocked message", () => {
      mockUseBillingQuota.mockReturnValue({
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

      expect(screen.getByText("Conversations")).toBeInTheDocument()
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

    it("renders astrologer detail panel", () => {
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

      expect(screen.getByText("Votre Astrologue")).toBeInTheDocument()
      expect(screen.getByText("#42")).toBeInTheDocument()
    })
  })
})
