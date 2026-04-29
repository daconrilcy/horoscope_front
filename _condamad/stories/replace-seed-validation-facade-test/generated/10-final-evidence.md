# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: replace-seed-validation-facade-test
- Source story: `_condamad/stories/replace-seed-validation-facade-test/00-story.md`
- Capsule path: `_condamad/stories/replace-seed-validation-facade-test`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/replace-seed-validation-facade-test/00-story.md`
- Initial `git status --short`: `?? _condamad/stories/replace-seed-validation-facade-test/`
- Pre-existing dirty files: untracked story capsule directory only.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing `generated/` files were created with `condamad_prepare.py`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific brief. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 mapped and passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Search and file map completed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No-op and seed guardrails recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/ops/llm/bootstrap/use_cases_seed.py::validate_use_case_seed_contracts`; `seed-validation-decision.md` | `pytest -q app/tests/unit/test_seed_validation.py` PASS; `rg -n "SeedValidationError\|persona" backend/app/ops/llm/bootstrap/use_cases_seed.py backend/app/tests/unit/test_seed_validation.py` | PASS | Required persona contracts with no non-empty placeholder are rejected before DB writes. |
| AC2 | `backend/app/tests/unit/test_seed_validation.py` no longer contains a `pass` facade. | `rg -n "assert True\|pass$" backend/app/tests backend/tests -g test_*.py` classified; `pytest -q app/tests/unit/test_backend_noop_tests.py` PASS. | PASS | Remaining `pass` hits are nested control-flow statements. |
| AC3 | `seed_use_cases` calls `validate_use_case_seed_contracts` before DB mutation; seed decision artifact persisted. | `pytest -q app/tests/unit/test_seed_validation.py` PASS; app import smoke PASS. | PASS | Current canonical contracts remain valid and blank placeholder values are rejected. |
| AC4 | Added `backend/app/tests/unit/test_backend_noop_tests.py`; converted pricing `assert True` to `pytest.raises`. | `pytest -q app/tests/unit/test_backend_noop_tests.py` PASS; full `pytest -q` PASS. | PASS | New durable invariant recorded as `RG-014`. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/ops/llm/bootstrap/use_cases_seed.py` | modified | Add executable seed contract validation and call it before DB writes. | AC1, AC3 |
| `backend/app/tests/unit/test_seed_validation.py` | modified | Replace facade `pass` with executable validation tests. | AC1, AC2, AC3 |
| `backend/app/tests/unit/test_backend_noop_tests.py` | added | Guard direct empty test bodies and executable `assert True`. | AC2, AC4 |
| `backend/app/tests/unit/test_pricing_experiment_service.py` | modified | Replace `assert True` with `pytest.raises`. | AC4 |
| `_condamad/stories/regression-guardrails.md` | modified | Add `RG-014` durable invariant. | AC4 |
| `_condamad/stories/replace-seed-validation-facade-test/**` | added/modified | Persist capsule, scans, decision, traceability, and final evidence. | AC1-AC4 |

## Files deleted

- None.

## Tests added or updated

- Added `backend/app/tests/unit/test_backend_noop_tests.py`.
- Updated `backend/app/tests/unit/test_seed_validation.py`.
- Updated `backend/app/tests/unit/test_pricing_experiment_service.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\replace-seed-validation-facade-test\00-story.md --root . --story-key replace-seed-validation-facade-test --with-optional` | repo root, venv active | PASS | 0 | Capsule generated. |
| `pytest -q app/tests/unit/test_seed_validation.py app/tests/unit/test_backend_noop_tests.py app/tests/unit/test_pricing_experiment_service.py` | `backend/`, venv active | PASS | 0 | 7 passed before residual-risk fix. |
| `ruff format app/ops/llm/bootstrap/use_cases_seed.py app/tests/unit/test_seed_validation.py` | `backend/`, venv active | PASS | 0 | 1 file reformatted after residual-risk fix. |
| `ruff check app/ops/llm/bootstrap/use_cases_seed.py app/tests/unit/test_seed_validation.py` | `backend/`, venv active | PASS | 0 | All checks passed after residual-risk fix. |
| `pytest -q app/tests/unit/test_seed_validation.py app/tests/unit/test_backend_noop_tests.py` | `backend/`, venv active | PASS | 0 | 5 passed after adding blank placeholder validation. |
| `pytest -q app/tests/unit/test_seed_validation.py app/tests/unit/test_backend_noop_tests.py app/tests/unit/test_pricing_experiment_service.py` | `backend/`, venv active | PASS | 0 | 8 passed after residual-risk fix. |
| `rg -n "assert True\|pass$" backend/app/tests backend/tests -g test_*.py` | repo root | PASS | 0 | Remaining hits classified in `noop-test-scan-after.md`. |
| `rg -n "SeedValidationError\|validate_use_case_seed_contracts\|persona_strategy\|persona" backend/app/ops/llm/bootstrap/use_cases_seed.py backend/app/tests/unit/test_seed_validation.py` | repo root | PASS | 0 | Seed validation symbols found in intended files. |
| `rg -n "seed_validation_required_persona_empty_allowed\|assert True" backend/app/tests backend/tests -g test_*.py` | repo root | PASS | 0 | Old facade absent; only guard text self-references `assert True`. |
| `ruff format .` | `backend/`, venv active | PASS | 0 | 2 story files reformatted, rest unchanged. |
| `ruff check .` | `backend/`, venv active | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_seed_validation.py app/tests/unit/test_backend_noop_tests.py app/tests/unit/test_pricing_experiment_service.py` | `backend/`, venv active | PASS | 0 | 7 passed after formatting. |
| `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/`, venv active | PASS | 0 | 3486 tests collected. |
| `pytest -q` | `backend/`, venv active | PASS | 0 | 3474 passed, 12 skipped, 7 warnings. |
| `python -c "from app.main import app; print(app.title)"` | `backend/`, venv active | PASS | 0 | FastAPI app imports; title `horoscope-backend`. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/replace-seed-validation-facade-test/00-story.md` | repo root, venv active | NOT APPLICABLE | n/a | Story-writer validation targets `Status: ready-for-dev`; this implemented story is now `Status: ready-for-review`. Final capsule validation below is the applicable post-dev gate. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/replace-seed-validation-facade-test/00-story.md` | repo root, venv active | NOT APPLICABLE | n/a | Story-writer lint calls the ready-for-dev validator; not counted as final evidence after implementation status moved to `ready-for-review`. |
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/replace-seed-validation-facade-test --final` | repo root, venv active | PASS | 0 | CONDAMAD capsule validation passed. |
| `ruff format --check .` | `backend/`, venv active | PASS | 0 | 1242 files already formatted after review fixes. |
| `ruff check .` | `backend/`, venv active | PASS | 0 | All checks passed after review fixes. |
| `pytest -q app/tests/unit/test_backend_noop_tests.py app/tests/unit/test_seed_validation.py app/tests/unit/test_pricing_experiment_service.py` | `backend/`, venv active | PASS | 0 | 9 passed after hardening the skip-reason guard. |
| `pytest -q` | `backend/`, venv active | PASS | 0 | Manual validation reported by user: 3476 passed, 12 skipped, 7 warnings in 839.74s (0:13:59). |
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/replace-seed-validation-facade-test --final` | repo root, venv active | PASS | 0 | CONDAMAD capsule validation passed after review fixes. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; untracked new files listed separately by status. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors. |

## Commands skipped or blocked

- Story-writer validate/lint are intentionally not counted as final post-dev evidence because they require `Status: ready-for-dev`; `condamad_validate.py --final` is the applicable capsule validator for this ready-for-review story.

## DRY / No Legacy evidence

- No compatibility wrapper, alias, fallback, or parallel seed validator was added.
- The facade test was replaced with executable assertions.
- `test_backend_noop_tests.py` blocks direct `pass` test bodies, executable `assert True`, and `pytest.skip` calls without a non-empty explicit reason.
- `RG-014` added to `_condamad/stories/regression-guardrails.md`.
- `noop-test-scan-before.md`, `noop-test-scan-after.md`, `seed-validation-current-behavior.md`, and `seed-validation-decision.md` persist the before/after and decision evidence.

## Diff review

- `git diff --stat`: reviewed; changed tracked files are story-scoped.
- `git diff --check`: PASS.
- Untracked additions are expected story capsule files and `backend/app/tests/unit/test_backend_noop_tests.py`.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/ops/llm/bootstrap/use_cases_seed.py
 M backend/app/tests/unit/test_pricing_experiment_service.py
 M backend/app/tests/unit/test_seed_validation.py
?? _condamad/stories/replace-seed-validation-facade-test/
?? backend/app/tests/unit/test_backend_noop_tests.py
```

`git status --short` also reported permission warnings for `.codex-artifacts/pytest-basetemp/`, `.codex-artifacts/tmp/pytest-of-cyril/`, and `artifacts/pytest-basetemp/`; these paths were not modified.

## Remaining risks

- None for the seed validation decision: the rule now rejects both absent and blank required placeholder values while proving current canonical contracts remain valid.
- Existing raw `pass$` scan hits remain in nested control-flow code, but the AST guard proves they are not direct empty collected test bodies.
- Full backend test suite passed manually after review fixes: 3476 passed, 12 skipped, 7 warnings in 839.74s.

## Suggested reviewer focus

- Review the exact seed validation rule in `validate_use_case_seed_contracts`.
- Review `test_backend_noop_tests.py` to confirm the guard scope is strict enough without flagging legitimate nested `pass` statements.
