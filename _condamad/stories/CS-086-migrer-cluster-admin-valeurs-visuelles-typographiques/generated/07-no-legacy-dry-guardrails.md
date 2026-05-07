# No Legacy / DRY Guardrails

## Applicable invariants

- `RG-044` - namespaces de tokens CSS frontend documentes.
- `RG-045` - valeurs visuelles migrees sans retour non classe.
- `RG-046` - roles typographiques semantiques pour les repetitions.
- `RG-047` - aucun style inline statique.
- `RG-048` - aucun fallback CSS non classe.
- `RG-049` - aucune surface CSS legacy creee.
- `RG-050` - suite anti-drift design-system executable.
- `RG-051` - aucun token page-scoped non admin consomme par admin.
- `RG-052` - aucun namespace migration-only.
- `RG-053`, `RG-057` - aucune compatibilite runtime frontend recreee.
- `RG-054` - aucun redirect ou route admin legacy recree.
- `RG-055`, `RG-056`, `RG-058`, `RG-059` - clusters deja migres preserves.
- `RG-060` - aucun vocabulaire No Legacy actif non classe dans CSS.

## Canonical destinations

- Tokens globaux: `frontend/src/styles/design-tokens.css`.
- Extensions semantiques admin: namespace `--admin-*`, documente dans `frontend/src/styles/token-namespace-registry.md`.
- Roles typographiques: `frontend/src/styles/typography-roles.md` et tokens `--type-*`.
- Evidence de decisions finales: `hardcoded-values-after.md`.

## Forbidden patterns

- `legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only` dans les fichiers applicatifs touches.
- `fallback` comme mecanisme CSS; les occurrences metier existantes dans le graphe de prompts doivent rester classees comme vocabulaire produit, pas comme exception style.
- `var(--token, literal)` dans le cluster admin.
- `--settings-*`, `--help-*`, `--chat-*`, `--app-*`, `--landing-*` dans le cluster admin.
- Nouvel owner admin non documente.

## Required negative evidence

```powershell
rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/AdminLayout.css src/pages/admin -g "*.css"
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only|PASS with limitation|TODO" src/layouts/AdminLayout.css src/pages/admin -g "*.css"
rg -n -- "--settings-|--help-|--chat-|--app-|--landing-" src/layouts/AdminLayout.css src/pages/admin -g "*.css"
```

## Review checklist

- Un seul owner par role visuel admin.
- Aucun elargissement d'allowlist.
- Aucun changement React/API/backend.
- Les scans after distinguent owner declarations, valeurs finales et hits metier.
