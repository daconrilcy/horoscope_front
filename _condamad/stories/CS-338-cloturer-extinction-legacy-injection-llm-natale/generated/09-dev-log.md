# Dev Log

<!-- Commentaire global: ce journal garde les decisions d'implementation et de validation CS-338. -->

## Preflight

- Initial `git status --short`: `?? _condamad/run-state.json`
- Current branch: not recorded by command; git repository present.
- Existing dirty files: `_condamad/run-state.json` pre-existing untracked.
- Capsule repair: missing generated files repaired with `condamad_prepare.py --repair-generated-only`.
- Erroneous temporary capsule `_condamad/stories/cs-338` was created by an initial prepare attempt and removed after path verification.

## Search evidence

- Mandatory briefs read: CS-338, CS-336, CS-337.
- Mandatory transition report read: `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`.
- Baseline scan persisted: `evidence/legacy-scan-before.txt`.
- Final scan persisted: `evidence/legacy-scan-after.txt`.
- Modern input scan persisted: `evidence/llm-astrology-input-v1-scan.txt`.

## Implementation notes

- Added negative guards to `backend/tests/integration/test_llm_legacy_extinction.py`.
- Created final closure report at `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`.
- No frontend, API router, migration, dependency, shim, alias, fallback, or compatibility path was added.
- No update to `_condamad/stories/regression-guardrails.md`, per story instruction.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale --root . --with-optional` | PASS | Venv active |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale` | PASS | Venv active |
| `ruff format tests\integration\test_llm_legacy_extinction.py` | PASS | Scoped formatting |
| `python -B -m pytest -q --long tests\integration\test_llm_legacy_extinction.py --tb=short` | PASS | 7 passed |
| `ruff check .` | PASS | Backend |
| `python -B -m pytest -q app\tests\unit\test_gateway_input_validation_payload.py --tb=short` | PASS | 2 passed |
| `python -B -m pytest -q --long tests\integration\test_llm_runtime_suppression.py --tb=short` | PASS | 8 passed |
| `python -B -m pytest -q --long tests --tb=short` | PASS | 1420 passed, 9 skipped |
| `rg -n "chart_json\|natal_data\|evidence_catalog\|legacy\|fallback\|transition-condition" backend\app backend\tests _condamad _story_briefs` | PASS | Occurrences classified in final report |
| `rg -n "llm_astrology_input_v1" backend\app backend\tests _condamad _story_briefs` | PASS | Modern path present |

## Issues encountered

- `pytest tests\integration\...` without `--long` deselected all integration tests by design in `backend/conftest.py`.
- A first test assertion expected `contract_id` to be prompt-visible; runtime correctly filters to prompt blocks, so the guard now asserts a `facts` value.

## Decisions made

- Classify generic `ExecutionContext.chart_json` / `natal_data` as ownerised outside the active natal prompt path, with new regression guards for natal rendering and validation.
- Classify `event_guidance` `chart_json` as non-natal and outside CS-338.
- Treat `_condamad` / `_story_briefs` textual occurrences as archive-documentaire when not executable runtime behavior.

## Final `git status --short`

- `M _condamad/stories/story-status.md`
- `M backend/tests/integration/test_llm_legacy_extinction.py`
- `?? _condamad/reports/extinction-legacy-injection-llm-natale/`
- `?? _condamad/run-state.json` (pre-existing)
- `?? _condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/`
- `?? _condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/generated/*.md`
