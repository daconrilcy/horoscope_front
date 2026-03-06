import { useState } from "react"
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

function getAvatarUrl(conversation: ChatConversationSummary): string {
  if (conversation.avatar_url) return conversation.avatar_url
  const seed = encodeURIComponent(conversation.persona_name ?? "astrologer")
  return `https://api.dicebear.com/7.x/bottts/svg?seed=${seed}`
}

export function ConversationItem({
  conversation,
  isActive,
  onClick,
}: ConversationItemProps) {
  const [imageError, setImageError] = useState(false)
  const lang = detectLang()
  const preview = conversation.last_message_preview || t("conversation_new", lang)
  const dateSource = conversation.last_message_at ?? conversation.updated_at
  const date = new Date(dateSource)
  const isValidDate = !Number.isNaN(date.getTime())

  const formattedDate = isValidDate
    ? date.toLocaleDateString(LOCALE_MAP[lang], {
        day: "numeric",
        month: "short",
      })
    : ""

  const personaName = conversation.persona_name || t("message_astrologer", lang)
  const avatarUrl = getAvatarUrl(conversation)

  return (
    <button
      type="button"
      onClick={onClick}
      className={`conversation-item ${isActive ? "conversation-item--active" : ""}`}
      aria-pressed={isActive}
    >
      <div className="conversation-item-avatar">
        {!imageError ? (
          <img
            src={avatarUrl}
            alt={`${t("avatar_alt", lang)} ${personaName}`}
            className="conversation-item-avatar-img"
            onError={() => setImageError(true)}
          />
        ) : (
          <span className="conversation-item-avatar-fallback">
            {personaName.charAt(0).toUpperCase()}
          </span>
        )}
      </div>
      <div className="conversation-item-body">
        <div className="conversation-item-header">
          <span className="conversation-item-name">{personaName}</span>
          <span className="conversation-item-date">{formattedDate}</span>
        </div>
        <span className="conversation-item-preview">{preview}</span>
      </div>
    </button>
  )
}

export function ConversationItemSkeleton() {
  return (
    <div className="conversation-item conversation-item-skeleton" aria-hidden="true">
      <div className="conversation-item-avatar conversation-item-avatar--skeleton" />
      <div className="conversation-item-body">
        <div className="conversation-item-header">
          <span className="skeleton-line skeleton-line--name" />
          <span className="skeleton-line skeleton-line--date" />
        </div>
        <span className="skeleton-line skeleton-line--preview" />
      </div>
    </div>
  )
}
