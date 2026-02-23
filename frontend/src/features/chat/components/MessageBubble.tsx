import { detectLang } from "../../../i18n/astrology"
import type { AstrologyLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

const LOCALE_MAP: Record<AstrologyLang, string> = {
  fr: "fr-FR",
  en: "en-US",
  es: "es-ES",
}

type MessageBubbleProps = {
  role: "user" | "assistant"
  content: string
  timestamp?: string
}

export function MessageBubble({
  role,
  content,
  timestamp,
}: MessageBubbleProps) {
  const isUser = role === "user"
  const lang = detectLang()

  return (
    <div
      className={`message-bubble ${isUser ? "message-bubble--user" : "message-bubble--assistant"}`}
      data-testid="chat-message"
    >
      <div className="message-bubble-content">
        <span className="message-bubble-author">
          {isUser ? t("message_you", lang) : t("message_astrologer", lang)}
        </span>
        <p className="message-bubble-text" data-testid="chat-message-content">
          {content}
        </p>
        {timestamp && (
          <span className="message-bubble-time">
            {new Date(timestamp).toLocaleTimeString(LOCALE_MAP[lang], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        )}
      </div>
    </div>
  )
}
