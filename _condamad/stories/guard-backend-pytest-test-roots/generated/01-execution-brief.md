# Execution Brief — guard-backend-pytest-test-roots

## Primary objective

Implement story `guard-backend-pytest-test-roots` exactly as defined in `../00-story.md`.

## Boundaries

- Use `backend/pyproject.toml` as the runtime source of pytest roots.
- Use `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md` as the persisted topology registry.
- Keep `backend/app/tests/unit/test_backend_test_topology.py` as the single topology guard owner.
- Do not move backend tests or change business assertions.
- Do not add dependencies or new backend root folders.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.
