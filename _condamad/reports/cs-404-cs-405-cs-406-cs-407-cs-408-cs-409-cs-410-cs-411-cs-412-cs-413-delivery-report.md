# Delivery Report - cs-404 to cs-413

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-31 18:40:08 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | `f77b9eae` / no range evidenced |
| Stories covered | Requested brief keys: `cs-404`, `cs-405`, `cs-406`, `cs-407`, `cs-408`, `cs-409`, `cs-410`, `cs-411`, `cs-412`, `cs-413` |
| Executable capsules covered | `CS-409-contrats-versionnes-lecture-natale-basic-v2` through `CS-418-integrer-basic-natal-v2-persistance-cache-qa` |
| Source documents | `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md`; `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md`; `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`; `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`; `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md`; `_story_briefs/cs-409-resoudre-contradictions-themes-natals-basic.md`; `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`; `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md`; `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md`; `_story_briefs/cs-413-integrer-basic-natal-v2-persistance-cache-qa.md` |
| Capsule source | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2`; `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic`; `_condamad/stories/CS-411-natal-fact-graph-basic-tracable`; `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree`; `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic`; `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic`; `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable`; `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan`; `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal`; `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa` |
| Status tracker | `_condamad/stories/story-status.md` rows `CS-409` to `CS-418` map the requested source briefs to `done` capsules |
| Regression guardrail source | `_condamad/stories/regression-guardrails.md` (`RG-159` to `RG-168` cover this Basic V2 series) |
| Audits in this series | None. User instruction says "Aucun audit dans cette serie"; no audit capsule was provided for `cs-404` to `cs-413`. |
| Diff source | Story final evidence, code-review artifacts, evidence folders, current `git status --short` |
| Validation source | Story-time evidence and reviews; report-time source inspection only |

## 1. Executive summary

The ten requested briefs are implemented through capsules `CS-409` to `CS-418`. Each capsule has `generated/10-final-evidence.md` and `generated/11-code-review.md`; reviews for `CS-409` through `CS-418` are `CLEAN`, with fixed findings recorded in the review artifacts.

Final initiative status is `Implemented but not validated`. The implemented story surfaces are evidenced by targeted backend/frontend tests, lint, scans, capsule validation and clean reviews, but release-level validation is incomplete: several stories explicitly skipped the full backend suite, and `CS-417` records a broad `python -B -m pytest -q --tb=short` run with two failures classified as unrelated pre-existing governance guards in `generated/10-final-evidence.md`.

No audit exists in this series, so there are no audit findings, risks or candidates to link. The only review findings are implementation-review findings inside the story capsules, and all are recorded as fixed before final `CLEAN` verdicts.

## 2. Initial context and trigger

The trigger is a Basic natal reading V2 delivery chain after the earlier public natal-reading stabilization work. The source briefs define, in order, versioned Basic V2 contracts, birth-time eligibility classification, traceable fact graph construction, calibrated salience, narrative theme taxonomy, contradiction resolution, inspectable reading-plan construction, constrained LLM payload, Basic draft validation/repair, and integration into persistence/cache/QA.

Evidence: `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md` through `_story_briefs/cs-413-integrer-basic-natal-v2-persistance-cache-qa.md`; tracker mappings in `_condamad/stories/story-status.md` from `CS-409` to `CS-418`; final evidence files under `_condamad/stories/CS-409-*` through `_condamad/stories/CS-418-*`.

## 3. Story scope

| Requested story | Executable capsule | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|---|
| `cs-404` | `CS-409-contrats-versionnes-lecture-natale-basic-v2` | Define strict versioned Basic V2 contracts and public boundary. | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/00-story.md`; `generated/03-acceptance-traceability.md` | Runtime LLM/provider execution excluded; pure contracts/docs/tests per `generated/10-final-evidence.md`. |
| `cs-405` | `CS-410-classifier-eligibilite-heure-naissance-basic` | Classify full/approximate/date-only birth-time eligibility and filter Basic surfaces. | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/00-story.md`; `generated/03-acceptance-traceability.md` | App startup and full backend suite not run; no route/API/frontend surface changed. |
| `cs-406` | `CS-411-natal-fact-graph-basic-tracable` | Build traceable internal Basic natal fact graph. | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`; `generated/03-acceptance-traceability.md` | Public/API/frontend `source_paths` exposure excluded and scanned. |
| `cs-407` | `CS-412-prioriser-faits-natals-basic-salience-calibree` | Prioritize facts by calibrated Basic salience. | `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/00-story.md`; `generated/03-acceptance-traceability.md` | Full backend suite not run; targeted model/fact-graph/scan evidence used. |
| `cs-408` | `CS-413-definir-taxonomie-themes-narratifs-basic` | Define versioned Basic narrative theme taxonomy. | `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/00-story.md`; `generated/03-acceptance-traceability.md` | Public narrative contracts unchanged except guarded integration evidence. |
| `cs-409` | `CS-414-resoudre-contradictions-themes-natals-basic` | Resolve Basic theme contradictions into nuanced internal syntheses. | `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/00-story.md`; `generated/03-acceptance-traceability.md` | Full backend suite not run; resolver remains internal, not public prose. |
| `cs-410` | `CS-415-reading-plan-basic-natal-inspectable` | Build inspectable Basic natal reading plan. | `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/00-story.md`; `generated/03-acceptance-traceability.md` | Full repository pytest not run; domain astrology unit suite and Basic pipeline regression used. |
| `cs-411` | `CS-416-contraindre-payload-llm-basic-par-reading-plan` | Constrain Basic provider payload to the reading plan. | `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`; `generated/03-acceptance-traceability.md` | Full backend suite not run; focused payload, architecture, provider and integration tests used. |
| `cs-412` | `CS-417-valider-reparer-narrative-basic-natal` | Validate, repair once, then reject/fallback Basic narrative drafts. | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/00-story.md`; `generated/03-acceptance-traceability.md` | Broad backend suite has two unrelated guard failures recorded in final evidence. |
| `cs-413` | `CS-418-integrer-basic-natal-v2-persistance-cache-qa` | Integrate Basic V2 plan/payload/validator with persistence, cache and QA. | `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`; `generated/03-acceptance-traceability.md` | Provider-live QA not run by design; fake gateway and targeted runtime evidence used. |

## 4. Implementation summary

- `CS-409`: `backend/app/domain/astrology/reading/basic_natal_contracts.py` defines strict Basic V2 contracts; `backend/docs/basic-natal-reading-v2-contract.md` documents the LLM as controlled writer; `backend/tests/unit/test_basic_natal_reading_contracts.py` and `backend/tests/architecture/test_basic_natal_reading_contract_boundaries.py` guard serialization and ownership.
- `CS-410`: `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py`, `structured_facts_v1_builder.py` and `llm_astrology_input_v1.py` classify birth-time confidence and filter house/angle/ruler surfaces for Basic.
- `CS-411`: `natal_fact_graph.py` and `natal_fact_graph_builder.py` create deterministic traceable internal facts while keeping `source_paths` out of API/frontend surfaces.
- `CS-412`: `natal_salience_model.py` scores facts with stable reason/exclusion codes and keeps minor/technical facts below eligible Sun, Moon and Ascendant pillars.
- `CS-413`: `natal_theme_taxonomy.py` defines ten versioned Basic theme codes, activation metadata, hierarchy and forbidden formulations.
- `CS-414`: `natal_synthesis_resolver.py` resolves mixed resources, constraints and tensions into nuanced internal syntheses; review evidence confirms no public/LLM boundary import.
- `CS-415`: `basic_natal_reading_plan.py` builds bounded inspectable Basic plans with public evidence, limitations, disclaimers and opaque evidence IDs.
- `CS-416`: `theme_astral_provider_payload_builder.py` emits `basic_natal_prompt_payload` from the plan, excluding PII, `chart_json`, raw IDs, source paths and internal scores.
- `CS-417`: `narrative_natal_reading_validator.py` and `interpretation_service.py` validate provider Basic drafts against the plan, repair once, then accept, reject or fallback with audited metadata.
- `CS-418`: `interpretation_service.py` integrates Basic V2 generation before persistence/cache handoff; frontend regression evidence keeps the public narrative rendering path guarded.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `cs-404` | AC1-AC9: strict version constants, public/internal evidence separation, unknown-field and technical-marker rejection, docs and artifacts. | `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md` | `_condamad/stories/CS-409-contrats-versionnes-lecture-natale-basic-v2/generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Contract pytest PASS, architecture guard PASS, narrative V1 PASS, docs ownership PASS, review `CLEAN` in `generated/11-code-review.md` | Delivered |
| `cs-405` | AC1-AC10: full/approximate/date-only eligibility, missing timezone downgrade, downstream filtering, no noon surrogate. | `_story_briefs/cs-405-classifier-eligibilite-heure-naissance-lecture-basic.md` | `_condamad/stories/CS-410-classifier-eligibilite-heure-naissance-basic/generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Targeted pytest PASS with 25 tests, ruff PASS, scans PASS with false-positive classification, review `CLEAN` | Delivered |
| `cs-406` | AC1-AC10: required fact families, stable IDs, source paths, date-only gates, runtime-only projections, no public `source_paths`. | `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md` | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Targeted pytest PASS (`19 passed`), `ruff check .` PASS, `ruff format --check .` PASS, public/API scan PASS, review `CLEAN` | Delivered |
| `cs-407` | AC1-AC14: salience score/level/reasons, pillar priority, weak-signal exclusion, archetype fixtures, no public salience leak. | `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md` | `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/generated/03-acceptance-traceability.md`; `evidence/salience-after.json` | Targeted salience/fact graph pytest PASS (`18 passed`), scans PASS, story validators PASS, review `CLEAN` | Delivered |
| `cs-408` | AC1-AC16: ten Basic themes, activation metadata, timed house availability, hierarchy, forbidden wording, public-boundary protection, `RG-162`. | `_story_briefs/cs-408-definir-taxonomie-themes-narratifs-basic.md` | `_condamad/stories/CS-413-definir-taxonomie-themes-narratifs-basic/generated/03-acceptance-traceability.md`; `evidence/theme-taxonomy-after.json` | Taxonomy/activation pytest PASS (`10 passed`), narrative public-boundary tests PASS, `ruff check .` PASS, review `CLEAN` | Delivered |
| `cs-409` | AC1-AC21: internal synthesis resolver, resource/constraint/tension integration, nuance for mixed signals, date-only downgrades, no public leakage. | `_story_briefs/cs-409-resoudre-contradictions-themes-natals-basic.md` | `_condamad/stories/CS-414-resoudre-contradictions-themes-natals-basic/generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Resolver/contradiction/support/narrative tests PASS (`26 passed`), scans PASS, capsule validation PASS, review `CLEAN` | Delivered |
| `cs-410` | AC1-AC23: inspectable plan, eligibility/salience/theme/synthesis inputs, bounded sections, opaque public evidence, public limits/disclaimers. | `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md` | `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Domain astrology suite PASS (`681 passed` in review), targeted plan pytest PASS (`14 passed`), app import PASS, scans PASS, review `CLEAN` | Delivered |
| `cs-411` | AC1-AC14: Basic provider payload derived from plan, style constraints, privacy, no `chart_json`, no scores/source paths/raw IDs. | `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md` | `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/generated/03-acceptance-traceability.md`; `evidence/basic-payload-after.json` | Payload/provider/architecture/integration tests PASS, `ruff check .` PASS, app import PASS, review `CLEAN` | Delivered |
| `cs-412` | AC1-AC18: validate draft against plan, reject unsupported sections/facts/date-only surfaces/technical markers, repair once, audit rejection. | `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md` | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/generated/03-acceptance-traceability.md`; `generated/10-final-evidence.md` | Targeted validator/regression/integration tests PASS; broad backend `pytest -q` FAIL on two unrelated governance guards recorded in final evidence; review `CLEAN` | Implemented but not validated |
| `cs-413` | AC1-AC15: integrate Basic V2 plan/payload/validator with persistence, cache invalidation, quota timing, frontend public narrative and QA artifacts. | `_story_briefs/cs-413-integrer-basic-natal-v2-persistance-cache-qa.md` | `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/generated/03-acceptance-traceability.md`; `evidence/qa-report.md`; `evidence/validation.txt` | Backend integration/unit/architecture tests PASS, frontend tests PASS (`87 passed`), lint/build PASS, scans PASS, review `CLEAN` | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/astrology/reading/basic_natal_contracts.py`: `CS-409` contract owner for `BasicNatalInterpretationV2`, strict serialization and version fields, evidenced by `test_basic_natal_reading_contracts.py`.
- `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py`: `CS-410` canonical eligibility owner, evidenced by `test_basic_natal_eligibility_context.py`.
- `backend/app/domain/astrology/interpretation/natal_fact_graph.py` and `natal_fact_graph_builder.py`: `CS-411` fact graph owner, evidenced by `test_basic_natal_fact_graph.py` and public `source_paths` scans.
- `backend/app/domain/astrology/interpretation/natal_salience_model.py`: `CS-412` salience owner, evidenced by `test_basic_natal_salience_model.py` and `test_basic_natal_salience_archetypes.py`.
- `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`: `CS-413` taxonomy owner, evidenced by taxonomy and activation tests.
- `backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py`: `CS-414` contradiction resolver owner, evidenced by resolver and contradiction tests.
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`: `CS-415` reading-plan owner, evidenced by plan builder, public evidence and archetype tests.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`: `CS-416` Basic prompt payload owner, evidenced by payload and provider tests.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` and `interpretation_service.py`: `CS-417` and `CS-418` validation/runtime integration owners, evidenced by Basic validator, rejected-boundary and Basic V2 pipeline tests.

