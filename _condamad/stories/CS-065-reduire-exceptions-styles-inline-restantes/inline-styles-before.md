<!-- Inventaire before des styles inline pour CS-065. -->

# Inline Styles Before

Commande:

```powershell
Push-Location frontend
rg -n "style=\{" src -g "*.tsx"
Pop-Location
```

Resultat:

```text
frontend\src\layouts\TwoColumnLayout.tsx:22:      style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}
frontend\src\components\DomainRankingCard.tsx:48:                  style={{ width: `${Math.min(domain.score_10 * 10, 100)}%` }}
frontend\src\components\ui\Badge\Badge.tsx:31:      style={{ background: color }}
frontend\src\components\ui\Skeleton\Skeleton.tsx:26:      style={style}
frontend\src\components\ui\Skeleton\Skeleton.tsx:53:      style={groupStyle}
frontend\src\components\prediction\DayTimelineSectionV4.tsx:139:                style={{ ['--period-accent' as string]: accentColor }}
```

Classification:

| File | Surface | Classification | Decision |
|---|---|---|---|
| `frontend/src/layouts/TwoColumnLayout.tsx` | `--sidebar-width` | pont custom-property runtime | keep |
| `frontend/src/components/DomainRankingCard.tsx` | `width` dynamique | geometrie runtime | keep |
| `frontend/src/components/prediction/DayTimelineSectionV4.tsx` | `--period-accent` | pont custom-property runtime | keep |
| `frontend/src/components/ui/Badge/Badge.tsx` | `background` | couleur finie tokenisable | migrate |
| `frontend/src/components/ui/Skeleton/Skeleton.tsx` | `style` width/height | dimensions runtime du skeleton | keep |
| `frontend/src/components/ui/Skeleton/Skeleton.tsx` | `--skeleton-gap` | pont custom-property runtime | keep |
