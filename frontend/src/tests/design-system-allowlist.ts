// Allowlists exactes des exceptions design-system verifiees par Vitest.

export type InlineStyleException = { file: string; style: string }
export type CssFallbackException = { file: string; token: string; literal: string }


export type AppCssSpecificityException = {
  kind: "custom-property" | "selector"
  name: string
  owner: "frontend/src/App.css"
  source: "CS-124"
  expiresAfter: "2026-06-30"
}

export const APP_CSS_SPECIFICITY_EXCEPTIONS: readonly AppCssSpecificityException[] = []

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
    "file": "components/ui/Skeleton/Skeleton.tsx",
    "style": "style={style}"
  },
  {
    "file": "components/ui/Skeleton/Skeleton.tsx",
    "style": "style={groupStyle}"
  }
] as const

export const CSS_FALLBACK_EXCEPTIONS: CssFallbackException[] = [
  {
    "file": "App.css",
    "token": "--usage-progress",
    "literal": "0"
  },
  {
    "file": "pages/settings/Settings.css",
    "token": "--usage-progress",
    "literal": "0"
  }
] as const
