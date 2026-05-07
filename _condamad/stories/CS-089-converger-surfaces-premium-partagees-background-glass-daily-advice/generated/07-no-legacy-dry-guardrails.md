<!-- Garde-fous No Legacy et DRY pour la story CS-089. -->

# No Legacy / DRY Guardrails

Regles appliquees:

- Aucun style inline ajoute.
- Aucun comportement React, API, route ou store modifie.
- Aucun fallback CSS literal ajoute.
- Aucun namespace legacy, compatibility, alias, shim ou migration-only cree.
- Les valeurs partagees sont routees vers `premium-theme.css` ou `glass.css`.
- Les fichiers Daily ne redefinissent plus les owners `--glass-*`.

Preuves attendues:

- Guard CS-089 dans `design-system-guards.test.ts`.
- `token-namespace-registry.md` classe `--glass-base-*`, `--glass-card-*`, `--glass-border*` et `--glass-surface-*`.
- Scans No Legacy zero-hit sur les quatre fichiers premium.
