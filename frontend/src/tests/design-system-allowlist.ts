// Allowlists exactes des exceptions design-system verifiees par Vitest.

export type InlineStyleException = { file: string; style: string }
export type CssFallbackException = { file: string; token: string; literal: string }

export const INLINE_STYLE_EXCEPTIONS: InlineStyleException[] = [
  {
    "file": "components/DomainRankingCard.tsx",
    "style": "style={{ width: `${Math.min(domain.score_10 * 10, 100)}"
  },
  {
    "file": "components/NatalInterpretation.tsx",
    "style": "style={{ color: 'var(--color-primary-strong)' }"
  },
  {
    "file": "components/NatalInterpretation.tsx",
    "style": "style={{ flexShrink: 0 }"
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
    "file": "components/prediction/PeriodCard.tsx",
    "style": "style={{ position: 'absolute', top: '1rem', right: '0.5rem', color: 'var(--primary)', opacity: 0.85 }"
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
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ marginBottom: \"2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ marginBottom: \"1rem\", color: \"var(--text-1)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", flexDirection: \"column\", gap: \"1rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ padding: \"1.25rem\", border: \"1px solid var(--primary)\", position: \"relative\", overflow: \"hidden\", cursor: onTurningPointClick ? \"pointer\" : \"default\", backgroundColor: \"rgba(var(--primary-rgb), 0.03)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ position: \"absolute\", top: 0, left: 0, width: \"4px\", height: \"100%\", backgroundColor: \"var(--primary)\", }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", justifyContent: \"space-between\", alignItems: \"baseline\", marginBottom: \"1rem\", }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"1.1rem\", fontWeight: \"bold\", color: \"var(--primary)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"600\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", flexDirection: \"column\", gap: \"0.75rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.7rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"bold\", display: \"block\", marginBottom: \"0.2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"1rem\", color: \"var(--text-1)\", fontWeight: \"500\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ margin: \"0.35rem 0 0 0\", fontSize: \"0.85rem\", lineHeight: \"1.4\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.7rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"bold\", display: \"block\", marginBottom: \"0.4rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", alignItems: \"center\", gap: \"0.5rem\", flexWrap: \"wrap\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", gap: \"0.2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\", color: \"var(--text-3)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", gap: \"0.2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.9rem\", color: \"var(--text-1)\", marginLeft: \"0.25rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ margin: \"0.5rem 0 0 0\", fontSize: \"0.9rem\", lineHeight: \"1.4\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.7rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"bold\", display: \"block\", marginBottom: \"0.2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ margin: 0, fontSize: \"0.95rem\", color: \"var(--text-1)\", fontWeight: \"500\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ margin: \"0.25rem 0 0 0\", fontSize: \"0.85rem\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ marginTop: \"0.4rem\", display: \"flex\", flexDirection: \"column\", gap: \"0.2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", flexDirection: \"column\", gap: \"0.1rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.85rem\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\", color: \"var(--text-3)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.7rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"bold\", display: \"block\", marginBottom: \"0.2rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ margin: 0, fontSize: \"0.95rem\", lineHeight: \"1.4\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", flexWrap: \"wrap\", gap: \"0.4rem\", alignItems: \"center\", marginTop: \"0.6rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.7rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"bold\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ margin: \"0 0 0.75rem 0\", fontSize: \"1rem\", lineHeight: \"1.5\", color: \"var(--text-1)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ marginBottom: \"0.5rem\", fontSize: \"0.85rem\", color: \"var(--text-2)\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ display: \"flex\", flexWrap: \"wrap\", gap: \"0.4rem\", alignItems: \"center\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.7rem\", color: \"var(--text-3)\", textTransform: \"uppercase\", fontWeight: \"bold\" }"
  },
  {
    "file": "components/prediction/TurningPointsList.tsx",
    "style": "style={{ fontSize: \"0.8rem\" }"
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
    "file": "components/ui/Form/Form.tsx",
    "style": "style={{ border: 'none', padding: 0, margin: 0 }"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.tsx",
    "style": "style={style}"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.tsx",
    "style": "style={{ display: 'flex', flexDirection: 'column', gap }"
  },
  {
    "file": "features/chat/components/AstrologerPickerModal.tsx",
    "style": "style={{ display: astrologer.avatar_url ? \"none\" : \"flex\" }"
  },
  {
    "file": "features/chat/components/ChatLayout.tsx",
    "style": "style={{ \"--sidebar-width\": \"320px\" }"
  },
  {
    "file": "layouts/TwoColumnLayout.tsx",
    "style": "style={{ '--sidebar-width': sidebarWidth }"
  },
  {
    "file": "pages/AstrologerProfilePage.tsx",
    "style": "style={{ background: 'var(--settings-purple)', color: '#fff' }"
  },
  {
    "file": "pages/AstrologerProfilePage.tsx",
    "style": "style={{ alignItems: 'center', flexWrap: 'wrap' }"
  },
  {
    "file": "pages/AstrologerProfilePage.tsx",
    "style": "style={{ cursor: 'pointer', border: isDefault ? '1px solid var(--settings-purple)' : '1px solid var(--settings-card-border)', background: isDefault ? 'var(--settings-purple-soft)' : 'rgba(255,255,255,0.5)', color: isDefault ? 'var(--settings-purple)' : 'inherit' }"
  },
  {
    "file": "pages/NotFoundPage.tsx",
    "style": "style={{ textAlign: 'center' }"
  },
  {
    "file": "pages/NotFoundPage.tsx",
    "style": "style={{ marginTop: 'var(--space-4)' }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ padding: \"120px 24px\", maxWidth: \"800px\", margin: \"0 auto\", color: \"var(--premium-text-main)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginBottom: \"40px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginRight: \"8px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ fontFamily: \"var(--premium-font-serif, serif)\", fontSize: \"2.5rem\", marginBottom: \"24px\", color: \"var(--premium-text-strong)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginBottom: \"24px\", lineHeight: \"1.6\", color: \"var(--premium-text-meta)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginBottom: \"40px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ fontSize: \"1.5rem\", marginBottom: \"16px\", color: \"var(--premium-text-strong)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ lineHeight: \"1.6\", marginBottom: \"16px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginBottom: \"40px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ fontSize: \"1.5rem\", marginBottom: \"16px\", color: \"var(--premium-text-strong)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ lineHeight: \"1.6\", marginBottom: \"16px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginBottom: \"40px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ fontSize: \"1.5rem\", marginBottom: \"16px\", color: \"var(--premium-text-strong)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ lineHeight: \"1.6\", marginBottom: \"16px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ marginBottom: \"40px\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ fontSize: \"1.5rem\", marginBottom: \"16px\", color: \"var(--premium-text-strong)\" }"
  },
  {
    "file": "pages/PrivacyPolicyPage.tsx",
    "style": "style={{ lineHeight: \"1.6\", marginBottom: \"16px\" }"
  },
  {
    "file": "pages/settings/AccountSettings.tsx",
    "style": "style={{ marginTop: '24px' }"
  },
  {
    "file": "pages/settings/AccountSettings.tsx",
    "style": "style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }"
  },
  {
    "file": "pages/settings/AccountSettings.tsx",
    "style": "style={{ marginTop: '4px', textDecoration: 'none', height: 'auto', minHeight: '32px' }"
  },
  {
    "file": "pages/settings/AccountSettings.tsx",
    "style": "style={{ background: 'rgba(192, 57, 43, 0.1)', color: '#c0392b', borderColor: 'rgba(192, 57, 43, 0.2)' }"
  }
] as const

