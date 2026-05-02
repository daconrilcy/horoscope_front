# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/harden-local-dev-stack-script/00-story.md`
- Scope reviewed: local worktree changes for `scripts/start-dev-stack.ps1`, docs, tests, story capsule, and regression guardrails.
- Review date: 2026-05-02
- Review state: post-fix rerun after CR-1 and CR-2 corrections.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- `scripts/start-dev-stack.ps1`
- `backend/app/tests/unit/test_start_dev_stack_script.py`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `docs/local-dev-stack.md`
- `docs/development-guide-backend.md`
- `scripts/ownership-index.md`

## Diff summary

- `scripts/start-dev-stack.ps1` adds `-WithStripe` and `-Help`; Stripe CLI/path validation and Stripe tab creation are conditional.
- `backend/app/tests/unit/test_start_dev_stack_script.py` adds static guards for default mode, Stripe mode, and documentation.
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md` registers `backend/app/tests/unit/test_start_dev_stack_script.py` and includes it in the targeted quality command.
- `backend/app/tests/unit/test_backend_quality_test_ownership.py` treats singular `script` and plural `scripts` test names as ownership-controlled.
- `_condamad/stories/regression-guardrails.md` aligns `RG-015` inventory evidence with the executable `scripts?` guard and adds `RG-024`.
- `generated/10-final-evidence.md` records the post-review ownership fix and latest targeted validation.

## Review layers

- Diff integrity: reviewed tracked diff and explicitly read untracked target files. Unrelated untracked story folders remain out of scope.
- Acceptance audit: AC1-AC5 have targeted evidence; full-suite timeout remains documented as a limitation.
- Validation audit: targeted pytest, targeted Ruff, PowerShell help, story validate/lint, scans, `RG-015` inventory, and `git diff --check` were rerun.
- DRY / No Legacy audit: no duplicate Stripe listener, no `SkipStripe`, no fallback, no compatibility alias.
- Regression guardrail audit: `RG-015`, `RG-023`, and `RG-024` have executable or objective evidence.

## Findings

No open findings.

Resolved:

- CR-1 Medium - `RG-015` documented inventory command missed singular `script` tests. Fixed by documenting `scripts?` and keeping the executable guard aligned.
- CR-2 Low - `generated/10-final-evidence.md` was stale after the ownership fix. Fixed by updating file-change evidence, command evidence, and final worktree status.

## Acceptance audit

- AC1: pass. Default `$wtArguments` contain Backend and Frontend only; Stripe validation and tab creation are gated by `if ($WithStripe)`.
- AC2: pass. `Assert-CommandExists -Name "stripe"` and Stripe script existence checks run only inside `if ($WithStripe)`, with an explicit hint to relaunch without `-WithStripe`.
- AC3: pass. `docs/local-dev-stack.md` documents `scripts/start-dev-stack.ps1` and `-WithStripe`; `docs/development-guide-backend.md` links it. The repository has no root `README.md`, so docs-only validation is acceptable with that limitation recorded.
- AC4: pass. No `SkipStripe`, fallback, compatibility switch, or alias found in `scripts/start-dev-stack.ps1`.
- AC5: pass with limitation. Story validate/lint pass; targeted guards and persistent evidence pass. Full backend `pytest -q` remains a recorded timeout in final evidence.

## Validation audit

Reviewer-rerun commands:

```powershell
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py
```

Result: pass, `12 passed in 0.16s`.

```powershell
.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py; ruff check app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py
```

Result: pass.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help
```

Result: pass; printed syntax including `-WithStripe` and `-Help`.

```powershell
rg -n "Get-Command stripe|stripe-listen-webhook.ps1|WithStripe|SkipStripe" scripts/start-dev-stack.ps1 docs
rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1
```

Result: expected Stripe/WithStripe hits; no fallback/compat/alias/SkipStripe hits.

```powershell
rg --files backend -g "test_*.py" | rg "(docs|scripts?|ops|secret|security)"
```

Result: includes `backend\app\tests\unit\test_start_dev_stack_script.py`.

```powershell
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\harden-local-dev-stack-script\00-story.md; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\harden-local-dev-stack-script\00-story.md
```

Result: pass.

```powershell
git diff --check
```

Result: pass with line-ending warnings only.

## DRY / No Legacy audit

- No duplicate Stripe listener implementation was introduced.
- The existing `scripts/stripe-listen-webhook.ps1` remains the referenced listener.
- No inverse `SkipStripe` compatibility switch was added.
- No silent fallback was found for explicit Stripe mode.

## Residual risks

- Full `pytest -q` is recorded as timed out in final evidence and was not rerun to completion during review.
- The local stack was not launched because it opens persistent Windows Terminal tabs.
- The worktree contains unrelated untracked story folders; they were not part of this single-target review.

## Verdict

ACCEPTABLE_WITH_LIMITATIONS
