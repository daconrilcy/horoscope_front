import { useEffect, type ReactNode } from "react"
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
import { getUserDisplayName } from "../utils/user"

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

/**
 * @deprecated This page has been replaced by TodayPage as the primary dashboard.
 * Kept for legacy reference or future B2B modules per AC7 of Story 17.8.
 */
export function DashboardPage() {
  const { lang } = useAstrologyLabels()
  const { title, welcome } = translateDashboardPage(lang)
  const accessToken = useAccessTokenSnapshot()
  const { data: user, isLoading: isUserLoading } = useAuthMe(accessToken)
  
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.warn("DashboardPage is deprecated. Use TodayPage instead.")
    }
  }, [])

  const userName = isUserLoading 
    ? "loading" 
    : getUserDisplayName(user)

  return (
    <div className="panel dashboard-container">
      <TodayHeader userName={userName} />
      
      <div>
        <h2 className="dashboard-title">{title}</h2>
        <p>{welcome}</p>
      </div>

      <nav className="dashboard-grid" aria-label="Navigation rapide">
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

      <DailyInsightsSection />
    </div>
  )
}
