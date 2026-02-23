import { MessageCircle, Layers } from 'lucide-react'
import { ShortcutCard } from './ShortcutCard'

export interface ShortcutsSectionProps {
  onChatClick?: () => void
  onTirageClick?: () => void
}

const SHORTCUTS = [
  {
    key: 'chat',
    title: 'Chat astrologue',
    subtitle: 'En ligne',
    icon: MessageCircle,
    badgeColor: 'var(--badge-chat)',
    path: '/chat',
  },
  {
    key: 'tirage',
    title: 'Tirage du jour',
    subtitle: '3 cartes',
    icon: Layers,
    badgeColor: 'var(--badge-tirage)',
    path: '/consultations',
  },
]

export function ShortcutsSection({ onChatClick, onTirageClick }: ShortcutsSectionProps) {
  return (
    <section>
      <h2 className="shortcuts-section__title">Raccourcis</h2>
      <div className="shortcuts-grid">
        <ShortcutCard
          title={SHORTCUTS[0].title}
          subtitle={SHORTCUTS[0].subtitle}
          icon={SHORTCUTS[0].icon}
          badgeColor={SHORTCUTS[0].badgeColor}
          onClick={onChatClick}
        />
        <ShortcutCard
          title={SHORTCUTS[1].title}
          subtitle={SHORTCUTS[1].subtitle}
          icon={SHORTCUTS[1].icon}
          badgeColor={SHORTCUTS[1].badgeColor}
          onClick={onTirageClick}
        />
      </div>
    </section>
  )
}
