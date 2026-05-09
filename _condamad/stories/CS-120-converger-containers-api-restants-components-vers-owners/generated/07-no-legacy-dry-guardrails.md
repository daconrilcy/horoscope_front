<!-- Guardrails No Legacy et DRY specifiques a CS-120. -->

# No Legacy / DRY Guardrails - CS-120

## Forbidden Legacy Patterns

- Compatibility wrapper under `frontend/src/components/**`.
- Transitional alias, re-export, barrel preservation or fallback module.
- Duplicate active component owner for the same API orchestration.
- Wildcard or folder-wide exception in `COMPONENT_API_IMPORT_EXCEPTIONS`.
- Stale allowlist row after a file becomes API-free or is deleted.
- API/feature imports, `apiFetch`, raw `fetch` or `axios` under
  `frontend/src/components/**` without an exact, justified blocker.

## Canonical Destinations

- Admin access guard: `frontend/src/app/guards/**`.
- Enterprise/B2B panels: precise enterprise/B2B feature or route/page owner.
- Support ops panel: precise support/admin ops owner.
- Settings privacy deletion modal: page-adjacent settings/privacy owner.
- Dashboard summary hook/container: dashboard feature/page owner.
- Layout auth state: app/layout owner or prop-driven presentational components.
- UpgradeCTA test fixture: local structural fixture or neutral contract.

## Required Negative Evidence

- Zero old import hits for moved component paths.
- Zero stale rows for moved files in `component-architecture-allowlist.ts`.
- Zero API/feature ownership hits under `frontend/src/components/**` after the story, unless an exact blocker is documented.
- No `@ts-nocheck`, inline styles or new component usage exceptions introduced.

## Applicable Regression Guardrails

- `RG-047`, `RG-048`, `RG-050`, `RG-056`, `RG-057`.
- `RG-069`, `RG-070`, `RG-071`, `RG-072`, `RG-073`, `RG-074`.

## Review Checklist

- Every old path is either deleted or made API-free with no stale exception.
- Every consumer imports the canonical owner directly.
- Tests prove runtime behavior, not only text scans.
- Final evidence records closure status for source finding `F-001`.
