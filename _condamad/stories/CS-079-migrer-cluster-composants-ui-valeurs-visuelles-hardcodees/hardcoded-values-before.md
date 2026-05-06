<!-- Baseline initial des valeurs visuelles hardcodees du cluster UI partage. -->

# CS-079 - Baseline before

Commande de baseline:

```powershell
Push-Location frontend
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(|font-size:|font-weight:|line-height:|letter-spacing:|box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*,|legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/components/ui -g "*.css" -g "*.tsx"
Pop-Location
```

## Cluster borne

Fichiers inspectes et inclus dans le cluster:

- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`

## Valeurs a migrer

| Fichier | Literal initial | Decision attendue |
|---|---|---|
| `Badge/Badge.css` | `border-radius: 16px` | migrer vers token de rayon dedie |
| `Badge/Badge.tsx` | `var(--primary)` | supprimer la valeur non canonique |
| `Button/Button.css` | `rgba(255, 255, 255, 0.05)` | migrer vers token d'interaction |
| `Button/Button.css` | `border-radius: 50%` | migrer vers `--radius-full` |
| `ErrorState/ErrorState.css` | `rgba(239, 68, 68, 0.1)` | migrer vers token status surface |
| `ErrorState/ErrorState.css` | `var(--error)` | migrer vers `--color-error` |
| `ErrorState/ErrorState.css` | `1.25rem`, `0.875rem`, `600`, `1.6` | migrer vers tokens typo existants |
| `LockedSection/LockedSection.css` | `var(--glass-2)`, `var(--glass)`, `var(--glass-border)`, `var(--text-1)` | migrer vers tokens globaux canoniques |
| `Modal/Modal.css` | `rgba(0, 0, 0, 0.5)` | migrer vers token overlay |
| `Skeleton/Skeleton.css` | `2s`, `ease-in-out`, `0.25em` | migrer vers tokens animation/spacing |
| `Skeleton/Skeleton.tsx` | `var(--space-2, 0.5rem)` | supprimer le fallback CSS local |
| `UpgradeCTA/UpgradeCTA.css` | `#ffffff` | migrer vers token texte sur fond astro |
| `UpgradeCTA/UpgradeCTA.css` | `0 10px 20px rgba(134, 108, 208, 0.3)` | migrer vers token shadow CTA hover |
| `UserAvatar/UserAvatar.css` | `50%`, `#fff`, `0.75rem`, `0.875rem`, `1.25rem`, `1` | migrer vers tokens radius/couleur/typo |
| `UserMenu/UserMenu.css` | `var(--glass)`, `var(--glass-blur)`, `var(--glass-border)`, `var(--text-1)`, `var(--text-2)`, `var(--glass-2)` | migrer vers tokens globaux canoniques |
| `UserMenu/UserMenu.css` | `0.04em`, `box-shadow: none` | migrer vers tokens typo/shadow |
| `Select/Select.css` | `0.05em` | migrer vers token typo UI |

## Valeurs one-off finales hors migration

Dimensions structurelles de composants (`32px`, `40px`, `48px`, `56px`,
largeurs de menu/modale, tailles d'icones) conservees comme contrats de layout
locaux, car la story cible les valeurs visuelles et typographiques repetees.
