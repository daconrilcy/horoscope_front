# Story Archetypes

<!-- Catalogue des archetypes CONDAMAD qui specialisent le contrat de story. -->

## Supported Archetypes

- `api-route-removal`
- `api-contract-change`
- `api-error-contract-centralization`
- `route-architecture-convergence`
- `api-adapter-boundary-convergence`
- `legacy-facade-removal`
- `field-contract-removal`
- `namespace-convergence`
- `ownership-routing-refactor`
- `module-move`
- `large-file-split`
- `dead-code-removal`
- `frontend-route-removal`
- `runtime-contract-preservation`
- `batch-migration`
- `architecture-guard-hardening`
- `registry-catalog-refactor`
- `test-guard-hardening`
- `service-boundary-refactor`
- `custom`

## Rule

The story writer must select exactly one primary archetype in the `Operation
Contract` section.

If no archetype fits, use:

```md
- Primary archetype: custom
- Archetype reason: <why no supported archetype fits>
- Additional validation rules:
  - ...
```

The archetype determines mandatory sections, AC patterns, validation evidence,
and anti-drift rules. Do not write the final story until the archetype-specific
contract has been applied.

## Contract Selection Matrix

| Archetype | Required contracts |
|---|---|
| `api-route-removal` | Runtime Source of Truth, Baseline Snapshot, Contract Shape, Reintroduction Guard, Persistent Evidence |
| `api-contract-change` | Runtime Source of Truth, Baseline Snapshot, Contract Shape, Reintroduction Guard, Persistent Evidence |
| `api-error-contract-centralization` | Runtime Source of Truth, Ownership Routing, Allowlist Exception, Contract Shape, Reintroduction Guard |
| `route-architecture-convergence` | Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Allowlist Exception, Reintroduction Guard, Persistent Evidence |
| `api-adapter-boundary-convergence` | Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Allowlist Exception, Reintroduction Guard |
| `legacy-facade-removal` | Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence |
| `field-contract-removal` | Baseline Snapshot, Contract Shape, Reintroduction Guard, Persistent Evidence |
| `namespace-convergence` | Baseline Snapshot, Ownership Routing, Batch Migration, Reintroduction Guard, Persistent Evidence |
| `ownership-routing-refactor` | Baseline Snapshot, Ownership Routing, Allowlist Exception, Reintroduction Guard |
| `module-move` | Baseline Snapshot, Ownership Routing, Reintroduction Guard |
| `large-file-split` | Baseline Snapshot, Ownership Routing, Reintroduction Guard |
| `dead-code-removal` | Baseline Snapshot, Reintroduction Guard, Persistent Evidence |
| `frontend-route-removal` | Baseline Snapshot, Contract Shape, Reintroduction Guard, Persistent Evidence |
| `runtime-contract-preservation` | Runtime Source of Truth, Baseline Snapshot, Contract Shape, Persistent Evidence |
| `batch-migration` | Baseline Snapshot, Batch Migration, Reintroduction Guard, Persistent Evidence |
| `architecture-guard-hardening` | Runtime Source of Truth, Allowlist Exception, Reintroduction Guard |
| `registry-catalog-refactor` | Baseline Snapshot, Ownership Routing, Batch Migration, Persistent Evidence |
| `test-guard-hardening` | Runtime Source of Truth, Allowlist Exception, Reintroduction Guard |
| `service-boundary-refactor` | Baseline Snapshot, Ownership Routing, Reintroduction Guard |
| `custom` | Select every contract activated by the story scope. |

## Removal Archetypes

Use `references/removal-story-contract.md` when the primary archetype is one of:

- `api-route-removal`
- `legacy-facade-removal`
- `field-contract-removal`
- `dead-code-removal`
- `frontend-route-removal`

Also use the removal contract when the operation type is `remove`, or when the
story source mentions deletion of routes, modules, fields, APIs, UI pages,
types, legacy states, aliases, wrappers, compatibility surfaces, or historical
facades.

## AC Templates For `api-route-removal`

Required AC themes:

1. Route inventory is complete.
2. Removal classification is deterministic and documented.
3. Historical-facade routes are deleted, not repointed.
4. External-active routes are preserved or escalated.
5. Router registration cannot reappear.
6. OpenAPI schema no longer exposes removed routes.
7. Backend imports/modules dedicated to deleted routes are removed.
8. First-party frontend consumers use canonical endpoints only.
9. Negative scans prove no nominal legacy consumption remains.
10. Targeted backend/frontend tests pass.

## AC Templates For `legacy-facade-removal`

Required AC themes:

1. Facade inventory identifies each compatibility surface.
2. Canonical ownership is explicit.
3. Internal consumers use canonical owner only.
4. Facade surfaces classified as removable are deleted.
5. External-active facade surfaces are escalated.
6. No wrapper, alias, fallback, re-export, or soft-delete remains.
7. Reintroduction guard fails if the facade returns.
8. Negative scans prove the legacy path is absent.

## AC Templates For `namespace-convergence`

Required AC themes:

1. Canonical namespace is defined.
2. Non-canonical namespace inventory is complete.
3. Consumers migrate to canonical imports.
4. Old namespace is deleted or escalated.
5. No compatibility re-export remains.
6. Importability checks prove removed namespace absence.
7. Architecture guard prevents namespace drift.

## AC Templates For `field-contract-removal`

Required AC themes:

1. Removed field inventory is complete.
2. Backend producers no longer emit the field.
3. Frontend consumers no longer read the field.
4. Type definitions no longer expose the field.
5. Generated contracts/schemas no longer contain the field when applicable.
6. Negative scans prove no nominal usage remains.
7. Tests prove canonical replacement or absence.

## AC Templates For `frontend-route-removal`

Required AC themes:

1. Frontend route inventory identifies removed route.
2. Route table no longer registers the removed path.
3. Navigation, menu entries, and deep links no longer target the removed path.
4. UI components dedicated only to the route are removed.
5. API clients used only by the route are removed or reclassified.
6. Tests prove canonical routing and absence of removed path.

## Archetype: `route-architecture-convergence`

Required contracts:

- Runtime Source of Truth Contract
- Baseline Snapshot Contract
- Ownership Routing Contract
- Allowlist Exception Contract
- Reintroduction Guard Contract

Required AC themes:

1. Runtime route inventory is captured from `app.openapi()`.
2. Before/after route contract is compared.
3. Python router ownership maps to effective HTTP roots.
4. Allowlist entries are exact and justified.
5. Architecture guard fails if route placement drifts again.

## Archetype: `api-error-contract-centralization`

Required contracts:

- Contract Shape Contract
- Ownership Routing Contract
- Allowlist Exception Contract
- Runtime Source of Truth Contract
- Reintroduction Guard Contract

Required AC themes:

1. HTTP error JSON shape is explicit.
2. Application errors live outside `app.api`.
3. API handlers translate but do not decide business logic.
4. Unmapped errors produce controlled generic responses.
5. Forbidden local `HTTPException` / `JSONResponse` patterns are guarded with narrow allowlist.
