import type { ReactNode } from "react"
import { DashboardCard } from "../components/dashboard"
import { StarIcon, ChatIcon, CrystalBallIcon, UserIcon, SettingsIcon } from "../components/icons"
import { useAstrologyLabels } from "../i18n/astrology"
import type { DashboardCardId } from "../i18n/dashboard"
import {
  DASHBOARD_CARD_IDS,
  DASHBOARD_CARD_PATHS,
  translateDashboardCard,
  translateDashboardPage,
} from "../i18n/dashboard"
import { TodayHeader } from "../components/TodayHeader"
import { DailyInsightsSection } from "../components/DailyInsightsSection"

import { useAccessTokenSnapshot } from "../utils/authToken"
import { useAuthMe } from "../api/authMe"

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
  const { lang } = useAstrologyLabels()
  const { title, welcome } = translateDashboardPage(lang)
  const accessToken = useAccessTokenSnapshot()
  const { data: user, isLoading: isUserLoading } = useAuthMe(accessToken)
  
  // Utilise l'email (partie avant @) si le nom n'est pas dispo
  const userName = isUserLoading 
    ? "..." 
    : (user?.email ? user.email.split('@')[0] : "Utilisateur")

  return (
    <div className="panel dashboard-container">
      <TodayHeader userName={userName} />
      
      <div>
        <h1>{title}</h1>
        <p>{welcome}</p>
      </div>

      <nav className="dashboard-grid" aria-label="Navigation principale">
        {DASHBOARD_CARD_IDS.map((cardId) => {
          const { label, description } = translateDashboardCard(cardId, lang)
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

      <DailyInsightsSection onSectionClick={() => {}} />
    </div>
  )
}
