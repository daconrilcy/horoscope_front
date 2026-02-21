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
  useChatConversations: () => mockUseChatConversations(),
  useChatConversationHistory: () => mockUseChatConversationHistory(),
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
    expect(screen.getByText("Aucun message pour le moment. Posez votre premiere question.")).toBeInTheDocument()
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
    expect(screen.getByText("Generation de la reponse en cours...")).toBeInTheDocument()
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
        details: { fallback_message: "Le service est indisponible temporairement. Reessayez dans un instant." },
      },
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(screen.getByText("Une erreur est survenue: llm provider timeout")).toBeInTheDocument()
    expect(
      screen.getByText("Le service est indisponible temporairement. Reessayez dans un instant."),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Reessayer" })).toBeInTheDocument()
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
        message: "La requete a expire. Reessayez dans un instant.",
        details: {},
      },
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(
      screen.getByText("Une erreur est survenue: La requete a expire. Reessayez dans un instant."),
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
    const mutateAsync = vi
      .fn()
      .mockResolvedValueOnce({
        conversation_id: 42,
        user_message: { message_id: 1, content: "Bonjour" },
        assistant_message: { message_id: 2, content: "Salut" },
      })
      .mockResolvedValueOnce({
        conversation_id: 42,
        user_message: { message_id: 3, content: "Suite" },
        assistant_message: { message_id: 4, content: "Reponse suite" },
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

    fireEvent.change(screen.getByLabelText("Votre message"), { target: { value: "Suite" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(await screen.findByText("Conversation active: #42")).toBeInTheDocument()
    expect(screen.getByText("Bonjour")).toBeInTheDocument()
    expect(screen.getByText("Salut")).toBeInTheDocument()
    expect(screen.getByText("Suite")).toBeInTheDocument()
    expect(screen.getByText("Reponse suite")).toBeInTheDocument()
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
          { conversation_id: 10, last_message_preview: "Apercu", status: "active", updated_at: "" },
        ],
        total: 1,
        limit: 20,
        offset: 0,
      },
    })
    mockUseChatConversationHistory.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        conversation_id: 10,
        status: "active",
        updated_at: "",
        messages: [
          { message_id: 1, role: "user", content: "Message historique", created_at: "" },
          { message_id: 2, role: "assistant", content: "Reponse historique", created_at: "" },
        ],
      },
    })
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    fireEvent.click(screen.getByRole("button", { name: "#10 - Apercu" }))

    expect(await screen.findByText("Conversation active: #10")).toBeInTheDocument()
    expect(screen.getByText("Message historique")).toBeInTheDocument()
    expect(screen.getByText("Reponse historique")).toBeInTheDocument()
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
    mockUseChatConversations.mockReturnValue({
      ...baseConversationsState,
      data: {
        conversations: [
          { conversation_id: 10, last_message_preview: "Apercu", status: "active", updated_at: "" },
        ],
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
      conversation_id: 10,
      user_message: { message_id: 1, content: "Suite" },
      assistant_message: { message_id: 2, content: "Reponse" },
    })
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync,
    })

    render(<ChatPage />)
    fireEvent.click(screen.getByRole("button", { name: "#10 - Apercu" }))
    fireEvent.change(screen.getByLabelText("Votre message"), { target: { value: "Suite" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(mutateAsync).toHaveBeenCalledWith({ message: "Suite", conversation_id: 10 })
  })

  it("requests daily and weekly guidance and renders response", async () => {
    const mutate = vi.fn()
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        period: "daily",
        summary: "Resume guidance",
        key_points: ["Point 1"],
        actionable_advice: ["Conseil 1"],
        disclaimer: "Disclaimer",
      },
      mutate,
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
    fireEvent.click(screen.getByRole("button", { name: "Guidance du jour" }))
    fireEvent.click(screen.getByRole("button", { name: "Guidance de la semaine" }))

    expect(mutate).toHaveBeenCalledWith({ period: "daily" })
    expect(mutate).toHaveBeenCalledWith({ period: "weekly" })
    expect(screen.getByText("Resume guidance")).toBeInTheDocument()
    expect(screen.getByText("Point 1")).toBeInTheDocument()
    expect(screen.getByText("Conseil 1")).toBeInTheDocument()
    expect(screen.getByText("Disclaimer")).toBeInTheDocument()
  })

  it("requests guidance on selected conversation context", async () => {
    const mutate = vi.fn()
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate,
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
          { conversation_id: 10, last_message_preview: "Apercu", status: "active", updated_at: "" },
        ],
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
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    fireEvent.click(screen.getByRole("button", { name: "#10 - Apercu" }))
    fireEvent.click(screen.getByRole("button", { name: "Guidance du jour" }))

    expect(mutate).toHaveBeenCalledWith({ period: "daily", conversation_id: 10 })
  })

  it("submits contextual guidance request and renders contextual response", async () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    const contextualMutate = vi.fn()
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        guidance_type: "contextual",
        situation: "Situation test",
        objective: "Objectif test",
        time_horizon: "48h",
        summary: "Resume contextualise",
        key_points: ["Point contextuel"],
        actionable_advice: ["Action contextuelle"],
        disclaimer: "Disclaimer contextuel",
      },
      mutate: contextualMutate,
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
    fireEvent.change(screen.getByLabelText("Situation"), { target: { value: "Situation test" } })
    fireEvent.change(screen.getByLabelText("Objectif"), { target: { value: "Objectif test" } })
    fireEvent.change(screen.getByLabelText("Horizon temporel (optionnel)"), { target: { value: "48h" } })
    fireEvent.click(screen.getByRole("button", { name: "Demander une guidance contextuelle" }))

    expect(contextualMutate).toHaveBeenCalledWith({
      situation: "Situation test",
      objective: "Objectif test",
      time_horizon: "48h",
    })
    expect(await screen.findByText("Resume contextualise")).toBeInTheDocument()
    expect(screen.getByText("Point contextuel")).toBeInTheDocument()
    expect(screen.getByText("Action contextuelle")).toBeInTheDocument()
    expect(screen.getByText("Disclaimer contextuel")).toBeInTheDocument()
  })

  it("does not submit contextual guidance when situation/objective are blank", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    const contextualMutate = vi.fn()
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: contextualMutate,
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
    fireEvent.change(screen.getByLabelText("Situation"), { target: { value: "   " } })
    fireEvent.change(screen.getByLabelText("Objectif"), { target: { value: "   " } })
    fireEvent.click(screen.getByRole("button", { name: "Demander une guidance contextuelle" }))

    expect(contextualMutate).not.toHaveBeenCalled()
  })

  it("trims contextual guidance fields before submit", () => {
    mockUseRequestGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: vi.fn(),
    })
    const contextualMutate = vi.fn()
    mockUseRequestContextualGuidance.mockReturnValue({
      isPending: false,
      error: null,
      data: null,
      mutate: contextualMutate,
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
    fireEvent.change(screen.getByLabelText("Situation"), { target: { value: "  Situation test  " } })
    fireEvent.change(screen.getByLabelText("Objectif"), { target: { value: "  Objectif test  " } })
    fireEvent.change(screen.getByLabelText("Horizon temporel (optionnel)"), {
      target: { value: "  48h  " },
    })
    fireEvent.click(screen.getByRole("button", { name: "Demander une guidance contextuelle" }))

    expect(contextualMutate).toHaveBeenCalledWith({
      situation: "Situation test",
      objective: "Objectif test",
      time_horizon: "48h",
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
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    const mutateAsync = vi.fn().mockResolvedValue({
      conversation_id: 42,
      user_message: { message_id: 1, content: "Bonjour" },
      assistant_message: { message_id: 2, content: "Reponse reformulee" },
      recovery: {
        off_scope_detected: true,
        off_scope_score: 0.95,
        recovery_strategy: "safe_fallback",
        recovery_applied: true,
        recovery_attempts: 2,
        recovery_reason: "explicit_marker",
      },
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

    expect(
      await screen.findByText(
        "Recuperation automatique appliquee (safe_fallback) pour recentrer la reponse.",
      ),
    ).toBeInTheDocument()
    expect(screen.getByText("Essayez de reformuler votre question avec un contexte plus precis.")).toBeInTheDocument()
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
      data: { ...baseQuotaState.data, consumed: 5, remaining: 0, blocked: true },
    })
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: true,
      error: {
        code: "quota_exceeded",
        message: "daily message quota exceeded",
        details: {
          consumed: "5",
          limit: "5",
          reset_at: "2026-02-20T00:00:00+00:00",
        },
      },
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    expect(screen.getByText("Quota journalier atteint. Vous pourrez reprendre apres le reset.")).toBeInTheDocument()
    expect(screen.getByText(/Quota atteint \(5\/5\)/)).toBeInTheDocument()
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
    const moduleRefetch = vi.fn()
    mockUseModuleAvailability.mockReturnValue({ ...baseModuleAvailability, refetch: moduleRefetch })
    const executeMutateAsync = vi.fn().mockResolvedValue({
      module: "tarot",
      status: "completed",
      interpretation: "Lecture test",
      persona_profile_code: "legacy-default",
      conversation_id: null,
    })
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: executeMutateAsync,
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(screen.getByRole("button", { name: "Lancer Tarot" }))
    fireEvent.click(screen.getByRole("button", { name: "Lancer Runes" }))

    await waitFor(() => {
      expect(executeMutateAsync).toHaveBeenCalledTimes(1)
    })
    expect(executeMutateAsync).toHaveBeenCalledWith({
      module: "tarot",
      payload: { question: "Question tarot" },
    })
    expect(moduleRefetch).toHaveBeenCalled()
    expect(screen.getByText("Lecture test")).toBeInTheDocument()
    const tarotCard = screen.getByRole("heading", { name: "Tarot" }).closest("article")
    expect(tarotCard).not.toBeNull()
    expect(tarotCard as HTMLElement).toHaveTextContent(/Etat:\s*completed/i)
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
    const deferred = createDeferred<{
      module: "tarot"
      status: "completed"
      interpretation: string
      persona_profile_code: string
      conversation_id: number | null
    }>()
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn().mockReturnValue(deferred.promise),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(screen.getByRole("button", { name: "Lancer Tarot" }))

    const tarotCard = screen.getByRole("heading", { name: "Tarot" }).closest("article")
    expect(tarotCard).not.toBeNull()
    await waitFor(() => {
      expect(tarotCard as HTMLElement).toHaveTextContent(/Etat:\s*in-progress/i)
    })
    expect(within(tarotCard as HTMLElement).getByText("Execution en cours...")).toBeInTheDocument()

    deferred.resolve({
      module: "tarot",
      status: "completed",
      interpretation: "Lecture differee",
      persona_profile_code: "legacy-default",
      conversation_id: null,
    })

    await waitFor(() => {
      expect(tarotCard as HTMLElement).toHaveTextContent(/Etat:\s*completed/i)
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
    mockUseModuleAvailability.mockReturnValue(baseModuleAvailability)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn().mockRejectedValue(new Error("module unavailable")),
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(screen.getByRole("button", { name: "Lancer Tarot" }))

    const tarotCard = screen.getByRole("heading", { name: "Tarot" }).closest("article")
    expect(tarotCard).not.toBeNull()
    await waitFor(() => {
      expect(tarotCard as HTMLElement).toHaveTextContent(/Etat:\s*error/i)
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
    const executeMutateAsync = vi.fn().mockResolvedValue({
      module: "tarot",
      status: "completed",
      interpretation: "Lecture a retirer",
      persona_profile_code: "legacy-default",
      conversation_id: null,
    })
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: executeMutateAsync,
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    const { rerender } = render(<ChatPage />)

    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question tarot" } })
    fireEvent.click(screen.getByRole("button", { name: "Lancer Tarot" }))
    expect(await screen.findByText("Lecture a retirer")).toBeInTheDocument()

    mockUseModuleAvailability.mockReturnValue({
      ...baseModuleAvailability,
      data: {
        modules: [
          {
            module: "tarot",
            flag_key: "tarot_enabled",
            status: "module-locked",
            available: false,
            reason: "feature_disabled",
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
        available_count: 0,
      },
    })
    rerender(<ChatPage />)

    const tarotCard = screen.getByRole("heading", { name: "Tarot" }).closest("article")
    expect(tarotCard).not.toBeNull()
    await waitFor(() => {
      expect(tarotCard as HTMLElement).toHaveTextContent(/Etat:\s*module-locked/i)
    })
    expect(tarotCard as HTMLElement).not.toHaveTextContent("Lecture a retirer")
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
    const deferred = createDeferred<{
      module: "tarot"
      status: "completed"
      interpretation: string
      persona_profile_code: string
      conversation_id: number | null
    }>()
    mockUseModuleAvailability.mockReturnValue({
      ...baseModuleAvailability,
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
            status: "module-ready",
            available: true,
            reason: "segment_match",
          },
        ],
        total: 2,
        available_count: 2,
      },
    })
    const executeMutateAsync = vi.fn().mockReturnValue(deferred.promise)
    mockUseExecuteModule.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: executeMutateAsync,
    })
    mockUseChatConversations.mockReturnValue(baseConversationsState)
    mockUseChatConversationHistory.mockReturnValue(baseHistoryState)
    mockUseBillingQuota.mockReturnValue(baseQuotaState)
    mockUseSendChatMessage.mockReturnValue({
      isPending: false,
      isError: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<ChatPage />)
    fireEvent.change(screen.getByLabelText("Question module"), { target: { value: "Question multi-module" } })
    fireEvent.click(screen.getByRole("button", { name: "Lancer Tarot" }))

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Lancer Runes" })).toBeDisabled()
    })

    fireEvent.click(screen.getByRole("button", { name: "Lancer Runes" }))
    expect(executeMutateAsync).toHaveBeenCalledTimes(1)

    deferred.resolve({
      module: "tarot",
      status: "completed",
      interpretation: "Lecture finale",
      persona_profile_code: "legacy-default",
      conversation_id: null,
    })
  })
})
