import type { LucideIcon } from 'lucide-react'

export interface ShortcutCardProps {
  title: string
  subtitle: string
  icon: LucideIcon
  badgeColor: string
  onClick?: () => void
}

export function ShortcutCard({ title, subtitle, icon: Icon, badgeColor, onClick }: ShortcutCardProps) {
  return (
    <button type="button" className="shortcut-card" onClick={onClick}>
      <div className="shortcut-card__badge" style={{ background: badgeColor }}>
        <Icon size={20} strokeWidth={1.75} />
      </div>
      <div className="shortcut-card__content">
        <span className="shortcut-card__title">{title}</span>
        <span className="shortcut-card__subtitle">{subtitle}</span>
      </div>
    </button>
  )
}
