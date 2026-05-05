// Allowlists exactes des exceptions design-system verifiees par Vitest.

export type InlineStyleException = { file: string; style: string }
export type CssFallbackException = { file: string; token: string; literal: string }

export const INLINE_STYLE_EXCEPTIONS: InlineStyleException[] = [
  {
    "file": "components/DomainRankingCard.tsx",
    "style": "style={{ width: `${Math.min(domain.score_10 * 10, 100)}"
  },
  {
    "file": "components/prediction/CategoryGrid.tsx",
    "style": "style={{ color: band.colorVar }"
  },
  {
    "file": "components/prediction/CategoryGrid.tsx",
    "style": "style={{ color: band.colorVar }"
  },
  {
    "file": "components/prediction/DayPredictionCard.tsx",
    "style": "style={isAstro ? undefined : { backgroundColor: toneColor }"
  },
  {
    "file": "components/prediction/DayTimelineSectionV4.tsx",
    "style": "style={{ ['--period-accent' as string]: accentColor }"
  },
  {
    "file": "components/prediction/DayTimelineSectionV4.tsx",
    "style": "style={{ backgroundColor: accentColor }"
  },
  {
    "file": "components/prediction/TimelineRail.tsx",
    "style": "style={{ width: thumbPct !== null ? `${thumbPct}"
  },
  {
    "file": "components/prediction/TimelineRail.tsx",
    "style": "style={{ left: `${pct}"
  },
  {
    "file": "components/prediction/TimelineRail.tsx",
    "style": "style={{ left: `${thumbPct}"
  },
  {
    "file": "components/TurningPointCard.tsx",
    "style": "style={{ background: badge.color }"
  },
  {
    "file": "components/TurningPointCard.tsx",
    "style": "style={{ color: badge.color, background: badge.bg }"
  },
  {
    "file": "components/ui/Badge/Badge.tsx",
    "style": "style={{ background: color }"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.tsx",
    "style": "style={style}"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.tsx",
    "style": "style={groupStyle}"
  },
  {
    "file": "layouts/TwoColumnLayout.tsx",
    "style": "style={{ '--sidebar-width': sidebarWidth }"
  }
] as const

export const CSS_FALLBACK_EXCEPTIONS: CssFallbackException[] = [
  {
    "file": "App.css",
    "token": "--usage-progress",
    "literal": "0"
  },
  {
    "file": "components/NatalInterpretation.css",
    "token": "--premium-glass-border-soft",
    "literal": "rgba(255, 255, 255, 0.2"
  },
  {
    "file": "components/NatalInterpretation.css",
    "token": "--premium-radius-pill",
    "literal": "999px"
  },
  {
    "file": "components/NatalInterpretation.css",
    "token": "--premium-radius-pill",
    "literal": "999px"
  },
  {
    "file": "components/NatalInterpretation.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/NatalInterpretation.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/NatalInterpretation.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/prediction/KeyPointCard.css",
    "token": "--shadow-hero-card",
    "literal": "0 4px 20px rgba(44, 28, 100, 0.15"
  },
  {
    "file": "components/prediction/KeyPointCard.css",
    "token": "--color-hero-ink",
    "literal": "var(--color-text-primary"
  },
  {
    "file": "components/prediction/KeyPointCard.css",
    "token": "--color-hero-ink-accent",
    "literal": "var(--color-primary"
  },
  {
    "file": "components/prediction/PeriodCard.css",
    "token": "--color-text-muted",
    "literal": "rgba(30, 27, 46, 0.45"
  },
  {
    "file": "components/prediction/PeriodCard.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/prediction/PeriodCard.css",
    "token": "--color-text-muted",
    "literal": "rgba(30, 27, 46, 0.55"
  },
  {
    "file": "components/prediction/PeriodCard.css",
    "token": "--color-text-secondary",
    "literal": "rgba(30, 27, 46, 0.72"
  },
  {
    "file": "components/prediction/PeriodCard.css",
    "token": "--color-text-muted",
    "literal": "rgba(30, 27, 46, 0.35"
  },
  {
    "file": "components/prediction/PeriodCard.css",
    "token": "--color-text-muted",
    "literal": "rgba(30, 27, 46, 0.5"
  },
  {
    "file": "components/SignUpForm.css",
    "token": "--danger",
    "literal": "#ff6b81"
  },
  {
    "file": "features/chat/components/ChatWindow.css",
    "token": "--premium-radius-pill",
    "literal": "999px"
  },
  {
    "file": "pages/admin/AdminEntitlementsPage.css",
    "token": "--glass-heavy",
    "literal": "#1a1a1a"
  },
  {
    "file": "pages/landing/sections/TestimonialsSection.css",
    "token": "--success",
    "literal": "#2ecc71"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-meta",
    "literal": "var(--text-faint"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-strong",
    "literal": "var(--text-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-border-strong",
    "literal": "rgba(255, 255, 255, 0.58"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-accent-purple-strong",
    "literal": "var(--primary-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-muted",
    "literal": "var(--text-muted"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-surface-1",
    "literal": "rgba(255, 255, 255, 0.45"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-border",
    "literal": "rgba(255, 255, 255, 0.5"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-radius-card",
    "literal": "24px"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-shadow-card",
    "literal": "0 10px 30px rgba(0,0,0,0.05"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-shadow-focus",
    "literal": "0 15px 45px rgba(0,0,0,0.08"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-strong",
    "literal": "var(--text-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-meta",
    "literal": "var(--text-faint"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-accent-purple-strong",
    "literal": "var(--primary-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-border-soft",
    "literal": "rgba(255, 255, 255, 0.2"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-strong",
    "literal": "var(--text-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-accent-purple-strong",
    "literal": "var(--primary-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-meta",
    "literal": "var(--text-faint"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-surface-2",
    "literal": "rgba(255, 255, 255, 0.35"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-border-soft",
    "literal": "rgba(255, 255, 255, 0.3"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-radius-card",
    "literal": "24px"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-surface-1",
    "literal": "rgba(255, 255, 255, 0.45"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-shadow-focus",
    "literal": "0 15px 45px rgba(0,0,0,0.08"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-accent-purple-strong",
    "literal": "var(--primary-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-strong",
    "literal": "var(--text-strong"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-main",
    "literal": "var(--text-main"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-meta",
    "literal": "var(--text-faint"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-text-strong",
    "literal": "var(--text-strong"
  },
  {
    "file": "pages/settings/Settings.css",
    "token": "--usage-progress",
    "literal": "0"
  }
] as const