### Test evidence

- `CS-409` review: `test_basic_natal_reading_contracts.py` PASS (`16 passed`), `test_basic_natal_reading_contract_boundaries.py` PASS (`2 passed`), `test_narrative_natal_reading_v1.py` PASS (`14 passed`).
- `CS-410` final evidence: targeted eligibility/LLM/structured facts tests PASS (`25 passed`).
- `CS-411` review: targeted fact graph/date-only/architecture tests PASS (`19 passed`), `ruff check .` PASS, `ruff format --check .` PASS.
- `CS-412` review: salience/fact graph targeted tests PASS (`18 passed`) and scans PASS.
- `CS-413` review: taxonomy and activation tests PASS (`10 passed`), public-boundary tests PASS, `ruff check .` PASS.
- `CS-414` review: synthesis resolver, contradictions, support elements and narrative V1 tests PASS (`26 passed`).
- `CS-415` review: domain astrology unit suite PASS (`681 passed`) and targeted CS-415 tests PASS (`14 passed`).
- `CS-416` review: Basic payload builder PASS (`5 passed`), provider builder PASS (`14 passed`), architecture boundary PASS (`7 passed`), long integration PASS (`3 passed`).
- `CS-417` review: validator PASS (`11 passed`), related unit tests PASS (`23 passed`), rejected public boundary long test PASS (`8 passed`).
- `CS-418` review: backend Basic V2/rejected-boundary integration PASS (`11 passed`), backend quota/contracts/validator/payload/architecture PASS (`43 passed`), frontend target PASS (`87 passed`), frontend lint/build PASS.

