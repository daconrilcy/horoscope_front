import { Calendar, Sparkles } from 'lucide-react'
import { ShortcutCard } from './ShortcutCard'
import type { BadgeColorValue } from './ui'
import { useAstrologyLabels } from '../i18n/astrology'
import { translateDashboardPage } from '../i18n/dashboard'

export interface ShortcutsSectionProps {
  onNatalClick?: () => void
  onHistoryClick?: () => void
}

export function ShortcutsSection({ onNatalClick, onHistoryClick }: ShortcutsSectionProps) {
  const { lang } = useAstrologyLabels()
  const { activities, shortcuts } = translateDashboardPage(lang)
  const shortcutItems = [
    {
      key: 'natal',
      title: shortcuts.natalTitle,
      subtitle: shortcuts.natalSubtitle,
      icon: Sparkles,
      badgeColor: 'var(--color-primary)',
      path: '/natal',
      isOnline: true,
    },
    {
      key: 'history',
      title: shortcuts.historyTitle,
      subtitle: shortcuts.historySubtitle,
      icon: Calendar,
      badgeColor: 'var(--color-primary)',
      path: '/dashboard',
      isOnline: false,
    },
  ] satisfies Array<{
    key: 'natal' | 'history'
    title: string
    subtitle: string
    icon: typeof Sparkles
    badgeColor: BadgeColorValue
    path: string
    isOnline: boolean
  }>

  return (
    <section className="shortcuts-section">
      <div className="summary-section-header shortcuts-section__header">
        <h3 className="summary-section-title shortcuts-section__title">{activities}</h3>
      </div>
      <div className="shortcuts-grid">
        {shortcutItems.map((shortcut) => {
          let handleClick = undefined;
          if (shortcut.key === 'natal') handleClick = onNatalClick;
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
