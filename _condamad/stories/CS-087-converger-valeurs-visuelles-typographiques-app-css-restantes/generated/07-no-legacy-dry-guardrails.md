<!-- Garde No Legacy / DRY pour CS-087. -->

# CS-087 No Legacy / DRY Guardrails

## Checks

- Aucun fichier React, route, store, API ou backend modifie.
- Aucun fallback CSS literal `var(--token, value)` dans `App.css`.
- Aucun namespace nouveau hors `--app-*`; le namespace existant est documente.
- Aucune allowlist CSS, inline-style ou legacy-style elargie.
- Les selecteurs d'etat image de remplacement existants restent classes comme UI nominale, pas comme compatibilite.

## Evidence

- `design-system-guards.test.ts` parse les declarations CSS actives.
- `hardcoded-values-after.md` documente les decisions finales.
- `regression-guardrails.md` contient `RG-061`.
