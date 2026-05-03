# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story metadata validation: PASS after review fix (`CS-001`, `ready-to-review`)
- Story key: `remove-bash-stripe-dev-listener`
- Source story: `_condamad/stories/remove-bash-stripe-dev-listener/00-story.md`
- Capsule path: `_condamad/stories/remove-bash-stripe-dev-listener/`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: permission warnings for artifact cache folders; no dirty file lines returned.
- Pre-existing dirty files: none reported by `git status --short`.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing `generated/` files were created.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated from story scope. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC6 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific forbidden surfaces listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `scripts/stripe-listen-webhook.sh` deleted; `removal-audit.md` classifies it as historical-facade/delete. | `rg --files scripts \| rg "stripe-listen-webhook\\.sh"` returned no hit. | PASS | |
| AC2 | `scripts/ownership-index.md` no longer has the Bash row or `blocked-support-decision`. | Targeted pytest passed; `rg --files scripts` inventory excludes the Bash listener. | PASS | |
| AC3 | `docs/billing-webhook-local-testing.md` states local dev-only Windows / PowerShell support. | `test_stripe_webhook_local_dev_assets.py` passed; forbidden active scan returned no hit. | PASS | |
| AC4 | `scripts/stripe-listen-webhook.ps1` remains the only listener asset and keeps the standardized event list and target URL. | `test_stripe_webhook_local_dev_assets.py` passed. | PASS | |
| AC5 | `scripts/start-dev-stack.ps1` still references `stripe-listen-webhook.ps1` and no `.sh` listener. | `test_start_dev_stack_script.py` passed. | PASS | |
| AC6 | `reference-baseline.txt` and `reference-after.txt` persist before/after scans. | Same scan after implementation has no active hit. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `scripts/ownership-index.md` | modified | Remove Bash listener ownership row and stale support decision. | AC2 |
| `docs/billing-webhook-local-testing.md` | modified | Document dev-only Windows / PowerShell support. | AC3 |
| `backend/app/tests/unit/test_scripts_ownership.py` | modified | Guard absence of Bash ownership row. | AC2 |
| `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` | modified | Guard PowerShell-only listener and docs. | AC3, AC4 |
| `backend/app/tests/unit/test_start_dev_stack_script.py` | modified | Guard `-WithStripe` PowerShell-only target. | AC5 |
| `_condamad/stories/remove-bash-stripe-dev-listener/generated/*` | added | Execution capsule and evidence. | AC6 |
| `_condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt` | added | Baseline scan before deletion. | AC1, AC6 |
| `_condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt` | added | After scan after deletion. | AC6 |
| `_condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md` | added | Removal classification and decision proof. | AC1 |

## Files deleted

| File | Purpose | Related AC |
|---|---|---|
| `scripts/stripe-listen-webhook.sh` | Remove non-canonical Bash listener. | AC1 |

## Tests added or updated

- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_start_dev_stack_script.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial command emitted permission warnings for artifact cache folders and no dirty file lines. Final command listed expected story changes plus unrelated `.agents/skills/condamad-story-writer/*` modifications. |
| `rg -n "stripe-listen-webhook\\.sh\|Git Bash\|WSL\|#!/usr/bin/env bash" scripts docs backend/app/tests` | repo root | PASS | 1 | Baseline had active hits; after implementation no hits. |
| `rg --files scripts` | repo root | PASS | 0 | Inventory excludes deleted Bash listener and keeps PowerShell listener. |
| `rg --files scripts \| rg "stripe-listen-webhook\\.sh"` | repo root | PASS | 1 | No deleted Bash listener path remains in scripts inventory. |
| `pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py` | `backend/` | PASS | 0 | 14 tests passed. |
| `ruff format --check app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py` | `backend/` | PASS | 0 | 3 files already formatted. |
| `ruff check app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py` | `backend/` | PASS | 0 | All checks passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-bash-stripe-dev-listener/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/remove-bash-stripe-dev-listener/00-story.md` | repo root | PASS | 0 | CONDAMAD story lint passed. |
| `pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py; ruff format --check ...; ruff check ...; python -B ...condamad_story_validate.py ...; python -B ...condamad_story_lint.py --strict ...; rg ...` | activated venv, repo root and `backend/` | PASS | 0 | Review fix rerun passed: 14 targeted tests, Ruff checks, story validate/lint, and forbidden scans. |
| `ruff format --check .` | `backend/` | PASS | 0 | 1252 files already formatted. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q` | `backend/` | BLOCKED | 124 | Timed out after 604 seconds. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reported LF/CRLF warnings. |
| `git diff --stat` | repo root | PASS | 0 | Reviewed; includes story files and unrelated `.agents/skills/condamad-story-writer/*` modifications already present in final worktree. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | yes | Timed out after 604 seconds in current environment. | Full backend regression completion is not proven in this run. | Story-targeted tests passed; backend Ruff format/lint passed; story-specific negative scans passed. |
| `./scripts/quality-gate.ps1` | conditional | Not run because full backend pytest already exceeded the validation window and quality gate would include broader checks outside this script cleanup. | End-to-end project gate not proven. | Targeted story guards, backend Ruff, story validation, and negative scans passed. |
| Local app startup | conditional | Not run because this story changes a dev-only helper, docs, and tests, not runtime app startup. | Startup smoke is not freshly proven by this story run. | `start-dev-stack.ps1` structural guard passed and backend lint/tests for touched area passed. |

## DRY / No Legacy evidence

| Pattern | Result | Classification | Action |
|---|---|---|---|
| `stripe-listen-webhook\\.sh` in `scripts docs backend/app/tests` | no hit after implementation | active legacy removed | PASS |
| `Git Bash` in `scripts docs backend/app/tests` | no hit after implementation | documentation support removed | PASS |
| `WSL` in `scripts docs backend/app/tests` | no hit after implementation | documentation support removed | PASS |
| `#!/usr/bin/env bash` in `scripts docs backend/app/tests` | no hit after implementation | Bash listener removed | PASS |
| `rg --files scripts \| rg "stripe-listen-webhook\\.sh"` | no hit | deleted file absent | PASS |

Historical mentions remain only in `_condamad/audits/**` and this story's own evidence files.

## Diff review

- `git diff --check`: PASS.
- Story diff reviewed for active code/docs/tests.
- No replacement listener, wrapper, alias, fallback, or secondary ownership registry added.
- Final `git diff --stat` also reports unrelated `.agents/skills/condamad-story-writer/*` modifications; they are outside this story and were not edited by the story patch.

## Final worktree status

```text
 M .agents/skills/condamad-story-writer/SKILL.md
 M .agents/skills/condamad-story-writer/references/story-output-contract.md
 M .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py
 M .agents/skills/condamad-story-writer/scripts/self_tests/condamad_story_validate_selftest.py
 M .agents/skills/condamad-story-writer/templates/story-template.md
 M .agents/skills/condamad-story-writer/workflow.md
 M _condamad/stories/remove-bash-stripe-dev-listener/00-story.md
 M backend/app/tests/unit/test_scripts_ownership.py
 M backend/app/tests/unit/test_start_dev_stack_script.py
 M backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py
 M docs/billing-webhook-local-testing.md
 M scripts/ownership-index.md
 D scripts/stripe-listen-webhook.sh
?? _condamad/stories/remove-bash-stripe-dev-listener/generated/
?? _condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt
?? _condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt
?? _condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md
```

`git status --short` also emitted permission warnings for `.codex-artifacts/pytest-basetemp/`, `.codex-artifacts/tmp/pytest-of-cyril/`, and `artifacts/pytest-basetemp/`.

## Remaining risks

- Full backend `pytest -q` did not complete before timeout.
- Unrelated `.agents/skills/condamad-story-writer/*` modifications are present in the worktree and should be reviewed separately from this story.

## Suggested reviewer focus

- Confirm removal of Bash/Git Bash/WSL support is acceptable for all local Stripe users.
- Review the guard tests that avoid literal forbidden scan hits while still failing if docs/scripts reintroduce the removed support.
- Treat unrelated `.agents/skills/condamad-story-writer/*` diffs as outside this story.
