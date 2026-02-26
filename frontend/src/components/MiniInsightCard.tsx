import type { LucideIcon } from 'lucide-react'
import './MiniInsightCard.css'

export type MiniInsightCardType = 'love' | 'work' | 'energy'

export interface MiniInsightCardProps {
  title: string
  description: string
  icon: LucideIcon
  badgeColor: string
  type?: MiniInsightCardType
  onClick?: () => void
}

export function MiniInsightCard({ title, description, icon: Icon, badgeColor, type, onClick }: MiniInsightCardProps) {
  const Wrapper = onClick ? 'button' : 'div'
  const typeClass = type ? ` mini-card--${type}` : ''

  return (
    <Wrapper
      className={`mini-card${typeClass} ${onClick ? 'mini-card--clickable' : ''}`}
      onClick={onClick}
      type={onClick ? 'button' : undefined}
      data-type={type}
    >
      <div className="mini-card__content">
        <div className="mini-card__badge" style={{ background: badgeColor }} aria-hidden="true">
          <Icon size={20} strokeWidth={1.75} />
        </div>
        <h3 className="mini-card__title">{title}</h3>
        <p className="mini-card__desc">{description}</p>
      </div>
    </Wrapper>
  )
}
