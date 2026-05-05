<!-- Inventaire initial des styles inline actifs du lot CS-045. -->

# CS-045 Inline Styles Before

Commande:

```powershell
Push-Location frontend
rg -n "style=" src -g "*.tsx"
Pop-Location
```

## Resultat

```text
frontend/src/layouts/TwoColumnLayout.tsx:22: style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}
frontend/src/features/chat/components/AstrologerPickerModal.tsx:96: style={{ display: astrologer.avatar_url ? "none" : "flex" }}
frontend/src/components/DomainRankingCard.tsx:48: style={{ width: `${Math.min(domain.score_10 * 10, 100)}%` }}
frontend/src/components/prediction/TimelineRail.tsx:29: style={{ width: thumbPct !== null ? `${thumbPct}%` : '0%' }}
frontend/src/components/prediction/TimelineRail.tsx:33: style={{ left: `${pct}%` }}
frontend/src/components/prediction/TimelineRail.tsx:37: style={{ left: `${thumbPct}%` }}
frontend/src/components/prediction/DayTimelineSectionV4.tsx:139: style={{ ['--period-accent' as string]: accentColor }}
frontend/src/components/prediction/DayTimelineSectionV4.tsx:142: style={{ backgroundColor: accentColor }}
frontend/src/components/prediction/DayPredictionCard.tsx:118: style={isAstro ? undefined : { backgroundColor: toneColor }}
frontend/src/components/prediction/CategoryGrid.tsx:38: style={{ color: band.colorVar }}
frontend/src/components/prediction/CategoryGrid.tsx:44: style={{ color: band.colorVar }}
frontend/src/components/TurningPointCard.tsx:29: style={{ background: badge.color }}
frontend/src/components/TurningPointCard.tsx:33: style={{ color: badge.color, background: badge.bg }}
frontend/src/components/ui/Badge/Badge.tsx:31: style={{ background: color }}
frontend/src/components/ui/Skeleton/Skeleton.tsx:26: style={style}
frontend/src/components/ui/Skeleton/Skeleton.tsx:53: style={groupStyle}
```

## Classification initiale

- `dynamic-custom-property`: `TwoColumnLayout.tsx`, `DayTimelineSectionV4.tsx`.
- `runtime-geometry`: `DomainRankingCard.tsx`, `TimelineRail.tsx`.
- `runtime-color`: `CategoryGrid.tsx`, `DayTimelineSectionV4.tsx`, `DayPredictionCard.tsx`, `TurningPointCard.tsx`, `Badge.tsx`.
- `runtime-visibility`: `AstrologerPickerModal.tsx`.
- `style-prop-bridge`: `Skeleton.tsx`.

Aucune occurrence `static` n'a ete identifiee dans le lot actif.
