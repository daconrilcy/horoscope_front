// Allowlists exactes des exceptions design-system verifiees par Vitest.

export type InlineStyleException = { file: string; style: string }
export type CssFallbackException = { file: string; token: string; literal: string }

export type AppCssAcceptedPrefix = {
  prefix: string
  owner: "frontend/src/App.css"
  source: "CS-125"
  classification: "canonical-active"
  decision: "retain-app-owned-prefix"
  proof: string
}

// Registry positive des premiers prefixes semantiques App conserves par CS-125.
export const APP_CSS_ACCEPTED_PREFIXES: readonly AppCssAcceptedPrefix[] = [
  { prefix: "account", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "account controls in App.css" },
  { prefix: "activities", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "activities page states in App.css" },
  { prefix: "activity", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "activity flow and premium cards in App.css" },
  { prefix: "admin", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "admin layout typography retained in App.css" },
  { prefix: "astro", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "astro catalog local roles in App.css" },
  { prefix: "banner", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "activity banner text roles in App.css" },
  { prefix: "bottom", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "bottom navigation primitive in App.css" },
  { prefix: "btn", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "button danger variant in App.css" },
  { prefix: "button", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "global button primitive in App.css" },
  { prefix: "card", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "card primitive in App.css" },
  { prefix: "chat", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "chat shells still styled by App.css" },
  { prefix: "checkbox", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "checkbox labels in App.css" },
  { prefix: "control", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "control panel roles in App.css" },
  { prefix: "danger", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "danger action roles in App.css" },
  { prefix: "day", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "day shell role in App.css" },
  { prefix: "degraded", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "degraded warning role in App.css" },
  { prefix: "drawing", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "drawing option cards in App.css" },
  { prefix: "error", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "error message primitive in App.css" },
  { prefix: "flow", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "consultation flow states in App.css" },
  { prefix: "form", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "form primitives in App.css" },
  { prefix: "interaction", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "interaction toggle section in App.css" },
  { prefix: "message", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "message bubble roles in App.css" },
  { prefix: "mobile", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "mobile navigation roles in App.css" },
  { prefix: "modal", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "modal primitives in App.css" },
  { prefix: "nickname", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "nickname input group in App.css" },
  { prefix: "nothing", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "empty collection notice in App.css" },
  { prefix: "other", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "other-person form roles in App.css" },
  { prefix: "panel", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "panel primitive in App.css" },
  { prefix: "people", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "people page header and error states in App.css" },
  { prefix: "person", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "person cards, picker, profile and options in App.css" },
  { prefix: "premium", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "premium page roles in App.css" },
  { prefix: "section", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "section header primitive in App.css" },
  { prefix: "shell", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "application shell roles in App.css" },
  { prefix: "skeleton", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "skeleton loading primitive in App.css" },
  { prefix: "state", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "application state primitives in App.css" },
  { prefix: "summary", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "summary details and panel roles in App.css" },
  { prefix: "type", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "type pill roles in App.css" },
  { prefix: "typing", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "typing indicator primitive in App.css" },
  { prefix: "usage", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "usage metrics and progress roles in App.css" },
  { prefix: "user", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "user data missing notice in App.css" },
  { prefix: "validation", owner: "frontend/src/App.css", source: "CS-125", classification: "canonical-active", decision: "retain-app-owned-prefix", proof: "validation summary and fields in App.css" },
] as const


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
