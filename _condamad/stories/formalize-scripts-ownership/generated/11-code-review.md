# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/formalize-scripts-ownership/00-story.md`
- Status reviewed: `ready-for-review`
- Review date: 2026-05-02
- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable guardrails: `RG-015`, `RG-023`

## Inputs reviewed

- `_condamad/stories/formalize-scripts-ownership/00-story.md`
- `_condamad/stories/formalize-scripts-ownership/generated/03-acceptance-traceability.md`
- `_condamad/stories/formalize-scripts-ownership/generated/06-validation-plan.md`
- `_condamad/stories/formalize-scripts-ownership/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/formalize-scripts-ownership/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `scripts/ownership-index.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- Current `rg --files scripts` inventory
- Current git status and diff

## Diff summary

- Added canonical ownership registry under `scripts/ownership-index.md`.
- Added persisted before/after inventories for the story.
- Extended `backend/app/tests/unit/test_scripts_ownership.py` with exact inventory coverage, visible registry header validation, row validation, snapshot comparison, and Stripe shell blocked-decision assertions.
- Added `RG-023` to `_condamad/stories/regression-guardrails.md`.
- Generated CONDAMAD capsule evidence files under `_condamad/stories/formalize-scripts-ownership/generated/`.

## Review layers

- Diff integrity: reviewed tracked diff plus target untracked story/register files.
- Acceptance audit: AC1-AC5 mapped to registry, snapshots, tests, scans, and story validators.
- Validation audit: reviewer reran targeted tests and check-only commands in the venv.
- DRY / No Legacy audit: no duplicate registry, moved script, wrapper, re-export, or compatibility alias found.
- Guardrail audit: `RG-015` and `RG-023` evidence reviewed.

## Findings

No open findings.

## Acceptance audit

- AC1: Satisfied. Current `rg --files scripts` inventory is covered exactly by `scripts/ownership-index.md`, and duplicate registry rows are rejected.
- AC2: Satisfied. `test_scripts_ownership_registry_exposes_required_header` guards the visible Markdown header, and `test_scripts_ownership_rows_are_actionable` guards row values.
- AC3: Satisfied. The baseline snapshot excludes `scripts/ownership-index.md`; the after snapshot equals baseline plus that registry file. This proves this story did not move existing scripts without freezing future legitimate additions.
- AC4: Satisfied. `scripts/stripe-listen-webhook.sh` is recorded with `needs-user-decision` and `blocked-support-decision`.
- AC5: Satisfied. Story validator and strict linter pass in the reviewer run.

## Validation audit

Reviewer commands:

| Command | Result |
|---|---|
| `git status --short` | PASS, target changes visible; unrelated untracked CONDAMAD story directories also present. |
| `git diff --stat` | PASS, tracked diff limited to guardrail registry and script ownership test. |
| `rg --files scripts` | PASS, 21 current paths including `scripts/ownership-index.md`. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_scripts_ownership.py` | PASS, `6 passed in 0.05s`. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | PASS, `3 passed in 0.09s`. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format --check app/tests/unit/test_scripts_ownership.py` | PASS, `1 file already formatted`. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check app/tests/unit/test_scripts_ownership.py` | PASS, `All checks passed!`. |
| `git diff --check` | PASS, CRLF warnings only. |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/formalize-scripts-ownership/00-story.md` | PASS. |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/formalize-scripts-ownership/00-story.md` | PASS. |
| `rg -n "stripe-listen" scripts\\ownership-index.md` | PASS, both Stripe listener rows found and `.sh` has blocked decision. |
| `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts backend/app/tests/unit/test_scripts_ownership.py` | PASS with expected/pre-existing hits only: registry text forbids aliases; LLM release and activation scripts contain pre-existing LLM wording outside this story's behavior. |
| `rg -n "5 passed|6 passed|visible registry header|visible Markdown header|AC2|CHANGES_REQUESTED|ACCEPTABLE_WITH_LIMITATIONS" _condamad\\stories\\formalize-scripts-ownership\\generated\\10-final-evidence.md _condamad\\stories\\formalize-scripts-ownership\\generated\\11-code-review.md` | PASS, final evidence references AC2 header coverage and `6 passed after review fixes`. |

Full backend `pytest -q` remains not treated as passed because implementation evidence records a timeout and the reviewer did not rerun the full suite.

## DRY / No Legacy audit

- No second `scripts/ownership-index.md` equivalent was found.
- No script was moved, wrapped, aliased, or re-exported.
- No behavior change was made to scripts.
- The permanent guard routes future script additions through `scripts/ownership-index.md` instead of encoding this story's historical inventory as a lasting ban.

## Commands run by reviewer

See validation audit table above.

## Residual risks

- Full backend `pytest -q` did not complete in the implementation evidence and was not rerun by the reviewer.
- Several unrelated CONDAMAD story directories remain untracked in the worktree and were not reviewed as part of this single-target review.
- `git status --short` emits permission warnings for existing pytest artifact directories under `.codex-artifacts/` and `artifacts/`.

## Verdict

ACCEPTABLE_WITH_LIMITATIONS

No actionable findings remain. The implementation and refreshed capsule evidence satisfy the reviewed ACs; the limitation is the documented full-suite timeout.
