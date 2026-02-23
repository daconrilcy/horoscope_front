import { useRef, useEffect } from "react"
import { MessageBubble } from "./MessageBubble"
import { TypingIndicator } from "./TypingIndicator"
import { ChatComposer } from "./ChatComposer"
import { useAutoScroll } from "../hooks/useAutoScroll"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

type ChatMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp?: string
}

type ChatWindowProps = {
  messages: ChatMessage[]
  onSendMessage: (message: string) => void
  isTyping?: boolean
  isSending?: boolean
  error?: Error | null
  quotaBlocked?: boolean
  onRetry?: () => void
  onBack?: () => void
  showBackButton?: boolean
  initialMessage?: string | null
  onInitialMessageConsumed?: () => void
}

export function ChatWindow({
  messages,
  onSendMessage,
  isTyping = false,
  isSending = false,
  error = null,
  quotaBlocked = false,
  onRetry,
  onBack,
  showBackButton = false,
  initialMessage = null,
  onInitialMessageConsumed,
}: ChatWindowProps) {
  const lang = detectLang()
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const scrollTrigger = `${messages.length}-${isTyping}`
  const { handleScroll, resetScroll } = useAutoScroll(
    messagesContainerRef,
    scrollTrigger
  )

  useEffect(() => {
    if (!isSending) {
      resetScroll()
    }
  }, [isSending, resetScroll])

  const isEmpty = messages.length === 0

  return (
    <div className="chat-window">
      {showBackButton && onBack && (
        <div className="chat-window-header">
          <button
            type="button"
            className="chat-window-back"
            onClick={onBack}
            aria-label={t("chat_back_to_list", lang)}
          >
            ← {t("chat_back", lang)}
          </button>
        </div>
      )}

      <div
        ref={messagesContainerRef}
        className="chat-window-messages"
        onScroll={handleScroll}
        aria-live="polite"
      >
        {isEmpty && !isTyping && (
          <div className="chat-window-empty">
            <p>{t("chat_empty_title", lang)}</p>
            <p>{t("chat_empty_subtitle", lang)}</p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))}

        {isTyping && <TypingIndicator />}
      </div>

      {error && (
        <div className="chat-window-error" role="alert">
          <p>{t("chat_error_prefix", lang)}: {error.message}</p>
          {onRetry && (
            <button type="button" onClick={onRetry}>
              {t("chat_retry", lang)}
            </button>
          )}
        </div>
      )}

      {quotaBlocked && (
        <div className="chat-window-quota" role="alert">
          <p>{t("chat_quota_exhausted", lang)}</p>
        </div>
      )}

      <ChatComposer
        onSend={onSendMessage}
        disabled={isSending || quotaBlocked}
        initialValue={initialMessage ?? undefined}
        onInitialValueConsumed={onInitialMessageConsumed}
        placeholder={t("chat_placeholder", lang)}
        sendLabel={t("chat_send", lang)}
        inputAriaLabel={t("chat_input_aria", lang)}
      />
    </div>
  )
}
