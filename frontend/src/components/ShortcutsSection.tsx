import { MessageCircle, Layers } from 'lucide-react'
import { ShortcutCard } from './ShortcutCard'

const SHORTCUTS = [
  {
    key: 'chat',
    title: 'Chat astrologue',
    subtitle: 'En ligne',
    icon: MessageCircle,
    badgeColor: 'var(--badge-chat)',
    path: '/chat',
    isOnline: true,
  },
  {
    key: 'tirage',
    title: 'Tirage du jour',
    subtitle: '3 cartes',
    icon: Layers,
    badgeColor: 'var(--badge-tirage)',
    path: '/consultations',
    isOnline: false,
  },
]

export interface ShortcutsSectionProps {
  onChatClick?: () => void
  onTirageClick?: () => void
}

export function ShortcutsSection({ onChatClick, onTirageClick }: ShortcutsSectionProps) {
  return (
    <section className="shortcuts-section">
      <h2 className="shortcuts-section__title">Activités</h2>
      <div className="shortcuts-grid">
        {SHORTCUTS.map((shortcut) => {
          const handleClick = shortcut.key === 'chat' ? onChatClick : onTirageClick
          return (
            <ShortcutCard
              key={shortcut.key}
              title={shortcut.title}
              subtitle={shortcut.subtitle}
              icon={shortcut.icon}
              badgeColor={shortcut.badgeColor}
              to={shortcut.path}
              onClick={handleClick}
              isOnline={shortcut.isOnline}
            />
          )
        })}
      </div>
    </section>
  )
}
