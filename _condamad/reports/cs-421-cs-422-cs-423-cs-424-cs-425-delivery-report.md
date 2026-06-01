# Delivery Report - CS-421 to CS-425

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-06-01 02:50:45 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Current commit | `c4a4632e` |
| Commit range | Not evidenced |
| Stories covered | CS-421, CS-422, CS-423, CS-424, CS-425 |
| Source documents | `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`; `_story_briefs/cs-422-simplifier-rendu-basic-natal-sources-mentions-legales.md`; `_story_briefs/cs-423-qa-live-lecture-basic-natal-lisible.md`; `_story_briefs/cs-424-verifier-corriger-generation-prompts-basic-natal.md`; `_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md` |
| Story capsules | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal`; `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales`; `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible`; `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal`; `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees` |
| Diff source | Story final evidence and implementation reviews; exact full commit range Not evidenced |
| Validation source | Story-time final evidence, `generated/11-code-review.md`, persisted evidence files, and `_condamad/codex-runs/*-final-validation.log` |
| Audits in this series | None. User instruction says "Aucun audit dans cette serie"; no audit story directory was provided for CS-421 to CS-425. |
| Report-time validation | NOT RUN. Report generation only; no applicative code was modified or revalidated. |

## 1. Executive summary

The CS-421 to CS-425 series is delivered from repository evidence. The chain covers backend editorial contract strengthening, frontend Basic V2 rendering simplification, QA evidence capture, final prompt correction, and runtime invalidation/regeneration of degraded Basic natal cache rows.

All five stories are marked `done` in `_condamad/stories/story-status.md` with last update `2026-06-01`. Each story has `generated/10-final-evidence.md`; each story has a final `generated/11-code-review.md` with verdict `CLEAN`; and each final-validation log shows CONDAMAD story validation and strict lint passing.

Final initiative status: `Delivered`.

Material residual gaps remain documented: CS-423 browser QA is fixture-origin and does not prove the real historical cache for `daconrilcy@hotmail.com`; no live provider call is evidenced; exact commit range is Not evidenced. CS-425 mitigates the cache risk at runtime by invalidating missing/old editorial versions and degraded baseline tokens.

## 2. Initial context and trigger

The initiative was triggered by Basic natal V2 public output that could still read as internal assembly rather than a public report. Evidence anchors:

- CS-421 story source states Basic natal V2 was exact at plan level but exposed raw labels, generic source explanations, weak deterministic fallback prose, and no clear narrative thread: `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md`.
- CS-422 story source states `/natal` repeated Basic V2 sources inside themes, repeated sources near the end, then showed two legal areas: `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md`.
- CS-423 story source states `/natal` needed QA proof that the Basic natal reading is readable, plan-backed, and free of known public leak tokens: `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/00-story.md`.
- CS-424 story source states CS-416 proved confidential plan-backed payload, but not that the final `theme_astral_prompt_v1` prompt told the model how to produce a human Basic report: `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/00-story.md`.
- CS-425 story source states persisted Basic V2 rows could remain schema-compatible while carrying old editorial content: `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/00-story.md`.

No audits were performed in this series. Therefore there are no audit findings, risks, or candidates to link to these stories. The relevant risks are story-origin risks and implementation-review residual risks, not audit-origin findings.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-421 | Create a backend Basic natal editorial contract derived from `BasicNatalReadingPlan`, then reject mechanical, technical, unaccented, duplicated, or disconnected public Basic text. | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md` | No frontend rendering, no live provider call, no historical regeneration. |
| CS-422 | Simplify React `/natal` Basic V2 rendering into one continuous report with one source appendix and one legal area. | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md` | No backend serializer/API/persistence change; no PDF/offers/quotas. |
| CS-423 | Produce QA-only evidence that `/natal` renders a readable Basic V2 output and classify remaining gaps. | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/00-story.md` | No product runtime correction; no prompt/cache/quota/persistence behavior change. |
| CS-424 | Prove and correct the final Basic prompt rendered for `theme_astral_prompt_v1`. | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/00-story.md` | No frontend, public API, DB migration, quota, or live provider call. |
| CS-425 | Make Basic complete cache compatibility depend on schema, engine, editorial version, and degraded-content detection. | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/00-story.md` | No batch migration of historical rows; no provider live call; no broad frontend redesign. |

## 4. Implementation summary

CS-421 strengthened backend editorial material and validation:

- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`: `generated/10-final-evidence.md` says it added `BasicNatalEditorialBrief`, localized labels/explanations, section-derived editorial brief builder, and corrected public French accents.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`: final evidence says it added `report_arc`, `section_editorial_briefs`, `plain_language_glossary`, `forbidden_template_phrases`, and `source_usage_policy`.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`: final evidence says it rejects mechanical templates, raw English labels, unaccented French forms, source listings, one-sentence themes, and disclaimer-only content.
- Durable invariant `RG-169` was added according to `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/generated/10-final-evidence.md`.

CS-422 changed frontend rendering:

- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: final evidence says inline Basic theme evidence was removed, one source appendix is rendered after conclusion, and one Basic legal area is produced.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`, `frontend/src/api/natal-chart/index.ts`, `frontend/src/i18n/natalChart.ts`, and `frontend/src/features/natal-chart/NatalInterpretation.css`: final evidence lists these as changed for evidence metadata, copy, and CSS.
- `collectBasicPublicEvidence` and `mergePublicLegalLines` are named in final evidence as centralized dedupe helpers.
- Durable invariant `RG-170` is covered by the story and final review.

CS-423 added QA evidence and tests without runtime product changes:

- Backend tests changed: `backend/tests/integration/test_basic_natal_v2_pipeline.py`; `backend/tests/unit/test_basic_natal_narrative_validator.py`.
- Frontend tests changed: `frontend/src/tests/natalPublicDomGuard.test.tsx`; `frontend/src/tests/NatalChartPage.test.tsx`; `frontend/e2e/cs-423-natal-basic-readable.spec.ts`.
- Persisted artifacts: `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/basic-readable-api-after.json`, `basic-readable-dom-text-after.txt`, `basic-readable-desktop-after.png`, `basic-readable-mobile-after.png`, `validation.txt`, and `qa-report.md`.
- QA origin is explicitly `fixture`, not hidden as live cache/provider output, in `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md`.

CS-424 corrected and proved final prompt generation:

- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`: final evidence says Basic-specific instructions were added through the canonical `theme_astral_prompt_v1` seed path.
- Tests added/updated: `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`, `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`, `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`, `backend/tests/llm_orchestration/test_assembly_resolution.py`.
- Persisted prompt artifacts: `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/evidence/basic-final-prompt-before.txt`, `basic-final-prompt-after.txt`, `basic-user-payload-after.json`, `validation.txt`.
- Durable invariant `RG-171` is evidenced by `Select-String` in final evidence.

CS-425 added runtime cache compatibility enforcement:

- `backend/app/domain/astrology/reading/basic_natal_contracts.py`, `backend/app/domain/astrology/reading/__init__.py`, and `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`: final evidence says they serialize/enforce `basic_editorial_contract_version`.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`, `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`, `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`, and `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`: final evidence says they own DRY/guard behavior including degraded-token detection.
- Tests changed: `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`; `backend/tests/unit/test_basic_natal_reading_contracts.py`.
- Persisted cache artifacts: `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/basic-cache-degraded-before.json`, `basic-cache-degraded-after.json`, `qa-report.md`, `validation.txt`.
- Durable invariant `RG-172` is cited by the story and final review.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-421 | AC1-AC4: Basic payload and provider payload expose controlled editorial material from `BasicNatalReadingPlan`. | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/00-story.md` | `generated/10-final-evidence.md` lists `BasicNatalEditorialBrief`, `report_arc`, `section_editorial_briefs`, glossary, source policy. | `test_basic_natal_prompt_payload_builder.py` PASS 6; `test_theme_astral_provider_payload_builder.py` PASS 14. | Delivered |
| CS-421 | AC5-AC13: public Basic validator rejects mechanical/source-list/raw/unaccented/weak/disclaimer-only content and fallback stays acceptable. | Same story AC table. | `narrative_natal_reading_validator.py` changes listed in final evidence. | `test_basic_natal_narrative_validator.py` + `test_basic_natal_reading_contracts.py` PASS 30. | Delivered |
| CS-421 | AC14-AC16: runtime fixture, upstream guards, snapshots, scans and final evidence persisted. | Same story AC table. | `evidence/basic-payload-after.json`; `evidence/basic-public-contract-after.json`; `evidence/scan-classification.md`; `evidence/validation-output.txt`. | Integration `test_basic_natal_v2_pipeline.py --long` PASS 1; final review `CLEAN`. | Delivered |
| CS-422 | AC1-AC7: Basic V2 report order, no inline source blocks, one deduped source appendix, one legal area, no raw source text. | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/00-story.md` | `NatalInterpretationContent.tsx`, `NatalInterpretationTypes.ts`, `NatalInterpretation.css`, `i18n/natalChart.ts` listed in final evidence. | `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` PASS 119; DOM/scans PASS. | Delivered |
| CS-422 | AC8-AC11: Free short and narrative v1 remain unchanged; no inline styles or technical markers. | Same story AC table. | Tests and targeted scans listed in final evidence. | `pnpm --dir frontend lint` PASS; `pnpm --dir frontend build` PASS; `rg style={` PASS no matches; technical marker scans PASS. | Delivered |
| CS-423 | AC1-AC8: payload and public DOM exclude degraded phrases/raw labels and remain plan-backed. | `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/00-story.md` | Backend and frontend QA tests listed in final evidence. | Backend pytest PASS 14 passed, 1 deselected; Vitest PASS 113. | Delivered |
| CS-423 | AC9-AC17: desktop/mobile screenshots, validation output, QA report, introduction, three themes, conclusion persisted. | Same story AC table. | `evidence/basic-readable-*.json/.txt/.png`; `evidence/qa-report.md`; `evidence/validation.txt`. | Playwright chromium-mobile PASS 1; evidence scans PASS zero match; final review `CLEAN`. | Delivered with documented fixture-origin limit |
| CS-424 | AC1-AC4, AC6-AC7: published Basic final prompt renders from `theme_astral_prompt_v1`, consumes enriched payload, asks for human report, source annexes, safety and denylist. | `_condamad/stories/CS-424-verifier-generation-prompts-basic-natal/00-story.md` | `seed_theme_astral_prompt_contract.py`; `basic-final-prompt-before.txt`; `basic-final-prompt-after.txt`. | Bigbang prompt contract pytest PASS 4; scans classified PASS. | Delivered |
| CS-424 | AC5, AC8-AC12: gateway handoff keeps Basic payload private, old prompt keys absent, non-Basic handoffs unchanged, artifacts persisted. | Same story AC table. | `basic-user-payload-after.json`; provider handoff and assembly tests listed. | Provider handoff PASS 2; payload builder tests PASS 20; assembly resolution PASS 5; persistence PASS 6; app import PASS. | Delivered |
| CS-424 | AC13: durable final-prompt guard exists. | Same story AC table. | `_condamad/stories/regression-guardrails.md` contains `RG-171` per final evidence. | `Select-String ... 'RG-171'` PASS. | Delivered |
| CS-425 | AC1-AC6: Basic rows persist editorial version; missing/old/degraded rows invalidate cache; clean compatible cache served. | `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/00-story.md` | `basic_natal_contracts.py`; `stored_interpretation_payload.py`; `BASIC_NATAL_DEGRADED_BASELINE_TOKENS` named in final review. | `test_basic_natal_v2_cache_invalidation.py --long` PASS 6; contract tests PASS 30 in final review. | Delivered |
| CS-425 | AC7-AC10: eligible degraded rows regenerate, non-regenerable state controlled, quota timing preserved, rejected outputs hidden. | Same story AC table. | `evidence/qa-report.md` states compatible cache, missing/old version, degraded tokens, non-regenerable state. | Quota test PASS 4; rejected boundary PASS 8; pipeline PASS 1. | Delivered |
| CS-425 | AC11-AC13: before/after cache snapshots, no batch path, validation persisted. | Same story AC table. | `basic-cache-degraded-before.json`; `basic-cache-degraded-after.json`; `validation.txt`. | Full story-time pytest PASS 3678 passed, 2 skipped, 1266 deselected; no-batch `rg` PASS. | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`: CS-421 final evidence says it owns plan-derived editorial briefs; CS-425 final evidence says it participates in DRY/guard ownership for degraded detection.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`: CS-421 and CS-425 final evidence say it exposes enriched Basic payload material and participates in shared guard policy.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`: CS-421 final evidence says it rejects mechanical/technical/unaccented/weak content; CS-425 final evidence says degraded baseline token ownership is reused.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`: CS-422 final evidence says it removes inline Basic theme evidence and renders one source appendix plus one legal area.
- `frontend/src/features/natal-chart/NatalInterpretation.css`: CS-422 final evidence lists it as the style owner for compact appendix/legal rendering, with inline-style scans passing.
- `frontend/e2e/cs-423-natal-basic-readable.spec.ts`: CS-423 final evidence says it captures `/natal` QA artifacts using fixture-origin API mocks.
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`: CS-424 final evidence says it carries Basic final prompt guidance through canonical `theme_astral_prompt_v1`.
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`: CS-425 final evidence says it enforces Basic editorial contract compatibility for cache reuse.

### Test evidence

- CS-421 final review: `test_basic_natal_prompt_payload_builder.py` PASS 6, `test_basic_natal_narrative_validator.py` plus `test_basic_natal_reading_contracts.py` PASS 30, `test_basic_natal_public_evidence.py` PASS 5, `test_basic_natal_v2_pipeline.py --long` PASS 1.
- CS-422 final evidence: `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` PASS 119; lint PASS; build PASS.
- CS-423 final review: backend targeted pytest PASS 14 passed, 1 deselected; frontend targeted test PASS 113; Playwright spec PASS 1; evidence scans PASS zero match.
- CS-424 final review: Bigbang prompt PASS 4; provider handoff PASS 2; Basic/theme payload builder PASS 20; assembly resolution PASS 5; prompt persistence PASS 6; app import PASS.
- CS-425 final review: cache invalidation PASS 6; quota PASS 4; rejected boundary PASS 8; Basic pipeline PASS 1; Basic contract/validator PASS 30; app import PASS.

### Documentation evidence

- `_condamad/stories/story-status.md`: CS-421 through CS-425 rows are `done`, last update `2026-06-01`.
- `_condamad/stories/regression-guardrails.md`: final evidence/reviews cite `RG-169`, `RG-170`, `RG-171`, and `RG-172` as durable invariants created or covered by this series.
- `generated/03-acceptance-traceability.md` exists for each story capsule and is referenced by final evidence.
- `generated/06-validation-plan.md` exists for each story capsule and is referenced by final evidence.
- `generated/10-final-evidence.md` exists for each story capsule and is the main completion evidence.
- `generated/11-code-review.md` exists for each story capsule and carries final `CLEAN` review evidence.

### Operational evidence

- `_condamad/codex-runs/cs-421-final-validation.log`: `condamad_story_validate.py` PASS and `condamad_story_lint.py --strict` PASS.
- `_condamad/codex-runs/cs-422-final-validation.log`: story validation PASS and strict lint PASS.
- `_condamad/codex-runs/cs-423-final-validation.log`: story validation PASS and strict lint PASS.
- `_condamad/codex-runs/cs-424-final-validation.log`: story validation PASS and strict lint PASS.
- `_condamad/codex-runs/cs-425-final-validation.log`: story validation PASS and strict lint PASS.
- `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md`: fixture-origin QA decision and known live-cache limitation.
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/qa-report.md`: compatible cache served, missing/old version and degraded tokens rejected for cache reuse, no batch migration added.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for CS-421 | targeted | PASS | `_condamad/codex-runs/cs-421-final-validation.log` | Story-time final validation log. |
| `ruff check .`; targeted backend pytests; integration `--long`; evidence checks | targeted | PASS | `_condamad/stories/CS-421-renforcer-contrat-redactionnel-basic-natal/generated/10-final-evidence.md`; `generated/11-code-review.md` | Story-time validation. |
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for CS-422 | targeted | PASS | `_condamad/codex-runs/cs-422-final-validation.log` | Story-time final validation log. |
| `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading` | targeted | PASS | `_condamad/stories/CS-422-simplifier-rendu-basic-natal-sources-mentions-legales/generated/10-final-evidence.md` | 119 tests. |
| `pnpm --dir frontend lint`; `pnpm --dir frontend build`; frontend scans | targeted | PASS | CS-422 `generated/10-final-evidence.md`; `generated/11-code-review.md` | Includes no inline style, no legacy UI, no technical marker scans. |
| Controlled local startup with `pnpm.cmd --dir frontend dev` | manual | PASS | CS-422 `generated/10-final-evidence.md`; `generated/11-code-review.md` | Vite responded on `http://127.0.0.1:5173/`; process stopped. |
| Playwright/browser QA desktop + mobile for CS-422 | manual | NOT RUN | CS-422 `generated/10-final-evidence.md` | Not required by minimal commands; compensated by DOM tests, build, Vite startup. |
| Backend Python tests for CS-422 | targeted | NOT RUN | CS-422 `generated/10-final-evidence.md` | Frontend render-only story; no backend files changed. |
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for CS-423 | targeted | PASS | `_condamad/codex-runs/cs-423-final-validation.log` | Story-time final validation log. |
| Backend pytest for Basic pipeline and validator | targeted | PASS | CS-423 `generated/10-final-evidence.md`; `generated/11-code-review.md` | 14 passed, 1 deselected. |
| `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage` | targeted | PASS | CS-423 `generated/10-final-evidence.md`; `generated/11-code-review.md` | 113 passed. |
| `pnpm --dir frontend exec playwright test e2e/cs-423-natal-basic-readable.spec.ts --project chromium-mobile ...` | manual | PASS | CS-423 `generated/10-final-evidence.md`; `generated/11-code-review.md`; `evidence/*.png` | 1 passed; fixture-origin screenshots/artifacts persisted. |
| Full backend pytest suite for CS-423 | full suite | NOT RUN | CS-423 `generated/10-final-evidence.md` | Targeted backend tests and lint passed. |
| Real historical cache verification for `daconrilcy@hotmail.com` | external | EXTERNALLY REQUIRED | CS-423 `evidence/qa-report.md` | Fixture QA does not prove real local historical cache. |
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for CS-424 | targeted | PASS | `_condamad/codex-runs/cs-424-final-validation.log` | Story-time final validation log. |
| Backend prompt, provider handoff, payload, assembly, persistence pytests | targeted | PASS | CS-424 `generated/10-final-evidence.md`; `generated/11-code-review.md` | Includes 4 + 2 + 20 + 5 + 6 passing test counts. |
| Live provider call for CS-424 | external | SKIPPED | CS-424 `generated/10-final-evidence.md` | Explicitly out of scope. |
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for CS-425 | targeted | PASS | `_condamad/codex-runs/cs-425-final-validation.log` | Story-time final validation log. |
| Backend cache/quota/public-boundary/pipeline/validator pytests and app import | targeted | PASS | CS-425 `generated/10-final-evidence.md`; `generated/11-code-review.md` | Fresh review commands pass. |
| `python -B -m pytest -q --tb=short` for CS-425 | full suite | PASS | CS-425 `generated/10-final-evidence.md` | 3678 passed, 2 skipped, 1266 deselected. |
| Batch migration path | targeted | SKIPPED | CS-425 story and final evidence | Batch migration explicitly out of scope; no batch path added. |
| Report-time lint/tests/build | targeted | NOT RUN | This report | Report-only phase; no applicative code changed. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- None evidenced as unresolved in final reviews. Each `generated/11-code-review.md` for CS-421 through CS-425 has verdict `CLEAN`.

### Known limits

- CS-423 QA is fixture-origin. `_condamad/stories/CS-423-qa-live-lecture-basic-natal-lisible/evidence/qa-report.md` states the real route is opened, but endpoints are mocked in Playwright to isolate Basic V2 readability from cache/provider state.
- CS-423 does not prove the real local historical cache for `daconrilcy@hotmail.com`; this is explicitly classified in CS-423 final evidence and QA report.
- CS-424 did not call a live provider; live provider call is explicitly skipped/out of scope in CS-424 final evidence.
- CS-425 does not batch-migrate historical rows; final evidence says historical rows are classified at runtime and regenerated only when existing corrective policy allows it.
- Exact commit range is Not evidenced. Current branch/commit were observed as `main` / `c4a4632e`, while CS-425 review names `b129340f` as its reviewed implementation commit.

### Assumptions

- The story-time final evidence and final implementation reviews are treated as authoritative for validation because this report phase was explicitly constrained not to modify applicative code.
- `Delivered` is assigned at initiative level because all stories are `done`, all final reviews are `CLEAN`, required story-time validations pass, and remaining limitations are documented as external/out-of-scope or mitigated by later stories in the same series.

## 9. Residual risks

- Real cache/live-account proof remains external for CS-423. Impact: a local historical row for `daconrilcy@hotmail.com` could still require environment-specific QA. Evidence: CS-423 `evidence/qa-report.md` says origin `fixture` and does not replace real cache proof. Mitigation: run an external QA pass against the actual local/prod-like cache after CS-425 runtime compatibility is deployed.
- Live provider prose quality is not evidenced. Impact: the final prompt contract is proven, but actual provider output can still vary. Evidence: CS-424 final evidence skips live provider call. Mitigation: run a provider smoke or manual QA story when credentials and environment are available.
- Historical rows are not batch-migrated. Impact: old rows are handled lazily at runtime, not rewritten. Evidence: CS-425 final evidence and QA report say no batch migration path was added. Mitigation: monitor controlled regeneration states and decide separately whether an operational batch remediation is needed.
- Exact diff/commit range is not evidenced. Impact: release traceability is weaker than a commit-range report. Evidence: report metadata. Mitigation: generate a follow-up release note from Git once the intended base and head commits are provided.

## 10. Evidence gaps

- Full initiative commit range: Not evidenced.
- CI validation for the combined series: Not evidenced. All validations cited are local/story-time evidence.
- Report-time rerun of lint/tests/build: NOT RUN by design for this report-only phase.
- Real historical cache validation for `daconrilcy@hotmail.com`: EXTERNALLY REQUIRED, because CS-423 persisted fixture-origin QA and CS-425 proves runtime invalidation by tests rather than a real account cache inspection.
- Live provider output validation after CS-424 prompt correction: SKIPPED / EXTERNALLY REQUIRED depending on environment availability; CS-424 explicitly excludes live provider calls.
- Audit-to-story traceability: Not applicable. User instruction states no audit in this series; no audit artifacts were provided.

## 11. Recommended next actions

1. Run an environment-backed QA pass on `/natal` for the real test account/cache after CS-425 is present in the target environment; anchor the result to a new QA artifact or story if it finds residual degraded rows.
2. If release traceability is required, provide the base/head commits and generate a commit-range validation appendix for CS-421 to CS-425.
3. When provider credentials are available, run a controlled live/provider smoke for Basic natal output to complement CS-424 prompt proof and CS-423 fixture QA.

## 12. Final delivery status

`Delivered`

CS-421 through CS-425 are evidenced as delivered because `_condamad/stories/story-status.md` marks all five stories `done`, each capsule contains final evidence with AC-level PASS coverage, each final implementation review is `CLEAN`, and story-time validations cover backend lint/tests, frontend tests/lint/build, Playwright fixture QA, scans, app import, and cache invalidation behavior. Remaining limitations are explicit and non-blocking for repository delivery: real-account cache proof and live provider output remain external, while CS-425 adds runtime invalidation/regeneration controls for degraded Basic cache rows.
