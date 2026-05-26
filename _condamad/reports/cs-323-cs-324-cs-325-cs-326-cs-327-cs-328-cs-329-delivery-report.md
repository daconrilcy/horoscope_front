# Delivery Report - CS-323 to CS-329

<!-- Commentaire global: ce rapport consolide les preuves de livraison de la serie CS-323 a CS-329 sans modifier le code applicatif. -->

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-27 01:16:54 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced; current HEAD observed as `b91e1a8a` |
| Stories covered | `CS-323`, `CS-324`, `CS-325`, `CS-326`, `CS-327`, `CS-328`, `CS-329` |
| Source documents | `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md`; `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`; `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`; `_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md`; `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`; `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`; `_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md` |
| Diff source | Story final evidence and report-time `git status --short`; current pre-report dirty file was `?? _condamad/run-state.json` |
| Validation source | Story-time and audit-time validation artifacts under `_condamad/stories/**/generated`, `_condamad/audits/**/validation-output.md`, `_condamad/architecture/**/validation-output.md`, `_condamad/reports/calculs-interpretations-vers-prompts-llm/**` |

## 1. Executive summary

The series is delivered as an evidence-backed closure package for one frontend cleanup story, four read-only domain audits, one architecture synthesis and one report-only synthesis.

`CS-323` removed the dormant Matomo analytics provider from active frontend analytics and has clean implementation review evidence. `CS-324` to `CS-327` produced the requested audit folders and validation outputs. `CS-328` produced the architecture transition package from those audits. `CS-329` produced the consolidated transition report and evidence files. No application code change is evidenced for `CS-324` to `CS-329`; the only application change in the series is the bounded frontend analytics change in `CS-323`.

Final initiative status: `Delivered`.

Material gaps remain: tracker rows for `CS-324` to `CS-328` still show `ready-to-dev` even though their deliverable folders and validations exist; the LLM transition itself is not implemented and remains future work by design.

## 2. Initial context and trigger

The series has two connected tracks:

