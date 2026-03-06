import { MessageCircle } from "lucide-react"

import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

type ChatEmptyStateProps = {
  onStartConversation: () => void
}

export function ChatEmptyState({ onStartConversation }: ChatEmptyStateProps) {
  const lang = detectLang()

  return (
    <div className="chat-empty-state">
      <div className="chat-empty-state-icon-wrap">
        <MessageCircle size={48} strokeWidth={1.5} />
      </div>
      <h2 className="chat-empty-state-title">{t("chat_empty_state_title", lang)}</h2>
      <p className="chat-empty-state-description">{t("chat_empty_state_description", lang)}</p>
      <button
        type="button"
        className="chat-empty-state-cta btn"
        onClick={onStartConversation}
      >
        {t("chat_empty_state_cta", lang)}
      </button>
    </div>
  )
}
