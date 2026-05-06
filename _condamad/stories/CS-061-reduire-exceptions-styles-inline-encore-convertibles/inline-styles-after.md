# CS-061 - Inline styles after

After capture apres migration.

Remaining scan:

```text
src/layouts/TwoColumnLayout.tsx: style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}
src/components/DomainRankingCard.tsx: style={{ width: `${Math.min(domain.score_10 * 10, 100)}%` }}
src/components/prediction/DayTimelineSectionV4.tsx: style={{ ['--period-accent' as string]: accentColor }}
src/components/ui/Badge/Badge.tsx: style={{ background: color }}
src/components/ui/Skeleton/Skeleton.tsx: style={style}
src/components/ui/Skeleton/Skeleton.tsx: style={groupStyle}
```

Count after: 6 inline style attributes.

Decisions:
- `TimelineRail` fixed positions moved to deterministic CSS classes in `TimelineRail.css`.
- Remaining entries are runtime geometry, custom-property bridges, color bridge, or public pass-through contracts.
- `Skeleton.style` preserved.

Registry sync:
- `frontend/src/tests/design-system-allowlist.ts` removed the three `TimelineRail` entries.
- `frontend/src/tests/inline-style-allowlist.ts` removed `TimelineRail` width/left dynamic entries.
