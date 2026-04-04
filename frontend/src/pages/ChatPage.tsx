import { useMemo, useState, useCallback, useEffect, useRef } from "react"
import { useParams, useNavigate, useSearchParams, Link } from "react-router-dom"

import { useChatEntitlementUsage } from "../api/billing"
import { CHAT_PREFILL_KEY } from "../state/consultationStore"
import { useAstrologers } from "../api/astrologers"
import {
  ChatApiError,
  useChatConversationHistory,
  useChatConversations,
  useSendChatMessage,
  useCreateConversationByPersona,
} from "../api/chat"
import {
  ChatLayout,
  ChatPageHeader,
  ConversationList,
  ChatWindow,
  useIsMobile,
} from "../features/chat"
import type { MobileView } from "../features/chat"
import { AstrologerPickerModal } from "../features/chat/components/AstrologerPickerModal"
import { ChatEmptyState } from "../features/chat/components/ChatEmptyState"
import { ChatQuotaBanner } from "../features/chat/components/ChatQuotaBanner"
import { SectionErrorBoundary } from "../components/ErrorBoundary"
import { PageLayout } from "../layouts"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import "./ChatPage.css"

type ChatUiMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp?: string
}

function resolveAstrologerForConversation(
  astrologers: ReturnType<typeof useAstrologers>["data"],
  conversation:
    | {
        persona_id?: string
        persona_name?: string
      }
    | undefined,
) {
  if (!astrologers || !conversation) {
    return undefined
  }

  return astrologers.find((astrologer) => {
    if (conversation.persona_id && astrologer.id === conversation.persona_id) {
      return true
    }
    return astrologer.name === conversation.persona_name
  })
}

function getAstrologerFullName(
  astrologer:
    | {
        first_name?: string
        last_name?: string
        name?: string
      }
    | undefined,
) {
  if (!astrologer) {
    return undefined
  }

  return [astrologer.first_name, astrologer.last_name].filter(Boolean).join(" ") || astrologer.name
}

