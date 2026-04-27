# Runtime Source of Truth Contract

<!-- Contrat transverse pour prouver les regles runtime par une source observable. -->

Use this contract when the story changes API routes, HTTP behavior, runtime
registration, loaded config, generated contracts, persistence behavior, DB
schema, or architecture rules enforced at runtime.

## Rule

Runtime architecture rules must be proven from an observable runtime source of
truth. Static text scans are secondary evidence only.

## Primary Sources

Acceptable primary sources include:

- `app.openapi()` for FastAPI route and contract exposure;
- `app.routes` or an equivalent runtime route table;
- AST-based architecture guard for imports and ownership boundaries;
- loaded settings/config object for effective configuration;
- migrated DB schema or reflected metadata for persistence behavior;
- generated manifest, generated client, or generated schema artifact.

## Required Story Content

The story must state:

- primary source of truth;
- secondary evidence;
- why static scans alone are insufficient;
- command, test, or guard that exercises the primary source.

## Forbidden

- using `rg` as the only proof for runtime behavior;
- inferring OpenAPI, routes, config, or DB state from file names only;
- accepting a manual check when a deterministic runtime artifact exists.
