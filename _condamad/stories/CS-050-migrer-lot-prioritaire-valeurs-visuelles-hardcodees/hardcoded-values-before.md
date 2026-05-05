<!-- Baseline des valeurs hardcodees du cluster CS-050. -->

# CS-050 Hardcoded Values Before

Cluster: prediction components.

Files:

- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/CategoryGrid.css`

| Item | Type | Classification | Decision |
|---|---|---|---|
| `DayPredictionCard.css` spacing fallbacks `var(--space-*, literal)` | fallback tokenise | migrate | supprimer fallback literal |
| `DayPredictionCard.css` font sizes `1.125rem`, `0.9rem`, `1rem`, `0.875rem`, `1.5rem` | typographie | migrate | utiliser `--font-*` / `--type-*` |
| `DayPredictionCard.css` `font-weight: 500`, `bold` | typographie | migrate | utiliser `--font-weight-*` |
| `DayPredictionCard.css` `0.75rem`, `1rem`, radius/shadow | spacing/radius/shadow | migrate | utiliser `--space-*`, `--radius-*`, `--shadow-card` |
| `CategoryGrid.css` font sizes/weights | typographie | migrate | utiliser tokens typographiques |
| Couleurs rgba de calibration/context | produit | keep-classified | conserver, decision visuelle locale |