export function ChatPage() {
  const { conversationId: urlConversationId } = useParams<{
    conversationId: string
  }>()
  const [searchParams] = useSearchParams()
  // AC2: support ?personaId=xxx for get-or-create redirect
  const personaIdFromUrl = searchParams.get("personaId")
  // Deprecated: astrologerId kept for backwards compatibility
  const astrologerIdFromUrl = searchParams.get("astrologerId")
  const navigate = useNavigate()
  const isMobile = useIsMobile()
  const lang = detectLang()

  const quota = useChatEntitlementUsage()
  const sendMessage = useSendChatMessage()
  const conversations = useChatConversations(20, 0)
  const astrologers = useAstrologers()
  const createConversation = useCreateConversationByPersona()

  const [localMessages, setLocalMessages] = useState<ChatUiMessage[]>([])
  const [mobileView, setMobileView] = useState<MobileView>("list")
  const [prefillMessage, setPrefillMessage] = useState<string | null>(null)
  const [showAstrologerPicker, setShowAstrologerPicker] = useState(false)
  const [isRedirecting, setIsRedirecting] = useState(false)

  // Track the last personaId we attempted to redirect for to avoid infinite loops
  // but allow switching to a different personaId in the same session.
  const lastRedirectedPersonaId = useRef<string | null>(null)

  useEffect(() => {
    const prefill = sessionStorage.getItem(CHAT_PREFILL_KEY)
    if (prefill) {
      setPrefillMessage(prefill)
      sessionStorage.removeItem(CHAT_PREFILL_KEY)
    }
  }, [])

  // AC2: Redirect ?personaId=xxx → POST by-persona → /chat/:conversationId
  useEffect(() => {
    if (!personaIdFromUrl || lastRedirectedPersonaId.current === personaIdFromUrl)
      return

    lastRedirectedPersonaId.current = personaIdFromUrl
    setIsRedirecting(true)

    createConversation
      .mutateAsync(personaIdFromUrl)
      .then((result) => {
        navigate(`/chat/${result.conversation_id}`, { replace: true })
      })
      .catch((err) => {
        console.error("Failed to redirect by personaId:", err)
        // AC4: unknown personaId → redirect to /astrologers
        // We skip the toast since no toast library is available in this project
        navigate("/astrologers", { replace: true })
      })
      .finally(() => {
        setIsRedirecting(false)
      })
  }, [personaIdFromUrl, navigate, createConversation])

  const parsedId = urlConversationId ? parseInt(urlConversationId, 10) : null
  const selectedConversationId =
    parsedId !== null && !Number.isNaN(parsedId) ? parsedId : null

  // AC3: Auto-redirect to last active conversation when navigating to /chat without ID
  // Disabled on mobile: the list view is the entry point there.
  useEffect(() => {
    if (
      !isMobile &&
      !urlConversationId &&
      !personaIdFromUrl &&
      !conversations.isPending &&
      conversations.data &&
      conversations.data.conversations.length > 0
    ) {
      navigate(
        `/chat/${conversations.data.conversations[0].conversation_id}`,
        { replace: true }
      )
    }
  }, [
    isMobile,
    urlConversationId,
    personaIdFromUrl,
    conversations.isPending,
    conversations.data,
    navigate,
  ])

  const conversationExistsInList =
    selectedConversationId !== null &&
    conversations.data?.conversations.some(
      (c) => c.conversation_id === selectedConversationId
    ) === true
  const history = useChatConversationHistory(
    conversationExistsInList ? selectedConversationId : null
  )
  const quotaBlocked = quota.data?.blocked === true

  useEffect(() => {
    if (urlConversationId && isMobile) {
      setMobileView("chat")
    }
  }, [urlConversationId, isMobile])

  const displayedMessages = useMemo(() => {
    const historyMsgs: ChatUiMessage[] =
      history.data?.messages.map((message) => ({
        id: `${message.role}-${message.message_id}`,
        role: message.role as "user" | "assistant",
        content: message.content,
        timestamp: message.created_at,
      })) ?? []

    const localOnly = localMessages.filter(
      (m) => !historyMsgs.some((hm) => hm.id === m.id)
    )

    return [...historyMsgs, ...localOnly]
  }, [history.data, localMessages])

  const handleSelectConversation = useCallback(
    (id: number) => {
      navigate(`/chat/${id}`)
      setLocalMessages([])
      if (isMobile) {
        setMobileView("chat")
      }
    },
    [navigate, isMobile]
  )

  const handlePickAstrologer = useCallback(
    async (astrologerId: string) => {
      try {
        const result = await createConversation.mutateAsync(astrologerId)
        setShowAstrologerPicker(false)
        void conversations.refetch()
        navigate(`/chat/${result.conversation_id}`)
        if (isMobile) setMobileView("chat")
      } catch {
        // silently fail — l'API est idempotente, l'état loading se ré-active naturellement
      }
    },
    [createConversation, conversations, navigate, isMobile]
  )

  const [lastClientMessageId, setLastClientMessageId] = useState<{content: string, id: string} | null>(null)

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || sendMessage.isPending || quotaBlocked) {
        return
      }

      // AC1: Generate or reuse idempotency key for retries of the same content.
      // If the user sends the EXACT SAME content immediately after a failure,
      // we reuse the previous UUID to hit the backend idempotence cache.
      let clientMessageId: string
      if (lastClientMessageId && lastClientMessageId.content === content) {
        clientMessageId = lastClientMessageId.id
      } else {
        clientMessageId = crypto.randomUUID()
        setLastClientMessageId({ content, id: clientMessageId })
      }

      const optimisticUserMsg: ChatUiMessage = {
        id: `optimistic-${clientMessageId}`,
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      }
      setLocalMessages((prev) => [...prev, optimisticUserMsg])

      try {
        const response = await sendMessage.mutateAsync({
          message: content,
          client_message_id: clientMessageId,
          ...(selectedConversationId
            ? { conversation_id: selectedConversationId }
            : {}),
          ...(astrologerIdFromUrl ? { persona_id: astrologerIdFromUrl } : {}),
        })

        if (!selectedConversationId) {
          navigate(`/chat/${response.conversation_id}`, { replace: true })
        }

        setLastClientMessageId(null)

        setLocalMessages((current) => {
          const filtered = current.filter(
            (m) => m.id !== optimisticUserMsg.id
          )
          return [
            ...filtered,
            {
              id: `user-${response.user_message.message_id}`,
              role: "user" as const,
              content: response.user_message.content,
              timestamp: response.user_message.created_at,
            },
            {
              id: `assistant-${response.assistant_message.message_id}`,
              role: "assistant" as const,
              content: response.assistant_message.content,
              timestamp: response.assistant_message.created_at,
            },
          ]
        })

        void conversations.refetch()
        void quota.refetch()
        if (selectedConversationId) {
          void history.refetch()
        }
      } catch {
        setLocalMessages((current) =>
          current.filter((m) => m.id !== optimisticUserMsg.id)
        )
      }
    },
    [
      sendMessage,
      selectedConversationId,
      quotaBlocked,
      navigate,
      conversations,
      quota,
      history,
      astrologerIdFromUrl,
      lastClientMessageId,
    ]
  )

  const handleBackToList = useCallback(() => {
    setMobileView("list")
    navigate("/chat")
  }, [navigate])

  const conversationError =
    (history.error as ChatApiError | null) ||
    (sendMessage.error as ChatApiError | null)

  const hasConversations =
    conversations.data && conversations.data.conversations.length > 0
  const hasSelectedConversation = selectedConversationId !== null

  const selectedConversationExists =
    selectedConversationId === null ||
    conversations.data?.conversations.some(
      (c) => c.conversation_id === selectedConversationId
    )

  // AC4: Detect 404 from history API (conversation deleted or truly invalid)
  const isHistoryNotFound =
    history.error instanceof ChatApiError && history.error.status === 404

  const isInvalidConversationUrl =
    (hasSelectedConversation &&
      !conversations.isPending &&
      conversations.data &&
      !selectedConversationExists) ||
    isHistoryNotFound

  // AC5: Persona details for empty conversation welcome state
  const selectedConversationSummary =
    selectedConversationId !== null
      ? conversations.data?.conversations.find(
          (c) => c.conversation_id === selectedConversationId
        )
      : undefined

  const resolvedConversations = useMemo(() => {
    const items = conversations.data?.conversations ?? []

    return items.map((conversation) => {
      const astrologer = resolveAstrologerForConversation(astrologers.data, conversation)
      const fullName = getAstrologerFullName(astrologer)
      return {
        ...conversation,
        persona_name: fullName ?? conversation.persona_name,
        avatar_url: astrologer?.avatar_url ?? conversation.avatar_url,
      }
    })
  }, [conversations.data?.conversations, astrologers.data])

  const resolvedSelectedConversationSummary =
    selectedConversationId !== null
      ? resolvedConversations.find((c) => c.conversation_id === selectedConversationId)
      : undefined

  const currentAstrologer = resolveAstrologerForConversation(
    astrologers.data,
    resolvedSelectedConversationSummary ?? selectedConversationSummary
  )

  return (
    <PageLayout className="chat-page-container is-chat-page">
      {isRedirecting && (
        <div className="chat-window-loading-overlay">
          <div className="spinner" />
        </div>
      )}

      {/* Decorative Halos and Noise (Story 60.19) */}
      <div className="chat-page-container__bg-halo" />
      <div className="chat-page-container__noise" />

      {!(isMobile && mobileView === "chat") && (
        <ChatPageHeader
          title={t("chat_page_title", lang)}
          showBackButton={!isMobile}
        />
      )}

      <ChatQuotaBanner />

      <SectionErrorBoundary onRetry={() => conversations.refetch()}>
        <ChatLayout
          mobileView={mobileView}
          onMobileViewChange={setMobileView}
          hasConversation={hasSelectedConversation}
          isMobile={isMobile}
          leftPanel={
            <ConversationList
              conversations={resolvedConversations}
              selectedId={selectedConversationId}
              onSelect={handleSelectConversation}
              onNewConversation={() => setShowAstrologerPicker(true)}
              isLoading={conversations.isPending}
              error={conversations.error as Error | null}
            />
          }
          centerPanel={
            !hasConversations && !conversations.isPending ? (
              <ChatEmptyState onStartConversation={() => setShowAstrologerPicker(true)} />
            ) : isInvalidConversationUrl ? (
              <div className="chat-empty-state">
                <span className="chat-empty-state-icon" role="img" aria-label={t("aria_search", lang)}>🔍</span>
                <h2 className="chat-empty-state-title">{t("chat_not_found", lang)}</h2>
                <p className="chat-empty-state-description">
                  {t("chat_not_found_description", lang).replace("{id}", String(selectedConversationId))}
                </p>
                <Link to="/chat" className="chat-empty-state-cta btn">
                  {t("back_to_conversations", lang)}
                </Link>
              </div>
            ) : (
              <ChatWindow
                messages={displayedMessages}
                onSendMessage={handleSendMessage}
                isTyping={sendMessage.isPending}
                isSending={sendMessage.isPending}
                error={conversationError}
                quotaBlocked={quotaBlocked}
                initialMessage={prefillMessage}
                onInitialMessageConsumed={() => setPrefillMessage(null)}
                personaName={
                  getAstrologerFullName(currentAstrologer) ??
                  resolvedSelectedConversationSummary?.persona_name
                }
                personaAvatarUrl={
                  currentAstrologer?.avatar_url ??
                  resolvedSelectedConversationSummary?.avatar_url
                }
                personaBio={currentAstrologer?.bio_short}
                personaSpecialties={currentAstrologer?.specialties}
                onBack={isMobile && mobileView === "chat" ? handleBackToList : undefined}
              />
            )
          }
        />
      </SectionErrorBoundary>
      {showAstrologerPicker && (
        <AstrologerPickerModal
          astrologers={astrologers.data ?? []}
          isLoading={astrologers.isPending}
          isCreating={createConversation.isPending}
          onSelect={handlePickAstrologer}
          onClose={() => setShowAstrologerPicker(false)}
        />
      )}
    </PageLayout>
  )
}