- Analytics cleanup: `CS-323` was triggered by `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md` and the story records that Matomo remained in the provider type and dormant `_paq` branch, increasing maintenance surface.
- LLM transition discovery and synthesis: `CS-324` to `CS-329` were triggered by the need to understand and plan the transition from current natal LLM injection through `chart_json`, `natal_data`, `evidence_catalog` and `astro_context` toward a structured prompt input contract. The consolidated report `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md` states that the transition is necessary and not yet realized in the audited natal path.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-323` | Remove dormant Matomo provider from active frontend analytics while preserving `noop` and Plausible. | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md` section `7. Acceptance Criteria` | No new provider, no backend/DB/prompt/auth/style/build changes; no shim or dormant replacement. |
| `CS-324` | Audit calculation and interpretation surfaces versus current LLM input. | `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md`; review artifact `generated/11-code-review.md` | Audit-only; no application code, tests, prompts, runtime, public contracts, frontend or guardrail registry changes. |
| `CS-325` | Audit natal LLM prompt pipeline, visibility and legacy-vs-canonical branches. | `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`; review artifact `generated/11-code-review.md` | Audit-only; forbids backend, frontend, prompt and test edits in the story contract review. |
| `CS-326` | Audit readiness of interpretive projections and contracts for LLM input. | `_condamad/stories/CS-326-audit-projections-interpretatives-llm-input-readiness/00-story.md`; review artifact `generated/11-code-review.md` | Read-only; no backend app or backend test modification. |
| `CS-327` | Audit prompt configuration, placeholders and input schema readiness. | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md`; review artifact `generated/11-code-review.md` | Audit-only; keeps `backend/app/**`, `backend/tests/**` and `frontend/**` out of intended modification set. |
| `CS-328` | Produce architecture transition synthesis over `CS-324` to `CS-327`. | `_condamad/stories/CS-328-architecture-transition-calculs-interpretations-injection-llm/00-story.md`; review artifact `generated/11-code-review.md` | Architecture-only; no app, prompt, provider, endpoint, DB, migration or frontend change. |
| `CS-329` | Produce the final synthesis report for transition injection prompts LLM. | `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/00-story.md`; `generated/10-final-evidence.md` | Report-only; no application behavior or source changes. |

## 4. Implementation summary

`CS-323` changed active frontend analytics surfaces:

- `frontend/src/config/analytics.ts`: `AnalyticsProvider` now exposes only `plausible` and `noop`, per `CS-323` final evidence AC1.
- `frontend/src/hooks/useAnalytics.ts`: `_paq` typing and Matomo branch are absent, per `CS-323` final evidence AC2.
- `frontend/src/tests/useAnalytics.test.tsx`: coverage was updated for unprepared provider normalization to `noop`, per `CS-323` final evidence.

`CS-324` to `CS-327` produced audit artifacts:

- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/**`: one High, two Medium and one Low finding; current input assembled from `chart_json`, `natal_data`, `evidence_catalog`, `astro_context`; recent owners are present but not invoked in the scoped natal LLM path.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/**`: `chart_json` is prompt-visible by default or through `{{chart_json}}`; `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code` are runtime-only in the audited `build_user_payload` path; `evidence_catalog` is validation-only in current evidence.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/**`: `AINarrativeInputContract` is the best candidate for canonical internal LLM input; `structured_facts_v1` is hashable facts source; B2C projections are not prompt payload owners.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/**`: active natal config still declares `chart_json`; no `llm_astrology_input`, `facts`, `signals`, `limits` or `proofs` contract exists in scoped config/runtime/orchestration paths.

`CS-328` produced architecture artifacts:

- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md`: target flow `CalculationGraph / ChartObjectRuntimeData -> ChartInterpretationInput -> AINarrativeInputContract -> llm_astrology_input_v1 -> prompt runtime -> narrative_answer_audit_v1`.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/05-risk-register.md`: highest sequencing risks and owners, including `chart_json` remaining source of truth and ambiguity around `evidence_catalog`.

`CS-329` produced the synthesis report:

- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`: final diagnostic, legacy map, target architecture, target contract and six future refactor story families.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/evidence-sources.md` and `validation-output.md`: source persistence and validation evidence.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-323` | Remove Matomo provider and `_paq`, preserve `noop`, Plausible and redaction. | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md` AC1-AC9 | `frontend/src/config/analytics.ts`; `frontend/src/hooks/useAnalytics.ts`; `frontend/src/tests/useAnalytics.test.tsx`; `generated/10-final-evidence.md` AC table | `pnpm lint` PASS; targeted and full Vitest PASS; `pnpm build` PASS; negative `rg` scans PASS; `generated/11-code-review.md` verdict CLEAN | `Delivered` |
| `CS-324` | Audit calculation/interpretation surfaces and identify gaps toward LLM input. | `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`; story review `generated/11-code-review.md` | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit-report.md`; `02-finding-register.md`; `03-gap-register.md`; `04-risk-matrix.md`; `05-executive-summary.md` | `validation-output.md`: audit validate PASS, audit lint PASS, required vocabulary scans PASS, `pytest -q backend/tests/unit/domain/astrology` PASS 594 tests | `Delivered` |
| `CS-325` | Audit natal prompt pipeline, field visibility and legacy branches. | `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`; story review `generated/11-code-review.md` | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit-report.md`; `03-branch-matrix.md`; `04-legacy-vs-canonical.md`; `05-executive-summary.md` | `validation-output.md`: audit validate/lint PASS, `pytest -q backend/tests/llm_orchestration` PASS 221 tests, `ruff format --check .` PASS, `ruff check .` PASS, no app/backend/frontend changes | `Delivered` |
| `CS-326` | Classify recent projection/contracts for LLM input readiness. | `_story_briefs/cs-326-audit-projections-interpretatives-llm-input-readiness.md`; story review `generated/11-code-review.md` | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit-report.md`; `01-contract-comparison.md`; `02-field-classification.md`; `03-llm-readiness-matrix.md`; `04-recommendations.md` | `validation-output.md`: audit validate/lint PASS, required scans PASS, no app/test changes, astrology pytest PASS 594 tests, rejected workflow pytest PASS 5 tests, ruff checks PASS | `Delivered` |
| `CS-327` | Audit prompt config placeholders and schema readiness. | `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`; story review `generated/11-code-review.md` | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/00-audit-report.md`; `02-placeholder-schema-matrix.md`; `03-legacy-fallbacks.md`; `04-readiness.md`; `05-executive-summary.md` | `validation-output.md`: audit validate/lint PASS, required scans PASS, no `backend/app` or `backend/tests` changes, `pytest -q backend/tests/llm_orchestration` PASS 221 tests, ruff checks PASS | `Delivered` |
| `CS-328` | Synthesize architecture decision and roadmap over CS-324 to CS-327. | `_story_briefs/cs-328-architecture-transition-calculs-interpretations-injection-llm.md`; story review `generated/11-code-review.md` | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md`; `01-evidence-map.md`; `02-target-contract.md`; `03-legacy-transition.md`; `04-story-candidates.md`; `05-risk-register.md` | `validation-output.md`: source audit folders exist, required IDs/tokens present, required files exist, no app/test/frontend/migration changes | `Delivered` |
| `CS-329` | Produce final consolidated transition report from CS-324 to CS-328. | `_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md`; `generated/10-final-evidence.md` AC1-AC9 | `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`; `evidence-sources.md`; `validation-output.md` | `generated/10-final-evidence.md`: path checks PASS, source-ID scans PASS, section scans PASS, no app changes PASS, story validate/lint PASS; `generated/11-code-review.md` verdict CLEAN | `Delivered` |

## 6. Evidence of completion

### Code evidence

- `frontend/src/config/analytics.ts`: proves the active analytics provider union was narrowed to `plausible` and `noop` for `CS-323`.
- `frontend/src/hooks/useAnalytics.ts`: proves the removed-provider `_paq` branch is not active for `CS-323`.
- `frontend/src/tests/useAnalytics.test.tsx`: proves behavior coverage was updated for `CS-323`.
- `git status --short -- backend/app backend/tests frontend/src backend/migrations` in `CS-329` evidence and `CS-328` validation proves no app source, backend test, frontend source or migration change for report/architecture stories.

### Test evidence

- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/generated/10-final-evidence.md`: frontend lint PASS, targeted Vitest PASS, expanded Vitest PASS, full Vitest PASS, build PASS.
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/validation-output.md`: `pytest -q backend/tests/unit/domain/astrology` PASS, 594 tests.
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/validation-output.md`: `pytest -q backend/tests/llm_orchestration` PASS, 221 tests; ruff format/check PASS.
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/validation-output.md`: astrology tests PASS, rejected workflow tests PASS, ruff checks PASS.
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/validation-output.md`: `pytest -q backend/tests/llm_orchestration` PASS, 221 tests; ruff checks PASS.

### Documentation evidence

- `_condamad/audits/**/05-executive-summary.md`: audit conclusions and findings for `CS-324` to `CS-327`.
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md`: target architecture and roadmap for `CS-328`.
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`: final synthesis for `CS-329`.

### Operational evidence

- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-before.txt`, `provider-scan-after.txt`, `removal-audit.md`, `validation-frontend.txt`: persisted before/after and validation evidence for provider removal.
- `_condamad/codex-runs/cs-323-dev-story.log`, `cs-323-final-validation.log`, `cs-323-review-fix-story.log`: useful run logs exist for the `CS-323` implementation and validation sequence.
- `_condamad/codex-runs/cs-324-domain-audit.log` through `cs-327-domain-audit.log`: audit execution logs exist for the four explicit audits.
- `_condamad/codex-runs/cs-328-product-architecture.log`: architecture execution log exists.
- `_condamad/codex-runs/cs-329-dev-story.log`, `cs-329-final-validation.log`, `cs-329-implementation-review-fix.log`: report-only implementation and validation logs exist.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `pnpm lint` | full suite | PASS | `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/generated/10-final-evidence.md` | Frontend lint/typecheck for analytics cleanup. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics` | targeted | PASS | same as above | 4 analytics tests. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | full suite | PASS | same as above | 116 files, 1280 passed, 8 existing skips. |
| `pnpm build` | targeted | PASS | same as above | `tsc -b` and Vite production build. |
| `rg -n "matomo|_paq" frontend/src .env.example docs` | targeted | PASS | same as above | Exit 1 expected no-match; active frontend/docs clear. |
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit>` | targeted | PASS | each audit `validation-output.md` | Python commands state venv activation before execution. |
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py <audit>` | targeted | PASS | each audit `validation-output.md` | Applies to `CS-324` to `CS-327`. |
| `pytest -q backend/tests/unit/domain/astrology` | targeted | PASS | `CS-324` and `CS-326` audit validation outputs | 594 tests recorded. |
| `pytest -q backend/tests/llm_orchestration` | targeted | PASS | `CS-325` and `CS-327` audit validation outputs | 221 tests recorded. |
| `ruff format --check .` | full suite | PASS | `CS-325`, `CS-326`, `CS-327` validation outputs | Non-mutating check. |
| `ruff check .` | full suite | PASS | `CS-325`, `CS-326`, `CS-327` validation outputs | All checks passed. |
| `git status --short -- backend/app backend/tests frontend/src backend/migrations` | targeted | PASS | `CS-328` validation output; `CS-329` final evidence | No application surfaces changed for architecture/report stories. |
| Local app startup for `CS-323` | manual | PASS | `CS-323` final evidence, current verification run 2026-05-27 | Port 5173 already in use; `Invoke-WebRequest http://127.0.0.1:5173` returned HTTP 200. |
| Local app startup for `CS-324` to `CS-329` | manual | SKIPPED | `CS-329` final evidence and validation output | Report/audit/architecture-only stories changed no runtime path. |
| Full backend pytest for `CS-329` | full suite | SKIPPED | `CS-329` final evidence | Skipped because no backend app/test file changed; no-app-change guard used. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No application-code deviation is evidenced for `CS-324` to `CS-329`; validation guards in audit/architecture/report artifacts record no `backend/app`, `backend/tests`, `frontend/src` or migration changes.
- `CS-323` story header still shows `Status: ready-to-review` in `00-story.md`, while `_condamad/stories/story-status.md` shows `CS-323` as `done` and `generated/11-code-review.md` records closure refresh. This is a story-file status mismatch, not an implementation evidence gap.
- `CS-324` to `CS-328` tracker rows show `ready-to-dev` in `_condamad/stories/story-status.md`, while deliverable folders and validation outputs exist. `CS-329` final evidence explicitly records this as a governance mismatch.

