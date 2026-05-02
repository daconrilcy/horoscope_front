# Audit de suppression du validateur racine route-removal

Commandes sources:

- `rg -n "validate_route_removal_audit.py|validate_route_removal_audit" . -g '!artifacts/**' -g '!.codex-artifacts/**'`
- `rg -n "validate_route_removal_audit.py" scripts backend frontend docs`
- `rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `scripts/validate_route_removal_audit.py` | root script | dead | Historical CONDAMAD evidence only; no production, backend test, frontend, docs, or durable ops consumer | `_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md` plus historical final evidence | delete | `reference-baseline.txt` shows references limited to CONDAMAD story/audit artifacts; `rg -n "validate_route_removal_audit.py" scripts backend frontend docs` has only the root file before deletion and no consumers | The old one-off command cannot be rerun from root; historical audit evidence remains as a delivered artifact. |
