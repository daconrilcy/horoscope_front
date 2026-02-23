import { Heart, Briefcase, Zap, ChevronRight } from 'lucide-react'
import { MiniInsightCard } from './MiniInsightCard'

const AMOUR_INSIGHTS = [
  {
    key: 'amour',
    title: 'Amour',
    description: 'Balance dans ta relation',
    icon: Heart,
    badgeColor: 'var(--badge-amour)',
  },
  {
    key: 'travail',
    title: 'Travail',
    description: 'Nouvelle opportunité à saisir',
    icon: Briefcase,
    badgeColor: 'var(--badge-travail)',
  },
  {
    key: 'energie',
    title: 'Énergie',
    description: 'Énergie haute, humeur positive',
    icon: Zap,
    badgeColor: 'var(--badge-energie)',
  },
]

export interface AmourSectionProps {
  onSectionClick?: () => void
}

export function AmourSection({ onSectionClick }: AmourSectionProps) {
  return (
    <section>
      <div className="section-header">
        <p className="section-header__title">Amour</p>
        <ChevronRight size={18} strokeWidth={1.75} color="var(--text-2)" onClick={onSectionClick} />
      </div>
      <div className="mini-cards-grid">
        {AMOUR_INSIGHTS.map((item) => (
          <MiniInsightCard
            key={item.key}
            title={item.title}
            description={item.description}
            icon={item.icon}
            badgeColor={item.badgeColor}
          />
        ))}
      </div>
    </section>
  )
}
