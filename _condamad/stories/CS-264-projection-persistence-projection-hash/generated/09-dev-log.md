# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: repository already dirty on unrelated CS-256, CS-257, CS-258, CS-259, CS-260, CS-261, CS-263 story artifacts and architecture docs.
- Story registry row verified for `CS-264`, target `Path`, and source brief.
- Required generated capsule files were missing, so `condamad_prepare.py --repair-generated-only` was run against the existing CS-264 capsule, then `condamad_validate.py` returned PASS.
- A mistaken preparer run created `_condamad/stories/cs-264`; it was removed immediately after path verification because it was a parallel capsule.

## Search evidence

- Existing persistence owners inspected: `ChartResultModel`, `ChartResultRepository`, Alembic env/model registry.
- Real builder selected: `AINarrativeInputBuilder.from_interpretation_input`, backed by existing `ChartInterpretationInputBuilder`/runtime contracts.
- Targeted guardrail scan found no exact CS-264 guardrail; story-local tests and scans cover the new invariants.

## Implementation notes

- Added canonical projection hash helper using sorted JSON keys, compact separators, UTF-8 SHA-256 and dataclass/enum normalization.
- Added `PersistedProjectionModel`, repository, service and Alembic migration for `persisted_projections`.
- Added builder gating: absence of a real builder raises `ProjectionBuilderUnavailableError` before any DB write.
- Added `AINarrativePersistedProjectionIdentity` to anchor `narrative_answer_audit_v1` references by type/version/hash without exposing payloads to API clients.
- Updated existing architecture guard tests to classify the new DB test fixtures and authorized root service file required by this story.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ...` | PASS | Generated missing capsule files. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | PASS | Capsule structure valid. |
| `ruff format <changed python paths>` | PASS | Scoped formatting only. |
| `python -B -m pytest -q tests\unit\projections tests\integration\test_projection_persistence_schema.py tests\unit\domain\astrology\interpretation\test_ai_narrative_input_contract.py --tb=short` | PASS | 11 passed, 2 deselected. |
| `ruff check .` | PASS | Backend lint clean. |
| `python -B -m alembic heads` | PASS | Head is `20260524_0138`. |
| `python -B -c "from app.main import app; ... app.openapi() ..."` | PASS | No projection persistence API exposure. |
| `python -B -m pytest -q --tb=short` | PASS | 3243 passed, 1 skipped, 1184 deselected. |

## Issues encountered

- First full pytest run failed on architecture guards for unclassified SQLite `create_all` tests and new root service file. Fixed by updating the existing guard allowlists with explicit CS-264 paths.
- `backend/.tmp-pytest` remained locked by Windows after cleanup retry; it is ignored/generated test data and not part of the tracked diff.

## Decisions made

- Persisted the first real builder-backed projection as `ai_narrative_input` / `ai_narrative_input.v1`; no structured-facts builder was present in this repository snapshot.
- Did not add frontend, public API routes, generated clients, or placeholder projection builders.

## Final `git status --short`

- CS-264 application changes: backend projection hash/model/repository/service/migration/tests and narrative audit linkage.
- CS-264 capsule/evidence files are untracked and ready for review.
- Pre-existing unrelated dirty files remain outside this story scope.
