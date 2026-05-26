# Final Evidence — CS-322-rapports-evidence-plan-plausible-reconciliation

<!-- Commentaire global: cette preuve finale clôt CS-322 en documentant les artefacts reconciliés, les validations et le statut review-ready. -->

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-322-rapports-evidence-plan-plausible-reconciliation
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation`
- Source finding closure status: full-closure for the report/evidence wording scope; runtime implementation is out of scope.
- Feedback loop routing: no-propagation; this story created local evidence only and did not reveal a reusable skill or guardrail update.

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story/status match: `story-status.md` row `CS-322` points to `00-story.md` and source brief `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md`.
- Initial `git status --short`: dirty worktree already contained `_condamad/stories/story-status.md`, `_condamad/critical-errors.jsonl`, `_condamad/run-state.json`, CS-323 files, and the CS-322/CS-323 briefs.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule repaired and validated because required generated files were missing before implementation.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story source loaded. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by `condamad_prepare.py`. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC-by-AC evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Present from repaired capsule. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present from repaired capsule. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present from repaired capsule. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated after implementation. |
| `generated/11-code-review.md` | no | yes | PASS | Pre-existing clean review artifact preserved. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `_condamad/reports/CS-312-CS-316-delivery-report.md` reconciled current plan wording. | `evidence/stale-wording-active-targets.txt`; `rg` active-target scan exit 1 means no stale match. | PASS | |
| AC2 | Report states all-plan backend alignment for `client_interpretation_projection_v1`. | Targeted current-term `rg` found `free`, `basic`, `premium` and projection ID in report/decision docs. | PASS | |
| AC3 | Report routes follow-ups to CS-320, CS-321 and CS-323. | `rg -n "CS-320\|CS-321\|CS-323\|LLM\|front\|Plausible" _condamad/reports/CS-312-CS-316-delivery-report.md` PASS. | PASS | |
| AC4 | Report and CS-318 evidence are Plausible-first and classify Matomo separately. | Stale `Plausible/Matomo` active-target scan PASS; provider terms found in expected current wording. | PASS | |
| AC5 | Runtime files unchanged. | `evidence/runtime-diff.txt` has no backend/frontend/shared paths; targeted diff list excludes runtime files. | PASS | |
| AC6 | Reconciliation journal persisted. | `python -B -c` existence/size assertion PASS. | PASS | |
| AC7 | Stale contradiction scans clean for active targets. | Unfiltered scan matches only the immutable source brief; filtered active-target scan is clean. | PASS | Source brief intentionally remains unchanged. |

## Files changed

- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`
- `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/generated/**`
- `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- `_condamad/stories/cs-322/**` was removed after an initial prepare command created a parallel capsule; the canonical CS-322 capsule is `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation`.

## Tests added or updated

- None. This is a documentation/evidence reconciliation; runtime and test source changes are out of scope.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-322-rapports-evidence-plan-plausible-reconciliation --root .` | repo root | PASS | 0 | Required capsule files repaired. |
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-322-rapports-evidence-plan-plausible-reconciliation` | repo root | PASS | 0 | Capsule structure valid before implementation. |
| `rg -n "premium-only|refus.*free|refus.*basic|routed backend follow-up|product/backend divergence|Plausible/Matomo|provider dashboard blocked|Delivered with routed backend follow-up" ... -g "!cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md"` | repo root | PASS | 1 | No active-target stale matches. |
| `rg -n "Plausible|Matomo|noop|client_interpretation_projection_v1|free|basic|premium" ...` | repo root | PASS | 0 | Current plan/provider terms present. |
| `rg -n "CS-320|CS-321|CS-323|LLM|front|Plausible" _condamad/reports/CS-312-CS-316-delivery-report.md` | repo root | PASS | 0 | Follow-up routing present. |
| `git diff --check` | repo root | PASS | 0 | Line-ending warnings only; no whitespace errors. |
| `. .\.venv\Scripts\Activate.ps1; python -B -c "from pathlib import Path; ... assert p.exists() ..."` | repo root | PASS | 0 | Reconciliation journal exists. |
| `. .\.venv\Scripts\Activate.ps1; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `. .\.venv\Scripts\Activate.ps1; python -B -m pytest -q --tb=short` | repo root | PASS | 0 | 3316 passed, 1 skipped, 1216 deselected. |

## Commands skipped or blocked

- Frontend lint/Vitest: skipped because CS-322 changes no frontend runtime or tests; full backend pytest and ruff were run for repository confidence.
- Local app startup: skipped because this story changes only reports and evidence, with no runtime application behavior.

## DRY / No Legacy evidence

- No shim, alias, fallback, compatibility path, provider adapter, runtime service, frontend component, CSS, migration or package change was introduced.
- `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md` was not modified.
- `_condamad/stories/regression-guardrails.md` was not modified.
- Active-target stale wording scan excludes only the immutable CS-322 source brief and is clean.

## Diff review

- `git diff --name-only -- _condamad/reports docs/architecture _story_briefs backend frontend`: report path only from the checked surface; no backend/frontend path.
- `git diff --name-only -- backend frontend shared`: no paths.
- `git diff --check`: PASS with line-ending warnings only.

## Final worktree status

- Story-owned changes are limited to the report, targeted final evidence, CS-322 evidence/generated files, and status row.
- Pre-existing/unrelated dirty files remain present and were not reverted.

## Remaining risks

- Unfiltered stale wording scans still match the immutable CS-322 source brief because it documents the problem terms; this is intentional and preserved by user instruction.

## Suggested reviewer focus

- Verify that the report preserves historical closure context while routing current plan/provider decisions to CS-320, CS-321 and CS-323 without implying runtime changes.
