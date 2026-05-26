# Delivery Report - CS-312 to CS-316

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-26 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | `e5231e57..89849e06` for story drafting and implementation evidence inspected |
| Stories covered | CS-312, CS-313, CS-314, CS-315, CS-316 |
| Source documents | `_condamad/reports/CS-307-CS-311-delivery-report.md`, `_story_briefs/cs-312-implementer-audit-ux-natal-cs307.md`, `_story_briefs/cs-313-stabiliser-validation-pnpm-lint-apres-cs308.md`, `_story_briefs/cs-314-capturer-pack-screenshots-profils-natal-cs310.md`, `_story_briefs/cs-315-faire-valider-matrice-produit-plans-projections-natal.md`, `_story_briefs/cs-316-verifier-ingestion-analytics-runtime-projections-natal.md` |
| Diff source | `git log --oneline --stat` over CS-312 to CS-316 story capsules, `docs/architecture`, `frontend/README.md`, and story-time final evidence |
| Validation source | story-time evidence, generated reviews, report-time repository inspection |

## 1. Executive summary

CS-312, CS-313 and CS-314 are `Delivered`: each has final evidence, clean review, passing required validation, and tracker status `done`.

CS-316 is repository-complete but depends on external provider verification: local runtime config is `noop`, so real analytics ingestion remains externally required. Its delivery status is `Requires business/QA validation`.

CS-315 is closed by CS-317 evidence: final evidence and implementation review exist, backend/frontend runtime checks pass, and the current product decision keeps `client_interpretation_projection_v1` available for `free`, `basic` and `premium`. Commercial differentiation is now routed to CS-320 for LLM/front shaping.

Final initiative status: `Delivered with repository evidence complete; CS-316 still needs external Plausible observation`.

## 2. Initial context and trigger

