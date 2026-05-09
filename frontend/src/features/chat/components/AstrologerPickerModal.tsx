import { useEffect, useRef } from "react"
import { X } from "lucide-react"

import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type AstrologerPickerModalProps = {
  experts: Astrologer[]
  isLoading: boolean
  isCreating: boolean
  onSelect: (astrologerId: string) => void
  onClose: () => void
}

export function AstrologerPickerModal({
  experts,
  isLoading,
  isCreating,
  onSelect,
  onClose,
}: AstrologerPickerModalProps) {
  const lang = detectLang()
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [onClose])

  return (
    <div
      className="person-picker-overlay"
      ref={overlayRef}
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose()
      }}
      role="dialog"
      aria-modal="true"
      aria-label={t("new_conversation", lang)}
    >
      <div className="person-picker-modal">
        <div className="person-picker-header">
          <h3 className="person-picker-title">{t("new_conversation", lang)}</h3>
          <button
            type="button"
            className="person-picker-close"
            onClick={onClose}
            aria-label={t("close", lang)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="person-picker-body">
          {isLoading && (
            <p className="person-picker-loading">{t("loading", lang)}</p>
          )}

          {!isLoading && experts.length === 0 && (
            <p className="person-picker-empty">{t("empty_state", lang)}</p>
          )}

          {!isLoading && experts.map((expert) => {
            const fullName =
              [expert.first_name, expert.last_name].filter(Boolean).join(" ") ||
              expert.name

            return (
            <button
              key={expert.id}
              type="button"
              className="person-picker-item"
              onClick={() => onSelect(expert.id)}
              disabled={isCreating}
            >
              <div className="person-picker-item-avatar">
                {expert.avatar_url ? (
                  <img
                    src={expert.avatar_url}
                    alt={`${t("avatar_alt", lang)} ${fullName}`}
                    className="person-picker-item-avatar-img"
                    onError={(e) => {
                      const target = e.currentTarget
                      target.hidden = true
                      const fallback = target.nextElementSibling as HTMLElement | null
                      if (fallback) fallback.hidden = false
                    }}
                  />
                ) : null}
                <span
                  className="person-picker-item-avatar-fallback"
                  hidden={Boolean(expert.avatar_url)}
                >
                  {fullName.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="person-picker-item-info">
                <span className="person-picker-item-name">{fullName}</span>
                {expert.bio_short && (
                  <span className="person-picker-item-bio">{expert.bio_short}</span>
                )}
              </div>
            </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}



