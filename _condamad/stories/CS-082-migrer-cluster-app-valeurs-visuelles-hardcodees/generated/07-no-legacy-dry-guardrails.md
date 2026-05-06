<!-- Garde DRY et No Legacy CS-082. -->

# No Legacy / DRY Guardrails

Applicable guardrails: RG-044, RG-045, RG-046, RG-047, RG-048, RG-049, RG-050,
RG-059.

Decisions:

- `--app-*` est le seul namespace nouveau.
- Le namespace est documente dans `token-namespace-registry.md`.
- Aucun `var(--app-*, literal)` n'est ajoute.
- Aucune allowlist n'est elargie.
- Aucun changement React, route ou API.

Static guards:

- `design-system-guards.test.ts` verifie la consommation `var(--app-*)` dans les sous-surfaces migrees.
- `theme-tokens.test.ts` verifie le registre des namespaces.
- `css-fallback-policy.test.ts` et `inline-style-policy.test.ts` restent inchanges.

