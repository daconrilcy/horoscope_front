# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `cover-both-backend-test-roots-in-cross-import-guard`
- Source story: `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/00-story.md`
- Capsule path: `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/`

## Preflight

- Repository root: `C:/dev/horoscope_front`
- Initial `git status --short`: permission warnings on temporary pytest/artifact directories; no tracked dirty files with `git -c status.showUntrackedFiles=no status --short`.
- Pre-existing dirty files: none detected in tracked files.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes, required generated files were created because only `00-story.md` existed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created for execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC4. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completion evidence in progress. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/tests/unit/test_backend_test_helper_imports.py` now uses `Path(__file__).resolve().parents[3]`; `test_backend_root_resolves_backend_directory` asserts the backend root and `pyproject.toml`. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py` passed with 3 tests. | PASS | Root now resolves to `backend`, not `backend/app`. |
| AC2 | `test_backend_test_roots_cover_app_and_backend_tests` asserts `TEST_ROOTS == ("app/tests", "tests")` relative to `BACKEND_ROOT` and checks both directories exist. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py` passed. | PASS | Both real backend test roots are covered. |
| AC3 | Existing AST guard remains in `test_backend_tests_do_not_import_executable_test_modules` and now iterates both real roots. | Targeted pytest guard passed; `rg` forbidden import scan returned zero hits. | PASS | `rg` exit status 1 is classified as expected zero-hit. |
| AC4 | `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md` and `cross-import-guard-after.md` persist before/after evidence. | Baseline and after artifacts record commands and root coverage evidence. | PASS | Allowlist register is zero-entry. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/tests/unit/test_backend_test_helper_imports.py` | modified | Correct backend root and assert both backend test roots. | AC1, AC2, AC3 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/00-story.md` | modified | Mark story tasks complete and status ready for review. | AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-allowlist.md` | added | Persist zero-entry allowlist register. | AC3, AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md` | added | Persist baseline evidence. | AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-after.md` | added | Persist after evidence. | AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/01-execution-brief.md` | added | Required CONDAMAD execution capsule. | AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/03-acceptance-traceability.md` | added | Required AC traceability. | AC1-AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/04-target-files.md` | added | Required file/search map. | AC1-AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/05-implementation-plan.md` | added | Focused implementation plan. | AC1-AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/06-validation-plan.md` | added | Required validation plan. | AC1-AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/07-no-legacy-dry-guardrails.md` | added | Required No Legacy / DRY guardrails. | AC3 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/09-dev-log.md` | added | Implementation and validation log. | AC4 |
| `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/10-final-evidence.md` | added | Final reviewer evidence. | AC1-AC4 |

## Files deleted

None.

## Tests added or updated

- Updated `backend/app/tests/unit/test_backend_test_helper_imports.py` from 1 guard test to 3 guard tests.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git rev-parse --show-toplevel` | repo root | PASS | 0 | Repository root is `C:/dev/horoscope_front`. |
| `git status --short` | repo root | PASS_WITH_LIMITATIONS | 0 | Command returned permission warnings for temp artifact directories; tracked status was checked separately. |
| `git -c status.showUntrackedFiles=no status --short` | repo root | PASS | 0 | No tracked dirty files before implementation. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_helper_imports.py` | repo root | PASS | 0 | Baseline before fix: `1 passed in 0.54s`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "from app\.tests\.(integration\|unit\|regression)\.test_\|from tests\.(integration\|unit\|regression)\.test_" app/tests tests -g "test_*.py"` | repo root | PASS | 1 | Baseline zero hits; exit 1 is expected for no matches. |
| PowerShell parent inspection of `backend\app\tests\unit\test_backend_test_helper_imports.py` | repo root | PASS | 0 | `parents[2]` was `backend/app`; `parents[3]` was `backend`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_helper_imports.py` | repo root | PASS | 0 | After fix: `3 passed in 0.66s`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "from app\.tests\.(integration\|unit\|regression)\.test_\|from tests\.(integration\|unit\|regression)\.test_" app/tests tests -g "test_*.py"` | repo root | PASS | 1 | After fix zero hits; exit 1 is expected for no matches. |
| `rg -n "test_backend_test_helper_imports\|FORBIDDEN_PREFIXES\|from app\.tests\.(integration\|unit\|regression)\.test_" backend _condamad -g "*.py" -g "*.md"` | repo root | PASS | 0 | Hits are expected guard/story/audit references; no duplicate active guard implementation. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | `1242 files left unchanged`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | `All checks passed!`. |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 0 | `3481 passed, 12 skipped in 682.51s`. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; command does not include untracked generated evidence files. |
| `git diff --check` | repo root | PASS | 0 | No whitespace or conflict marker errors; Git emitted expected LF/CRLF warning for modified Python file. |
| `git -c status.showUntrackedFiles=all status --short -- backend/app/tests/unit/test_backend_test_helper_imports.py _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard` | repo root | PASS | 0 | Expected modified guard and story evidence files. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- The AST guard remains in the existing canonical owner: `backend/app/tests/unit/test_backend_test_helper_imports.py`.
- No duplicate active guard was introduced.
- `cross-import-allowlist.md` is a zero-entry register.
- Forbidden import scan returned zero active hits under `backend/app/tests` and `backend/tests`.
- Duplicate-owner search hits are classified as expected story/audit references or the canonical guard file, not active duplicate implementations.

## Diff review

- Application diff is limited to `backend/app/tests/unit/test_backend_test_helper_imports.py`.
- Story/capsule diff is limited to this story directory.
- No dependencies, requirements file, DB harness, pytest topology, or app behavior changed.
- `git diff --check` passed.

## Final worktree status

Final targeted status:

```text
 M backend/app/tests/unit/test_backend_test_helper_imports.py
 M _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/00-story.md
?? _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-allowlist.md
?? _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md
?? _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-after.md
?? _condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/
```

Full `git status --short` reports the same story files plus permission warnings for temporary artifact directories under `.codex-artifacts/`, `artifacts/`, and `backend/.tmp-pytest/`.

## Remaining risks

None identified. Full backend suite passed.

## Suggested reviewer focus

Review the corrected `parents[3]` root calculation and the two explicit assertions that lock `app/tests` and `tests` as scanned roots.
