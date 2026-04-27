# Reintroduction Guard Contract

<!-- Contrat transverse pour empecher le retour d'une surface legacy. -->

Use this contract when the story removes, forbids, or converges away from a
legacy route, field, import, module, prefix, OpenAPI path, frontend route, or
status.

## Rule

The implementation must include a deterministic guard that fails if the legacy
surface returns.

## Acceptable Guard Sources

- registered router prefixes;
- `app.openapi()` paths;
- importable Python modules;
- AST import graph;
- frontend route table;
- generated manifests;
- targeted forbidden symbol scans.

## Required Story Content

The story must name the forbidden examples and the guard command/test that
detects each category.
