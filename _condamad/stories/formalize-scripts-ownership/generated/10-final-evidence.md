# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `formalize-scripts-ownership`
- Source story: `_condamad/stories/formalize-scripts-ownership/00-story.md`
- Capsule path: `_condamad/stories/formalize-scripts-ownership/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: untracked CONDAMAD story directories already present.
- Pre-existing dirty files: `_condamad/stories/classify-critical-load-scenarios/`, `_condamad/stories/classify-natal-cross-tool-dev-report/`, `_condamad/stories/formalize-scripts-ownership/`, `_condamad/stories/harden-local-dev-stack-script/`, `_condamad/stories/portable-llm-release-readiness/`.
- AGENTS.md files considered: `AGENTS.md`.
- Guardrail registry consulted: `_condamad/stories/regression-guardrails.md`.
- Capsule generated: yes, required generated files added.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story exists. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC5. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Contains executable checks. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `scripts/ownership-index.md` contains one row for every current `rg --files scripts` path; `test_scripts_ownership.py` compares registry rows to filesystem inventory. | `pytest -q app/tests/unit/test_scripts_ownership.py` PASS. | PASS | Current inventory is 21 paths after adding the registry itself. |
| AC2 | Registry columns are `script`, `family`, `owner`, `usage`, `validation_command`, `support_status`, `decision`; test validates the visible Markdown header and actionable row values. | `pytest -q app/tests/unit/test_scripts_ownership.py` PASS. | PASS | Header guard added after review fix. |
| AC3 | `scripts-inventory-baseline.txt` has the pre-registry 20 script paths; `scripts-inventory-after.txt` has the same paths plus `scripts/ownership-index.md`. | `rg --files scripts` PASS; snapshot test PASS. | PASS | No executable script path changed. |
| AC4 | `scripts/stripe-listen-webhook.sh` row uses `needs-user-decision` and `blocked-support-decision`. | `rg -n "stripe-listen" scripts/ownership-index.md` PASS; dedicated test PASS. | PASS | |
| AC5 | Required capsule files generated; story status/tasks updated; final evidence completed. | `condamad_story_validate.py` PASS; `condamad_story_lint.py --strict` PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `scripts/ownership-index.md` | added | Canonical script ownership registry. | AC1, AC2, AC4 |
| `backend/app/tests/unit/test_scripts_ownership.py` | modified | Architecture guard for exact registry coverage, required visible header and row columns, snapshots, and blocked Stripe shell decision. | AC1, AC2, AC3, AC4 |
| `_condamad/stories/regression-guardrails.md` | modified | Added durable invariant `RG-023` for script ownership. | AC1 |
| `_condamad/stories/formalize-scripts-ownership/scripts-inventory-baseline.txt` | added | Baseline script inventory before registry creation. | AC3 |
| `_condamad/stories/formalize-scripts-ownership/scripts-inventory-after.txt` | added | After inventory including the new registry file. | AC3 |
| `_condamad/stories/formalize-scripts-ownership/generated/01-execution-brief.md` | added | CONDAMAD execution capsule. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/generated/03-acceptance-traceability.md` | added | AC traceability and final statuses. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/generated/04-target-files.md` | added | Target file map. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/generated/05-implementation-plan.md` | added | Implementation plan. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/generated/06-validation-plan.md` | added | Validation contract. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/generated/07-no-legacy-dry-guardrails.md` | added | No Legacy / DRY guardrails. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/generated/10-final-evidence.md` | added | Final evidence. | AC5 |
| `_condamad/stories/formalize-scripts-ownership/00-story.md` | modified | Status and task checkboxes updated after validation. | AC5 |

## Files deleted

None.

## Tests added or updated

- Updated `backend/app/tests/unit/test_scripts_ownership.py`.
- Added coverage for exact registry inventory, duplicate rows, visible registry header, required row fields, snapshot comparison, and `stripe-listen-webhook.sh` blocked decision.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial worktree had pre-existing untracked CONDAMAD story directories. |
| `rg --files scripts` | repo root | PASS | 0 | Listed 20 paths before registry creation, then 21 after `scripts/ownership-index.md` was added. |
| `rg -n "stripe-listen" scripts/ownership-index.md` | repo root | PASS | 0 | Found both Stripe listener rows; `.sh` has blocked decision. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_scripts_ownership.py` | repo root | PASS | 0 | 6 passed after review fixes. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | repo root | PASS | 0 | 3 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/integration/test_pipeline_scripts.py app/tests/integration/test_secrets_scan_script.py app/tests/integration/test_security_verification_script.py` | repo root | PASS | 0 | 13 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format app/tests/unit/test_scripts_ownership.py` | repo root | PASS | 0 | 1 file reformatted. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format --check app/tests/unit/test_scripts_ownership.py` | repo root | PASS | 0 | File already formatted. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check app/tests/unit/test_scripts_ownership.py` | repo root | PASS | 0 | All checks passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format --check .` | repo root | PASS | 0 | 1248 files already formatted. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/formalize-scripts-ownership/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation PASS. |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/formalize-scripts-ownership/00-story.md` | repo root | PASS | 0 | CONDAMAD story lint PASS. |
| `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts backend/app/tests/unit/test_scripts_ownership.py` | repo root | PASS | 0 | Hits classified below; no active compatibility path introduced. |
| `git diff --stat` | repo root | PASS | 0 | Tracked diff limited to guardrail registry and script ownership test; untracked story/register files listed in final status. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` | repo root | BLOCKED | 124 | Timed out after 10 minutes without final pytest summary. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` | conditional broader regression | Timed out after 10 minutes. | A failure outside the targeted script ownership surface could remain undiscovered. | Targeted unit guard, related ownership guard, story integration tests, Ruff full backend checks all passed. |
| Local app startup | no for this story | No runtime backend/frontend behavior changed; story is registry/test/documentation governance. | Startup regression is unlikely but not directly proven by this story. | Existing script integration tests and Ruff checks passed. |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `alias` | `scripts/ownership-index.md` | documentation_guard_expected_hit | The registry states aliases are forbidden. | PASS |
| `legacy` | `scripts/llm-release-readiness.ps1` | out_of_scope_with_justification | Existing LLM release report command; not changed by this story. | PASS |
| `fallback` | `scripts/activate-llm-release.ps1` | out_of_scope_with_justification | Existing LLM release smoke fields; not changed by this story. | PASS |

