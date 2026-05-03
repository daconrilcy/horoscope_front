# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `classify-natal-cross-tool-dev-report`
- Source story: `_condamad/stories/classify-natal-cross-tool-dev-report/00-story.md`
- Capsule path: `_condamad/stories/classify-natal-cross-tool-dev-report`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? _condamad/stories/classify-natal-cross-tool-dev-report/` plus cache access warnings.
- Pre-existing dirty files: untracked story capsule directory.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-013, RG-015, RG-023 mapped. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed with final validation evidence. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py` runs `scripts/natal-cross-tool-report-dev.py` in subprocess with `CI=true` and expects exit code 2 plus `dev-only` / `forbidden in CI`. | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` PASS; full `pytest -q` PASS. | PASS | Refusal message comes from existing `ensure_dev_only_runtime`. |
| AC2 | `docs/natal-pro-dev-guide.md` and `dev-only-contract.md` document `.\.venv\Scripts\Activate.ps1` before the script command. | `rg -n "natal-cross-tool-report-dev.py\|Activate.ps1" docs scripts/ownership-index.md backend/README.md` PASS. | PASS | `backend/README.md` already had the command; docs now carry story-specific classification. |
| AC3 | AST guard scans `backend/app` outside `app/tests` and fails on any `app.tests.golden` import; only the dev script remains allowed. | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` PASS; `rg -n "app\.tests\.golden" backend/app scripts -g "*.py"` hits only test/golden surfaces plus the classified dev script. | PASS | Runtime backend packages remain clean. |
| AC4 | AST/file guard proves no root `scripts/cross_tool_report*.py` helper exists and the dev script imports `scripts.cross_tool_report`. | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` PASS; `rg -n "cross_tool_report" scripts backend` shows expected helper/test/story hits only. | PASS | Existing `backend/scripts/cross_tool_report.py` remains the single helper. |
| AC5 | Required capsule files, `import-baseline.txt`, `import-after.txt`, and `dev-only-contract.md` are present. | Story validate PASS; story lint PASS; diff check PASS. | PASS | Final evidence complete. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `scripts/natal-cross-tool-report-dev.py` | modified | Add French dev-only module/function documentation. | AC1, AC3 |
| `docs/natal-pro-dev-guide.md` | modified | Document dev-only execution with venv activation and CI/import boundary. | AC2, AC3 |
| `backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py` | added | Guard CI refusal, runtime golden import boundary, and helper duplication. | AC1, AC3, AC4 |
| `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | modified | Register new script quality test required by RG-015. | AC3, AC4 |
| `_condamad/stories/classify-natal-cross-tool-dev-report/import-baseline.txt` | added | Persist baseline import/reference evidence. | AC3, AC4 |
| `_condamad/stories/classify-natal-cross-tool-dev-report/import-after.txt` | added | Persist after-scan import/reference evidence. | AC3, AC4 |
| `_condamad/stories/classify-natal-cross-tool-dev-report/dev-only-contract.md` | added | Persist dev-only contract and execution command. | AC1, AC2, AC3, AC4 |
| `_condamad/stories/classify-natal-cross-tool-dev-report/generated/*` | added/modified | CONDAMAD traceability, plan, guardrails and final evidence. | AC5 |

## Files deleted

None.

## Tests added or updated

- `backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py` added.
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` updated so RG-015 continues to pass.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` | `backend/` | PASS | 0 | 3 tests passed. |
| `pytest -q app/tests/unit/test_cross_tool_report.py` | `backend/` | PASS | 0 | 3 tests passed. |
| `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py app/tests/unit/test_cross_tool_report.py` | `backend/` | PASS | 0 | 6 tests passed. |
| `pytest -q app/tests/unit/test_backend_test_helper_imports.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py` | `backend/` | FAIL then PASS | 1 then 0 | Initial RG-015 failure identified missing ownership row for the new script test; after registry update, 12 tests passed. |
| `ruff format app/tests/unit/test_natal_cross_tool_report_dev_script.py ..\scripts\natal-cross-tool-report-dev.py` | `backend/` | PASS | 0 | 1 file reformatted, 1 unchanged. |
| `ruff format --check .` | `backend/` | PASS | 0 | 1252 files already formatted. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q` | `backend/` | FAIL then PASS | 124 then 0 | First run timed out after 604s; rerun with larger timeout passed: 3546 passed, 12 skipped in 535.62s. |
| `rg -n "app\.tests\.golden" backend/app scripts -g "*.py"` | repo root | PASS | 0 | Hits limited to test/golden modules, expected tests, and the classified dev script. |
| `rg -n "cross_tool_report" scripts backend` | repo root | PASS | 0 | No root duplicate helper; expected helper/test/story hits. |
| `rg -n "natal-cross-tool-report-dev.py\|Activate.ps1" docs scripts/ownership-index.md backend/README.md` | repo root | PASS | 0 | Venv activation and script command documented. |
| `rg -n "from app\.tests\.(integration\|unit\|regression)\.test_\|from tests\.integration\.test_" backend/app/tests backend/tests -g "test_*.py"` | repo root | PASS | 1 | No hits for forbidden cross-test module imports. |
| `rg --files backend -g "test_*.py" \| rg "(docs\|scripts?\|ops\|secret\|security)"` | repo root | PASS | 0 | Inventory includes new script test and is covered by ownership registry. |
| `rg --files scripts` | repo root | PASS | 0 | Script inventory unchanged; no duplicate helper. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/classify-natal-cross-tool-dev-report/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/classify-natal-cross-tool-dev-report/00-story.md` | repo root | PASS | 0 | CONDAMAD story lint passed. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reports LF-to-CRLF warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app startup | no | Story touches a dev script contract, docs, tests, and evidence only; no app runtime path changed. | Low; runtime startup not exercised by this story. | Full backend pytest passed. Standard backend start remains `.\.venv\Scripts\Activate.ps1; cd backend; uvicorn app.main:app --reload`. |

## DRY / No Legacy evidence

- `app.tests.golden` search hits are classified: runtime backend hits are absent; `backend/app/tests/**` hits are expected test fixtures/tests; `scripts/natal-cross-tool-report-dev.py` is explicitly dev-only.
- `cross_tool_report` search hits are classified: `backend/scripts/cross_tool_report.py` is the single helper; root `scripts/` has no duplicate helper; test/story hits are expected guards/evidence.
- RG-013 covered by test helper import guard and targeted negative scan.
- RG-015 covered by `test_backend_quality_test_ownership.py` after registering the new script test.
- RG-023 covered by `test_scripts_ownership.py` and `rg --files scripts`; script inventory unchanged.

## Diff review

- `git diff --stat` reviewed: expected tracked files only; untracked story capsule and new test are expected.
- `git diff --check` PASS, with line-ending warnings only.

## Final worktree status

` M _condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
` M docs/natal-pro-dev-guide.md`
` M scripts/natal-cross-tool-report-dev.py`
`?? _condamad/stories/classify-natal-cross-tool-dev-report/`
`?? backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py`

Git also reports permission warnings while scanning existing pytest cache/artifact directories.

## Remaining risks

None.

## Suggested reviewer focus

- Review that the dev-only classification is sufficient instead of moving the command under `backend/scripts`.
- Review the AST guard scope for `app.tests.golden` runtime imports.
- Review the added RG-015 ownership row for the new script test.
