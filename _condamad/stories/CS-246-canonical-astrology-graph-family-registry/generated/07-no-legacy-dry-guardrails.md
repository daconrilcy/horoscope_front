# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?

## CS-246 result

- Canonical registry path: `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.
- No compatibility wrapper, re-export, alias, shim, or fallback resolver was introduced.
- Unknown family codes raise `AstrologyGraphFamilyRegistryError`.
- Duplicate family declarations raise `AstrologyGraphFamilyRegistryError`.
- The only architecture allowlist update is a permanent CS-246 exception for the required family code `narrative_generation_v1` in `backend/tests/architecture/test_astrology_runtime_boundary.py`; it does not expose a public API surface.
- Negative API/frontend/migration scan for `graph-family|graph_family|AstrologyGraphFamily` returned no matches.