### Documentation evidence

- `backend/docs/basic-natal-reading-v2-contract.md`: `CS-409` documentation for the controlled-writer Basic V2 contract.
- `_condamad/stories/regression-guardrails.md`: `RG-159` through `RG-168` record durable guardrails for eligibility, fact graph, salience, taxonomy, synthesis, reading plan, payload privacy, validation, runtime engine and Basic V2 public contract.
- Each capsule's `generated/03-acceptance-traceability.md` maps ACs to implementation and validation evidence.
- Each capsule's `generated/10-final-evidence.md` records files changed, commands run/skipped, DRY/No Legacy evidence, risks and final worktree status.

### Operational evidence

- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/evidence/qa-report.md`: persisted QA report for Basic V2 integration.
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/evidence/validation.txt`: relaunch results for backend lint/tests, frontend tests/lint/build, scans and story validators.
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json`: provider-visible Basic payload after-proof.
- `_condamad/stories/CS-415-reading-plan-basic-natal-inspectable/generated/11-code-review.md`: app import smoke check with title `horoscope-backend`.
- Report-time `git status --short`: `M _condamad/run-state.json`. This report adds `_condamad/reports/cs-404-cs-405-cs-406-cs-407-cs-408-cs-409-cs-410-cs-411-cs-412-cs-413-delivery-report.md`.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | targeted / backend quality | PASS | `CS-411`, `CS-413`, `CS-416`, `CS-417` review/final evidence | Story-time evidence. |
| `ruff format --check .` | targeted / backend format | PASS | `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/generated/10-final-evidence.md` | `1743 files already formatted`. |
| `python -B -m pytest -q backend\tests\unit\test_basic_natal_reading_contracts.py --tb=short` | targeted | PASS | `CS-409` review | 16 passed. |
| `python -B -m pytest -q backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py ... --tb=short` | targeted | PASS | `CS-410` final evidence | 25 passed. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_basic_natal_fact_graph.py ... --tb=short` | targeted | PASS | `CS-411` review/final evidence | 19 passed after alignment. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_basic_natal_fact_graph.py backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py --tb=short` | targeted | PASS | `CS-412` final evidence | 18 passed. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_basic_natal_theme_taxonomy.py tests\unit\domain\astrology\test_basic_natal_theme_activation.py --tb=short` | targeted | PASS | `CS-413` review | 10 passed. |
| `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py tests/unit/domain/astrology/test_client_interpretation_support_elements.py tests/unit/test_narrative_natal_reading_v1.py --tb=short` | targeted | PASS | `CS-414` review | 26 passed. |
| `python -B -m pytest -q tests\unit\domain\astrology --tb=short` | targeted / domain suite | PASS | `CS-415` review | 681 passed. |
| `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short` | targeted | PASS | `CS-416` review | 5 passed. |
| `python -B -m pytest -q tests\unit\test_basic_natal_narrative_validator.py --tb=short` | targeted | PASS | `CS-417` review | 11 passed. |
| `python -B -m pytest -q --tb=short` | broad backend | FAIL | `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/generated/10-final-evidence.md` | 3667 passed, 2 skipped, 1253 deselected, 2 failed; failures classified as unrelated pre-existing governance guards. |
| `python -B -m pytest -q --long backend\tests\integration\test_basic_natal_v2_pipeline.py backend\tests\integration\test_basic_natal_v2_cache_invalidation.py backend\tests\integration\test_natal_interpretation_rejected_public_boundary.py --tb=short` | targeted / integration | PASS | `CS-418` final evidence | 11 passed. |
| `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard` | targeted / frontend | PASS | `CS-418` final evidence | 87 passed. |
| `pnpm --dir frontend lint` | targeted / frontend quality | PASS | `CS-418` final evidence | TypeScript lint/typecheck passed. |
| `pnpm --dir frontend build` | targeted / frontend build | PASS | `CS-418` review | Build passed. |
| Full backend suite for stories that skipped it | full suite | NOT RUN | `CS-409`, `CS-410`, `CS-411`, `CS-412`, `CS-414`, `CS-416`, `CS-418` final evidence | Skipped with story-specific justification; not a release-level PASS. |
| Provider-live QA for Basic V2 | external | EXTERNALLY REQUIRED | `CS-418` final evidence says provider-live QA not run by design; fake gateway used | External live provider behavior remains outside automated proof. |
| Report-time lint/tests/build | full suite | NOT RUN | This report | Report phase only synthesized evidence per user constraint; no application code changed. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No audit story exists in this series. User instruction explicitly states "Aucun audit dans cette serie"; therefore no audit findings, risks or candidates are linked.
- `CS-417` implementation is reviewed `CLEAN`, but its own final evidence records a broad backend test command as failed on two unrelated governance guards. This prevents treating the initiative as release-validated.
- `CS-418` uses fake-gateway/runtime QA and targeted regression evidence; provider-live QA is explicitly not run.

