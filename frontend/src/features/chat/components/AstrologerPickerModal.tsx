import { useEffect, useRef } from "react"
import { X } from "lucide-react"

import type { Astrologer } from "@api/astrologers"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type AstrologerPickerModalProps = {
  astrologers: Astrologer[]
  isLoading: boolean
  isCreating: boolean
  onSelect: (astrologerId: string) => void
  onClose: () => void
}

export function AstrologerPickerModal({
  astrologers,
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
      className="astrologer-picker-overlay"
      ref={overlayRef}
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose()
      }}
      role="dialog"
      aria-modal="true"
      aria-label={t("new_conversation", lang)}
    >
      <div className="astrologer-picker-modal">
        <div className="astrologer-picker-header">
          <h3 className="astrologer-picker-title">{t("new_conversation", lang)}</h3>
          <button
            type="button"
            className="astrologer-picker-close"
            onClick={onClose}
            aria-label={t("close", lang)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="astrologer-picker-body">
          {isLoading && (
            <p className="astrologer-picker-loading">{t("loading", lang)}</p>
          )}

          {!isLoading && astrologers.length === 0 && (
            <p className="astrologer-picker-empty">{t("empty_state", lang)}</p>
          )}

          {!isLoading && astrologers.map((astrologer) => {
            const fullName =
              [astrologer.first_name, astrologer.last_name].filter(Boolean).join(" ") ||
              astrologer.name

            return (
            <button
              key={astrologer.id}
              type="button"
              className="astrologer-picker-item"
              onClick={() => onSelect(astrologer.id)}
              disabled={isCreating}
            >
              <div className="astrologer-picker-item-avatar">
                {astrologer.avatar_url ? (
                  <img
                    src={astrologer.avatar_url}
                    alt={`${t("avatar_alt", lang)} ${fullName}`}
                    className="astrologer-picker-item-avatar-img"
                    onError={(e) => {
                      const target = e.currentTarget
                      target.style.display = "none"
                      const fallback = target.nextElementSibling as HTMLElement | null
                      if (fallback) fallback.style.display = "flex"
                    }}
                  />
                ) : null}
                <span
                  className="astrologer-picker-item-avatar-fallback"
                  style={{ display: astrologer.avatar_url ? "none" : "flex" }}
                >
                  {fullName.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="astrologer-picker-item-info">
                <span className="astrologer-picker-item-name">{fullName}</span>
                {astrologer.bio_short && (
                  <span className="astrologer-picker-item-bio">{astrologer.bio_short}</span>
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



