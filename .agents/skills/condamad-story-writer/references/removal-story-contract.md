# Removal Story Contract

<!-- Contrat specialise pour les stories de suppression No Legacy. -->

Use this contract when the story removes routes, modules, fields, APIs, UI
pages, types, legacy states, import paths, aliases, wrappers, or compatibility
surfaces.

## Required Extra Sections

A removal story must include these markdown sections:

- `Removal Classification Rules`
- `Removal Audit Format`
- `Canonical Ownership`
- `Delete-Only Rule`
- `External Usage Blocker`
- `Reintroduction Guard`
- `Generated Contract Check`

## Removal Classification Rules

Classification must be deterministic:

- `canonical-active`:
  - item is referenced by first-party production code; or
  - item is the canonical owner defined in `Canonical Ownership`.

- `external-active`:
  - item is referenced by email templates, public docs, generated links, webhook
    docs, OpenAPI clients, analytics events, or explicit audit evidence.

- `historical-facade`:
  - item delegates to a canonical implementation; and
  - item exists only to preserve an older route, field, type, status, import
    path, or UI.

- `dead`:
  - item has zero references in production code, tests, docs, generated
    contracts, and known external surfaces.

- `needs-user-decision`:
  - allowed only after all required scans;
  - must include unresolved ambiguity and deletion risk;
  - cannot be silently deleted.

## Classification Decision Matrix

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

The story must require an audit table with this exact shape:

```md
| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
```

Rules:

- `Item` must be a route, field, file, symbol, status, import path, or UI route.
- `Classification` must use the allowed classification values.
- `Decision` must be one of:
  - `keep`
  - `delete`
  - `replace-consumer`
  - `needs-user-decision`
- `Proof` must include command output, file path evidence, or explicit audit
  source.
- `Risk` must be filled for every `delete` or `needs-user-decision` item.

For `api-route-removal`, the audit must be written to:

```text
_condamad/stories/<story-key>/route-consumption-audit.md
```

## Canonical Ownership

The story must include a table:

```md
| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
```

Any item listed as non-canonical must either be deleted, classified as
`external-active`, or escalated as `needs-user-decision`.

## Delete-Only Rule

An item classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint;
- preserving a wrapper;
- adding a compatibility alias;
- keeping a deprecated route active;
- preserving the old path through re-export;
- replacing deletion with soft-disable behavior.

## External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.

The story must require a blocker or explicit user decision with the exact
external evidence and deletion risk.

## Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes;
- importable Python modules;
- frontend route table;
- generated OpenAPI paths;
- forbidden symbols or states.

Required forbidden examples:

- `<removed route prefix>`
- `<removed import path>`
- `<removed frontend route>`
- `<removed legacy field>`

## Generated Contract Check

When generated contracts exist, the story must require a check proving removed
surfaces are absent from generated artifacts, for example:

- FastAPI OpenAPI paths;
- generated TypeScript clients;
- route manifests;
- public API docs;
- typed schema snapshots.

If no generated contract, route manifest, schema, public API doc, or generated
client can be affected, the section may state:

```md
- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.
```
