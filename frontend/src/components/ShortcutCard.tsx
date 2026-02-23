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
    <button className="shortcut-card" onClick={onClick}>
      <div className="shortcut-card__badge" style={{ background: badgeColor }}>
        <Icon size={20} strokeWidth={1.75} />
      </div>
      <div>
        <div className="shortcut-card__title">{title}</div>
        <div className="shortcut-card__subtitle">{subtitle}</div>
      </div>
    </button>
  )
}
