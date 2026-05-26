# Delivery Report - cs-322-cs-323

<!-- Commentaire global: ce rapport consolide les preuves de livraison CS-322 et CS-323 sans modifier le code applicatif. -->

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-26 22:41:26 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced |
| Stories covered | `CS-322`, `CS-323` |
| Source documents | `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md`; `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md`; `_condamad/stories/story-status.md` |
| Diff source | Story final evidence, story-time `git diff` summaries, report-time `git status --short` |
| Validation source | story-time evidence and report-time evidence collection |
| Audits in this series | None declared by the delivery request; no audit folder was linked to `CS-322` or `CS-323` |

## 1. Executive summary

The series status is `Delivered`. `CS-322` is delivered as a reporting/evidence reconciliation with no runtime application changes, backed by final evidence `PASS` and implementation review `CLEAN` in `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/generated/10-final-evidence.md` and `generated/11-code-review.md`. `CS-323` is delivered as a frontend analytics cleanup, backed by final evidence `PASS` and code review `CLEAN` in `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/generated/10-final-evidence.md` and `generated/11-code-review.md`.

No audits were part of this series. Therefore there are no audit findings, risks, or candidates to link to the implemented stories.

## 2. Initial context and trigger

`CS-322` was triggered by stale closure wording after CS-320 and CS-321 decisions: all plans calculate/interpret, differentiation moves to LLM/front shaping, and Plausible is the analytics preparation target. Evidence: `_story_briefs/cs-322-reconcilier-rapports-evidence-apres-decision-plan-plausible.md`.

`CS-323` was triggered by dormant Matomo frontend analytics support while the current target is Plausible with local `noop`. Evidence: `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-322` | Reconcile targeted reports/evidence with all-plan projection and Plausible-first decisions, without runtime changes. | `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/generated/03-acceptance-traceability.md` | No backend/frontend runtime change; no Plausible activation; no Matomo code removal; no CS-320 implementation. |
| `CS-323` | Remove dormant Matomo provider from active frontend analytics while preserving `noop`, Plausible and redaction behavior. | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/generated/03-acceptance-traceability.md` | No Plausible production activation; no new provider; no event taxonomy, backend, DB, prompt, LLM provider, auth, i18n or style change. |

## 4. Implementation summary

`CS-322` updated `_condamad/reports/CS-312-CS-316-delivery-report.md`, CS-317 final evidence, CS-318 final evidence, story status, and CS-322 evidence/generated artifacts. The reconciliation journal at `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/reconciliation-journal.md` records the artifact-level mapping from stale terms to current CS-320/CS-321/CS-323 routing.

`CS-323` changed `frontend/src/config/analytics.ts` so `AnalyticsProvider` is only `'plausible' | 'noop'`, removed the `_paq`/Matomo branch from `frontend/src/hooks/useAnalytics.ts`, and added/updated coverage in `frontend/src/tests/useAnalytics.test.tsx`. The removal audit at `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/removal-audit.md` classifies the Matomo provider type and hook branch as `historical-facade` and records deletion without shim, alias or fallback.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-322` | Report no longer presents all-plan `client_interpretation_projection_v1` as a divergence. | CS-322 brief AC1 | `_condamad/reports/CS-312-CS-316-delivery-report.md`; CS-322 traceability AC1 | `evidence/stale-wording-active-targets.txt`; active-target `rg` exit 1 recorded in final evidence | Delivered |
| `CS-322` | Report states backend all-plan alignment. | CS-322 brief AC2 | CS-322 traceability AC2; report scan shows `free`, `basic`, `premium` and projection ID | `rg -n "Plausible|Matomo|noop|client_interpretation_projection_v1|free|basic|premium" ...` PASS in `evidence/validation.txt` | Delivered |
| `CS-322` | Follow-up routing points to CS-320, CS-321 and CS-323. | CS-322 brief AC3 | `_condamad/stories/CS-322-.../evidence/reconciliation-journal.md` | `rg -n "CS-320|CS-321|CS-323|LLM|front|Plausible" ...` PASS | Delivered |
| `CS-322` | Provider wording is Plausible-first and Matomo not current. | CS-322 brief AC4 | CS-318 final evidence and CS-312-CS-316 report reconciled | Stale `Plausible/Matomo` active-target scan PASS; final review `CLEAN` | Delivered |
| `CS-322` | No runtime files changed. | CS-322 brief AC5 | CS-322 final evidence files changed list excludes backend/frontend runtime | `git diff --name-only -- backend frontend shared` recorded as no paths | Delivered |
| `CS-322` | Journal persisted and stale contradiction scans clean. | CS-322 brief AC6-AC7 | `evidence/reconciliation-journal.md`; `evidence/validation.txt` | Journal Python existence check PASS after venv activation; capsule validation PASS | Delivered |
| `CS-323` | `AnalyticsProvider` excludes `matomo`. | CS-323 brief AC1 | `frontend/src/config/analytics.ts` line evidence: union is `'plausible' | 'noop'` | `pnpm lint` PASS; `rg -n "matomo" frontend/src/config/analytics.ts` exit 1 | Delivered |
| `CS-323` | `_paq` absent from active hook. | CS-323 brief AC2 | `frontend/src/hooks/useAnalytics.ts` has only `noop` and `plausible` branches | `rg -n "_paq" frontend/src/hooks/useAnalytics.ts` exit 1 | Delivered |
| `CS-323` | `noop` default and Plausible sanitized props preserved. | CS-323 brief AC3-AC4, AC7 | `frontend/src/hooks/useAnalytics.ts`; `frontend/src/tests/useAnalytics.test.tsx` tests default, unsupported provider, Plausible and redaction | `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics` PASS; expanded Vitest PASS | Delivered |
| `CS-323` | No direct provider calls or active Matomo docs/config/backend path. | CS-323 brief AC5-AC8 | `evidence/provider-scan-after.txt`; `evidence/removal-audit.md` | `rg -n "matomo|_paq" frontend/src .env.example docs` exit 1; `rg -n "matomo|_paq" backend` exit 1; direct Plausible call scan exit 1 | Delivered |
| `CS-323` | Persistent evidence artifacts exist. | CS-323 brief AC9 | `provider-scan-before.txt`, `provider-scan-after.txt`, `removal-audit.md`, `validation-frontend.txt` | `condamad_validate.py` PASS after venv activation | Delivered |

