# Final Evidence - CS-186

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-186-fix-runtime-reference-sign-fixtures`
- Source story: user request on 2026-05-18
- Capsule path: `_condamad/stories/CS-186-fix-runtime-reference-sign-fixtures`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing user changes in DB models, reference seed services, migration and astrology JSON docs.
- AGENTS.md considered: `AGENTS.md`
- Regression guardrails considered: `RG-107`, `RG-108`, `RG-112`, `RG-114`

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Affected tests now pass `complete_sign_payloads()` to runtime references. | Targeted pytest over six affected files plus guard: `99 passed`. | PASS | The original missing-profile failure is gone. |
| AC2 | `_complete_sign_payload()` still raises on missing `element`, `modality`, `polarity`; no fallback added to `runtime_reference_from_mapping()`. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py` included in targeted run; full suite passed. | PASS | Strictness preserved. |
| AC3 | `backend/tests/factories/astrology_runtime_reference_factory.py` exposes `complete_sign_payloads()` and `complete_reference()` reuses it. | Diff review and targeted tests passed. | PASS | Centralized test fixture helper. |
| AC4 | No production `backend/app/domain/astrology` or `backend/app/services/natal` files changed by this story. | RG-114 app scan returned `NO_MATCH`; `SIGN_PROFILE_DATA` scan has only guard self-check hits. | PASS | Pre-existing unrelated app DB changes left untouched. |
| AC5 | All commands were run through `.\.venv\Scripts\Activate.ps1; cd backend; ...`. | `ruff format .`, `ruff check .`, full `pytest -q` passed. | PASS | Venv rule respected. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/tests/factories/astrology_runtime_reference_factory.py` | modified | Add explicit complete sign fixture helper and reduce duplicated full-sign payload. | AC2, AC3 |
| `backend/app/tests/unit/test_aspect_orb_overrides.py` | modified | Use complete sign payloads in runtime reference fixture. | AC1, AC3 |
| `backend/app/tests/unit/test_aspect_ruleset_schema.py` | modified | Use complete sign payloads in runtime reference fixture. | AC1, AC3 |
| `backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py` | modified | Use complete sign payloads in runtime reference fixture. | AC1, AC3 |
| `backend/app/tests/unit/test_natal_metadata.py` | modified | Use complete sign payloads in runtime reference fixture. | AC1, AC3 |
| `backend/app/tests/unit/test_natal_pipeline_swisseph.py` | modified | Use complete sign payloads in runtime reference fixture. | AC1, AC3 |
| `backend/app/tests/unit/test_natal_tt.py` | modified | Use complete sign payloads in TT natal result fixtures. | AC1, AC3 |
| `_condamad/stories/CS-186-fix-runtime-reference-sign-fixtures/**` | added/modified | Story capsule and final evidence. | AC5 |
| `_condamad/stories/story-status.md` | modified | Register CS-186 as ready-to-review. | AC5 |

## Files deleted

None.

## Tests added or updated

- Updated existing unit test fixtures only; no new test file required because the failure was fixture completeness.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspect_ruleset_schema.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_metadata.py app/tests/unit/test_natal_pipeline_swisseph.py app/tests/unit/test_natal_tt.py app/tests/unit/test_astrology_runtime_reference_guard.py` | repo root | FAIL | 1 | Initial run after first patch failed because only subset signs were supplied; fixed by using all 12 signs. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspect_ruleset_schema.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_metadata.py app/tests/unit/test_natal_pipeline_swisseph.py app/tests/unit/test_natal_tt.py app/tests/unit/test_astrology_runtime_reference_guard.py` | repo root | PASS | 0 | `99 passed in 1.15s`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .; ruff check .` | repo root | PASS | 0 | `6 files reformatted`; `All checks passed!`. |
| `rg -n "ELEMENT_BY_SIGN\|MODALITY_BY_SIGN\|POLARITY_BY_SIGN\|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"` | `backend/` | PASS | 1 | No matches; reported as `NO_MATCH`. |
| `rg -n "SIGN_PROFILE_DATA" tests/factories app/tests -g "*.py"` | `backend/` | PASS | 0 | Only expected self-check hits in `app/tests/unit/test_astrology_runtime_reference_guard.py`; no factory hit. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 0 | `2621 passed, 1 skipped, 1175 deselected in 173.35s`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; Git emitted CRLF normalization warnings for pre-existing dirty files. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; includes pre-existing unrelated user changes plus CS-186 files. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- `runtime_reference_from_mapping()` remains strict; no silent fallback was added.
- `complete_sign_payloads()` is a test helper that makes complete fixture construction explicit at call sites.
- `rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"` returned `NO_MATCH`.
- `rg -n "SIGN_PROFILE_DATA" tests/factories app/tests -g "*.py"` returned only the guard file that asserts the factory does not contain `SIGN_PROFILE_DATA`.

## Diff review

- Story-owned code changes are limited to test factory and affected tests.
- No production runtime, DB repository, migration, or seed JSON file was intentionally modified by CS-186.
- Pre-existing dirty files remain present and are not reverted.
- `git diff --check` passed with CRLF normalization warnings only.

## Final worktree status

Final `git status --short` still includes pre-existing user changes under DB models/repositories/seeds, migration, and docs/seed JSON files, plus CS-186 modified tests/factory and new capsule files.

## Remaining risks

None for the reported test failures. The worktree has unrelated pre-existing changes outside this story.

## Suggested reviewer focus

Review that strict fixture validation remains intact and no production fallback was added.
