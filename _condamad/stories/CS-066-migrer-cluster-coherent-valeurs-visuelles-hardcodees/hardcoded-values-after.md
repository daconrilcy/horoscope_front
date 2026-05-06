<!-- Inventaire after des valeurs hardcodees du cluster badge pour CS-066. -->

# Hardcoded Values After

Cluster: `ui Badge`.

Valeurs migrees:

| File | Before | After |
|---|---|---|
| `frontend/src/components/ui/Badge/Badge.tsx` | `style={{ background: color }}` | classe tokenisee `badge--color-*` |
| `frontend/src/components/ui/Badge/Badge.css` | `rgba(255, 255, 255, 0.55)` | `var(--color-glass-border)` |
| `frontend/src/components/ui/Badge/Badge.css` | `0 10px 18px rgba(20, 20, 40, 0.1)` | `var(--shadow-card)` |

Registres:

- Aucun nouveau namespace token.
- Aucun nouveau role typographique.
- `design-system-allowlist.ts` et `inline-style-allowlist.ts` synchronises pour retirer l'exception inline badge.
