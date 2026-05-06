# Implementation Plan - CS-081

## Findings

- Les valeurs visuelles chat etaient dispersees entre `ChatPage.css` et six CSS
  de composants.
- Les roles existants couvrent une partie de la typographie mais pas les
  compositions chat glass, message, scrollbar et elevations.
- Le registre de tokens accepte les extensions semantiques documentees.

## Approach

1. Declarer `--chat-*` dans `.chat-page-container`, owner naturel du cluster.
2. Remplacer les literals repetables dans les composants par `var(--chat-*)`,
   `var(--type-*)`, `var(--radius-*)`, `var(--premium-*)` ou tokens globaux.
3. Documenter le namespace `--chat-*` dans `token-namespace-registry.md`.
4. Ajouter une garde Vitest qui ignore le bloc owner et interdit les valeurs
   migrees hors owner.
5. Capturer les artefacts before/after et validations.

## Tests

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
- `npm run lint`
- `npm run build`
- Scans cibles dans `frontend/`.

## Rollback

Revenir les CSS du cluster chat, la ligne `--chat-*` du registre et la garde
CS-081, puis supprimer les artefacts generated de cette story.
