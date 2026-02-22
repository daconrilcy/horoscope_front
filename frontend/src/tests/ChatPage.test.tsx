import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ChatPage } from "../pages/ChatPage"

const mockUseSendChatMessage = vi.fn()
const mockUseChatConversations = vi.fn()
const mockUseChatConversationHistory = vi.fn()
const mockUseModuleAvailability = vi.fn()
const mockUseExecuteModule = vi.fn()
const mockUseRequestGuidance = vi.fn()
const mockUseRequestContextualGuidance = vi.fn()
const mockUseBillingQuota = vi.fn()

function createDeferred<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

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
  useModuleAvailability: () => mockUseModuleAvailability(),
  useExecuteModule: () => mockUseExecuteModule(),
}))

vi.mock("../api/guidance", () => ({
  GuidanceApiError: class extends Error {
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
  useRequestGuidance: () => mockUseRequestGuidance(),
  useRequestContextualGuidance: () => mockUseRequestContextualGuidance(),
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

afterEach(() => {
  cleanup()
  mockUseSendChatMessage.mockReset()
  mockUseChatConversations.mockReset()
  mockUseChatConversationHistory.mockReset()
  mockUseModuleAvailability.mockReset()
  mockUseExecuteModule.mockReset()
  mockUseRequestGuidance.mockReset()
  mockUseRequestContextualGuidance.mockReset()
  mockUseBillingQuota.mockReset()
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
  }

  const baseQuotaState = {
    isLoading: false,
    error: null,
    data: {
      quota_date: "2026-02-19",
      limit: 5,
      consumed: 0,
      remaining: 5,
      reset_at: "2026-02-20T00:00:00+00:00",
      blocked: false,
    },
    refetch: vi.fn(),
  }

  const baseModuleAvailability = {
    isPending: false,
    error: null,
    data: {
      modules: [
        {
          module: "tarot",
          flag_key: "tarot_enabled",
          status: "module-ready",
          available: true,
          reason: "segment_match",
        },
        {
          module: "runes",
          flag_key: "runes_enabled",
          status: "module-locked",
          available: false,
          reason: "feature_disabled",
        },
      ],
      total: 2,
      available_count: 1,
    },
    refetch: vi.fn(),
  }

  beforeEach(() => {
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
  })

  it("renders empty state", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(screen.getByText("Aucun message dans cette conversation.")).toBeInTheDocument()
  })

  it("renders loading state", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: true,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(screen.getByText("Génération de la réponse en cours...")).toBeInTheDocument()
  })

  it("renders technical error with actionable fallback", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: true,
      error: {
        message: "llm provider timeout",
        details: { fallback_message: "Le service est indisponible temporairement. Réessayez dans un instant." },
      },
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(screen.getByText("Erreur: llm provider timeout")).toBeInTheDocument()
    expect(
      screen.getByText("Le service est indisponible temporairement. Réessayez dans un instant."),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument()
  })

  it("renders timeout transport error message", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: true,
      error: {
        code: "request_timeout",
        message: "La requête a expiré. Réessayez dans un instant.",
        details: {},
      },
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(
      screen.getByText("Erreur: La requête a expiré. Réessayez dans un instant."),
    ).toBeInTheDocument()
  })

  it("submits message through mutation", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    const refetch = vi.fn()
    mockUseChatConversations.mockReturnValue({ ...baseConversationsState, refetch })
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    const quotaRefetch = vi.fn()
    mockUseBillingQuota.mockReturnValue({ ...baseQuotaState, refetch: quotaRefetch })
    const mutateAsync = vi.fn().mockResolvedValue({
      conversation_id: 42,
      user_message: { message_id: 1, content: "Bonjour" },
      assistant_message: { message_id: 2, content: "Guidance astrologique: Bonjour" },
      recovery: { off_scope_detected: false, recovery_applied: false },
    })
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync,
    })

    render(<ChatPage />)
    fireEvent.change(screen.getByLabelText("Votre message"), { target: { value: "Bonjour" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(mutateAsync).toHaveBeenCalledWith({ message: "Bonjour" })
    await waitFor(() => {
      expect(refetch).toHaveBeenCalled()
    })
    expect(quotaRefetch).toHaveBeenCalled()
  })

  it("shows active conversation indicator and keeps message history continuity", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    const refetch = vi.fn()
    mockUseChatConversations.mockReturnValue({
      ...baseConversationsState,
      refetch,
      data: {
        conversations: [{ conversation_id: 42, last_message_preview: "Dernier message", status: "active", updated_at: "" }],
        total: 1,
        limit: 20,
        offset: 0,
      },
    })
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    const mutateAsync = vi.fn().mockResolvedValue({
      conversation_id: 42,
      user_message: { message_id: 1, content: "Bonjour" },
      assistant_message: { message_id: 2, content: "Salut" },
      recovery: { off_scope_detected: false, recovery_applied: false },
    })

    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync,
    })

    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Votre message"), { target: { value: "Bonjour" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    await waitFor(() => {
      expect(screen.getByText(/Salut/)).toBeInTheDocument()
    })

    expect(screen.getByText(/Bonjour/)).toBeInTheDocument()
    expect(screen.getByText(/Conversation active: #42/)).toBeInTheDocument()
  })

  it("restores messages from selected conversation history", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue({
      ...baseConversationsState,
      data: {
        conversations: [
          { conversation_id: 42, last_message_preview: "Dernier 42", status: "active", updated_at: "" },
          { conversation_id: 43, last_message_preview: "Dernier 43", status: "active", updated_at: "" },
        ],
        total: 2,
        limit: 20,
        offset: 0,
      },
    })
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    // Mock history for 43
    mockUseChatConversationHistory.mockImplementation((id) => {
      if (id === 43) {
        return {
          isPending: false,
          error: null,
          data: {
            conversation_id: 43,
            status: "active",
            updated_at: "",
            messages: [
              { message_id: 10, role: "user", content: "Question 43", created_at: "" },
              { message_id: 11, role: "assistant", content: "Réponse 43", created_at: "" },
            ],
          },
        }
      }
      return baseHistoryState
    })

    render(<ChatPage />)

    fireEvent.click(screen.getByRole("button", { name: /#43 - Dernier 43/ }))

    expect(await screen.findByText(/Question 43/)).toBeInTheDocument()
    expect(screen.getByText(/Réponse 43/)).toBeInTheDocument()
    expect(screen.getByText(/Conversation active: #43/)).toBeInTheDocument()
  })

  it("sends follow-up on selected conversation", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    
    // Initial state: conversation 43 selected
    mockUseChatConversationHistory.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        conversation_id: 43,
        status: "active",
        updated_at: "",
        messages: [{ message_id: 10, role: "user", content: "Init", created_at: "" }],
      },
    })

    const mutateAsync = vi.fn().mockResolvedValue({
      conversation_id: 43,
      user_message: { message_id: 11, content: "Follow up" },
      assistant_message: { message_id: 12, content: "Réponse follow up" },
      recovery: { off_scope_detected: false, recovery_applied: false },
    })
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync,
    })

    const { rerender } = render(<ChatPage />)
    
    mockUseChatConversations.mockReturnValue({
      ...baseConversationsState,
      data: {
        conversations: [{ conversation_id: 43, last_message_preview: "Init", status: "active", updated_at: "" }],
        total: 1, limit: 20, offset: 0
      }
    })
    rerender(<ChatPage />)
    
    fireEvent.click(screen.getByRole("button", { name: /#43 - Init/ }))

    fireEvent.change(screen.getByLabelText("Votre message"), { target: { value: "Follow up" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(mutateAsync).toHaveBeenCalledWith({
      message: "Follow up",
      conversation_id: 43,
    })
  })

  it("requests daily and weekly guidance and renders response", async () => {
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })

    const mutateGuidance = vi.fn()
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        guidance_id: "g1",
        period: "daily",
        summary: "Belle journée.",
        key_points: ["point 1"],
        actionable_advice: ["conseil 1"],
        disclaimer: "Pour divertissement.",
      },
      mutate: mutateGuidance,
    })

    render(<ChatPage />)

    fireEvent.click(screen.getByRole("button", { name: "Guidance du jour" }))
    expect(mutateGuidance).toHaveBeenCalledWith({ period: "daily" })

    expect(screen.getByText("Guidance quotidienne")).toBeInTheDocument()
    expect(screen.getByText("Belle journée.")).toBeInTheDocument()
    expect(screen.getByText("point 1")).toBeInTheDocument()
  })

  it("requests guidance on selected conversation context", async () => {
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })

    mockUseChatConversationHistory.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        conversation_id: 43,
        status: "active",
        updated_at: "",
        messages: [{ message_id: 10, role: "user", content: "Context", created_at: "" }],
      },
    })

    const mutateGuidance = vi.fn()
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: mutateGuidance,
    })

    const { rerender } = render(<ChatPage />)
    
    // Select 43
    mockUseChatConversations.mockReturnValue({
      ...baseConversationsState,
      data: {
        conversations: [{ conversation_id: 43, last_message_preview: "Context", status: "active", updated_at: "" }],
        total: 1, limit: 20, offset: 0
      }
    })
    rerender(<ChatPage />)
    fireEvent.click(screen.getByRole("button", { name: /#43 - Context/ }))

    fireEvent.click(screen.getByRole("button", { name: "Guidance du jour" }))
    expect(mutateGuidance).toHaveBeenCalledWith({
      period: "daily",
      conversation_id: 43,
    })
  })

  it("submits contextual guidance request and renders contextual response", async () => {
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })

    const mutateContextual = vi.fn()
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        guidance_id: "cg1",
        summary: "Décision sage.",
        key_points: ["p1"],
        actionable_advice: ["a1"],
        disclaimer: "Disclaimer",
      },
      mutate: mutateContextual,
    })

    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Situation"), { target: { value: "Situation complexe" } })
    fireEvent.change(screen.getByLabelText("Objectif"), { target: { value: "Voir clair" } })
    fireEvent.change(screen.getByLabelText("Horizon temporel (optionnel)"), { target: { value: "1 semaine" } })
    fireEvent.click(screen.getByRole("button", { name: "Demander une guidance contextuelle" }))

    expect(mutateContextual).toHaveBeenCalledWith({
      situation: "Situation complexe",
      objective: "Voir clair",
      time_horizon: "1 semaine",
    })

    const card = screen.getByText("Décision sage.").closest("article")
    expect(card).not.toBeNull()
    expect(within(card as HTMLElement).getByText("Guidance contextuelle")).toBeInTheDocument()
    expect(screen.getByText("Décision sage.")).toBeInTheDocument()
  })

  it("does not submit contextual guidance when situation/objective are blank", async () => {
    const mutateContextual = vi.fn()
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: mutateContextual,
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })

    render(<ChatPage />)

    fireEvent.click(screen.getByRole("button", { name: "Demander une guidance contextuelle" }))
    expect(mutateContextual).not.toHaveBeenCalled()
  })

  it("trims contextual guidance fields before submit", async () => {
    const mutateContextual = vi.fn()
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: mutateContextual,
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })

    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Situation"), { target: { value: "  Situation trimmed  " } })
    fireEvent.change(screen.getByLabelText("Objectif"), { target: { value: "  Objectif trimmed  " } })
    fireEvent.click(screen.getByRole("button", { name: "Demander une guidance contextuelle" }))

    expect(mutateContextual).toHaveBeenCalledWith({
      situation: "Situation trimmed",
      objective: "Objectif trimmed",
    })
  })

  it("shows recovery feedback when off-scope recovery is applied", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn().mockResolvedValue({
        conversation_id: 100,
        user_message: { message_id: 500, content: "Météo?" },
        assistant_message: { message_id: 501, content: "Hors sujet." },
        recovery: {
          off_scope_detected: true,
          recovery_applied: true,
          recovery_reason: "Pas d'astro ici.",
        },
      }),
    })

    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Votre message"), { target: { value: "Météo?" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(await screen.findByText("Désolé, je ne peux traiter que les sujets liés à l'astrologie.")).toBeInTheDocument()
    expect(screen.getByText("Raison: Pas d'astro ici.")).toBeInTheDocument()
  })

  it("renders quota blocked hint and explicit quota error details", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseBillingQuota.mockReturnValue({
      ...baseQuotaState,
      data: { ...baseQuotaState.data, blocked: true },
    })
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: true,
      error: {
        code: "quota_exceeded",
        message: "daily message quota exceeded",
        details: { reset_at: "2026-02-20T01:00:00Z" },
      },
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(screen.getByText("Votre quota quotidien est épuisé. Veuillez revenir demain ou changer de plan.")).toBeInTheDocument()
    expect(screen.getByText(/Quota épuisé\. Réessayez après le/)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled()
  })

  it("executes available module and does not execute locked module", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    const executeMutateAsync = vi.fn().mockResolvedValue({
      module: "tarot",
      status: "completed",
      interpretation: "Lecture tarot ok",
      conversation_id: null,
    })
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: executeMutateAsync,
    })

    render(<ChatPage />)

    const tarotCard = screen.getByText("Tarot").closest("article")
    expect(tarotCard).not.toBeNull()
    
    const runesCard = screen.getByText("Runes").closest("article")
    expect(within(runesCard as HTMLElement).getByRole("button")).toBeDisabled()

    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(within(tarotCard as HTMLElement).getByRole("button", { name: "Lancer Tarot" }))

    await waitFor(() => {
      expect(executeMutateAsync).toHaveBeenCalledTimes(1)
    })
    expect(executeMutateAsync).toHaveBeenCalledWith({
      module: "tarot",
      payload: {
        question: "Question tarot",
        situation: undefined,
        conversation_id: undefined,
      },
    })
    expect(screen.getByText("Lecture tarot ok")).toBeInTheDocument()
  })

  it("shows module in-progress state while execution is pending", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    const deferred = createDeferred<any>()
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: () => deferred.promise,
    })

    render(<ChatPage />)

    const tarotCard = screen.getByText("Tarot").closest("article")
    expect(tarotCard).not.toBeNull()

    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(within(tarotCard as HTMLElement).getByRole("button", { name: "Lancer Tarot" }))

    await waitFor(() => {
      expect(tarotCard as HTMLElement).toHaveTextContent(/État:\s*en cours/i)
    })
    expect(within(tarotCard as HTMLElement).getByText("Exécution en cours...")).toBeInTheDocument()

    deferred.resolve({
      module: "tarot",
      status: "completed",
      interpretation: "Lecture terminée",
      conversation_id: null,
    })

    await waitFor(() => {
      expect(screen.getByText("Lecture terminée")).toBeInTheDocument()
    })
  })

  it("shows module error state when execution fails", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: () => Promise.reject(new Error("module unavailable")),
    })

    render(<ChatPage />)

    const tarotCard = screen.getByText("Tarot").closest("article")
    expect(tarotCard).not.toBeNull()

    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(within(tarotCard as HTMLElement).getByRole("button", { name: "Lancer Tarot" }))

    await waitFor(() => {
      expect(tarotCard as HTMLElement).toHaveTextContent(/État:\s*erreur/i)
    })
    expect(within(tarotCard as HTMLElement).getByRole("alert")).toHaveTextContent(
      "Erreur Tarot: module unavailable",
    )
  })

  it("clears completed state immediately when module becomes locked", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    const mockUseModuleAvailabilityValue = vi.fn().mockReturnValue(baseModuleAvailability)
    mockUseModuleAvailability.mockImplementation(mockUseModuleAvailabilityValue)
    
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn().mockResolvedValue({
        module: "tarot",
        status: "completed",
        interpretation: "Lecture à retirer",
        conversation_id: null,
      }),
    })

    const { rerender } = render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(screen.getByRole("button", { name: "Lancer Tarot" }))
    expect(await screen.findByText(/Lecture à retirer/)).toBeInTheDocument()

    mockUseModuleAvailabilityValue.mockReturnValue({
      ...baseModuleAvailability,
      data: {
        ...baseModuleAvailability.data,
        modules: baseModuleAvailability.data.modules.map(m => 
          m.module === "tarot" ? { ...m, available: false, status: "module-locked", reason: "quota" } : m
        )
      }
    })

    rerender(<ChatPage />)

    expect(screen.queryByText(/Lecture à retirer/)).not.toBeInTheDocument()
    expect(screen.getByText("Module verrouillé (quota).")).toBeInTheDocument()
  })

  it("blocks concurrent module execution while a module request is pending", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseModuleAvailability.mockReturnValue({
      ...baseModuleAvailability,
      data: {
        ...baseModuleAvailability.data,
        modules: baseModuleAvailability.data.modules.map(m => ({ ...m, available: true, status: "module-ready" }))
      }
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: () => new Promise(() => {}), // never resolves
    })

    render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question" } })
    
    const tarotBtn = screen.getByRole("button", { name: "Lancer Tarot" })
    const runesBtn = screen.getByRole("button", { name: "Lancer Runes" })

    fireEvent.click(tarotBtn)
    
    await waitFor(() => {
      expect(runesBtn).toBeDisabled()
    })
  })
})
