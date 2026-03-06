import type { ReactNode } from "react"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/astrologers"

type MobileView = "list" | "chat"

type ChatLayoutProps = {
  leftPanel: ReactNode
  centerPanel: ReactNode
  rightPanel: ReactNode
  mobileView: MobileView
  onMobileViewChange: (view: MobileView) => void
  hasConversation: boolean
  isMobile: boolean
}

export function ChatLayout({
  leftPanel,
  centerPanel,
  rightPanel,
  mobileView,
  onMobileViewChange,
  hasConversation,
  isMobile,
}: ChatLayoutProps) {
  const lang = detectLang()

  if (isMobile) {
    return (
      <div className="chat-layout chat-layout--mobile">
        {mobileView === "list" && (
          <div className="chat-layout-panel chat-layout-panel--left">
            {leftPanel}
            {hasConversation && (
              <button
                type="button"
                className="chat-layout-mobile-action"
                onClick={() => onMobileViewChange("chat")}
                aria-label={t("chat_resume_conversation", lang)}
              >
                {t("chat_resume_conversation", lang)}
              </button>
            )}
          </div>
        )}
        {mobileView === "chat" && (
          <div className="chat-layout-panel chat-layout-panel--center">
            {centerPanel}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="chat-layout chat-layout--desktop">
      <div className="chat-layout-panel chat-layout-panel--left">
        {leftPanel}
      </div>
      <div className="chat-layout-panel chat-layout-panel--center">
        {centerPanel}
      </div>
      <div className="chat-layout-panel chat-layout-panel--right">
        {rightPanel}
      </div>
    </div>
  )
}

export type { MobileView }
