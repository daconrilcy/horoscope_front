# Dev Log

## Preflight

- Initial `git status --short`: `?? _condamad/run-state.json`.
- Current branch: not required for implementation.
- Existing dirty files: `_condamad/run-state.json` was pre-existing and not touched intentionally.
- Capsule: required generated files were missing in target capsule; `condamad_prepare.py --repair-generated-only` repaired the target capsule. A stray `_condamad/stories/cs-331` capsule created by an initial prepare invocation was removed immediately.

## Search evidence

- Story-status row matched `CS-331`, target path and source brief.
- Scoped guardrails resolved from story: `RG-002`, `RG-022`; registry gap handled by story-local owner/public-surface guards.
- Existing canonical contract module found: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`; no parallel mapper was created.

## Implementation notes

- Extended `structured_facts_v1` structural facts with existing sign profile balances when available.
- Refined `llm_astrology_input_v1` mapping so facts, signals, limits, evidence and shaping keep distinct owners.
- Added architecture guard `backend/tests/architecture/test_llm_astrology_input_boundary.py`.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `ruff format <modified python files>` | PASS | Scoped formatting only. |
| `ruff check .` | PASS | Backend working directory. |
| `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_structured_facts_v1_builder.py tests/architecture/test_llm_astrology_input_boundary.py --tb=short` | PASS | 18 passed. |
| `python -B -m pytest -q tests/architecture/test_astrology_doctrine_governance_guardrails.py tests/unit/domain/astrology/test_llm_astrology_input_v1.py --tb=short` | PASS | 10 passed after marker fix. |
| `python -B -m pytest -q tests --tb=short` | PASS | 1172 passed, 215 deselected. |
| OpenAPI and route guard commands | PASS | No public `llm_astrology` surface. |
| Targeted API/infra import scan | PASS | No matches; exit code 1 expected for negative scan. |

## Issues encountered

- The full suite initially failed on `test_rule_marker_surfaces_are_declared_in_doctrine_governance` because emitted-key constants introduced an unclassified `profile` AST marker in the mapper. Fixed by preserving emitted JSON keys while avoiding rule-marker constants/names in the domain module.

## Decisions made

- No frontend delegation: story scope is backend-domain only and no frontend file is touched.
- No new dependency, API route, DB, migration, prompt template or provider integration.

## Final `git status --short`

- Recorded after final validation in `generated/10-final-evidence.md`.
