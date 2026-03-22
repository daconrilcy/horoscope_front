import { useRef, useEffect } from "react"
import { MessageBubble } from "./MessageBubble"
import { TypingIndicator } from "./TypingIndicator"
import { ChatComposer } from "./ChatComposer"
import { useAutoScroll } from "../hooks/useAutoScroll"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import "./ChatWindow.css"

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
  initialMessage?: string | null
  onInitialMessageConsumed?: () => void
  personaName?: string
  personaAvatarUrl?: string
  personaBio?: string
  personaSpecialties?: string[]
}

export function ChatWindow({
  messages,
  onSendMessage,
  isTyping = false,
  isSending = false,
  error = null,
  quotaBlocked = false,
  onRetry,
  initialMessage = null,
  onInitialMessageConsumed,
  personaName,
  personaAvatarUrl,
  personaBio,
  personaSpecialties,
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
      <div className="chat-window-header">
        {personaName && (
          <div className="astrologer-chip">
            {personaAvatarUrl ? (
              <img
                src={personaAvatarUrl}
                alt={personaName}
                className="astrologer-chip-avatar"
              />
            ) : (
              <span className="astrologer-chip-fallback" aria-hidden="true">✨</span>
            )}
            <span className="astrologer-chip-name">{personaName}</span>
            {(personaBio || (personaSpecialties && personaSpecialties.length > 0)) && (
              <div className="astrologer-chip-card" role="tooltip">
                {personaBio && (
                  <p className="astrologer-chip-card-bio">{personaBio}</p>
                )}
                {personaSpecialties && personaSpecialties.length > 0 && (
                  <ul className="astrologer-chip-card-specialties">
                    {personaSpecialties.map((s) => (
                      <li key={s}>{s}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div
        ref={messagesContainerRef}
        className="chat-window-messages"
        onScroll={handleScroll}
        aria-live="polite"
      >
        {isEmpty && !isTyping && (
          <MessageBubble
            role="assistant"
            content={t("chat_opening_message", lang)}
          />
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


