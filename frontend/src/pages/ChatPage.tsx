import { useMemo, useState, useCallback, useEffect } from "react"
import { useParams, useNavigate, useSearchParams, Link } from "react-router-dom"

import { useBillingQuota } from "../api/billing"
import { CHAT_PREFILL_KEY } from "../state/consultationStore"
import { useAstrologer } from "../api/astrologers"
import {
  ChatApiError,
  useChatConversationHistory,
  useChatConversations,
  useSendChatMessage,
} from "../api/chat"
import {
  ChatLayout,
  ConversationList,
  ChatWindow,
  AstrologerDetailPanel,
  useIsMobile,
} from "../features/chat"
import type { MobileView } from "../features/chat"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/astrologers"

type ChatUiMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp?: string
}

export function ChatPage() {
  const { conversationId: urlConversationId } = useParams<{
    conversationId: string
  }>()
  const [searchParams] = useSearchParams()
  const astrologerIdFromUrl = searchParams.get("astrologerId")
  const navigate = useNavigate()
  const isMobile = useIsMobile()
  const lang = detectLang()

  const quota = useBillingQuota()
  const sendMessage = useSendChatMessage()
  const conversations = useChatConversations(20, 0)
  const selectedAstrologer = useAstrologer(astrologerIdFromUrl || undefined)

  const [localMessages, setLocalMessages] = useState<ChatUiMessage[]>([])
  const [mobileView, setMobileView] = useState<MobileView>("list")
  const [prefillMessage, setPrefillMessage] = useState<string | null>(null)

  useEffect(() => {
    const prefill = sessionStorage.getItem(CHAT_PREFILL_KEY)
    if (prefill) {
      setPrefillMessage(prefill)
      sessionStorage.removeItem(CHAT_PREFILL_KEY)
    }
  }, [])

  const parsedId = urlConversationId ? parseInt(urlConversationId, 10) : null
  const selectedConversationId =
    parsedId !== null && !Number.isNaN(parsedId) ? parsedId : null

  const history = useChatConversationHistory(selectedConversationId)
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

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || sendMessage.isPending || quotaBlocked) {
        return
      }

      const optimisticUserMsg: ChatUiMessage = {
        id: `optimistic-user-${Date.now()}`,
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      }
      setLocalMessages((prev) => [...prev, optimisticUserMsg])

      try {
        const response = await sendMessage.mutateAsync({
          message: content,
          ...(selectedConversationId
            ? { conversation_id: selectedConversationId }
            : {}),
        })

        if (!selectedConversationId) {
          navigate(`/chat/${response.conversation_id}`, { replace: true })
        }

        setLocalMessages((current) => {
          const filtered = current.filter(
            (m) => m.id !== optimisticUserMsg.id
          )
          return [
            ...filtered,
            {
              id: `u-${response.user_message.message_id}`,
              role: "user" as const,
              content: response.user_message.content,
              timestamp: response.user_message.created_at,
            },
            {
              id: `a-${response.assistant_message.message_id}`,
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

  const isInvalidConversationUrl =
    hasSelectedConversation &&
    !conversations.isPending &&
    conversations.data &&
    !selectedConversationExists

  if (!hasConversations && !conversations.isPending) {
    const astrologerName = selectedAstrologer.data?.name
    const description = astrologerName
      ? t("chat_no_conversation_with_astrologer", lang).replace("{name}", astrologerName)
      : t("chat_no_conversation_description", lang)

    return (
      <div className="chat-empty-state">
        <span className="chat-empty-state-icon" role="img" aria-label={t("aria_chat_bubble", lang)}>💬</span>
        <h2 className="chat-empty-state-title">{t("chat_no_conversation", lang)}</h2>
        <p className="chat-empty-state-description">{description}</p>
        <Link to="/astrologers" className="chat-empty-state-cta btn">
          {t("choose_astrologer", lang)}
        </Link>
      </div>
    )
  }

  if (isInvalidConversationUrl) {
    return (
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
    )
  }

  return (
    <ChatLayout
      mobileView={mobileView}
      onMobileViewChange={setMobileView}
      hasConversation={hasSelectedConversation}
      isMobile={isMobile}
      leftPanel={
        <ConversationList
          conversations={conversations.data?.conversations ?? []}
          selectedId={selectedConversationId}
          onSelect={handleSelectConversation}
          isLoading={conversations.isPending}
          error={conversations.error as Error | null}
        />
      }
      centerPanel={
        <ChatWindow
          messages={displayedMessages}
          onSendMessage={handleSendMessage}
          isTyping={sendMessage.isPending}
          isSending={sendMessage.isPending}
          error={conversationError}
          quotaBlocked={quotaBlocked}
          showBackButton={isMobile}
          onBack={handleBackToList}
          initialMessage={prefillMessage}
          onInitialMessageConsumed={() => setPrefillMessage(null)}
        />
      }
      rightPanel={
        <AstrologerDetailPanel
          conversationId={selectedConversationId}
          selectedAstrologer={selectedAstrologer.data}
        />
      }
    />
  )
}
