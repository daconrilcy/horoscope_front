<!-- Commentaire global: rapport de livraison consolide pour la serie CONDAMAD CS-356 a CS-360. -->

# Delivery Report - cs-356-cs-357-cs-358-cs-359-cs-360

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-28 02:57:39 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced; report-time `git rev-parse --short HEAD` returned `9c807372`, but no implementation range was provided. |
| Stories covered | CS-356, CS-357, CS-358, CS-359, CS-360 |
| Source documents | `_story_briefs/cs-356-documenter-construction-prompts-theme-astral-par-plan.md`; `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md`; `_story_briefs/cs-358-generer-exemples-json-prompts-theme-astral-par-plan.md`; `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md`; `_story_briefs/cs-360-audit-admin-manual-execution-provider-capable.md`; `_condamad/stories/story-status.md` |
| Diff source | Story capsules, final evidence files, audit artifacts, and report-time `git status --short` showing only `?? _condamad/run-state.json` before this report was added. |
| Validation source | Story-time and audit-time evidence under `_condamad/stories/CS-356-*/evidence`, `_condamad/stories/CS-357-*/evidence`, `_condamad/stories/CS-358-*/evidence`, `_condamad/stories/CS-359-*/evidence`, and `_condamad/stories/CS-360-*/evidence`. Report-time validation of app behavior: NOT RUN. |

## 1. Executive summary

The series delivered four implementation/documentation stories and one audit story around natal prompt construction, prompt examples, legacy carrier removal, and admin manual execution policy.

Initiative status: `Partially delivered`.

Rationale: CS-356, CS-357, CS-358, and CS-359 have implementation evidence and PASS validation in their final evidence. CS-360 delivered the requested audit report and selected the `migrate` policy, but the audit itself records active findings F-001 through F-004 and candidate implementation stories. Those findings are not expected to be closed by an audit-only story, but they keep the overall series from being a fully delivered implementation closure.

## 2. Initial context and trigger

The initial trigger is the prompt-generation cartography continuation:

- CS-356 documents natal prompt construction by plan after CS-350 mapped the general prompt generation flow. Evidence: `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md`.
- CS-357 adds Mermaid diagrams for the natal prompt construction path. Evidence: `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md`.
- CS-358 creates concrete final provider-handoff JSON examples for `free`, `basic`, and `premium`. Evidence: `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/00-story.md`.
- CS-359 closes a No Legacy decision by deleting the dormant `event_guidance` provider-capable path that still depended on `chart_json`. Evidence: `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/00-story.md` and `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/generated/10-final-evidence.md`.
- CS-360 audits a separate admin-only provider-capable manual execution surface and selects `migrate` as the policy. Evidence: `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/01-admin-manual-execution-provider-capable-audit.md`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-356 | Create `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` explaining natal prompt construction by `free`, `basic`, `premium`. | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/00-story.md` | No runtime code, prompt seed, output schema, frontend, DB, migration, or provider call. |
| CS-357 | Create Mermaid diagrams for the same natal prompt construction flow. | `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md` | No runtime behavior, rendering dependency, generated JSON examples, frontend, DB, or provider call. |
| CS-358 | Create example provider-handoff JSON payloads and intermediate data for `1973-04-24`, Paris, `12:00:00` convention. | `_condamad/stories/CS-358-generer-exemples-json-prompts-theme-astral-par-plan/00-story.md` | No real LLM call, no provider response, no secret, no runtime prompt/config change. |
| CS-359 | Eliminate `event_guidance` legacy `chart_json` dependency by migration or deletion; final decision recorded as `delete`. | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/00-story.md` | No frontend, DB, public API route, provider integration, or unrelated guidance/natal behavior changes. |
| CS-360 | Produce a sourced audit for admin manual execution provider capability and policy. | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/00-story.md` | Audit-only: no backend runtime/test/frontend/DB/migration/provider behavior changes. |

## 4. Implementation summary

Documentation and examples:

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`: CS-356 final evidence says this document was created, includes 15 required sections, plan matrices, source citations, prompt-visible/backend-only/validation-only/audit-only boundaries, and no real provider call statement.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`: CS-357 final evidence says this annex contains 8 Mermaid blocks and is cited from the CS-356 document.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/README.md`, `intermediate-data.json`, `free-provider-payload.json`, `basic-provider-payload.json`, `premium-provider-payload.json`: CS-358 final evidence says these five deliverables were created, JSON parsed, plan payloads differ, and provider calls are marked false.

