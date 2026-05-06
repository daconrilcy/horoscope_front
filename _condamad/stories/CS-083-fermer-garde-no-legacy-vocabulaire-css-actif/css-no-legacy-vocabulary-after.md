<!-- Audit after du vocabulaire CSS actif. -->

# CS-083 CSS No Legacy Vocabulary After

Scope: commentaires CSS actifs sous `frontend/src/**/*.css`.

## Decisions finales

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| Admin Prompts route comment | CSS comment | dead | none | `Route d'investigation hors catalogue` | replace-comment | `npm run test -- design-system legacy-style` | none |
| AstroMoodBackground dynamic comment | CSS comment | dead | none | `Fond dynamique de secours via variables de theme` | replace-comment | `npm run test -- design-system legacy-style` | none |

## Guard executable

- `frontend/src/tests/legacy-style-policy.test.ts` collecte les commentaires CSS via `extractCssComments`.
- La garde echoue si un commentaire CSS actif contient les vocabulaires interdits non classes.

## Scans apres implementation

- `npm run test -- design-system legacy-style` - PASS.
- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke AdminPromptsPage` - PASS.
- `rg -n --glob "*.css" "--default_dropshadow|migration-only|compatibility|legacy|alias" src` - PASS pour les vocabulaires cibles; les hits `fallback` restants sont des selectors runtime hors commentaire.
