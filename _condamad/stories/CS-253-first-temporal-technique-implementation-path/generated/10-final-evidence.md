# Final Evidence

## Story status

`done`.

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- `.git`: present.
- Initial worktree: dirty before CS-253, with pre-existing changes across CS-246 to CS-252 and backend runtime/tests.
- Story-status mapping: CS-253 path and source brief matched the requested story.
- Capsule: generated files were missing, repaired with `condamad_prepare.py`, duplicate helper-created capsule removed, target capsule validated.

## Capsule validation

- Before implementation: PASS after repair.
- Final: PASS after evidence formatting.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `transit_chart_v1` selected in `temporal_technique_selection.py`. | Unit and architecture tests pass. | PASS |
| AC2 | Seven rejected candidates have explicit `closed` reasons. | `test_rejected_candidates_keep_explicit_non_selection_reasons`. | PASS |
| AC3 | Required inputs are typed in the contract and persisted in JSON evidence. | `test_required_inputs_graph_contracts_and_relationships_are_declared`. | PASS |
| AC4 | Required graph code and CS-246/247/248/250 graph contracts are declared. | Unit test plus no executable temporal graph guard. | PASS |
| AC5 | Chart objects and transit-to-natal relationships are declared. | Unit test for objects and relationships. | PASS |
| AC6 | Local CS-250 is already `done`; pre-done remains blocked and risk acceptance is explicitly non-public. | Gate tests, risk-acceptance assertion and API-neutrality tests. | PASS |
| AC7 | All non-selected candidates remain `closed`; no public surface family matches. | Single-family architecture guard and targeted `rg` scan. | PASS |
| AC8 | No API route, OpenAPI schema, frontend or migration surface was added. | API neutrality tests and `app.openapi()` / `app.routes` checks. | PASS |
| AC9 | Evidence files exist under the CS-253 story folder. | Evidence existence command and capsule validation. | PASS |

## Files changed

- `backend/app/domain/astrology/runtime/temporal_technique_selection.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`.
- `backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`.
- `backend/tests/architecture/test_temporal_family_single_path.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/**`.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/**`.
- `_condamad/stories/story-status.md`.

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`.
- Added `backend/tests/architecture/test_temporal_family_single_path.py`.
- Updated `backend/tests/architecture/test_api_contract_neutrality.py`.

## Commands run

- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...`: PASS, with duplicate helper capsule repaired into target path.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-253-first-temporal-technique-implementation-path`: PASS.
- `.\.venv\Scripts\Activate.ps1; ruff format <modified python files>`: PASS.
- `.\.venv\Scripts\Activate.ps1; ruff check backend`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_temporal_technique_selection.py`: PASS, `7 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_temporal_family_single_path.py`: PASS, `4 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py`: PASS, `14 passed`.
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "<risk-accepted-non-public gate assertion>"`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_astrology_doctrine_governance_guardrails.py ...`: PASS, `26 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend`: PASS, `3228 passed, 1 skipped, 1182 deselected`.
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert 'temporal_technique_selection' not in str(app.openapi())"`: PASS.
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "from app.main import app; assert not any('temporal' in getattr(r, 'path', '') for r in app.routes)"`: PASS.
- `rg -n "temporal_technique_selection|transit_chart_v1|synastry_chart_v1|solar_return_v1|lunar_return_v1|progressed_chart_v1|composite_chart_v1|profection_v1|forecasting_v1|transit_chart" backend\app\api frontend\src backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"`: PASS, exit `1` means no matches.
- `rg -n "app\.domain\.prediction|app\.services\.prediction" backend\app\domain\astrology\runtime\temporal_technique_selection.py backend\app\domain\astrology\runtime\__init__.py -g "*.py"`: PASS, exit `1` means no matches.
- `git diff --check -- <CS-253 touched paths>`: PASS.

## Commands skipped or blocked

- None.
- Discarded attempt: `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q` from `backend/` used the wrong activation path for that working directory and found the doctrine-governance classification gap before it was fixed. It is not counted as final evidence.

## DRY / No Legacy evidence

- One canonical selection module was added under `backend/app/domain/astrology/runtime`.
- No compatibility shim, alias, fallback resolver or duplicate temporal implementation was added.
- No prediction import is present in the touched temporal runtime contract/facade.
- No public API route, OpenAPI schema, frontend route, DB model or migration was added.
- Non-selected temporal families remain explicit `closed` decisions.

## Diff review

- Reviewed scoped diff and `git diff --check` for touched CS-253 paths.
- No unrelated file was intentionally modified; existing dirty files from prior stories were preserved.
- The new doctrine-governance classification is required by an existing architecture guard triggered by the new module.

## Final worktree status

- Worktree remains dirty due to pre-existing changes plus CS-253 files.
- CS-253-owned new files include `temporal_technique_selection.py`, `test_temporal_technique_selection.py`, `test_temporal_family_single_path.py`, and CS-253 evidence/generated files.

## Remaining risks

- The worktree contains many pre-existing uncommitted changes from adjacent stories.
- A discarded validation attempt used the wrong venv activation path from `backend/`; final counted validations were rerun from repository root with `.\.venv` activated.

## Review fix iteration

- Iteration 1 finding: the non-public risk acceptance branch initially kept `cs250_gate_state=blocked`, then used `non-public-risk-accepted`,
  which did not match the CS-250 gate vocabulary.
- Fix applied: `risk_acceptance_non_public=True` now returns `cs250_gate_state=risk-accepted-non-public`; the unit test and validation evidence were updated.
- Fresh review result: CLEAN; no remaining actionable implementation, proof, test, guardrail or AC-alignment issue found.

## Suggested reviewer focus

- Review the CS-250 nuance: local `CS-250` is `done`, so persisted after-snapshot is `selected-ready-after-cs250`, while tests still prove pre-done blocking and no public surface was introduced.

## Feedback loop routing

- `no-propagation`: reusable learning was captured as a local governance classification and evidence; no AGENTS.md or skill update is needed.
