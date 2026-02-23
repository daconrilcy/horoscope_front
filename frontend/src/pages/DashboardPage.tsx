import type { ReactNode } from "react"

import { DashboardCard } from "../components/dashboard"
import { StarIcon, ChatIcon, CrystalBallIcon, UserIcon, SettingsIcon } from "../components/icons"
import { detectLang } from "../i18n/astrology"
import type { DashboardCardId } from "../i18n/dashboard"
import {
  DASHBOARD_CARD_IDS,
  DASHBOARD_CARD_PATHS,
  translateDashboardCard,
  translateDashboardPage,
} from "../i18n/dashboard"

function getDashboardCardIcon(cardId: DashboardCardId): ReactNode {
  const iconMap: Record<DashboardCardId, ReactNode> = {
    natal: <StarIcon />,
    chat: <ChatIcon />,
    consultations: <CrystalBallIcon />,
    astrologers: <UserIcon />,
    settings: <SettingsIcon />,
  }
  return iconMap[cardId]
}

export function DashboardPage() {
  const locale = detectLang()
  const { title, welcome } = translateDashboardPage(locale)

  return (
    <div className="panel">
      <h1>{title}</h1>
      <p>{welcome}</p>
      <nav className="dashboard-grid" aria-label="Navigation principale">
        {DASHBOARD_CARD_IDS.map((cardId) => {
          const { label, description } = translateDashboardCard(cardId, locale)
          return (
            <DashboardCard
              key={cardId}
              label={label}
              path={DASHBOARD_CARD_PATHS[cardId]}
              icon={getDashboardCardIcon(cardId)}
              description={description}
            />
          )
        })}
      </nav>
    </div>
  )
}
