import React from "react"
import { useChatEntitlementUsage } from "../../../api/billing"
import { useAstrologyLabels } from "../../../i18n/astrology"
import { getChatQuotaMessages } from "../../../i18n/billing"
import { formatDateTime } from "../../../utils/formatDate"
import { UpgradeCTA } from "../../../components/ui"
import "./ChatQuotaBanner.css"

export function ChatQuotaBanner() {
  const { data } = useChatEntitlementUsage()
  const { lang } = useAstrologyLabels()

  if (!data) {
    return null
  }

  const t = getChatQuotaMessages(lang)
  const resetDateLabel = data.reset_at ? formatDateTime(data.reset_at) : "—"
  const isExhausted = data.blocked || data.remaining === 0
  const limit = data.limit > 0 ? data.limit : 1
  if (isExhausted) {
    return (
      <div className="chat-quota-banner chat-quota-banner--exhausted" role="alert">
        <span className="chat-quota-banner__text">{t.exhausted(resetDateLabel)}</span>
        <UpgradeCTA featureCode="astrologer_chat" variant="button" />
      </div>
    )
  }

  return (
    <div className="chat-quota-banner chat-quota-banner--info">
      <progress
        className="chat-quota-banner__meter"
        aria-label={t.remaining(data.remaining, data.limit)}
        value={Math.min(data.consumed, limit)}
        max={limit}
      />
      <span className="chat-quota-banner__reset">{t.resetDate(resetDateLabel)}</span>
    </div>
  )
}