Backend No Legacy convergence:

- CS-359 final evidence records final decision `delete` for `event_guidance`.
- CS-359 changed `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/runtime/adapter.py`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/domain/llm/configuration/catalog.py`, `backend/app/domain/llm/governance/data/prompt_governance_registry.json`, `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`, `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`, and targeted tests/docs/guardrails.
- CS-359 evidence states `event_guidance` is absent from canonical contracts, seed prompts, taxonomy mapping, prompt catalog, paid use-case set, and adapter routing; residual backend hits are anti-return tests or `offer_event_guidance` chat intent.

Audit:

- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/01-admin-manual-execution-provider-capable-audit.md`: CS-360 audit report classifies admin manual execution as admin-only and provider-capable, separates sample payload CRUD from live execution, classifies `chart_json` as `migration target`, and selects primary recommendation `migrate`.
- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/02-finding-register.md`: CS-360 records active findings F-001 to F-004.
- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/03-story-candidates.md`: CS-360 maps those findings to SC-001, SC-004, SC-002, and SC-003.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-356 | Dedicated natal prompt construction document exists and contains mandatory sections. | `_story_briefs/cs-356-documenter-construction-prompts-theme-astral-par-plan.md`; `00-story.md` AC1-AC2 | `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`; `generated/10-final-evidence.md` AC1-AC2 | VC1/VC2 PASS in `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/evidence/validation.txt` | Delivered |
| CS-356 | Plan-specific prompt journey, injected data, persona, safety, exclusions, source citations, no provider call. | `00-story.md` AC3-AC10 | Same document; `_condamad/stories/CS-356-*/evidence/source-coverage.md` | VC3-VC6 PASS; source scans and content review recorded in final evidence | Delivered |
| CS-356 | Application code unchanged and evidence persisted. | `00-story.md` AC11-AC12 | CS-356 evidence folder and final evidence | VC7/VC8 PASS; `ruff check .` PASS; backend pytest PASS `3487 passed, 1 skipped, 1222 deselected` | Delivered |
| CS-357 | Mermaid document with at least seven diagrams, all three plans, global pipeline, injected data, persona, safety, message order, exclusions, no-call boundary. | `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md`; `00-story.md` AC1-AC10 | `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`; `generated/10-final-evidence.md` | Mermaid count PASS `mermaid_blocks 8`; targeted `rg` scans PASS; full backend pytest PASS `3487 passed, 1 skipped, 1222 deselected` | Delivered |
| CS-357 | CS-356 integration explicit, application source unchanged, evidence persisted. | `00-story.md` AC11-AC13 | Citation added in `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`; CS-357 evidence folder | Annex citation `rg` PASS; bounded `git status --short -- backend/app backend/tests frontend/src` PASS | Delivered |
| CS-358 | Five example deliverables under `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/`. | `_story_briefs/cs-358-generer-exemples-json-prompts-theme-astral-par-plan.md`; `00-story.md` AC1 | README, intermediate data, and three plan payload JSON files | Path checks in `_condamad/stories/CS-358-*/evidence/json-validation.txt` PASS | Delivered |
| CS-358 | JSON parses, payloads distinct, provider message roles correct, no provider call, prompt-only boundary enforced. | `00-story.md` AC2-AC7 | Static JSON examples and README | `python -B -m json.tool`; Python shape/distinct/role/boundary assertions PASS; targeted provider-boundary pytest PASS | Delivered |
| CS-358 | Missing birth time convention, generation method, and forbidden provider artifacts handled. | `00-story.md` AC8-AC10 | README and JSON markers | Positive `rg` markers PASS; forbidden scan corrected to separate `provider_response` exclusion label; AC10 PASS in final evidence | Delivered |
| CS-359 | Final `event_guidance` decision persisted as `delete`. | `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md`; `00-story.md` AC1 | `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/event-guidance-decision.md`; final evidence | Before/after scans persisted; capsule validation PASS | Delivered |
| CS-359 | Runtime contracts, seeds, governance, adapter routing, docs and RG-149 converge without `chart_json`/`natal_data` for `event_guidance`. | `00-story.md` AC2-AC8, AC11 | Changed backend LLM runtime/config/seeds/tests/docs listed in final evidence | Targeted LLM/tests PASS `54 passed, 16 deselected`; AST/JSON guard PASS; `rg` residual hits classified | Delivered |
| CS-359 | Public API unchanged and evidence persisted. | `00-story.md` AC9-AC10 | OpenAPI before/after snapshots; CS-359 evidence folder | OpenAPI paths equal; `TestClient(app).get('/openapi.json')` PASS 200; full backend pytest PASS `3349 passed, 1 skipped, 1223 deselected` | Delivered |
| CS-360 | Timestamped admin manual execution audit report exists with required sections and single recommendation. | `_story_briefs/cs-360-audit-admin-manual-execution-provider-capable.md`; `00-story.md` AC1-AC2, AC8 | `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/01-admin-manual-execution-provider-capable-audit.md`; `report-shape-check.txt` | Domain audit validate/lint PASS; required headings `rg` PASS; recommendation `migrate` recorded | Delivered for audit scope |
| CS-360 | Route-to-gateway trace, admin-only exposure, CRUD/live execution separation, `chart_json` policy, observability, and candidates documented. | `00-story.md` AC3-AC7, AC9 | Audit report; `01-evidence-log.md`; `02-finding-register.md`; `03-story-candidates.md`; `04-risk-matrix.md` | Targeted scan evidence; integration pytest PASS `40 passed in 3.09s`; no provider call executed | Delivered for audit scope |
| CS-360 | Application source unchanged and story evidence persisted. | `00-story.md` AC10-AC11 | CS-360 evidence folder; audit folder | Bounded status guard PASS for `backend/app`, `backend/tests`, `frontend/src`; real provider call SKIPPED by story | Delivered for audit scope |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`: CS-359 final evidence states the canonical `event_guidance` contract was removed.
- `backend/app/domain/llm/runtime/adapter.py`: CS-359 final evidence states the adapter special-case for `event_guidance` was removed.
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`: CS-359 final evidence states `chart_json` and `event_description` were removed from the guidance governance family.
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`: CS-359 final evidence states the `event_guidance` seed was removed.

### Test evidence

- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`: CS-359 final evidence says targeted legacy-extinction tests passed and guard that `event_guidance` has no supported fallback surface.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`: CS-359 final evidence says governance tests passed and `event_description` is rejected for the guidance family.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`: CS-358 and CS-359 final evidence cite this as provider-boundary / natal legacy carrier proof.
- `backend/tests/integration/test_admin_llm_catalog.py` and `backend/tests/integration/test_admin_llm_sample_payloads.py`: CS-360 validation evidence records `40 passed in 3.09s` with `--long`.

