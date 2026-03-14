import { useState } from "react"
import { Plus } from "lucide-react"

import type { ChatConversationSummary } from "@api/chat"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import { ConversationItem, ConversationItemSkeleton } from "./ConversationItem"

type ConversationListProps = {
  conversations: ChatConversationSummary[]
  selectedId: number | null
  onSelect: (id: number) => void
  onNewConversation: () => void
  isLoading?: boolean
  error?: Error | null
}

export function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onNewConversation,
  isLoading = false,
  error = null,
}: ConversationListProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const lang = detectLang()

  const filteredConversations = conversations.filter((conv) => {
    const query = searchQuery.toLowerCase()
    return (
      conv.persona_name?.toLowerCase().includes(query) ||
      conv.last_message_preview?.toLowerCase().includes(query)
    )
  })

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <div className="conversation-list-title-row">
          <h2 className="conversation-list-title">{t("conversations_title", lang)}</h2>
          <button
            type="button"
            className="conversation-list-new-btn"
            onClick={onNewConversation}
            aria-label={t("new_conversation", lang)}
            title={t("new_conversation", lang)}
          >
            <Plus size={18} />
          </button>
        </div>
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
          <>
            <ConversationItemSkeleton />
            <ConversationItemSkeleton />
            <ConversationItemSkeleton />
          </>
        )}

        {error && (
          <p className="conversation-list-error" role="alert">
            {t("conversations_error", lang)}
          </p>
        )}

        {!isLoading && !error && filteredConversations.length === 0 && (
          <div className="conversation-list-empty-wrap">
            <p className="conversation-list-empty">
              {searchQuery ? t("conversations_no_results", lang) : t("chat_no_conversation", lang)}
            </p>
          </div>
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



