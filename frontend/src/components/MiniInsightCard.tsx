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
      <div className="mini-card__badge" style={{ background: badgeColor }}>
        <Icon size={18} strokeWidth={1.75} />
      </div>
      <p className="mini-card__title">{title}</p>
      <p className="mini-card__desc">{description}</p>
    </div>
  )
}
