# CS-041 inline styles after

## Result

- Remaining style={ occurrences: 16.
- Remaining entries are runtime-dependent: width/left geometry, runtime colors, custom properties, skeleton public style bridge, avatar display bridge.
- Static migrated occurrences now live in CSS classes in adjacent or existing stylesheets.

## Current scan

`	ext
frontend/src\layouts\TwoColumnLayout.tsx:22:      style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}
frontend/src\components\DomainRankingCard.tsx:48:                  style={{ width: `${Math.min(domain.score_10 * 10, 100)}%` }}
frontend/src\features\chat\components\AstrologerPickerModal.tsx:96:                  style={{ display: astrologer.avatar_url ? "none" : "flex" }}
frontend/src\components\TurningPointCard.tsx:29:      <div className="turning-point-card__rail" style={{ background: badge.color }} />
frontend/src\components\TurningPointCard.tsx:33:          <span className="turning-point-card__type" style={{ color: badge.color, background: badge.bg }}>
frontend/src\components\prediction\CategoryGrid.tsx:38:              style={{ color: band.colorVar }}
frontend/src\components\prediction\CategoryGrid.tsx:44:              style={{ color: band.colorVar }}
frontend/src\components\prediction\DayPredictionCard.tsx:118:          style={isAstro ? undefined : { backgroundColor: toneColor }}
frontend/src\components\prediction\DayTimelineSectionV4.tsx:139:                style={{ ['--period-accent' as string]: accentColor }}
frontend/src\components\prediction\DayTimelineSectionV4.tsx:142:                <div className="day-timeline-v4__dot" style={{ backgroundColor: accentColor }} />
frontend/src\components\prediction\TimelineRail.tsx:29:          style={{ width: thumbPct !== null ? `${thumbPct}%` : '0%' }}
frontend/src\components\prediction\TimelineRail.tsx:33:          <div key={pct} className="timeline-rail__tick" style={{ left: `${pct}%` }} />
frontend/src\components\prediction\TimelineRail.tsx:37:          <div className="timeline-rail__thumb" style={{ left: `${thumbPct}%` }} />
frontend/src\components\ui\Badge\Badge.tsx:31:      style={{ background: color }}
frontend/src\components\ui\Skeleton\Skeleton.tsx:26:      style={style}
frontend/src\components\ui\Skeleton\Skeleton.tsx:53:      style={groupStyle}
`

## Guard evidence

- 
pm run test -- inline-style design-system: covered by combined target run and PASS.
