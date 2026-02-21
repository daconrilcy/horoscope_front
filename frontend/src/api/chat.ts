import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

type SendChatResponse = {
  conversation_id: number
  attempts: number
  user_message: {
    message_id: number
    role: string
    content: string
    created_at: string
  }
  assistant_message: {
    message_id: number
    role: string
    content: string
    created_at: string
  }
  fallback_used: boolean
  recovery: {
    off_scope_detected: boolean
    off_scope_score: number
    recovery_strategy: "none" | "reformulate" | "retry_once" | "safe_fallback"
    recovery_applied: boolean
    recovery_attempts: number
    recovery_reason: string | null
  }
  context: {
    message_ids: number[]
    message_count: number
    context_characters: number
    prompt_version: string
  }
}

type SendChatPayload = {
  message: string
  conversation_id?: number
}

type ChatConversationSummary = {
  conversation_id: number
  status: string
  updated_at: string
  last_message_preview: string
}

type ChatConversationListResponse = {
  conversations: ChatConversationSummary[]
  total: number
  limit: number
  offset: number
}

type ChatConversationHistoryResponse = {
  conversation_id: number
  status: string
  updated_at: string
  messages: {
    message_id: number
    role: string
    content: string
    created_at: string
  }[]
}

export class ChatApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>

  constructor(code: string, message: string, status: number, details: Record<string, unknown> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

function toTransportError(error: unknown): ChatApiError {
  if (error instanceof ChatApiError) {
    return error
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return new ChatApiError(
      "request_timeout",
      "La requete a expire. Reessayez dans un instant.",
      408,
      {},
    )
  }
  return new ChatApiError("network_error", "Erreur reseau. Reessayez plus tard.", 0, {})
}

async function sendChatMessage(requestPayload: SendChatPayload): Promise<SendChatResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/chat/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAccessTokenAuthHeader(),
      },
      body: JSON.stringify(requestPayload),
    })

    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new ChatApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: SendChatResponse }
    return payload.data
  } catch (error) {
    throw toTransportError(error)
  }
}

async function getChatConversations(limit = 20, offset = 0): Promise<ChatConversationListResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/chat/conversations?limit=${limit}&offset=${offset}`, {
      method: "GET",
      headers: {
        ...getAccessTokenAuthHeader(),
      },
    })

    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new ChatApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: ChatConversationListResponse }
    return payload.data
  } catch (error) {
    throw toTransportError(error)
  }
}

async function getChatConversationHistory(conversationId: number): Promise<ChatConversationHistoryResponse> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/chat/conversations/${conversationId}`, {
      method: "GET",
      headers: {
        ...getAccessTokenAuthHeader(),
      },
    })

    if (!response.ok) {
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new ChatApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: ChatConversationHistoryResponse }
    return payload.data
  } catch (error) {
    throw toTransportError(error)
  }
}

export function useSendChatMessage() {
  return useMutation({
    mutationFn: sendChatMessage,
  })
}

export function useChatConversations(limit = 20, offset = 0) {
  return useQuery({
    queryKey: ["chat-conversations", limit, offset],
    queryFn: () => getChatConversations(limit, offset),
  })
}

export function useChatConversationHistory(conversationId: number | null) {
  return useQuery({
    queryKey: ["chat-conversation", conversationId],
    queryFn: () => getChatConversationHistory(conversationId as number),
    enabled: conversationId !== null,
  })
}

export type {
  ChatConversationHistoryResponse,
  ChatConversationListResponse,
  ChatConversationSummary,
  SendChatPayload,
  SendChatResponse,
}
