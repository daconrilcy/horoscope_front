import type { LucideIcon } from 'lucide-react'

export interface MiniInsightCardProps {
  title: string
  description: string
  icon: LucideIcon
  badgeColor: string
}

export function MiniInsightCard({ title, description, icon: Icon, badgeColor }: MiniInsightCardProps) {
  return (
    <div className="mini-card">
      <div className="mini-card__badge" style={{ background: badgeColor }} aria-hidden="true">
        <Icon size={18} strokeWidth={1.75} />
      </div>
      <h3 className="mini-card__title">{title}</h3>
      <p className="mini-card__desc">{description}</p>
    </div>
  )
}
