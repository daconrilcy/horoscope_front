import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

export function TypingIndicator() {
  const lang = detectLang()

  return (
    <div className="typing-indicator" aria-label={t("typing_label", lang)}>
      <div className="typing-indicator-content">
        <span className="typing-indicator-author">{t("message_astrologer", lang)}</span>
        <div className="typing-indicator-dots">
          <span className="typing-indicator-dot" />
          <span className="typing-indicator-dot" />
          <span className="typing-indicator-dot" />
        </div>
      </div>
    </div>
  )
}
