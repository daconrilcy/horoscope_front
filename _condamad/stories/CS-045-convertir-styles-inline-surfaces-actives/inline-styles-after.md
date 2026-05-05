<!-- Inventaire final des styles inline actifs du lot CS-045. -->

# CS-045 Inline Styles After

Commande:

```powershell
Push-Location frontend
rg -n "style=" src -g "*.tsx"
Pop-Location
```

## Resultat

Les 16 occurrences restantes sont identiques au baseline et sont toutes des exceptions runtime synchronisees dans:

- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`

## Decisions finales

- `static`: 0 occurrence, donc aucune migration CSS necessaire.
- `dynamic-custom-property`: conserve et allowliste.
- `runtime-geometry`: conserve et allowliste.
- `runtime-color`: conserve et allowliste.
- `runtime-visibility`: conserve et allowliste.
- `style-prop-bridge`: conserve et allowliste pour le composant UI `Skeleton`.

Zero `unclassified`, `TODO` ou `TBD`.
