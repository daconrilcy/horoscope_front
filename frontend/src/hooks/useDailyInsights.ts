import { useMemo } from 'react'
import { Heart, Briefcase, Zap, type LucideIcon } from 'lucide-react'
import { useAstrologyLabels } from '../i18n/astrology'
import { translateInsight, translateInsightSection, type InsightId } from '../i18n/insights'
import type { MiniInsightCardType } from '../components/MiniInsightCard'

export interface InsightItem {
  id: InsightId
  type: MiniInsightCardType
  icon: LucideIcon
  badgeColor: string
  title: string
  description: string
}

export interface DailyInsightsData {
  ariaLabel: string
  items: InsightItem[]
}

const INSIGHT_CONFIG = [
  { id: 'amour' as const, type: 'love' as const, icon: Heart, badgeColor: 'var(--badge-amour)' },
  { id: 'travail' as const, type: 'work' as const, icon: Briefcase, badgeColor: 'var(--badge-travail)' },
  { id: 'energie' as const, type: 'energy' as const, icon: Zap, badgeColor: 'var(--badge-energie)' },
]

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
