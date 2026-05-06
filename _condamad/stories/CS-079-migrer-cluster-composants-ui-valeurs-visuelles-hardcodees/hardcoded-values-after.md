<!-- Preuves finales de migration des valeurs visuelles du cluster UI partage. -->

# CS-079 - Evidence after

## Decisions finales

| Fichier | Ancienne valeur | Nouvelle surface | Decision |
|---|---|---|---|
| `Badge/Badge.css` | `16px` | `--radius-shortcut-badge` | `registered-semantic-owner` |
| `Badge/Badge.tsx` | `var(--primary)` | `var(--color-primary)` | `migrated` |
| `Button/Button.css` | `rgba(255, 255, 255, 0.05)` | `--color-interactive-ghost-hover` | `registered-semantic-owner` |
| `Button/Button.css` | `50%` | `--radius-full` | `migrated` |
| `ErrorState/ErrorState.css` | `rgba(239, 68, 68, 0.1)` | `--color-error-surface` | `registered-semantic-owner` |
| `ErrorState/ErrorState.css` | `var(--error)` | `--color-error` | `migrated` |
| `ErrorState/ErrorState.css` | `1.25rem`, `0.875rem`, `600`, `1.6` | `--font-size-xl`, `--font-size-sm`, `--font-weight-semibold`, `--line-height-relaxed` | `migrated` |
| `LockedSection/LockedSection.css` | `var(--glass-2)`, `var(--glass)`, `var(--glass-border)`, `var(--text-1)` | `--color-glass-bg-2`, `--color-glass-bg`, `--color-glass-border`, `--color-text-primary` | `migrated` |
| `Modal/Modal.css` | `rgba(0, 0, 0, 0.5)` | `--color-overlay-modal` | `registered-semantic-owner` |
| `Skeleton/Skeleton.css` | `2s`, `ease-in-out`, `0.25em` | `--duration-skeleton-sheen`, `--easing-skeleton-sheen`, `--space-skeleton-text-gap` | `registered-semantic-owner` |
| `Skeleton/Skeleton.tsx` | `var(--space-2, 0.5rem)` | `var(--space-2)` | `migrated` |
| `UpgradeCTA/UpgradeCTA.css` | `#ffffff` | `--color-text-on-astro` | `migrated` |
| `UpgradeCTA/UpgradeCTA.css` | `0 10px 20px rgba(134, 108, 208, 0.3)` | `--shadow-cta-hover` | `registered-semantic-owner` |
| `UserAvatar/UserAvatar.css` | `50%`, `#fff`, literal typography | canonical radius/color/type tokens | `migrated` |
| `UserMenu/UserMenu.css` | `var(--glass)`, `var(--glass-blur)`, `var(--glass-border)`, `var(--text-1)`, `var(--text-2)`, `var(--glass-2)` | `--color-glass-bg`, `--surface-glass-blur`, `--color-glass-border`, `--color-text-primary`, `--color-text-secondary`, `--color-glass-bg-2` | `migrated` |
| `UserMenu/UserMenu.css` | `0.04em`, `box-shadow: none` | `--type-ui-role-letter-spacing`, `--shadow-none` | `registered-semantic-owner` |
| `Select/Select.css` | `0.05em` | `--type-ui-group-letter-spacing` | `registered-semantic-owner` |

Les namespaces ajoutes restent dans les familles canoniques deja enregistrees:
`--color-*`, `--type-*`, `--space-*`, `--radius-*`, `--shadow-*`,
`--duration-*` et `--easing-*`. Aucun namespace interdit de compatibilite ou
de migration n'a ete cree.

## Scans anti-retour

```powershell
Push-Location frontend
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(|var\(\s*--[a-zA-Z0-9_-]+\s*,|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/components/ui -g "*.css" -g "*.tsx"
rg -n "#(?:fff|ffffff)\b|rgba\(239,\s*68,\s*68,\s*0\.1\)|rgba\(255,\s*255,\s*255,\s*0\.05\)|rgba\(0,\s*0,\s*0,\s*0\.5\)|box-shadow:\s*(?:none|0\s+10px\s+20px\s+rgba\(134,\s*108,\s*208,\s*0\.3\))|border-radius:\s*(?:50%|16px);|font-size:\s*(?:0\.75rem|0\.875rem|1\.25rem);|font-weight:\s*600;|line-height:\s*(?:1|1\.6);|letter-spacing:\s*(?:0\.04em|0\.05em);|var\(--(?:primary|text-[12]|glass(?:-2|-border|-blur)?|error)\)|var\(\s*--space-2\s*,\s*0\.5rem\s*\)" src/components/ui -g "*.css" -g "*.tsx"
Pop-Location
```

Resultat: zero hit pour les literals migres et les termes No Legacy dans le
cluster UI.

## Guards executables

- `frontend/src/tests/design-system-guards.test.ts` contient le guard
  `bloque le retour des literals composants UI migres par CS-079`.
- La commande combinee de guards frontend demandee par la story passe sur 128
  tests.
- `npm run lint` passe.

## Decisions one-off finales

Les dimensions structurelles de composants (`32px`, `40px`, `48px`, `56px`,
largeurs de menu/modale et tailles d'icones) restent des contrats de layout
one-off finals. Elles ne sont pas classees comme dette ancienne et ne creent pas
de fallback.
