# Primitives App CSS apres CS-121

## Primitives creees

- Layout: `.app-page`, `.app-section`, `.app-stack`, `.app-grid`.
- Contenu: `.app-panel`, `.app-card`.
- Listes et etats: `.app-list`, `.app-state` et variantes `loading`, `empty`, `success`, `error`, `warning`.
- Actions et objets: `.app-actions`, `.app-action--danger`, `.app-badge`, `.app-pill`, `.app-avatar`, `.app-overlay`, `.app-modal`.

## Registres

- `frontend/src/styles/token-namespace-registry.md` classe `--app-*` comme extension semantique App generique.
- `frontend/src/styles/typography-roles.md` documente l'usage App des roles typographiques.
- `frontend/src/tests/design-system-allowlist.ts` garde `APP_CSS_SPECIFICITY_EXCEPTIONS` vide.

## Garde

- `frontend/src/tests/design-system-guards.test.ts` bloque les noms App page-specific non allowlistes.