- No second ownership registry was added.
- No script was moved, wrapped, aliased, or re-exported.
- `RG-023` now protects exact ownership coverage for `scripts/`.

## Diff review

- `git diff --stat` reviewed for tracked files.
- `git diff --check` passed with CRLF warnings only.
- Untracked files are expected story artifacts or pre-existing untracked story directories.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/tests/unit/test_scripts_ownership.py
?? _condamad/stories/classify-critical-load-scenarios/
?? _condamad/stories/classify-natal-cross-tool-dev-report/
?? _condamad/stories/formalize-scripts-ownership/
?? _condamad/stories/harden-local-dev-stack-script/
?? _condamad/stories/portable-llm-release-readiness/
?? scripts/ownership-index.md
```

`git status --short` also emitted permission warnings for existing pytest artifact directories under `.codex-artifacts/`, `artifacts/`, and `backend/.tmp-pytest/`.

## Remaining risks

- Full backend `pytest -q` did not complete within 10 minutes.
- The initial attempt to run Python commands from `backend/` used the wrong relative activation path and is discarded; commands were rerun from the repository root with `.\\.venv\\Scripts\\Activate.ps1` before `cd backend`.

## Suggested reviewer focus

- Review the family/status classifications in `scripts/ownership-index.md`, especially follow-up statuses and the blocked `stripe-listen-webhook.sh` support decision.
- Review whether `RG-023` is the right durable invariant wording for script ownership.