The initial trigger is `_condamad/reports/CS-307-CS-311-delivery-report.md`, which recommended five follow-up actions: implement the missing CS-307 UX audit, stabilize CS-308 `pnpm lint`, add CS-310 screenshot evidence, obtain CS-309 product matrix sign-off, and verify CS-311 analytics ingestion. CS-312 to CS-316 map directly to those follow-up briefs under `_story_briefs/`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-312 | Close the CS-307 UX audit evidence gap with browser audit artifacts and screenshots. | `_condamad/stories/CS-312-implementer-audit-ux-natal-cs307/00-story.md` | No frontend/backend code changes unless a proven UX defect requires them. |
| CS-313 | Stabilize or prove the standard `pnpm lint` validation path after CS-308 EPERM. | `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/00-story.md` | No package-manager change, dependency reinstall, or broad frontend refactor. |
| CS-314 | Add a real browser screenshot pack for the five CS-310 profile categories. | `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/00-story.md` | No subjective astrology validation and no runtime app changes. |
| CS-315 | Record a product-owned free/basic/premium `/natal` projection plan matrix decision. | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md` | No React entitlement matrix, backend entitlement change, Stripe/pricing/subscription/DB/migration change. |
| CS-316 | Verify analytics ingestion readiness for the seven CS-311 `/natal` projection events. | `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/00-story.md` | No new analytics provider, dashboard, backend persistence, prompt, provider, or replay changes. |

## 4. Implementation summary

- CS-312 created the missing CS-307 audit evidence under `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/**`, completed CS-307 final evidence, validated browser screenshots and states, and changed no application source.
- CS-313 proved `pnpm lint` now passes, classified the CS-308 EPERM as a resolved Windows-environment blocker, and updated `frontend/README.md` so lint examples use the existing pnpm package-manager contract.
- CS-314 added a deterministic Chromium screenshot pack, `screenshot-ledger.json`, anomaly ledger, backend startup proof, frontend/backend validation aggregate logs, and no application source changes.
- CS-315 added `docs/architecture/natal-projection-plan-matrix-product-decision.md`, final evidence, implementation review and runtime validation transcript; the backend/product divergence is routed to a separate follow-up brief.
- CS-316 added runtime analytics config and ingestion ledger evidence, documented external provider validation requirements, fixed evidence/review/status drift, and kept runtime source unchanged.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-312 | CS-307 UX audit artifacts, screenshots, no-overlap proof, state/disclaimer visibility, tracker closure. | `_condamad/reports/CS-307-CS-311-delivery-report.md` action 1 | CS-307 `evidence/ux-audit-before.md`, `ux-audit-after.md`, `browser-qa.md`, `browser-screenshots/`, CS-307 `generated/10-final-evidence.md`; CS-312 final evidence. | `pnpm lint` PASS; targeted Vitest 108 PASS; architecture guard 91 PASS; full Vitest 1276 PASS; capsule validation PASS. | Delivered |
| CS-313 | Standard `pnpm lint` closure path restored and CS-308 EPERM classified. | `_condamad/reports/CS-307-CS-311-delivery-report.md` action 2 | `frontend/README.md`, `evidence/pnpm-lint-before.txt`, `pnpm-lint-after.txt`, `typescript-lint.txt`, `cause-ledger.md`. | `pnpm lint` PASS; both `tsc.CMD` lint projects PASS; package-manager drift scans PASS; capsule/story validation PASS. | Delivered |
| CS-314 | Fresh browser screenshot pack for five CS-310 profiles and QA ledger closure. | `_condamad/reports/CS-307-CS-311-delivery-report.md` action 3 | `evidence/screenshots/*.png`, `screenshot-ledger.json`, `anomaly-ledger.json`, `capture-cs314-screenshots.mjs`, validation aggregates. | Capture script PASS with 7 screenshots; backend `/health` PASS; `pnpm lint` PASS; targeted Vitest 123 PASS; backend pytest 12 PASS. | Delivered |
| CS-315 | Product sign-off matrix for free/basic/premium `/natal` projections. | `_condamad/reports/CS-307-CS-311-delivery-report.md` action 4 | `docs/architecture/natal-projection-plan-matrix-product-decision.md`; CS-315 `generated/10-final-evidence.md`, `generated/11-code-review.md`, `evidence/source-alignment.md` and `validation.txt`; CS-320 differentiation brief. | Backend pytest PASS; OpenAPI/routes PASS; frontend lint PASS; Vite logged Vitest PASS; real-conditions backend suite PASS with all plans aligned to the current decision. | Delivered |
| CS-316 | Runtime ingestion verification or explicit external validation requirement for CS-311 analytics. | `_condamad/reports/CS-307-CS-311-delivery-report.md` action 5 | `analytics-runtime-config.json`, `analytics-ingestion-ledger.json`, `external-validation-required.md`, `redaction-scan.txt`, CS-316 final evidence. | Runtime config PASS; seven-event ledger PASS; catalog field comparison PASS; `pnpm lint` PASS; targeted Vitest 54 PASS; full Vitest 1276 PASS; provider dashboard BLOCKED by local `noop`. | Requires business/QA validation |

## 6. Evidence of completion

### Code evidence

- `frontend/README.md`: proves CS-313 documentation alignment to `pnpm lint`; no runtime code changed.
- No frontend/backend application source changed for CS-312, CS-314, CS-315, or CS-316 according to their final evidence and commit stats.
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`: proves CS-315 product matrix decision content, accepted matrix, backend authorization boundary, frontend render-only policy, and plan-differentiation boundary.

### Test evidence

- CS-312 final evidence: `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage` PASS with 108 tests; full Vitest PASS with 1276 passed, 8 skipped.
- CS-313 final evidence: `pnpm lint` PASS and both TypeScript lint projects PASS.
- CS-314 final evidence: targeted frontend Vitest PASS with 123 tests; backend projection pytest PASS with 12 tests.
- CS-316 final evidence: targeted analytics/natal Vitest PASS with 54 tests; full Vitest PASS with 1276 passed, 8 skipped.

### Documentation evidence

- `_condamad/stories/CS-312-implementer-audit-ux-natal-cs307/generated/10-final-evidence.md`: proves CS-307 gap full closure and clean implementation review.
- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/generated/10-final-evidence.md`: proves the standard lint path now passes and no fallback is used.
- `_condamad/stories/CS-314-capturer-pack-screenshots-profils-natal-cs310/generated/10-final-evidence.md`: proves screenshot pack and validation artifacts.
- `_condamad/stories/CS-316-verifier-ingestion-analytics-runtime-projections-natal/generated/10-final-evidence.md`: proves repo-local analytics ingestion readiness and external provider limitation.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md`: proves the CS-315 report covers the source brief, CS-307-CS-311 report action, CS-309 matrix, CS-283 policy, and frontend/backend evidence paths.

### Operational evidence

- CS-312 commits: `221a5541`, `93776185`, `60aae37c`, `08cf92f9` record story implementation, review fix, brief alignment, and final dev-story evidence.
- CS-313 commits: `5c087d3b`, `af8bbf2a`, `c11c7a36` record implementation, review fix, and brief alignment.
- CS-314 commits: `fb4ddb1d`, `8204d864`, `193ae70f` record screenshot implementation, review fix, and brief alignment.
- CS-315 commits: `8783e75b`, `6221f6e6` record product architecture document and review corrections, but not CONDAMAD closure.
- CS-316 commits: `3229a04f`, `07b6a547`, `89849e06` record implementation, review fix, and brief alignment.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| CS-312 browser audit script | manual | PASS | CS-312 final evidence | Browser proof and screenshots regenerated. |
| `pnpm lint` | targeted | PASS | CS-312, CS-313, CS-314, CS-316 final evidence | Standard frontend lint path is green in delivered follow-ups. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | full suite | PASS | CS-312 and CS-316 final evidence | 116 files, 1276 passed, 8 skipped. |
| CS-313 TypeScript lint projects | targeted | PASS | CS-313 final evidence | `tsconfig.lint.json` and `tsconfig.node.json` pass. |
| CS-314 capture script | manual | PASS | CS-314 final evidence | 7 screenshots produced for 5 profile categories. |
| CS-314 backend startup smoke | targeted | PASS | CS-314 final evidence | FastAPI `/health` returned 200 with venv active. |
| CS-314 backend pytest | targeted | PASS | CS-314 final evidence | 12 projection tests passed with venv active. |
| CS-315 documentation field scans | targeted | PASS | CS-315 `evidence/validation.txt` | Required fields and vocabulary found. |
| CS-315 backend pytest | targeted | PASS | CS-315 final evidence | Authorization/endpoint suite 5 passed; real-conditions suite 9 passed. |
| CS-315 frontend Vitest parity | targeted | PASS | CS-315 final evidence | Vite logged target 123 tests passed. |
| CS-316 runtime config and ingestion ledger checks | targeted | PASS | CS-316 final evidence | Local provider is `noop`; seven event names covered. |
| CS-316 external provider dashboard check | external | EXTERNALLY REQUIRED | `external-validation-required.md` | Blocked by unavailable local Plausible sink; Matomo is not currently used. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- CS-315 has no remaining backend entitlement divergence after the current product decision: backend accepts `client_interpretation_projection_v1` for `free`, `basic` and `premium`, and CS-320 owns the LLM/front differentiation contract.
- CS-315 runtime parity checks are now executed in CS-317 final evidence; the remaining CS-315-related follow-up is specification of plan-aware LLM/front shaping, not backend access restriction.

### Known limits

- CS-316 cannot prove real provider ingestion locally because the loaded analytics provider is `noop`; external validation is required.
- CS-312 visual quality still depends on reviewer judgment over screenshots, although no-overlap and state checks passed.
- CS-314 screenshots use deterministic API route responses in a real Chromium/Vite browser pass; backend runtime was smoke-checked separately.

### Assumptions

- Story-time final evidence is treated as authoritative for commands not rerun during this report generation.
- `git status --short` at report time is clean; prior final evidence mentions `_condamad/run-state.json` as pre-existing untracked context during story execution, but it is not present as dirty report-time state.

## 9. Residual risks

- CS-315 plan differentiation risk: product, backend, LLM and frontend owners still need to specify the plan-aware enrichment contract for `client_interpretation_projection_v1`.
- CS-316 external validation risk: production/staging analytics ingestion could still fail despite repo-local event catalog, redaction, and test evidence.
- CS-313 environment risk: Windows EPERM can recur if another process locks pnpm internals, even though the standard `pnpm lint` path currently passes.
- CS-314 evidence risk: deterministic screenshot replay may not catch every authenticated real-user browser variance.

## 10. Evidence gaps

- No remaining CS-315 closure evidence gap. The remaining CS-315-related item is the routed backend/product decision brief.
- CS-316 lacks real Plausible ingestion evidence; the story correctly records this as externally required, while Matomo is not the current provider target.

## 11. Recommended next actions

1. Specify the CS-320 plan-aware LLM/front differentiation contract for `free`, `basic` and `premium`.
2. Execute CS-321 Plausible preparation and CS-316 external analytics-provider validation in staging or production when Plausible is configured and observable.
3. Route Matomo code removal to CS-323; do not activate Matomo as a current analytics provider.

## 12. Final delivery status

`Delivered with repository evidence complete; external Plausible observation still required`

CS-312, CS-313, CS-314 and CS-315 are delivered within repository evidence limits, and CS-316 is complete within repository limits but requires external Plausible ingestion validation. CS-315 no longer has a closure evidence gap; its remaining work is CS-320 plan-aware LLM/front differentiation.
