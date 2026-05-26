# Acceptance Traceability

<!-- Commentaire global: cette trace relie les critères CS-322 aux artefacts reconciliés et aux validations locales. -->

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | CS-312 to CS-316 report uses current plan wording. | `_condamad/reports/CS-312-CS-316-delivery-report.md` replaces the old backend mismatch wording with all-plan availability and CS-320 LLM/front routing. | `evidence/stale-wording-active-targets.txt`; targeted `rg` exit 1 means no active stale match. | PASS |
| AC2 | The report states backend all-plan alignment. | Report states `client_interpretation_projection_v1` remains available for `free`, `basic` and `premium`, with all plans aligned to the current decision. | `rg -n "Plausible\|Matomo\|noop\|client_interpretation_projection_v1\|free\|basic\|premium" ...` returned the expected current terms. | PASS |
| AC3 | Current follow-up routing is explicit. | Report routes plan differentiation to CS-320, Plausible preparation to CS-321, and Matomo removal to CS-323. | `rg -n "CS-320\|CS-321\|CS-323\|LLM\|front\|Plausible" _condamad/reports/CS-312-CS-316-delivery-report.md` found the expected routing. | PASS |
| AC4 | Provider wording is Plausible-first. | Report and CS-318 evidence now refer to Plausible observation; Matomo is explicitly not currently used or routed separately. | Provider wording scan persisted in `evidence/validation.txt`; stale `Plausible/Matomo` active-target scan has no match. | PASS |
| AC5 | Runtime files stay unchanged. | No backend, frontend or shared file was edited; no runtime test source changed. | `git diff --name-only -- backend frontend shared` persisted to `evidence/runtime-diff.txt` with no paths; `git diff --name-only -- _condamad/reports docs/architecture _story_briefs backend frontend` lists no runtime path. | PASS |
| AC6 | Reconciliation journal is persisted. | `evidence/reconciliation-journal.md` records source decisions, ledger, scans, provider wording and runtime proof. | `. .\.venv\Scripts\Activate.ps1; python -B -c "... assert p.exists() ..."` PASS. | PASS |
| AC7 | Stale contradiction scans are clean. | Active report/evidence targets no longer contain stale plan/provider contradictions. | Unfiltered scan only matches the immutable CS-322 source brief; active-target scan excluding that source brief is `PASS: no matches`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