### Documentation evidence

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`: CS-356 deliverable for plan-specific prompt construction, boundaries, safety, validation, and no-call statement.
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`: CS-357 deliverable with 8 Mermaid diagrams and no-call boundary.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/`: CS-358 example folder containing provider-handoff payload examples and generation notes.
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`: CS-359 final evidence states CS-350 wording now says `event_guidance` is deleted by CS-359.

### Audit evidence

- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/01-admin-manual-execution-provider-capable-audit.md`: primary CS-360 audit report.
- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/02-finding-register.md`: active findings F-001, F-002, F-003, F-004.
- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/03-story-candidates.md`: candidates SC-001, SC-004, SC-002, SC-003.
- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/04-risk-matrix.md`: F-001/F-002 P1 risks; F-003/F-004 P2 risks.
- `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/01-evidence-log.md`: E-001 to E-018 source, scan, runtime test, and status evidence.

### Operational evidence

- `_condamad/stories/story-status.md`: rows CS-356 through CS-360 are marked `done` with last update `2026-05-28`.
- `_condamad/codex-runs/cs-356-dev-story.log`, `cs-356-review-fix-story.log`, `cs-356-final-validation.log`: useful implementation and review logs exist for CS-356.
- `_condamad/codex-runs/cs-357-dev-story.log`, `cs-357-review-fix-story.log`, `cs-357-final-validation.log`: useful implementation and review logs exist for CS-357.
- `_condamad/codex-runs/cs-358-dev-story.log`, `cs-358-review-fix-story.log`, `cs-358-final-validation.log`: useful implementation and review logs exist for CS-358.
- `_condamad/codex-runs/cs-359-dev-story.log`, `cs-359-review-fix-story.log`, `cs-359-final-validation.log`: useful implementation and review logs exist for CS-359.
- `_condamad/codex-runs/cs-360-domain-audit.log`, `cs-360-domain-audit-review.log`, `cs-360-final-validation.log`: useful audit and validation logs exist for CS-360.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| CS-356 VC1-VC8 document/content/status checks | targeted | PASS | `_condamad/stories/CS-356-documenter-construction-prompts-theme-astral-par-plan/generated/10-final-evidence.md`; `evidence/validation.txt` | Initial VC2 quoting issue was rerun and passed. |
| CS-356 `. .\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .` | targeted | PASS | CS-356 final evidence | Story-time validation. |
| CS-356 `. .\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --tb=short` | full suite | PASS | CS-356 final evidence | `3487 passed, 1 skipped, 1222 deselected`. |
| CS-357 targeted Python and `rg` diagram checks | targeted | PASS | CS-357 final evidence and `evidence/validation.txt` | Mermaid count 8 and required terms found. |
| CS-357 `ruff format --check .`; `ruff check .`; `python -B -m pytest -q --tb=short` from `backend` | full suite | PASS | CS-357 final evidence | `3487 passed, 1 skipped, 1222 deselected`. |
| CS-358 JSON parse, payload shape, distinct plans, role order, prompt boundary, forbidden scan | targeted | PASS | CS-358 final evidence; `evidence/json-validation.txt`; `evidence/forbidden-scan.txt` | Provider response label handled only as required exclusion label. |
| CS-358 `pytest` targeted files: `test_llm_astrology_input_boundaries.py`, `test_llm_astrology_input_v1.py`, `test_differentiation.py` | targeted | PASS | CS-358 final evidence | Existing tests reused; no app code changed. |
| CS-358 `ruff check backend` | targeted | PASS | CS-358 final evidence | `ruff format backend` SKIPPED because no Python file changed. |
| CS-359 targeted LLM/tests | targeted | PASS | CS-359 final evidence | `54 passed, 16 deselected`. |
| CS-359 `ruff check .`; full backend pytest | full suite | PASS | CS-359 final evidence | `3349 passed, 1 skipped, 1223 deselected`. |
| CS-359 OpenAPI before/after and TestClient `/openapi.json` | targeted | PASS | CS-359 final evidence | Public API route paths unchanged; TestClient 200. |
| CS-360 `pytest -q --long backend/tests/integration/test_admin_llm_catalog.py backend/tests/integration/test_admin_llm_sample_payloads.py` | targeted | PASS | `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/evidence/validation.txt` | `40 passed in 3.09s`; gateway is mocked; no real provider call. |
| CS-360 domain audit validate/lint scripts | targeted | PASS | CS-360 `evidence/validation.txt` | `condamad_domain_audit_validate.py` and `condamad_domain_audit_lint.py` passed. |
| CS-360 bounded status guard for `backend/app`, `backend/tests`, `frontend/src` | targeted | PASS | CS-360 `evidence/validation.txt` | No app/test/frontend source changes. |
| Real provider LLM call | external/manual | SKIPPED | CS-356, CS-357, CS-358, CS-360 story contracts and evidence | Explicitly forbidden by the stories. |
| Report-time app lint/tests/startup | full suite | NOT RUN | This report | Reporting phase was constrained to report and associated artifacts only; no code app change was made in this phase. |
| Local app startup | manual | NOT RUN | This report | No app startup evidence was produced for the report generation phase. Story-time backend pytest/OpenAPI evidence exists for implementation stories. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- CS-360 has no `generated/10-final-evidence.md`. Evidence exists through domain-audit artifacts and `evidence/validation.txt`, but the missing final evidence file is a report evidence gap relative to the usual dev-story capsule contract.
- CS-358 `00-story.md` still shows `Status: ready-to-review` in the file content read for this report, while `_condamad/stories/story-status.md` and CS-358 final evidence say `done`. This contradiction is recorded as an evidence gap.
- CS-360 `00-story.md` still shows `Status: ready-to-dev`, while `_condamad/stories/story-status.md` says `done` and the audit report exists. This contradiction is recorded as an evidence gap.

