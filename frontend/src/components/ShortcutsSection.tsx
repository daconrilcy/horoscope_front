import { MessageCircle, Layers, Calendar } from 'lucide-react'
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
  {
    key: 'history',
    title: 'Historique',
    subtitle: 'Mes prédictions',
    icon: Calendar,
    badgeColor: 'var(--primary)',
    path: '/dashboard', // For now, stays on dashboard or a modal
    isOnline: false,
  },
]

export interface ShortcutsSectionProps {
  onChatClick?: () => void
  onTirageClick?: () => void
  onHistoryClick?: () => void
}

export function ShortcutsSection({ onChatClick, onTirageClick, onHistoryClick }: ShortcutsSectionProps) {
  return (
    <section className="shortcuts-section">
      <h2 className="shortcuts-section__title">Activités</h2>
      <div className="shortcuts-grid">
        {SHORTCUTS.map((shortcut) => {
          let handleClick = undefined;
          if (shortcut.key === 'chat') handleClick = onChatClick;
          else if (shortcut.key === 'tirage') handleClick = onTirageClick;
          else if (shortcut.key === 'history') handleClick = onHistoryClick;

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
