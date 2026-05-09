<!-- Carte des fichiers cibles inspectes pour CS-125. -->

# CS-125 Target Files

## Primary Files

- `frontend/src/App.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`

## Conditional Consumer Files

Exact consumers returned by:

```powershell
Push-Location frontend
rg -n "app-(page|section|stack|grid|card|panel|state|badge|avatar|modal|actions|list)|precision-badge|evidence-pill|evidence-tags" src -g "*.tsx"
Pop-Location
```

## Evidence Files

- `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-before.md`
- `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/app-prefix-taxonomy-after.md`
- `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/generated/10-final-evidence.md`