### Known limits

- CS-356 deliberately does not quote exact runtime prompt text; final evidence records exact wording as `a extraire depuis la configuration runtime`.
- CS-357 validates diagram presence and terms, but final evidence asks reviewers to verify Mermaid readability in the preferred renderer.
- CS-358 examples are `synthetic_example` provider-handoff examples, not verified ephemerides, provider results, or live runtime extraction.
- CS-360 audit uses mocked/admin integration tests and source inspection; no real provider call was performed because it was forbidden.

### Assumptions

- Delivery status uses the `condamad-delivery-report` workflow status vocabulary. Story-internal `PASS` evidence is mapped to `Delivered`; CS-360 is treated as delivered for audit scope but not as closure of its candidate implementation findings.

## 9. Residual risks

- CS-360 F-001, High: selected `migrate` policy is not yet encoded in runtime behavior, audit metadata, documentation, or guards. Evidence: `_condamad/audits/admin-manual-llm-execution/2026-05-28-0245/02-finding-register.md`.
- CS-360 F-002, High: natal admin samples still require `chart_json`, and manual execution can copy sample payload into gateway execution context. Evidence: same finding register, plus `01-evidence-log.md` E-007/E-010/E-011/E-015.
- CS-360 F-003, Medium: manual execution audit details do not persist policy classification. Evidence: `02-finding-register.md`.
- CS-360 F-004, Medium: no exact guard prevents future promotion of execute-sample outside admin-only provider-capable classification. Evidence: `02-finding-register.md` and `04-risk-matrix.md`.
- CS-359 residual product risk: final evidence asks reviewers to confirm `offer_event_guidance` remains acceptable as chat intent distinct from the deleted LLM use case.
- CS-356/CS-357/CS-358 documentation/example drift risk: future runtime prompt configuration, provider parameters, or plan shaping can diverge unless the docs/examples are refreshed with source-aligned validation.

