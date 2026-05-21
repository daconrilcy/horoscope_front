# Final Evidence - CS-209

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-209-solar-proximity-conditions-calculator`
- Source story: `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- Capsule path: `_condamad/stories/CS-209-solar-proximity-conditions-calculator`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean before generated capsule files.
- Pre-existing dirty files: none.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes.
- Story sufficiency gate: PASS; story is finite and exact, not audit-sourced, and has deterministic guard coverage.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated capsule file present |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Completed with AC evidence |
| `generated/04-target-files.md` | yes | yes | PASS | Completed with inspected/changed surfaces |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands and scans explicit |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-135/RG-136 mapped |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `solar_proximity_calculator.py` and package export added. | Targeted pytest PASS; full pytest PASS. | PASS | |
| AC2 | `SolarProximityThresholds` added in `contracts.py`. | Contract test PASS. | PASS | |
| AC3 | Ordered branches cazimi, combust, under beams, none. | Calculator tests PASS. | PASS | |
| AC4 | Minimal angular distance helper handles wrap-around. | Calculator wrap-around test PASS. | PASS | |
| AC5 | Longitude normalization helper uses modulo 360. | Calculator normalization test PASS. | PASS | |
| AC6 | Inclusive thresholds and `15.0001` none behavior. | Boundary test PASS. | PASS | |
| AC7 | Sun returns inactive none. | Sun test PASS. | PASS | |
| AC8 | Severity mapping implemented. | Calculator tests PASS. | PASS | |
| AC9 | Custom thresholds accepted via contract. | Custom threshold test PASS. | PASS | |
| AC10 | Batch function returns all input keys including sun. | Batch test PASS. | PASS | |
| AC11 | Calculator forbidden surfaces absent. | RG-136 scans PASS. | PASS | |
| AC12 | Adjacent integrations unchanged. | Adjacent diff empty. | PASS | |
| AC13 | Backend quality checks pass in venv. | Ruff and full pytest PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/planetary_conditions/contracts.py` | modified | Add immutable solar proximity thresholds | AC2, AC9 |
| `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py` | added | Pure calculator for solar proximity conditions | AC1, AC3-AC11 |
| `backend/app/domain/astrology/planetary_conditions/__init__.py` | modified | Public exports for thresholds and functions | AC1, AC10 |
| `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | modified | Threshold contract tests | AC2, AC9 |
| `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py` | added | Calculator behavior tests | AC1, AC3-AC10 |
| `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/*` | generated/modified | CONDAMAD evidence and review files | AC11-AC13 |
| `_condamad/stories/CS-209-solar-proximity-conditions-calculator/evidence/validation.md` | added | Persistent validation evidence | AC11-AC13 |

## Files deleted

None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`.
- Updated `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | PASS | 0 | First run: `18 passed in 0.40s`; after review fix: `19 passed in 0.37s` |
| `ruff format .` | repo root | PASS | 0 | `1 file reformatted, 1488 files left unchanged` |
| `ruff format --check .` | repo root | PASS | 0 | Fresh review run: `1489 files already formatted` |
| `ruff check .` | repo root | PASS | 0 | `All checks passed!` |
| `pytest -q` | repo root | PASS | 0 | First run: `2834 passed, 1 skipped, 1177 deselected in 238.71s`; after review fix: `2835 passed, 1 skipped, 1177 deselected in 207.54s`; fresh review run: `2835 passed, 1 skipped, 1177 deselected in 265.18s` |
| Story validate/lint commands from `06-validation-plan.md` | repo root | PASS | 0 | Validation and lint passed, no missing required contract |
| Required RG-135/RG-136 scans | repo root | PASS | 0/1 expected for zero-hit scans | Forbidden scans zero-hit; public symbols limited to package/tests |
| `git diff -- <adjacent forbidden surfaces>` | repo root | PASS | 0 | Empty diff |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8020` + `GET /openapi.json` | `backend` | PASS | 0 | Fresh review run: HTTP 200, OpenAPI response bytes `541782`; server stopped after check |
| Startup command with identical stdout/stderr redirection | repo root | BLOCKED then corrected | 1 then 0 | PowerShell rejected the first `Start-Process` shape; rerun with separate logs passed. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No compatibility wrapper, alias, fallback, shim or duplicate owner introduced.
- Threshold ownership is single and contract-level in `contracts.py`.
- Calculator imports only standard library plus `planetary_conditions.contracts`.
- `RG-135` remains valid for contract purity.
- `RG-136` is satisfied for calculator purity.

## Diff review

- Changed files are limited to `planetary_conditions`, its unit tests, and CS-209 evidence.
- No API, infra, migration, frontend, `NatalResult`, or JSON projection change.

## Final worktree status

- Modified tracked files:
  - `_condamad/stories/story-status.md`
  - `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- Untracked story files:
  - `_condamad/stories/CS-209-solar-proximity-conditions-calculator/evidence/validation.md`
  - `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/*.md`
  - `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `git diff --check`: PASS.

## Review/fix iteration

- Iteration 1 accepted finding: implicit `planet_key` alias through `strip().lower()`.
- Fix: exact caller key is preserved; only exact `planet_key == "sun"` returns inactive Sun condition.
- Added validation: `test_planet_key_is_not_normalized_as_alias`.
- Rejected findings: none. Low evidence finding for missing `11-code-review.md` was accepted and resolved by adding the artifact.
- Fresh closure review: CLEAN; no additional issue found after rerunning targeted tests, Ruff, full pytest, story validation, scans, adjacent diff and startup check.

## Remaining risks

- None identified after validation.

## Suggested reviewer focus

- Confirm threshold semantics and `orb_deg` ownership are acceptable for the new contract.
- Confirm no future-story integration was introduced.
