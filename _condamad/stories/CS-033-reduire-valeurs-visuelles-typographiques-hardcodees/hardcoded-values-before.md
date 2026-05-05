<!-- Inventaire avant migration CS-033 des valeurs visuelles et typographiques hardcodees. -->

# CS-033 Hardcoded Values Before

Lot selectionne:

- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`

Commande:

```powershell
Push-Location frontend
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|\b[0-9]+(?:\.[0-9]+)?(?:px|rem|em)\b|font-size|font-weight|line-height|letter-spacing|border-radius|box-shadow|gap|padding|margin" src/components/ui/Select/Select.css src/components/ui/UserMenu/UserMenu.css -g "*.css"
Pop-Location
```

Resultat initial:

- `Select.css`: nombreux fallbacks litteraux dans `var(--token, value)` pour espacements, typographie, couleurs, rayons, durees et ombres.
- `UserMenu.css`: fallbacks litteraux dans `var(--token, value)`, ombre directe `0 8px 32px rgba(...)`, duree directe `0.15s`.
- Categories touchees: spacing, radius, shadow, typography, color-like, animation duration.

Decision:

- Migrer les literals equivalentes vers les tokens existants.
- Conserver uniquement les valeurs structurelles non tokenisees hors lot (`min-width: 220px`, keyframe translate, z-index/fallbacks explicitement classes par CS-035).
