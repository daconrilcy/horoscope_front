import { MessageCircle, Layers, Calendar } from 'lucide-react'
import { ShortcutCard } from './ShortcutCard'
import { useAstrologyLabels } from '../i18n/astrology'
import { translateDashboardPage } from '../i18n/dashboard'

export interface ShortcutsSectionProps {
  onChatClick?: () => void
  onConsultationClick?: () => void
  onHistoryClick?: () => void
}

export function ShortcutsSection({ onChatClick, onConsultationClick, onHistoryClick }: ShortcutsSectionProps) {
  const { lang } = useAstrologyLabels()
  const { activities, shortcuts } = translateDashboardPage(lang)
  const shortcutItems = [
    {
      key: 'chat',
      title: shortcuts.chatTitle,
      subtitle: shortcuts.chatSubtitle,
      icon: MessageCircle,
      badgeColor: 'var(--badge-chat)',
      path: '/chat',
      isOnline: true,
    },
    {
      key: 'consultation',
      title: shortcuts.consultationTitle,
      subtitle: shortcuts.consultationSubtitle,
      icon: Layers,
      badgeColor: 'var(--badge-consultation)',
      path: '/consultations',
      isOnline: false,
    },
    {
      key: 'history',
      title: shortcuts.historyTitle,
      subtitle: shortcuts.historySubtitle,
      icon: Calendar,
      badgeColor: 'var(--primary)',
      path: '/dashboard',
      isOnline: false,
    },
  ]

  return (
    <section className="shortcuts-section">
      <h2 className="shortcuts-section__title">{activities}</h2>
      <div className="shortcuts-grid">
        {shortcutItems.map((shortcut) => {
          let handleClick = undefined;
          if (shortcut.key === 'chat') handleClick = onChatClick;
          else if (shortcut.key === 'consultation') handleClick = onConsultationClick;
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
