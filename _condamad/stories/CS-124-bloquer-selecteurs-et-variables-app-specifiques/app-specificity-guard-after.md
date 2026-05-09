# Garde specificite App apres CS-124

## Etat final

- `APP_CSS_SPECIFICITY_EXCEPTIONS` est vide.
- `design-system-guards.test.ts` echoue si une classe ou variable `--app-*` de `App.css` contient un domaine audite non allowliste.
- `rg -n "(astrologer|consultation|dashboard|settings|wizard)" src/App.css` depuis `frontend`: zero hit.
- `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css` depuis `frontend`: zero hit.

## Guardrail durable

- Ajout de `RG-075` dans `_condamad/stories/regression-guardrails.md`.