## 6. Evidence of completion

### Code evidence

- `frontend/src/config/analytics.ts`: `AnalyticsProvider` is now limited to `plausible` and `noop`; unsupported configured values normalize to `noop`.
- `frontend/src/hooks/useAnalytics.ts`: `SENSITIVE_ANALYTICS_FIELD_NAMES`, `sanitizeAnalyticsProps`, `noop`, and Plausible behavior remain; no `_paq` branch is present.
- `frontend/src/tests/useAnalytics.test.tsx`: analytics tests cover local `noop`, unsupported provider normalization, Plausible emission and sensitive-field redaction.

### Test evidence

- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/validation-frontend.txt`: `pnpm lint` PASS; targeted Vitest PASS; expanded Vitest PASS; full Vitest PASS; `pnpm build` PASS.
- `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/validation.txt`: `ruff check .` PASS; `python -B -m pytest -q --tb=short` PASS with `3316 passed, 1 skipped, 1216 deselected`.

### Documentation / evidence

- `_condamad/stories/CS-322-rapports-evidence-plan-plausible-reconciliation/evidence/reconciliation-journal.md`: proves artifact-level reconciliation to CS-320, CS-321 and CS-323.
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/removal-audit.md`: proves deletion classification for dormant Matomo provider surfaces.
- `_condamad/stories/story-status.md`: `CS-322` and `CS-323` rows are `done` as of 2026-05-26.

### Operational evidence

