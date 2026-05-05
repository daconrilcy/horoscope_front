# CS-037 - Inventaire avant

Lot selectionne: `frontend/src/components/prediction/DayTimeline.css`.

Commande source:

```powershell
rg -n "(2rem|1rem|0\.75rem|0\.5rem|0\.875rem|white|font-weight:\s*(bold|500))" frontend/src/components/prediction/DayTimeline.css
```

Occurrences candidates avant migration:

| Categorie | Compte | Exemples |
|---|---:|---|
| spacing | 6 | `2rem`, `1rem`, `0.75rem`, `0.5rem`, `0.25rem` |
| typography | 4 | `0.875rem`, `1rem`, `font-weight: bold`, `font-weight: 500` |
| color | 1 | `white` |

Classification: toutes les valeurs ci-dessus sont statiques et remplacables par les tokens existants `--space-*`, `--font-size-*`, `--font-weight-*` et `--color-text-on-astro`.
