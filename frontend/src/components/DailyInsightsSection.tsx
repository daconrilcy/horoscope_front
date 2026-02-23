import { useMemo } from 'react'
import { Heart, Briefcase, Zap, ChevronRight, type LucideIcon } from 'lucide-react'
import { MiniInsightCard } from './MiniInsightCard'
import { useAstrologyLabels } from '../i18n/astrology'
import { translateInsight, translateInsightSection, type InsightId } from '../i18n/insights'

interface InsightConfigItem {
  id: InsightId
  icon: LucideIcon
  badgeColor: string
}

const INSIGHT_CONFIG: InsightConfigItem[] = [
  { id: 'amour', icon: Heart, badgeColor: 'var(--badge-amour)' },
  { id: 'travail', icon: Briefcase, badgeColor: 'var(--badge-travail)' },
  { id: 'energie', icon: Zap, badgeColor: 'var(--badge-energie)' },
]

export interface DailyInsightsSectionProps {
  onSectionClick?: () => void
}

export function DailyInsightsSection({ onSectionClick }: DailyInsightsSectionProps) {
  const { lang } = useAstrologyLabels()
  
  const { sectionTitle, ariaLabel } = useMemo(() => {
    const { title, ariaLabel: label } = translateInsightSection(lang)
    return { sectionTitle: title, ariaLabel: label }
  }, [lang])

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
        />
      )
    })
  }, [lang])

  const HeaderContainer = onSectionClick ? 'button' : 'div'

  return (
    <section aria-labelledby="daily-insights-title">
      <HeaderContainer 
        className={`section-header ${onSectionClick ? 'section-header--clickable' : ''}`}
        onClick={onSectionClick}
        type={onSectionClick ? 'button' : undefined}
        aria-label={onSectionClick ? ariaLabel : undefined}
      >
        <h2 id="daily-insights-title" className="section-header__title">{sectionTitle}</h2>
        <ChevronRight size={18} strokeWidth={1.75} color="var(--text-2)" />
      </HeaderContainer>
      
      <div className="mini-cards-grid">
        {renderedCards}
      </div>
    </section>
  )
}
