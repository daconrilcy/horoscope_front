import type { ChatConversationSummary } from "../../../api/chat"
import { detectLang } from "../../../i18n/astrology"
import type { AstrologyLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

const LOCALE_MAP: Record<AstrologyLang, string> = {
  fr: "fr-FR",
  en: "en-US",
  es: "es-ES",
}

type ConversationItemProps = {
  conversation: ChatConversationSummary
  isActive: boolean
  onClick: () => void
}

export function ConversationItem({
  conversation,
  isActive,
  onClick,
}: ConversationItemProps) {
  const lang = detectLang()
  const preview = conversation.last_message_preview || t("conversation_new", lang)
  const date = new Date(conversation.updated_at)
  const formattedDate = date.toLocaleDateString(LOCALE_MAP[lang], {
    day: "numeric",
    month: "short",
  })

  return (
    <button
      type="button"
      onClick={onClick}
      className={`conversation-item ${isActive ? "conversation-item--active" : ""}`}
      aria-pressed={isActive}
    >
      <div className="conversation-item-content">
        <span className="conversation-item-preview">{preview}</span>
        <span className="conversation-item-date">{formattedDate}</span>
      </div>
    </button>
  )
}