- `_condamad/codex-runs/cs-322-dev-story.log`: records CS-322 implementation summary, validations, final `ready-to-review` handoff and runtime non-change proof.
- `_condamad/codex-runs/cs-323-dev-story.log`: records CS-323 implementation summary, frontend validations, capsule/story validations and scan outcomes.
- Report-time `git status --short`: only `_condamad/critical-errors.jsonl` and `_condamad/run-state.json` were untracked before this report was written; no application file was modified by this delivery-report phase.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | full suite | PASS | CS-322 `generated/10-final-evidence.md`; `evidence/validation.txt` | Story-time, venv activated. |
| `python -B -m pytest -q --tb=short` | full suite | PASS | CS-322 `generated/10-final-evidence.md` | Story-time, venv activated; `3316 passed, 1 skipped, 1216 deselected`. |
| `pnpm lint` | targeted | PASS | CS-323 `evidence/validation-frontend.txt` | Story-time frontend validation. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics` | targeted | PASS | CS-323 `evidence/validation-frontend.txt` | 4 analytics tests passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi` | targeted | PASS | CS-323 `evidence/validation-frontend.txt` | 56 tests passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | full suite | PASS | CS-323 `evidence/validation-frontend.txt` | 1280 passed, 8 existing skips. |
| `pnpm build` | targeted | PASS | CS-323 `evidence/validation-frontend.txt` | `tsc -b` and Vite build completed. |
| `rg -n "matomo|_paq" frontend/src .env.example docs` | targeted | PASS | CS-323 `evidence/provider-scan-after.txt` | Exit 1 expected: no active match. |
| `rg -n "matomo|_paq" backend` | targeted | PASS | CS-323 `evidence/provider-scan-after.txt` | Exit 1 expected: no backend match. |
| `rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api` | targeted | PASS | CS-323 `evidence/provider-scan-after.txt` | Exit 1 expected: no direct provider calls outside hook. |
| `condamad_validate.py` for CS-322 capsule | targeted | PASS | CS-322 `generated/10-final-evidence.md` | Story-time, venv activated. |
| `condamad_validate.py` for CS-323 capsule | targeted | PASS | CS-323 `generated/10-final-evidence.md` | Story-time, venv activated. |
| Local app dev server startup | manual | NOT RUN | CS-322 and CS-323 final evidence | CS-322 report-only; CS-323 used `pnpm build` instead of leaving a server running. |
| External Plausible dashboard observation | external | EXTERNALLY REQUIRED | `_condamad/reports/CS-312-CS-316-delivery-report.md` and CS-318 evidence referenced by CS-322 | Requires configured observable Plausible environment; not part of CS-323 Matomo removal. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- None evidenced. CS-322 final review states no runtime changes and `CLEAN`; CS-323 review states no compatibility alias, shim, re-export, fallback provider path or backend Matomo path.

### Known limits

- Local app dev server startup was not run for this report. CS-323 story-time evidence used `pnpm build` as the local build/startup confidence check.
- External Plausible dashboard observation remains `EXTERNALLY REQUIRED`; it depends on provider environment outside the repository and is carried from the CS-316/CS-318 line through CS-322 report reconciliation.

### Assumptions

- Current worktree diff does not prove the original implementation range because `Commit range` is not evidenced. This report relies on story final evidence, review artifacts and Codex run logs for implementation provenance.

## 9. Residual risks

- CS-322: unfiltered stale-wording scans still match the immutable CS-322 source brief, because the brief intentionally lists stale phrases as the problem statement. Risk is low if reviewers preserve the distinction recorded in CS-322 final evidence.
- External analytics: Plausible dashboard observation is still outside repository validation. Impact is analytics ingestion confidence outside local code paths; mitigation is staged or production Plausible observation when provider config is available.
- Provenance: no commit range was evidenced for this report. Impact is weaker release provenance; mitigation is to attach the final commit/PR reference when publishing.

## 10. Evidence gaps

- Commit range: Not evidenced.
- CI status for this exact final series: Not evidenced.
- Report-time rerun of full frontend/backend test suites: NOT RUN; story-time validations are used instead.
- External Plausible dashboard evidence: EXTERNALLY REQUIRED.
- Audits: no audit was declared for this series, so no audit finding/candidate linkage exists.

## 11. Recommended next actions

1. Attach the final commit or PR reference to this report once the series is committed/published.
2. Execute external Plausible observation in an environment where Plausible is configured and observable, then update the CS-316/CS-318 evidence chain.
3. Keep CS-320 as the owner for plan-aware LLM/front differentiation; do not reopen backend entitlement restriction based on pre-CS-320 wording.

## 12. Final delivery status

`Delivered`

Both stories are marked `done` in `_condamad/stories/story-status.md`, have final evidence `PASS`, and have review verdict `CLEAN`. CS-322 completed the report/evidence reconciliation without runtime application changes; CS-323 removed the dormant Matomo frontend provider path while preserving `noop`, Plausible and redaction validations. The only material gaps are external Plausible observation, absent commit/CI provenance, and report-time non-rerun of the full suites.
