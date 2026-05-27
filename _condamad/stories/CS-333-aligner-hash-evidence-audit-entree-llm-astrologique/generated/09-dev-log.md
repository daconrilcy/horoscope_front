# Dev Log

## Preflight

- Initial `git status --short`: `?? _condamad/run-state.json`
- Existing dirty files: `_condamad/run-state.json` only, left untouched.
- Story status row verified: CS-333 path and brief source matched.
- Capsule repaired with `condamad_prepare.py --repair-generated-only` and validated.

## Search evidence

- Scoped guardrails resolved: RG-002, RG-022.
- Targeted scans found owners: `llm_astrology_input_v1.py`, `evidence_refs_validation.py`, `projection_hash.py`, natal `interpretation_service.py`.
- Negative app scan after implementation: no `llm_input_identity`, no `hashlib.sha`, no `request_id.*llm_input_hash`, no `llm-input`, no unavailable fallback hash under touched app surfaces.

## Implementation notes

- Added one canonical hash-material helper in the existing LLM input owner.
- Kept `projection_hash` separate from full prompt input identity.
- Replaced request-id-derived audit `llm_input_hash` with the required contract provenance hash.
- Persisted LLM input evidence refs for non-rejected audit rows.
- Added collected tests at the story-requested paths.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_validate.py <capsule>` | PASS | Capsule structure valid. |
| `ruff format <changed files>` | PASS | Scoped format only. |
| `ruff check .` | PASS | Backend lint clean. |
| `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_hash.py --tb=short` | PASS | 3 passed. |
| `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short` | PASS | 2 passed. |
| `python -B -m pytest --long -q tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short` | PASS | 2 passed. |
| `python -B -m pytest -q tests/architecture/test_llm_astrology_input_audit_boundary.py --tb=short` | PASS | 3 passed. |
| `python -B -c "from app.main import app; assert 'llm_input_hash' not in str(app.openapi())"` | PASS | Public OpenAPI neutral. |
| `python -B -c "from app.main import app; assert all('llm-input' not in getattr(r, 'path', '') for r in app.routes)"` | PASS | No route exposure. |
| `python -B -m pytest -q tests --tb=short` | PASS | 1189 passed, 217 deselected. |

## Issues encountered

- Initial `condamad_prepare.py --story-key CS-333` created `_condamad/stories/cs-333`; removed immediately and repaired the official capsule with `--repair-generated-only`.
- Integration tests are deselected by default; reran the CS-333 integration audit test with `--long`.
- The audit path was made strict after diff review so missing LLM input provenance raises explicitly instead of producing fallback hash material.

## Decisions made

- No frontend, API route, DB model, migration or provider file was modified.
- No new dependency added.
- No feedback-loop propagation required; this run did not reveal a reusable process defect beyond story-local evidence.

## Final `git status --short`

- Captured after final validation in `10-final-evidence.md`.