## 10. Evidence gaps

- No implementation commit range is evidenced for the series; only current HEAD `9c807372` and story artifacts are evidenced.
- CS-360 lacks `_condamad/stories/CS-360-audit-admin-manual-execution-provider-capable/generated/10-final-evidence.md`.
- CS-358 story file status contradicts final evidence/tracker: `00-story.md` says `ready-to-review`; final evidence/tracker say `done`.
- CS-360 story file status contradicts tracker/audit completion: `00-story.md` says `ready-to-dev`; tracker says `done`.
- Report-time app validation was not run. This is intentional for a report-only phase, but it means this report does not add fresh PASS evidence beyond existing story-time/audit-time validation.
- Local app startup is Not evidenced for this reporting phase.

## 11. Recommended next actions

1. Implement CS-360 SC-001 `migrate-admin-manual-execution-sample-payload-carriers` to close F-001 and F-002 by migrating admin manual execution away from natal `chart_json`.
2. If SC-001 is split, run SC-004 `remove-chart-json-requirement-from-admin-sample-payloads` first to remove the concrete validation requirement.
3. After migration, implement SC-002 to persist policy classification in `llm_catalog_execute_sample` audit details.
4. Add SC-003 exact guard for admin-only provider-capable route ownership, admin dependency, caller scope, and post-migration carrier policy.
5. Reconcile story status metadata for CS-358 and CS-360 so `00-story.md`, `_condamad/stories/story-status.md`, and final/audit evidence agree.

## 12. Final delivery status

`Partially delivered`

CS-356, CS-357, CS-358, and CS-359 are delivered with implementation evidence and PASS validation recorded in their capsules. CS-360 is delivered for audit scope: it produced the required timestamped audit report, validated required sections, ran targeted admin integration tests, and explicitly linked active findings and candidates. The consolidated initiative remains `Partially delivered` because CS-360 intentionally leaves active implementation findings F-001 through F-004, with P1 next action SC-001/SC-004 required before the admin manual execution provider-capable policy can be considered fully implemented.
