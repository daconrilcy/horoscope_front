// Allowlists exactes des exceptions design-system verifiees par Vitest.

export type InlineStyleException = { file: string; style: string }
export type CssFallbackException = { file: string; token: string; literal: string }

export const INLINE_STYLE_EXCEPTIONS: InlineStyleException[] = [
  {
    "file": "components/DomainRankingCard.tsx",
    "style": "style={{ width: `${Math.min(domain.score_10 * 10, 100)}"
  },
  {
    "file": "components/prediction/DayTimelineSectionV4.tsx",
    "style": "style={{ ['--period-accent' as string]: accentColor }"
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
    "token": "--premium-text-muted",
    "literal": "var(--text-muted"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-border-soft",
    "literal": "rgba(255, 255, 255, 0.2"
  },
  {
    "file": "pages/NatalChartPage.css",
    "token": "--premium-glass-border-soft",
    "literal": "rgba(255, 255, 255, 0.3"
  },
  {
    "file": "pages/settings/Settings.css",
    "token": "--usage-progress",
    "literal": "0"
  }
] as const
