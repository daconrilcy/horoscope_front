import type { LucideIcon } from 'lucide-react'

export interface MiniInsightCardProps {
  title: string
  description: string
  icon: LucideIcon
  badgeColor: string
  onClick?: () => void
}

export function MiniInsightCard({ title, description, icon: Icon, badgeColor, onClick }: MiniInsightCardProps) {
  const Wrapper = onClick ? 'button' : 'div'
  
  return (
    <Wrapper 
      className={`mini-card ${onClick ? 'mini-card--clickable' : ''}`} 
      onClick={onClick}
      type={onClick ? 'button' : undefined}
    >
      <div className="mini-card__badge" style={{ background: badgeColor }} aria-hidden="true">
        <Icon size={18} strokeWidth={1.75} />
      </div>
      <h3 className="mini-card__title">{title}</h3>
      <p className="mini-card__desc">{description}</p>
    </Wrapper>
  )
}
