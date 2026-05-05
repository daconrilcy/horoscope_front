<!-- Preuve after des valeurs hardcodees du cluster CS-050. -->

# CS-050 Hardcoded Values After

Cluster: prediction components.

Files:

- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/CategoryGrid.css`

| Item | Decision finale | Proof |
|---|---|---|
| Fallbacks `var(--space-*, literal)` | remplaces par tokens directs | allowlist synchronisee |
| Typographie recurrente | migree vers `--font-*`, `--type-*`, `--line-height-*` | scan final |
| Spacing clairs | migres vers `--space-*` | scan final |
| Radius `0.75rem` / `1rem` | keep-classified | pas de token exact, convergence near-equivalent refusee |
| Shadow tone `4px 4px 12px rgba(...)` | keep-classified | pas de token equivalent, `--shadow-card` juge trop different en revue |
| Font sizes `0.8rem`, `0.9rem`, `1.75rem` | keep-classified | pas de token exact, pas de creation pour valeur unique |
| Couleurs rgba contextuelles | keep-classified | etats calibration/astro locaux, pas de token unique cree |
| Couleur astro tone | migree vers `color-mix(... var(--color-primary) ...)` | pas de dependance au namespace admin |

Total before: 31 declarations candidates dans le cluster. Total after: 10 declarations candidates, toutes classees.
