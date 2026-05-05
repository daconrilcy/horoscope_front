<!-- Garde No Legacy / DRY CS-047. -->

# CS-047 No Legacy / DRY Guardrails

Forbidden: restaurer `18px`, `12px`, `font-weight: 500` comme contrat nominal; supprimer les checks d'opacite.

Canonical owner: `design-tokens.css` pour `--font-size-lg`, `--font-size-xs`, `--font-weight-medium`.

Evidence: scans negative + `visual-smoke` PASS.

