<!-- Inventaire after des styles inline pour CS-065. -->

# Inline Styles After

Commande:

```powershell
Push-Location frontend
rg -n "style=\{" src -g "*.tsx"
Pop-Location
```

Resultat attendu apres migration badge:

```text
frontend\src\layouts\TwoColumnLayout.tsx:22:      style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}
frontend\src\components\DomainRankingCard.tsx:48:                  style={{ width: `${Math.min(domain.score_10 * 10, 100)}%` }}
frontend\src\components\ui\Skeleton\Skeleton.tsx:26:      style={style}
frontend\src\components\ui\Skeleton\Skeleton.tsx:53:      style={groupStyle}
frontend\src\components\prediction\DayTimelineSectionV4.tsx:139:                style={{ ['--period-accent' as string]: accentColor }}
```

Differences autorisees:

- `Badge.tsx` ne contient plus `style={{ background: color }}`.
- Les exceptions restantes sont des dimensions ou custom properties runtime conservees dans les allowlists.