### Known limits

- Full backend pytest was skipped in multiple capsules with targeted compensating tests: `CS-409`, `CS-410`, `CS-411`, `CS-412`, `CS-414`, `CS-416`, `CS-418`.
- Current worktree had `M _condamad/run-state.json` before this report was written; it is not application code evidence for this delivery.
- Several stories use bounded `rg` scans with expected/false-positive hits classified in final evidence instead of zero-hit global scans.

### Assumptions

- Requested lowercase keys `cs-404` to `cs-413` are source-brief identifiers. The executable evidence is in tracker rows `CS-409` to `CS-418`, which map to those source briefs in `_condamad/stories/story-status.md`.
- Review values such as `CLEAN`, `pass`, `done` and `targeted-pass-after-review-fix-with-full-suite-unrelated-failures` are source evidence; final delivery statuses in this report use only the workflow status values.

## 9. Residual risks

- Release-level validation gap: broad backend validation is not clean across the whole series because `CS-417` records two broad-suite failures, even though they are classified as unrelated. Impact: final initiative status cannot be `Delivered`.
- Full-suite coverage gap: several stories did not run full backend pytest. Impact: unrelated regressions outside targeted Basic V2 surfaces may remain undetected.
- Provider-live gap: `CS-418` did not run live provider QA. Impact: fake-gateway evidence may miss provider-specific response shape or content variance.
- Tracker/provenance ambiguity: requested brief keys `cs-404` to `cs-413` correspond to executable capsules `CS-409` to `CS-418`, not same-number tracker rows. Impact: future release notes must cite both brief key and capsule key.