### Known limits

- The LLM transition is not implemented in runtime code by this series. `CS-329` states no code, prompt, endpoint, provider, frontend, DB or migration was modified.
- `CS-328` records open owner decisions for schema naming, evidence role, legacy natal branch classification and prompt placeholder shape.
- No commit range proving the full implementation span was evidenced in this report; current HEAD only was observed.

### Assumptions

- Audit and architecture deliverable folders dated `2026-05-26-0000` are treated as the canonical deliverables for `CS-324` to `CS-328` because `CS-329` final evidence lists and uses exactly those folders.

## 9. Residual risks

- `chart_json` remains de facto source of truth until future implementation stories execute the architecture roadmap. Impact: future prompt work may preserve the legacy carrier. Evidence: `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/05-risk-register.md`.
- `evidence_catalog` role remains ambiguous between validation-only and prompt-visible evidence refs. Impact: grounding and auditability may diverge. Evidence: `CS-325` and `CS-328` risk records.
- Product compatibility branches such as `/users`, `free_short`, schema compatibility and fallback branches need classification before removal. Impact: unsafe breaking changes or hidden fallback retention. Evidence: `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/05-executive-summary.md` and `CS-328` risk register.
- Tracker governance mismatch for `CS-324` to `CS-328` can mislead future automation into treating completed audit/architecture deliverables as not implemented. Evidence: `_condamad/stories/story-status.md` rows and `CS-329` final evidence residual risk.

