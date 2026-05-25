# No Legacy / DRY Guardrails

## Story-local forbidden changes

- No B2C route, serializer, OpenAPI schema, generated client or UI component.
- No activation of `ASTRO_EXPERT` in RBAC constants, claims or backend app code.
- No projection builder, service, DB model, migration, seed or persistence object.
- No alias, shim, compatibility wrapper, duplicate projection document or parallel registry.
- No fallback branch granting access to target-only roles.
- No raw runtime traces, prompt internals, replay payloads, provider debug dumps or unrestricted technical diagnostics in the accepted projection contract.

## Canonical owners reused

- `docs/architecture/expert-technical-projection-v1-contract.md` owns `expert_technical_projection_v1`.
- `docs/architecture/official-product-primitives-public-projections.md` remains the primitive registry.
- CS-270 owns internal role vocabulary.
- `docs/architecture/admin-permission-matrix.md` from CS-271 owns permission decisions.
- `docs/architecture/structured-facts-v1-contract.md` owns `structured_facts_v1`.
- `docs/architecture/evidence-refs-contract.md` owns `evidence_refs`.
- CS-266 and `app.openapi()` own public OpenAPI neutrality.
- CS-272 owns admin/internal access-log vocabulary.

## Reintroduction guards added

- `backend/tests/unit/test_expert_technical_projection_contract.py` fails if the contract loses internal classification, B2C denial, CS-271 ownership, data families, evidence links, exclusions, access-log fields, registry reclassification or runtime neutrality.
- Expert registry row scan fails if the row returns to public API/client/UI ownership wording.
- Runtime command fails if `expert_technical_projection_v1` appears in public OpenAPI or route paths.

## Validation result

- No legacy public path was introduced.
- No duplicate active implementation was introduced.
- No silent fallback was introduced.
- No application runtime surface was changed by CS-273.