## 10. Evidence gaps

- NOT RUN: report-time lint, tests, build or app startup. This phase created only the delivery report and inspected existing evidence.
- NOT RUN: full backend pytest for `CS-409`, `CS-410`, `CS-411`, `CS-412`, `CS-414`, `CS-416`, `CS-418`.
- FAIL: broad backend pytest recorded by `CS-417` final evidence has two failures classified as unrelated pre-existing governance guards.
- EXTERNALLY REQUIRED: live provider QA for Basic V2 integration after `CS-418`.
- Not evidenced: a single clean release-gate log covering backend full suite, frontend lint/test/build and app startup after all ten stories.

## 11. Recommended next actions

1. Run a release validation gate after activating the Python venv: backend full pytest, backend `ruff check .`, frontend lint/test/build, and local app startup; persist the log under `_condamad/reports/` or a follow-up capsule.
2. Resolve or formally waive the two broad-suite governance failures recorded in `CS-417` before marking the initiative `Delivered`.
3. Run provider-live Basic V2 QA for a Basic complete natal reading and link the result to `CS-418` evidence.
4. Add a tracker note or report index that maps requested briefs `cs-404` to `cs-413` to capsules `CS-409` to `CS-418`.

## 12. Final delivery status

`Implemented but not validated`

The implementation is evidenced story by story: all ten capsules have completed final evidence, clean implementation reviews, AC traceability and targeted validation. The consolidated delivery is not release-validated because full-suite validation is either skipped on several stories or failed in `CS-417` on classified unrelated governance guards, and provider-live QA for the final Basic V2 integration is still externally required.
