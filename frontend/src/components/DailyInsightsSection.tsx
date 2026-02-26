import { useMemo } from 'react'
import { Heart, Briefcase, Zap, type LucideIcon } from 'lucide-react'
import { MiniInsightCard, type MiniInsightCardType } from './MiniInsightCard'
import { useAstrologyLabels } from '../i18n/astrology'
import { translateInsight, translateInsightSection, type InsightId } from '../i18n/insights'

interface InsightConfigItem {
  id: InsightId
  type: MiniInsightCardType
  icon: LucideIcon
  badgeColor: string
}

const INSIGHT_CONFIG: InsightConfigItem[] = [
  { id: 'amour', type: 'love', icon: Heart, badgeColor: 'var(--badge-amour)' },
  { id: 'travail', type: 'work', icon: Briefcase, badgeColor: 'var(--badge-travail)' },
  { id: 'energie', type: 'energy', icon: Zap, badgeColor: 'var(--badge-energie)' },
]

export interface DailyInsightsSectionProps {
  onSectionClick?: () => void
}

export function DailyInsightsSection({ onSectionClick }: DailyInsightsSectionProps) {
  const { lang } = useAstrologyLabels()

  const ariaLabel = useMemo(() => translateInsightSection(lang).ariaLabel, [lang])

  const renderedCards = useMemo(() => {
    return INSIGHT_CONFIG.map((config) => {
      const { title, description } = translateInsight(config.id, lang)
      return (
        <MiniInsightCard
          key={config.id}
          title={title}
          description={description}
          icon={config.icon}
          badgeColor={config.badgeColor}
          onClick={onSectionClick}
        />
      )
    })
  }, [lang, onSectionClick])

  return (
    <section aria-label={ariaLabel}>
      <div className="mini-cards-grid">
        {renderedCards}
      </div>
    </section>
  )
}
