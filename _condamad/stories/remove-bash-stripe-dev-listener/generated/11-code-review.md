# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/remove-bash-stripe-dev-listener/00-story.md`
- Review date: 2026-05-03
- Scope reviewed: story diff, generated capsule evidence, removal audit, active docs/scripts/tests, regression guardrails `RG-023` and `RG-024`.

## Inputs reviewed

- `_condamad/stories/remove-bash-stripe-dev-listener/00-story.md`
- `_condamad/stories/remove-bash-stripe-dev-listener/generated/03-acceptance-traceability.md`
- `_condamad/stories/remove-bash-stripe-dev-listener/generated/06-validation-plan.md`
- `_condamad/stories/remove-bash-stripe-dev-listener/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/remove-bash-stripe-dev-listener/generated/10-final-evidence.md`
- `_condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt`
- `_condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt`
- `_condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md`
- `scripts/ownership-index.md`
- `scripts/start-dev-stack.ps1`
- `scripts/stripe-listen-webhook.ps1`
- `docs/billing-webhook-local-testing.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_start_dev_stack_script.py`

## Diff summary

- Deleted `scripts/stripe-listen-webhook.sh`.
- Removed the Bash listener row and stale `blocked-support-decision` from `scripts/ownership-index.md`.
- Updated the local Stripe runbook to document Windows / PowerShell dev-only support.
- Tightened tests for ownership coverage, PowerShell-only Stripe listener assets, and `start-dev-stack.ps1 -WithStripe`.
- Fixed story metadata to the current story validator contract: `# Story CS-001 ...` and `Status: ready-to-review`.
- Added and updated CONDAMAD evidence artifacts for baseline, after-scan, removal classification, final evidence, and review result.

## Findings

No actionable findings.

## Acceptance audit

- AC1: PASS. `scripts/stripe-listen-webhook.sh` is deleted, `removal-audit.md` classifies the surface, and `rg --files scripts | rg "stripe-listen-webhook\\.sh"` has no hit.
- AC2: PASS. `scripts/ownership-index.md` no longer lists the Bash listener or `blocked-support-decision`; `test_scripts_ownership.py` passes and `rg --files scripts` inventory remains aligned.
- AC3: PASS. `docs/billing-webhook-local-testing.md` states local dev-only Windows / PowerShell support; active forbidden scan has no hit.
- AC4: PASS. `scripts/stripe-listen-webhook.ps1` remains canonical and the standardized event list / target URL are guarded by tests.
- AC5: PASS. `scripts/start-dev-stack.ps1 -WithStripe` remains PowerShell-only and Stripe remains opt-in; targeted guard passes.
- AC6: PASS. `reference-baseline.txt`, `reference-after.txt`, and final evidence are present and consistent with the current scans.

## Validation audit

- Reviewer reran targeted pytest from `backend/` after activating `.\.venv\Scripts\Activate.ps1`: `14 passed in 0.12s`.
- Reviewer reran `ruff format --check` on touched backend tests from `backend/`: PASS.
- Reviewer reran `ruff check` on touched backend tests from `backend/`: PASS.
- Reviewer reran CONDAMAD story validation from the activated venv: PASS.
- Reviewer reran CONDAMAD strict story lint from the activated venv: PASS.
- Reviewer reran active forbidden scan for `stripe-listen-webhook\\.sh`, `Git Bash`, `WSL`, and `#!/usr/bin/env bash` under `scripts docs backend/app/tests`: no hits.
- Reviewer reran deleted script inventory scan: no `scripts/stripe-listen-webhook.sh` hit.
- Reviewer reran `git diff --check` on story-scoped files: PASS, with LF/CRLF warnings only.
- Full backend `pytest -q` was not rerun to completion in this review. Existing final evidence records a previous timeout after 604 seconds.

## DRY / No Legacy audit

- No active Bash listener, shell wrapper, alias, fallback, re-export, or replacement listener path was found.
- No active docs/tests/scripts expose Git Bash or WSL as a supported Stripe listener path.
- `RG-023` is preserved through the ownership inventory test and current script inventory.
- `RG-024` is preserved through the start-dev-stack guard: default startup remains Stripe-free and Stripe remains opt-in via `-WithStripe`.

## Commands run by reviewer

```powershell
git status --short -- '_condamad/stories/remove-bash-stripe-dev-listener' backend/app/tests/unit/test_scripts_ownership.py backend/app/tests/unit/test_start_dev_stack_script.py backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py docs/billing-webhook-local-testing.md scripts/ownership-index.md scripts/stripe-listen-webhook.sh
git diff --stat -- '_condamad/stories/remove-bash-stripe-dev-listener' backend/app/tests/unit/test_scripts_ownership.py backend/app/tests/unit/test_start_dev_stack_script.py backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py docs/billing-webhook-local-testing.md scripts/ownership-index.md scripts/stripe-listen-webhook.sh
git diff -- '_condamad/stories/remove-bash-stripe-dev-listener' backend/app/tests/unit/test_scripts_ownership.py backend/app/tests/unit/test_start_dev_stack_script.py backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py docs/billing-webhook-local-testing.md scripts/ownership-index.md scripts/stripe-listen-webhook.sh
rg -n "stripe-listen-webhook\\.sh|Git Bash|WSL|#!/usr/bin/env bash" scripts docs backend/app/tests
rg --files scripts | rg "stripe-listen-webhook\\.sh"
.\.venv\Scripts\Activate.ps1
Push-Location backend
pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py
ruff format --check app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py
ruff check app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py
Pop-Location
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-bash-stripe-dev-listener/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/remove-bash-stripe-dev-listener/00-story.md
git diff --check -- '_condamad/stories/remove-bash-stripe-dev-listener' backend/app/tests/unit/test_scripts_ownership.py backend/app/tests/unit/test_start_dev_stack_script.py backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py docs/billing-webhook-local-testing.md scripts/ownership-index.md scripts/stripe-listen-webhook.sh
```

## Residual risks

- Full backend `pytest -q` completion is still not proven for this story because the implementation evidence records a timeout after 604 seconds and this review did not rerun the full suite.
- Unrelated `.agents/skills/condamad-story-writer/*` modifications remain in the wider worktree and are outside this story review.

## Verdict

ACCEPTABLE_WITH_LIMITATIONS
