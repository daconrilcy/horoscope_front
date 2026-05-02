# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `harden-local-dev-stack-script`
- Source story: `_condamad/stories/harden-local-dev-stack-script/00-story.md`
- Capsule path: `_condamad/stories/harden-local-dev-stack-script`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: untracked CONDAMAD story folders; access warnings for pytest temp artifact directories.
- Pre-existing dirty files: `_condamad/stories/classify-critical-load-scenarios/`, `_condamad/stories/classify-natal-cross-tool-dev-report/`, `_condamad/stories/harden-local-dev-stack-script/`, `_condamad/stories/portable-llm-release-readiness/`
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails read: `_condamad/stories/regression-guardrails.md` (`RG-015`, `RG-023`, new `RG-024`)
- Capsule generated: yes, generated files created under this directory.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story exists. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC5. |
| `generated/04-target-files.md` | yes | yes | PASS | Targeted files and searches listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `scripts/start-dev-stack.ps1` defines `-WithStripe`; base `$wtArguments` contains only backend and frontend tabs; Stripe script path and CLI check are outside the default path. | `pytest -q app/tests/unit/test_start_dev_stack_script.py` passed; `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help` passed without requiring Stripe. | PASS | Default branch ignores Stripe. |
| AC2 | `Assert-CommandExists -Name "stripe"` and `Assert-PathExists -Path $stripeScriptPath` are inside `if ($WithStripe)` with install hint `relancez sans -WithStripe`. | `pytest -q app/tests/unit/test_start_dev_stack_script.py` passed; Stripe branch scan classified hits as expected conditional/documentation hits. | PASS | Explicit Stripe mode requires CLI. |
| AC3 | `docs/local-dev-stack.md` documents default and `-WithStripe`; `docs/development-guide-backend.md` links the local stack doc. | `rg -n "start-dev-stack.ps1|WithStripe" docs` returned expected documentation hits. | PASS | No root `README.md` exists; documentation lives under `docs/`. |
| AC4 | No `SkipStripe`, compatibility alias, or fallback branch was added. | `rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1` returned zero hits (exit 1 expected for no matches). | PASS | No silent fallback. |
| AC5 | Capsule files generated; final evidence and traceability updated. | Story validate and lint passed after venv activation. Full `pytest -q` timed out after 604s with no failure details, so final outcome is limited. | PASS_WITH_LIMITATIONS | Targeted checks passed; full suite timeout remains a validation limitation. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/harden-local-dev-stack-script/generated/01-execution-brief.md` | generated | CONDAMAD execution brief | AC5 |
| `_condamad/stories/harden-local-dev-stack-script/generated/03-acceptance-traceability.md` | generated | AC evidence plan | AC1-AC5 |
| `_condamad/stories/harden-local-dev-stack-script/generated/04-target-files.md` | generated | Target map | AC1-AC5 |
| `_condamad/stories/harden-local-dev-stack-script/generated/06-validation-plan.md` | generated | Validation plan | AC1-AC5 |
| `_condamad/stories/harden-local-dev-stack-script/generated/07-no-legacy-dry-guardrails.md` | generated | No Legacy guardrails | AC4 |
| `_condamad/stories/harden-local-dev-stack-script/generated/10-final-evidence.md` | generated | Final evidence shell | AC5 |
| `_condamad/stories/harden-local-dev-stack-script/dev-stack-usage-evidence.md` | added | Persist local script usage evidence | AC3 |
| `_condamad/stories/regression-guardrails.md` | modified | Add `RG-024` invariant for Stripe opt-in dev stack and align `RG-015` inventory evidence with singular/plural script tests. | AC1, AC2, AC4 |
| `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` | modified | Register the new script-quality test in the canonical `RG-015` ownership registry. | AC5 |
| `scripts/start-dev-stack.ps1` | modified | Add `-WithStripe` and `-Help`; make Stripe checks/tab conditional | AC1, AC2 |
| `backend/app/tests/unit/test_start_dev_stack_script.py` | added | Guard default and Stripe branches plus docs | AC1, AC2, AC3, AC4 |
| `backend/app/tests/unit/test_backend_quality_test_ownership.py` | modified | Ensure `RG-015` covers singular `script` and plural `scripts` test names. | AC5 |
| `docs/local-dev-stack.md` | added | Document default and Stripe modes | AC3 |
| `docs/development-guide-backend.md` | modified | Link local stack script documentation | AC3 |
| `scripts/ownership-index.md` | modified | Update script ownership validation command/status after hardening | AC1, AC2 |

## Files deleted

None.

## Tests added or updated

| File | Change type | Purpose |
|---|---|---|
| `backend/app/tests/unit/test_start_dev_stack_script.py` | added | Pytest architecture guard for local dev script branches and documentation. |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Pre-existing untracked story folders recorded; artifact access warnings observed. |
| `pytest -q app/tests/unit/test_start_dev_stack_script.py` | `backend` | FAIL | 1 | Initial run caught missing normalized `scripts/start-dev-stack.ps1` doc text; fixed in `docs/local-dev-stack.md`. |
| `pytest -q app/tests/unit/test_start_dev_stack_script.py` | `backend` | PASS | 0 | 3 tests passed. |
| `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | FAIL | 1 | Review follow-up showed the singular `test_start_dev_stack_script.py` needed canonical ownership coverage; the registry row and guard pattern were aligned. |
| `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | PASS | 0 | 3 tests passed. |
| `pytest -q app/tests/unit/test_scripts_ownership.py` | `backend` | PASS | 0 | 6 tests passed. |
| `pytest -q app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py` | `backend` | PASS | 0 | 12 tests passed. |
| `pytest -q app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py` | `backend` | PASS | 0 | Post-review rerun after `RG-015` evidence correction: 12 tests passed. |
| `ruff format --check app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | PASS | 0 | 2 files already formatted. |
| `ruff check app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | PASS | 0 | All checks passed; one earlier run reported a non-blocking Ruff cache write warning. |
| `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help` | repo root | FAIL | 1 | Initial run failed because `-Help` was not an explicit parameter; fixed by adding `-Help`. |
| `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help` | repo root | PASS | 0 | Printed parameter summary including `-WithStripe` and `-Help`; did not require Stripe. |
| `rg -n "start-dev-stack.ps1|WithStripe" docs` | repo root | PASS | 0 | Expected hits in `docs/local-dev-stack.md` and `docs/development-guide-backend.md`. |
| `rg -n "Get-Command stripe|stripe-listen-webhook.ps1|WithStripe|SkipStripe" scripts/start-dev-stack.ps1 docs` | repo root | PASS | 0 | Hits are expected conditional code and documentation; no `SkipStripe` hit. |
| `rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1` | repo root | PASS | 1 | No hits; exit 1 is expected for a negative scan. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\harden-local-dev-stack-script\00-story.md` | repo root | PASS | 0 | CONDAMAD story validation passed. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\harden-local-dev-stack-script\00-story.md` | repo root | PASS | 0 | CONDAMAD story lint passed. |
| `ruff format --check .` | `backend` | PASS | 0 | 1249 files already formatted. |
| `ruff check .` | `backend` | PASS | 0 | All checks passed. |
| `pytest -q` | `backend` | BLOCKED | 124 | Timed out after 604 seconds without failure output. |
| `git diff --stat` | repo root | PASS | 0 | Story-related tracked diff reviewed; untracked new files not shown by git stat. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; line-ending warnings only. |
| `git status --short` | repo root | PASS | 0 | Final worktree status recorded; artifact access warnings observed. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Full local stack launch via `.\scripts\start-dev-stack.ps1` | yes | Not launched because it opens persistent Windows Terminal tabs and long-running backend/frontend processes in this shared session. | Runtime environment issues with `wt`, `npm`, or app boot could remain outside static/script guards. | `-Help` execution passed; pytest guard validates command composition; exact manual commands documented in `docs/local-dev-stack.md`. |
| Full backend `pytest -q` completion | yes | Command timed out after 604 seconds. | A regression outside the script/test/doc surface may remain undetected by this run. | Targeted story guards, ownership guards, story validators, Ruff checks, and scans passed. |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `Get-Command stripe` | `scripts/start-dev-stack.ps1` | test_guard_expected_hit | Kept inside `Assert-CommandExists`, called for Stripe only inside `if ($WithStripe)`. | PASS |
| `stripe-listen-webhook.ps1` | `scripts/start-dev-stack.ps1`, `docs/local-dev-stack.md`, `docs/billing-webhook-local-testing.md` | allowed_canonical_reference | Reused existing listener script; no duplicate listener logic added. | PASS |
| `WithStripe` | `scripts/start-dev-stack.ps1`, `docs/local-dev-stack.md`, `docs/development-guide-backend.md` | canonical_opt_in_flag | Explicit opt-in branch documented and tested. | PASS |
| `SkipStripe` | none | negative_evidence | No compatibility inverse switch introduced. | PASS |
| `fallback|compat|alias|SkipStripe` in `scripts/start-dev-stack.ps1` | none | negative_evidence | No silent fallback, alias, or compatibility shim introduced. | PASS |

## Diff review

- `git diff --stat` and `git diff --check` reviewed.
- Tracked diff is limited to script/doc/ownership files; new untracked story, test, and doc files are expected.
- Line-ending warnings were reported by Git for existing text files; no whitespace errors were reported.

## Final worktree status

Final status recorded after implementation:

```text
M _condamad/stories/regression-guardrails.md
M _condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md
M backend/app/tests/unit/test_backend_quality_test_ownership.py
M docs/development-guide-backend.md
M scripts/ownership-index.md
M scripts/start-dev-stack.ps1
?? _condamad/stories/classify-critical-load-scenarios/
?? _condamad/stories/classify-natal-cross-tool-dev-report/
?? _condamad/stories/harden-local-dev-stack-script/
?? _condamad/stories/portable-llm-release-readiness/
?? backend/app/tests/unit/test_start_dev_stack_script.py
?? docs/local-dev-stack.md
```

`git status --short` also reported access warnings for pytest artifact temp directories.

## Remaining risks

- Full backend `pytest -q` did not complete within 604 seconds.
- The local stack was not launched because it opens persistent Windows Terminal tabs; commands are documented for manual execution.

## Suggested reviewer focus

- Review the PowerShell branch composition in `scripts/start-dev-stack.ps1`.
- Review whether adding `RG-024` is the desired durable invariant wording.
- Decide whether the full-suite timeout is acceptable for this ops-script story.
