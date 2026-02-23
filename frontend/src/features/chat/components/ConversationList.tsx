import { useState } from "react"

import type { ChatConversationSummary } from "../../../api/chat"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"
import { ConversationItem } from "./ConversationItem"

type ConversationListProps = {
  conversations: ChatConversationSummary[]
  selectedId: number | null
  onSelect: (id: number) => void
  isLoading?: boolean
  error?: Error | null
}

export function ConversationList({
  conversations,
  selectedId,
  onSelect,
  isLoading = false,
  error = null,
}: ConversationListProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const lang = detectLang()

  const filteredConversations = conversations.filter((conv) =>
    conv.last_message_preview?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h2 className="conversation-list-title">{t("conversations_title", lang)}</h2>
        <input
          type="search"
          className="conversation-list-search"
          placeholder={t("conversations_search", lang)}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          aria-label={t("conversations_search", lang)}
        />
      </div>

      <div className="conversation-list-items">
        {isLoading && (
          <p className="conversation-list-loading" aria-busy="true">
            {t("loading", lang)}
          </p>
        )}

        {error && (
          <p className="conversation-list-error" role="alert">
            {t("conversations_error", lang)}
          </p>
        )}

        {!isLoading && !error && filteredConversations.length === 0 && (
          <p className="conversation-list-empty">
            {searchQuery ? t("conversations_no_results", lang) : t("chat_no_conversation", lang)}
          </p>
        )}

        {filteredConversations.map((conv) => (
          <ConversationItem
            key={conv.conversation_id}
            conversation={conv}
            isActive={conv.conversation_id === selectedId}
            onClick={() => onSelect(conv.conversation_id)}
          />
        ))}
      </div>
    </div>
  )
}
