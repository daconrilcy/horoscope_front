<!-- Inventaire before des valeurs hardcodees du cluster badge pour CS-066. -->

# Hardcoded Values Before

Cluster: `ui Badge`.

Valeurs ciblees:

| File | Value | Usage | Decision |
|---|---|---|---|
| `frontend/src/components/ui/Badge/Badge.tsx` | `style={{ background: color }}` | couleur badge runtime | migrer vers classes tokenisees |
| `frontend/src/components/ui/Badge/Badge.css` | `rgba(255, 255, 255, 0.55)` | bordure glass locale | remplacer par `--color-glass-border` |
| `frontend/src/components/ui/Badge/Badge.css` | `0 10px 18px rgba(20, 20, 40, 0.1)` | ombre locale | remplacer par `--shadow-card` |

Valeurs conservees:

| File | Value | Reason |
|---|---|---|
| `frontend/src/components/ui/Badge/Badge.css` | `36px`, `40px`, `44px` | tailles propres aux variantes badge, hors sous-lot de tokenisation |
| `frontend/src/components/ui/Badge/Badge.css` | `18px`, `20px` | tailles SVG associees aux variantes, hors sous-lot |
