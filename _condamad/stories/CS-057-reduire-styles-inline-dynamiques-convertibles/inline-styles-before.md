# Inline styles before CS-057

Scan command: `rg -n "style=\\{" src -g "*.tsx"` from `frontend`.

Initial executable allowlist count: 14 entries.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `CategoryGrid.tsx` `color: band.colorVar` x2 | inline-style | dead | score and band label | band key modifier classes in `CategoryGrid.css` | delete | finite `band.key` values | low |
| `DayPredictionCard.tsx` `backgroundColor: toneColor` | inline-style | dead | tone pill | tone modifier classes in `DayPredictionCard.css` | delete | finite tone values from `getToneLabel`/legacy tones | low |
| `TurningPointCard.tsx` badge rail/type styles x2 | inline-style | dead | turning point rail and badge | change-type modifier classes in `TurningPointCard.css` | delete | finite public change types with default class | low |
| `Skeleton.tsx` `style` and `--skeleton-gap` | inline-style | canonical-active | public primitive sizing/gap | public pass-through/custom property bridge | keep | story preserves `Skeleton.style` contract | low |
| `TimelineRail.tsx` width/left | inline-style | canonical-active | runtime geometry | runtime geometry | keep | values are percentages computed at runtime | low |
| `TwoColumnLayout.tsx` `--sidebar-width` | inline-style | canonical-active | runtime layout width | custom property bridge | keep | dynamic layout prop | low |
| `DayTimelineSectionV4.tsx` `--period-accent` | inline-style | canonical-active | runtime accent | custom property bridge | keep | per-period runtime color | low |
| `DomainRankingCard.tsx` width | inline-style | canonical-active | runtime score width | runtime geometry | keep | score-derived percentage | low |
| `Badge.tsx` background | inline-style | canonical-active | public color prop | public primitive color bridge | keep | public generic UI prop | low |
