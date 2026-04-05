import type { ReactNode } from "react"
import { detectLang } from "@i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"

type MobileView = "list" | "chat"

type ChatLayoutProps = {
  leftPanel: ReactNode
  centerPanel: ReactNode
  topBanner?: ReactNode
  mobileView: MobileView
  onMobileViewChange: (view: MobileView) => void
  hasConversation: boolean
  isMobile: boolean
}

export function ChatLayout({
  leftPanel,
  centerPanel,
  topBanner,
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
    <div
      className="two-col-layout chat-layout chat-layout--desktop"
      style={{ "--sidebar-width": "320px" } as React.CSSProperties}
    >
      {topBanner ? <div className="chat-layout__banner">{topBanner}</div> : null}
      <div className="chat-layout__body">
        <div className="two-col-layout__sidebar two-col-layout__sidebar--collapsible">
          {leftPanel}
        </div>
        <div className="two-col-layout__main">
          {centerPanel}
        </div>
      </div>
    </div>
  )
}

export type { MobileView }


