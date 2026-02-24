import { Link } from 'react-router-dom'
import type { LucideIcon } from 'lucide-react'

export interface ShortcutCardProps {
  title: string
  subtitle: string
  icon: LucideIcon
  badgeColor: string
  onClick?: () => void
  to?: string
  isOnline?: boolean
}

export function ShortcutCard({ 
  title, 
  subtitle, 
  icon: Icon, 
  badgeColor, 
  onClick, 
  to, 
  isOnline
}: ShortcutCardProps) {
  const subtitleClass = `shortcut-card__subtitle${isOnline ? " shortcut-card__subtitle--online" : ""}`

  const content = (
    <>
      <div className="shortcut-card__badge" style={{ background: badgeColor }}>
        <Icon size={20} strokeWidth={1.75} />
      </div>
      <div className="shortcut-card__content">
        <span className="shortcut-card__title">{title}</span>
        <span className={subtitleClass}>
          {subtitle}
        </span>
      </div>
    </>
  )

  if (to) {
    return (
      <Link to={to} className="shortcut-card" onClick={onClick}>
        {content}
      </Link>
    )
  }

  return (
    <button type="button" className="shortcut-card" onClick={onClick}>
      {content}
    </button>
  )
}