## 10. Evidence gaps

- Commit range is Not evidenced; only current branch `main` and current HEAD `b91e1a8a` were observed.
- `CS-324` to `CS-328` do not have `generated/10-final-evidence.md` files in the story capsules; their delivery evidence is held in audit/architecture `validation-output.md` files and `generated/11-code-review.md` story-contract review artifacts.
- No production analytics ingestion validation is evidenced for `CS-323`; the story scope validated local frontend behavior, scans, build and local app availability.
- No external business/product signoff is evidenced for future LLM owner decisions; `CS-328` explicitly leaves owner decisions open.

## 11. Recommended next actions

1. Align `_condamad/stories/story-status.md` for `CS-324` to `CS-328` with the existing audit/architecture deliverables, or create an explicit governance note explaining why completed deliverables remain `ready-to-dev`.
2. Start the first roadmap implementation story from `CS-328`: formalize `llm_astrology_input_v1` around `AINarrativeInputContract`, with explicit owner approval and no raw `ChartObjectRuntimeData` prompt/provider exposure.
3. Before changing prompt runtime, decide whether `evidence_refs` are prompt-visible, validation-only or both, because this blocks hash/audit and grounding design.
4. Classify `/users`, `free_short`, schema compatibility and fallback branches as `intentional`, `delete-candidate` or `needs-user-decision` before removing legacy prompt carriers.

## 12. Final delivery status

`Delivered`

The requested series has evidence for all seven stories: `CS-323` has code, tests, scans, build and CLEAN review evidence; `CS-324` to `CS-327` have audit folders with validation outputs and findings; `CS-328` has an architecture package with validation output; `CS-329` has a final synthesis report with CLEAN review evidence. Remaining risks are future LLM implementation and governance/status alignment risks, not missing delivery evidence for this report package.
