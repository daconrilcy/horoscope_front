import { useMemo } from 'react'
import { Heart, Briefcase, Zap, type LucideIcon } from 'lucide-react'
import { useAstrologyLabels } from '../i18n/astrology'
import { translateInsight, translateInsightSection, type InsightId } from '../i18n/insights'
import type { MiniInsightCardType } from '../components/MiniInsightCard'
import type { BadgeColorValue } from '../components/ui'

export interface InsightItem {
  id: InsightId
  type: MiniInsightCardType
  icon: LucideIcon
  badgeColor: BadgeColorValue
  title: string
  description: string
}

export interface DailyInsightsData {
  ariaLabel: string
  items: InsightItem[]
}

const INSIGHT_CONFIG = [
  { id: 'amour' as const, type: 'love' as const, icon: Heart, badgeColor: 'var(--color-badge-amour)' },
  { id: 'travail' as const, type: 'work' as const, icon: Briefcase, badgeColor: 'var(--color-badge-travail)' },
  { id: 'energie' as const, type: 'energy' as const, icon: Zap, badgeColor: 'var(--color-badge-energie)' },
] satisfies ReadonlyArray<{
  id: InsightId
  type: MiniInsightCardType
  icon: LucideIcon
  badgeColor: BadgeColorValue
}>

export function useDailyInsights(): DailyInsightsData {
  const { lang } = useAstrologyLabels()

  const ariaLabel = useMemo(() => translateInsightSection(lang).ariaLabel, [lang])

  const items = useMemo(() => {
    return INSIGHT_CONFIG.map((config) => {
      const { title, description } = translateInsight(config.id, lang)
      return {
        ...config,
        title,
        description,
      }
    })
  }, [lang])

  return {
    ariaLabel,
    items,
  }
}