export const CSS_FALLBACK_EXCEPTIONS: CssFallbackException[] = [
  {
    "file": "App.css",
    "token": "--error",
    "literal": "#ff6b6b"
  },
  {
    "file": "App.css",
    "token": "--success",
    "literal": "#4ade80"
  },
  {
    "file": "App.css",
    "token": "--success",
    "literal": "#4ade80"
  },
  {
    "file": "App.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "App.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "App.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "App.css",
    "token": "--radius-lg",
    "literal": "12px"
  },
  {
    "file": "App.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "App.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "App.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "App.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "App.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "App.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "App.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "App.css",
    "token": "--radius-lg",
    "literal": "12px"
  },
  {
    "file": "App.css",
    "token": "--duration-normal",
    "literal": "200ms"
  },
  {
    "file": "App.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "App.css",
    "token": "--radius-lg",
    "literal": "12px"
  },
  {
    "file": "App.css",
    "token": "--success",
    "literal": "#4ade80"
  },
  {
    "file": "App.css",
    "token": "--success",
    "literal": "#4ade80"
  },
  {
    "file": "App.css",
    "token": "--usage-progress",
    "literal": "0"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--radius-md",
    "literal": "0.5rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Header.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/layout/Sidebar.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/layout/Sidebar.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/layout/Sidebar.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Sidebar.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Sidebar.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/layout/Sidebar.css",
    "token": "--radius-md",
    "literal": "0.5rem"
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
    "file": "components/prediction/CategoryGrid.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/prediction/DayPredictionCard.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/prediction/DayPredictionCard.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/prediction/DayPredictionCard.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/prediction/DayPredictionCard.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/prediction/DayPredictionCard.css",
    "token": "--space-1",
    "literal": "0.25rem"
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
    "file": "components/ui/Badge/Badge.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/Badge/Badge.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--radius-full",
    "literal": "999px"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--font-weight-semibold",
    "literal": "600"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--shadow-cta",
    "literal": "0 14px 30px rgba(90, 120, 255, 0.25"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--font-size-md",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--font-size-lg",
    "literal": "1.125rem"
  },
  {
    "file": "components/ui/Button/Button.css",
    "token": "--duration-normal",
    "literal": "250ms"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--radius-lg",
    "literal": "24px"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--color-bg-surface",
    "literal": "#ffffff"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--color-bg-surface",
    "literal": "#ffffff"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--shadow-card",
    "literal": "0 18px 40px rgba(0,0,0,0.45"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--shadow-hero",
    "literal": "0 20px 50px rgba(0,0,0,0.3"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-8",
    "literal": "2rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Card/Card.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--space-12",
    "literal": "3rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--font-size-lg",
    "literal": "1.125rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--font-weight-bold",
    "literal": "700"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--font-size-md",
    "literal": "1rem"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--color-text-secondary",
    "literal": "rgba(30,27,46,0.72"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--line-height-normal",
    "literal": "1.5"
  },
  {
    "file": "components/ui/EmptyState/EmptyState.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/ErrorState/ErrorState.css",
    "token": "--space-8",
    "literal": "2rem"
  },
  {
    "file": "components/ui/ErrorState/ErrorState.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/ErrorState/ErrorState.css",
    "token": "--error",
    "literal": "#ef4444"
  },
  {
    "file": "components/ui/ErrorState/ErrorState.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/ErrorState/ErrorState.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--font-weight-medium",
    "literal": "500"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-secondary",
    "literal": "rgba(30,27,46,0.72"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--font-size-md",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--line-height-normal",
    "literal": "1.5"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-glass-bg",
    "literal": "rgba(255,255,255,0.55"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-primary",
    "literal": "#866CD0"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-primary",
    "literal": "#866CD0"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-glass-bg-2",
    "literal": "rgba(255,255,255,0.38"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-glass-mini",
    "literal": "rgba(255,255,255,0.40"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-10",
    "literal": "2.5rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-10",
    "literal": "2.5rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--font-weight-medium",
    "literal": "500"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Field/Field.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--glass-2",
    "literal": "rgba(255, 255, 255, 0.38"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--radius-full",
    "literal": "999px"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--glass",
    "literal": "rgba(255, 255, 255, 0.55"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--font-weight-medium",
    "literal": "500"
  },
  {
    "file": "components/ui/LockedSection/LockedSection.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--z-index-modal",
    "literal": "2000"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-bg-surface",
    "literal": "#ffffff"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--radius-lg",
    "literal": "24px"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--shadow-hero",
    "literal": "0 20px 50px rgba(0,0,0,0.3"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--duration-normal",
    "literal": "250ms"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--font-size-lg",
    "literal": "1.125rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--font-weight-bold",
    "literal": "700"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--radius-full",
    "literal": "999px"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-glass-bg",
    "literal": "rgba(255,255,255,0.55"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-text-secondary",
    "literal": "rgba(30,27,46,0.72"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--font-size-md",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--line-height-normal",
    "literal": "1.5"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-6",
    "literal": "1.5rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-glass-mini",
    "literal": "rgba(255,255,255,0.40"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Modal/Modal.css",
    "token": "--color-primary",
    "literal": "#866CD0"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-weight-medium",
    "literal": "500"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-secondary",
    "literal": "rgba(30,27,46,0.72"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-md",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--line-height-normal",
    "literal": "1.5"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-bg",
    "literal": "rgba(255,255,255,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-primary",
    "literal": "#866CD0"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-primary",
    "literal": "#866CD0"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-mini",
    "literal": "rgba(255,255,255,0.40"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--z-index-dropdown",
    "literal": "1000"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-bg-surface",
    "literal": "#ffffff"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--shadow-card",
    "literal": "0 18px 40px rgba(0,0,0,0.45"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-border",
    "literal": "rgba(255,255,255,0.65"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--radius-full",
    "literal": "999px"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-bg",
    "literal": "rgba(255,255,255,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-md",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--radius-sm",
    "literal": "8px"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-primary",
    "literal": "#1E1B2E"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-bg",
    "literal": "rgba(255,255,255,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-glass-shortcut",
    "literal": "rgba(255,255,255,0.08"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-primary",
    "literal": "#866CD0"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-weight-semibold",
    "literal": "600"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-xs",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-weight-bold",
    "literal": "700"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-text-muted",
    "literal": "rgba(30,27,46,0.55"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--font-weight-medium",
    "literal": "500"
  },
  {
    "file": "components/ui/Select/Select.css",
    "token": "--color-error",
    "literal": "#ff6b81"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.css",
    "token": "--color-glass-mini",
    "literal": "rgba(255, 255, 255, 0.15"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.css",
    "token": "--color-glass-bg",
    "literal": "rgba(255, 255, 255, 0.25"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.css",
    "token": "--color-glass-mini",
    "literal": "rgba(255, 255, 255, 0.15"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.css",
    "token": "--radius-sm",
    "literal": "8px"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.css",
    "token": "--radius-full",
    "literal": "999px"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--font-weight-semibold",
    "literal": "600"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--radius-md",
    "literal": "14px"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/UpgradeCTA/UpgradeCTA.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/UserAvatar/UserAvatar.css",
    "token": "--primary",
    "literal": "var(--color-primary, #7c3aed"
  },
  {
    "file": "components/ui/UserAvatar/UserAvatar.css",
    "token": "--font-weight-bold",
    "literal": "700"
  },
  {
    "file": "components/ui/UserAvatar/UserAvatar.css",
    "token": "--primary",
    "literal": "var(--color-primary, #7c3aed"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--radius-lg",
    "literal": "12px"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--space-1",
    "literal": "0.25rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--font-weight-semibold",
    "literal": "600"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--font-size-xs",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "components/ui/UserMenu/UserMenu.css",
    "token": "--primary",
    "literal": "var(--color-primary, #7c3aed"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--space-4",
    "literal": "1rem"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--font-size-xs",
    "literal": "0.75rem"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--space-2",
    "literal": "0.5rem"
  },
  {
    "file": "features/chat/components/ChatQuotaBanner.css",
    "token": "--space-3",
    "literal": "0.75rem"
  },
  {
    "file": "features/chat/components/ChatWindow.css",
    "token": "--premium-radius-pill",
    "literal": "999px"
  },
  {
    "file": "layouts/PageLayout.css",
    "token": "--layout-page-max-width",
    "literal": "900px"
  },
  {
    "file": "layouts/PageLayout.css",
    "token": "--layout-page-padding",
    "literal": "var(--space-6"
  },
  {
    "file": "layouts/TwoColumnLayout.css",
    "token": "--sidebar-width",
    "literal": "320px"
  },
  {
    "file": "layouts/WizardLayout.css",
    "token": "--radius-full",
    "literal": "999px"
  },
  {
    "file": "layouts/WizardLayout.css",
    "token": "--font-size-sm",
    "literal": "0.875rem"
  },
  {
    "file": "layouts/WizardLayout.css",
    "token": "--font-weight-semibold",
    "literal": "600"
  },
  {
    "file": "layouts/WizardLayout.css",
    "token": "--duration-fast",
    "literal": "150ms"
  },
  {
    "file": "layouts/WizardLayout.css",
    "token": "--easing-default",
    "literal": "ease"
  },
  {
    "file": "pages/admin/AdminEntitlementsPage.css",
    "token": "--glass-heavy",
    "literal": "#1a1a1a"
  },
  {
    "file": "pages/admin/AdminPromptsPage.css",
    "token": "--color-accent",
    "literal": "var(--color-primary"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--border-color",
    "literal": "#eee"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--text-secondary",
    "literal": "#666"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--bg-secondary",
    "literal": "#f9f9f9"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--bg-button-secondary",
    "literal": "#eee"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--text-button-secondary",
    "literal": "#333"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--border-color",
    "literal": "#ccc"
  },
  {
    "file": "pages/BirthProfilePage.css",
    "token": "--bg-button-secondary-hover",
    "literal": "#ddd"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-body",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-heading",
    "literal": "var(--text-1"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-muted",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-body",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-muted",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-muted",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-body",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-muted",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-body",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-muted",
    "literal": "var(--text-2"
  },
  {
    "file": "pages/HelpPage.css",
    "token": "--settings-text-body",
    "literal": "var(--text-2"
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
    "token": "--settings-purple-border",
    "literal": "rgba(134, 108, 208, 0.28"
  },
  {
    "file": "pages/settings/Settings.css",
    "token": "--settings-purple",
    "literal": "#866cd0"
  },
  {
    "file": "pages/settings/Settings.css",
    "token": "--usage-progress",
    "literal": "0"
  },
  {
    "file": "styles/glass.css",
    "token": "--surface-glass-blur",
    "literal": "14px"
  },
  {
    "file": "styles/glass.css",
    "token": "--surface-glass-blur",
    "literal": "14px"
  },
  {
    "file": "styles/utilities.css",
    "token": "--surface-glass-blur",
    "literal": "14px"
  },
  {
    "file": "styles/utilities.css",
    "token": "--surface-glass-blur",
    "literal": "14px"
  }
] as const
