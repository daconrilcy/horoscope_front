# Delivery Report - cs-361 to cs-371

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-28 15:24:18 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced; current HEAD observed as `b335aab2` |
| Stories covered | `cs-361`, `cs-362`, `cs-363`, `cs-364`, `cs-365`, `cs-366`, `cs-367`, `cs-368`, `cs-369`, `cs-370`, `cs-371` |
| Source documents | `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md`; `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md`; `_story_briefs/cs-363-archi-contrat-theme-astral-llm-input-v1-et-provider-payload.md`; `_story_briefs/cs-364-definir-persistence-versionnee-contrats-prompt-theme-astral.md`; `_story_briefs/cs-365-implementer-interpretation-material-builder-theme-astral.md`; `_story_briefs/cs-366-implementer-provider-payload-builder-theme-astral-stable-par-feature.md`; `_story_briefs/cs-367-bigbang-remplacer-ancien-contrat-prompt-theme-astral-supprimer-legacy.md`; `_story_briefs/cs-368-audit-cloture-bascule-theme-astral-prompt-contract.md`; `_story_briefs/cs-369-audit-review-adversariale-correction-theme-astral-prompt-contract.md`; `_story_briefs/cs-370-documenter-synthese-nouvelle-structure-json-theme-astral-llm.md`; `_story_briefs/cs-371-generer-exemples-json-theme-astral-llm-v1-par-plan.md` |
| Diff source | Story-time final evidence, audit logs, review artifacts, and `git status --short` observed during report generation |
| Validation source | story-time logs and final evidence; report-time validation is document/source inspection only |

## 1. Executive summary

The series is `Delivered` with residual risks documented. `_condamad/stories/story-status.md` marks all 11 story rows `done` as of 2026-05-28. The implemented development path moved from audit findings to architecture, persistence, material building, provider payload building, legacy-carrier removal, closure audits, documentation, and examples.

Historical status after CS-372 to CS-375 corrections: this report remains the delivery record for `cs-361` to `cs-371`, but current `theme_astral` JSON documentation, depth names, structured `birth_context`, and example source-status wording are superseded by the corrected post-CS-371 documentation and examples.

Audits explicitly performed in the series:

- `cs-361`: read-only interpretive-text usage audit under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/`; findings were 2 High and 2 Medium and produced candidates for `cs-363` through `cs-368`.
- `cs-362`: read-only current provider JSON contract audit under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/`; findings were 2 High and 3 Medium and drove `cs-363` and `cs-366`.
- `cs-368`: closure audit under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/`; verdict `valide avec risques residuels acceptes`, with no active in-domain finding remaining.
- `cs-369`: adversarial correction audit under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/`; no Critical/High/Medium/Low implementation finding, one Info finding for no real provider invocation.

Material gaps: report generation did not rerun backend lint/tests; `generated/10-final-evidence.md` is absent for `cs-361`, `cs-362`, `cs-363`, `cs-368`, and `cs-369`; no real LLM provider call is evidenced.

## 2. Initial context and trigger

The trigger was the `theme_astral` prompt contract transition. `cs-361` established that rich interpretive sources existed but were not proven provider-visible, while `cs-362` established that existing provider payloads parsed but exposed commercial plan labels, duplicated developer/user data carriers, mixed backend-only metadata into provider artifacts, and contained premium-oriented wording in `basic`.

Evidence:

- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/02-finding-register.md`: F-001 through F-004.
- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/03-story-candidates.md`: candidates mapped to `CS-363` through `CS-368`.
- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/02-finding-register.md`: F-001 through F-005.
- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/03-story-candidates.md`: candidates mapped to `CS-363` and `CS-366`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `cs-361` | Audit interpretive text/table usage and source reachability. | `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` | Read-only audit; no application code changes per `_condamad/codex-runs/cs-361-domain-audit.log`. |
| `cs-362` | Audit current provider JSON prompt contracts for plan payloads. | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md` | Read-only audit; no app/provider JSON/prompt seed/docs/test/frontend/DB/migration edits per `_condamad/codex-runs/cs-362-domain-audit.log`. |
| `cs-363` | Define target architecture for `theme_astral_llm_input_v1` and provider payload. | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/00-story.md` | No application code changed per `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/generated/11-code-review.md`. |
| `cs-364` | Persist versioned prompt contract ownership through existing LLM owners. | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/00-story.md` | No parallel contract table/model/registry; no migration added, per `generated/10-final-evidence.md`. |
| `cs-365` | Implement canonical interpretation material builder. | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/00-story.md` | No provider, output schema, frontend, migration, or SQL-owner change per `generated/10-final-evidence.md`. |
| `cs-366` | Implement stable provider payload builder by feature. | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/00-story.md` | Protected frontend, migrations, DB models and repositories unchanged per `generated/10-final-evidence.md`. |
| `cs-367` | Replace old prompt contract carriers and remove legacy path for `theme_astral`. | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/00-story.md` | Public API routes unchanged; no real provider call claimed, per `generated/10-final-evidence.md`. |
| `cs-368` | Audit closure of the `theme_astral` prompt contract switch. | `_condamad/stories/CS-368-audit-cloture-bascule-theme-astral-prompt-contract/00-story.md` | Real provider calls and non-domain old natal/admin/test carriers excluded by audit summary. |
| `cs-369` | Adversarial audit/review of corrected implementation. | `_condamad/stories/CS-369-audit-review-adversariale-correction-theme-astral-prompt-contract/00-story.md` | Real LLM provider behavior deferred as non-domain context per audit finding F-001 Info. |
| `cs-370` | Document final JSON structure for Theme Astral LLM. | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/00-story.md` | Documentation-only; application code unchanged per `generated/10-final-evidence.md`. |
| `cs-371` | Generate Theme Astral LLM v1 JSON examples by plan. | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/00-story.md` | No provider client call; no protected application diffs per `generated/10-final-evidence.md`. |

## 4. Implementation summary

Audit and architecture:

- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/`: `cs-361` proved initial gaps F-001 to F-004 and produced candidates for contract architecture, persistence, material builder, provider builder, bigbang removal, and closure audit.
- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/`: `cs-362` proved provider JSON risks F-001 to F-005, including prompt-visible commercial plan labels and duplicated carriers.
- `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`: `cs-363` named `theme_astral_llm_input_v1`, decided reuse of existing LLM persistence concepts, identified the developer/user carrier contradiction, and defined roadmap stories `cs-364` through `cs-368`.

Backend implementation:

- `backend/app/domain/llm/configuration/theme_astral_contracts.py`, `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`, and related tests implement and validate `cs-364` versioned contract persistence through existing LLM owners.
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`, `interpretation_material_contracts.py`, `theme_astral_llm_input_v1_builder.py`, and repository/tests implement `cs-365` source-attributed `interpretation_material`.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`, `backend/app/domain/llm/runtime/gateway.py`, and provider handoff tests implement `cs-366` single stable provider payload path.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` and `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py` provide `cs-367` guardrails that reject old carriers for `theme_astral`.

Closure and documentation:

- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/`: `cs-368` closure audit found no active in-domain findings and accepted residual risks.
- `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/`: `cs-369` adversarial audit found no active implementation findings; only provider invocation remained unproven.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`: `cs-370` documents the final JSON structure, visibility rules, source evidence, plan-label boundary and Mermaid diagrams.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`: `cs-371` stores intermediate data and free/basic/premium provider payload examples generated without provider calls.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `cs-361` | Audit interpretive sources, runtime reach, LLM/provider visibility, gaps and candidates. | `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md`; `00-story.md` AC1-AC12 | `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/00-audit-report.md`; `01-audit-usage-tables-textes-interpretation.md`; `02-finding-register.md`; `03-story-candidates.md` | `_condamad/codex-runs/cs-361-domain-audit.log`: domain audit validate/lint PASS, targeted tests 9 passed and 4 passed, app diff guard unchanged. | Delivered |
| `cs-362` | Audit provider JSON shape, plan differences, backend-only data, duplication and prompt wording. | `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md`; `00-story.md` AC1-AC12 | `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/00-audit-report.md`; `02-audit-json-provider-theme-astral-actuels.md`; `02-finding-register.md`; `03-story-candidates.md` | `_condamad/codex-runs/cs-362-domain-audit.log`: domain audit validate/lint PASS, JSON parsed, targeted LLM tests 19 passed, diff guard OK. | Delivered |
| `cs-363` | Define architecture contract and roadmap from CS-361/CS-362. | CS-361 SC-001/SC-002/SC-003/SC-004/SC-005/SC-006; CS-362 SC-001/SC-002/SC-003/SC-004/SC-005 | `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md` | `_condamad/stories/CS-363-archi-contrat-theme-astral-llm-input-v1-provider-payload/generated/11-code-review.md`: fresh review PASS after correction; `_condamad/codex-runs/cs-363-final-validation.log`: story validate/lint PASS. | Delivered |
| `cs-364` | Persist contract versions through one existing LLM owner surface. | CS-361 F-003; CS-363 persistence decisions | `generated/10-final-evidence.md`: AC1-AC10 PASS; changed `theme_astral_contracts.py`, `seed_theme_astral_prompt_contract.py`, governance registry and tests. | `generated/10-final-evidence.md`: `ruff check .` PASS; full backend `pytest -q tests --tb=short` PASS with 1217 passed, 227 deselected; app import PASS. | Delivered |
| `cs-365` | Build source-attributed interpretation material from canonical owner. | CS-361 F-001; CS-363 `interpretation_material` block | `generated/10-final-evidence.md`: AC1-AC13 PASS; changed material contracts/builder/repository/LLM input builder/tests. | `generated/10-final-evidence.md`: targeted pytest PASS with 7 passed; ruff format/check PASS; app import PASS; `condamad_validate.py` PASS. | Delivered |
| `cs-366` | Compose stable provider payload from canonical feature contract. | CS-361 F-002; CS-362 F-002/F-004/F-005; CS-363 provider skeleton | `generated/10-final-evidence.md`: AC1, AC13, AC14 shown PASS; changed provider payload builder, gateway and tests; legacy builder deleted. | `generated/10-final-evidence.md`: `ruff check .` PASS; capsule validation PASS; no-duplication proof recorded; protected surfaces unchanged. | Delivered |
| `cs-367` | Enforce bigbang switch and reject old carriers. | CS-361 F-002; CS-362 F-001/F-002; CS-363 bigbang plan | `generated/10-final-evidence.md`: AC1-AC11 PASS; `theme_astral` gateway handoff requires `theme_astral_llm_input_v1`, rejects `chart_json`/`natal_data`, keeps plan labels backend-only. | `generated/10-final-evidence.md`: targeted integration/architecture tests PASS; full backend `pytest` PASS with 1233 passed, 232 deselected; startup command PASS. | Delivered |
| `cs-368` | Closure audit of migration and source classification. | CS-361 F-004; CS-363 roadmap Story 5 | `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/00-audit-report.md`; `03-audit-cloture-bascule-theme-astral-prompt-contract.md`; empty in-domain `02-finding-register.md` | `_condamad/codex-runs/cs-368-domain-audit.log`: audit validate/lint PASS, backend `ruff check .` PASS, targeted theme_astral tests 10 passed/9 deselected, smoke import PASS. | Delivered |
| `cs-369` | Adversarial read-only correction audit after closure. | `_story_briefs/cs-369-audit-review-adversariale-correction-theme-astral-prompt-contract.md` | `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/04-review-adversariale-correction-theme-astral-prompt-contract.md`; `02-finding-register.md` only F-001 Info | `_condamad/codex-runs/cs-369-domain-audit.log`: audit validate/lint PASS; targeted pytest 10 passed/10 deselected; backend `ruff check .` OK. | Delivered |
| `cs-370` | Document final JSON structure and source/visibility rules. | Closure audits and implemented contract evidence | `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`; `generated/10-final-evidence.md` AC1-AC13 PASS | `generated/10-final-evidence.md`: document/evidence checks PASS, scans PASS, `ruff check .` PASS, full pytest PASS with 3362 passed, 1 skipped, 1233 deselected. | Delivered |
| `cs-371` | Generate complete JSON examples by plan without provider calls. | CS-370 AC10 and CS-371 brief | `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`; `generated/10-final-evidence.md` AC1-AC12 PASS | `generated/10-final-evidence.md`: example generation/validation PASS, ruff format/check scripts PASS, targeted pytest PASS with 8 passed/1 deselected, diff check PASS. | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/llm/configuration/theme_astral_contracts.py`: proves `cs-364` canonical contract constants and `cs-366` provider-builder configuration surface.
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`: proves `cs-364` seed/bootstrap owner for persisted prompt/profile/assembly rows.
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`: proves `cs-365` canonical material builder owner.
- `backend/app/domain/astrology/interpretation/theme_astral_llm_input_v1_builder.py`: proves `cs-365` writes `input_data.interpretation_material`.
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`: proves `cs-366` canonical provider payload builder owner.
- `backend/app/domain/llm/runtime/gateway.py`: proves `cs-366`/`cs-367` gateway boundary for the canonical handoff and old-carrier rejection.

### Test evidence

- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`: validates `cs-364` active persisted contract reads.
- `backend/tests/integration/test_theme_astral_prompt_contract_migration.py`: validates `cs-364` existing LLM ORM/migration metadata compatibility.
- `backend/tests/unit/domain/astrology/interpretation/test_interpretation_material_builder.py`: validates `cs-365` source matching, absence behavior and material shape.
- `backend/tests/integration/astrology/test_theme_astral_interpretation_material_input.py`: validates `cs-365` LLM input integration.
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`: validates `cs-366`/`cs-371` provider payload behavior.
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`: validates `cs-366`/`cs-371` no-provider-call and handoff behavior.
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`: validates `cs-367` bigbang path.
- `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`: validates `cs-367` reintroduction guard.

### Documentation evidence

- `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`: architecture contract for `theme_astral_llm_input_v1`, persistence, provider skeleton, registries, rules, roadmap and open questions.
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`: `cs-370` final JSON structure and visibility documentation.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`: `cs-371` generated examples and comparison documents.

### Operational evidence

- `_condamad/codex-runs/cs-361-domain-audit.log`: read-only audit validations and dirty-state context.
- `_condamad/codex-runs/cs-362-domain-audit.log`: provider JSON parsing and targeted validation results.
- `_condamad/codex-runs/cs-363-final-validation.log`: story validate/lint PASS.
- `_condamad/codex-runs/cs-368-domain-audit.log`: closure audit validations and backend smoke import.
- `_condamad/codex-runs/cs-369-domain-audit.log`: adversarial audit validations and residual risk.
- `_condamad/stories/story-status.md`: all covered story rows marked `done`.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `condamad_domain_audit_validate.py` and `condamad_domain_audit_lint.py` for `2026-05-28-1152` | targeted | PASS | `_condamad/codex-runs/cs-361-domain-audit.log` | Story-time audit validation. |
| `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | targeted | PASS | `_condamad/codex-runs/cs-361-domain-audit.log` | 9 passed. |
| `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | targeted | PASS | `_condamad/codex-runs/cs-361-domain-audit.log` | 4 passed. |
| `condamad_domain_audit_validate.py` and `condamad_domain_audit_lint.py` for `2026-05-28-1203` | targeted | PASS | `_condamad/codex-runs/cs-362-domain-audit.log` | Story-time audit validation. |
| `python -m json.tool` on provider JSON payloads | targeted | PASS | `_condamad/codex-runs/cs-362-domain-audit.log` | Free/basic/premium parsed. |
| targeted LLM tests for `cs-362` | targeted | PASS | `_condamad/codex-runs/cs-362-domain-audit.log` | 19 passed. |
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for `cs-363` | targeted | PASS | `_condamad/codex-runs/cs-363-final-validation.log` | Story-time validation. |
| `ruff check .` | full suite | PASS | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/generated/10-final-evidence.md` | Full backend lint for `cs-364`. |
| `python -B -m pytest -q tests --tb=short` | full suite | PASS | `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/generated/10-final-evidence.md` | 1217 passed, 227 deselected. |
| Targeted material-builder pytest | targeted | PASS | `_condamad/stories/CS-365-interpretation-material-builder-theme-astral/generated/10-final-evidence.md` | 7 passed after repository test addition. |
| `ruff check .` | full suite | PASS | `_condamad/stories/CS-366-provider-payload-builder-theme-astral/generated/10-final-evidence.md` | Full backend lint for `cs-366`. |
| `python -B -m pytest -q tests --tb=short` | full suite | PASS | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/generated/10-final-evidence.md` | 1233 passed, 232 deselected. |
| `python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | manual | PASS | `_condamad/stories/CS-367-bigbang-theme-astral-prompt-contract/generated/10-final-evidence.md` | Startup proof recorded and stopped. |
| `condamad_domain_audit_validate.py`, `condamad_domain_audit_lint.py`, backend `ruff check .`, targeted theme_astral tests, smoke import | targeted | PASS | `_condamad/codex-runs/cs-368-domain-audit.log` | 10 passed, 9 deselected; smoke import `horoscope-backend`, 230 routes. |
| `condamad_domain_audit_validate.py`, `condamad_domain_audit_lint.py`, backend `ruff check .`, targeted theme_astral tests | targeted | PASS | `_condamad/codex-runs/cs-369-domain-audit.log` | 10 passed, 10 deselected. |
| `python -B -m pytest -q --tb=short` | full suite | PASS | `_condamad/stories/CS-370-documenter-synthese-json-theme-astral-llm/generated/10-final-evidence.md` | 3362 passed, 1 skipped, 1233 deselected. |
| `python -B evidence\generate_examples.py` and `python -B evidence\validate_examples.py` | targeted | PASS | `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/generated/10-final-evidence.md` | Examples generated and validated. |
| Real LLM provider call | external | EXTERNALLY REQUIRED | `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/02-finding-register.md` F-001 | Explicitly outside audit/story scope. |
| Report-time backend lint/tests rerun | full suite | NOT RUN | This report generation session | Report-only phase; no application code modified. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No implementation files were modified during this delivery-report phase. Evidence: report generation `git status --short` showed only pre-existing `?? _condamad/run-state.json` before the report was added.
- `cs-361`, `cs-362`, `cs-363`, `cs-368`, and `cs-369` do not have `generated/10-final-evidence.md`; delivery evidence is taken from audit/architecture artifacts, reviews, and logs instead.

### Known limits

- Real provider execution is not evidenced. `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/02-finding-register.md` records F-001 Info: provider invocation is outside the audit-only run.
- `cs-369` did not rerun the full backend suite and did not start the app, per `_condamad/codex-runs/cs-369-domain-audit.log`.
- `cs-361` and `cs-362` were read-only audits and intentionally skipped broad format/full-suite validation where the audit scope did not authorize it; this is recorded in their domain audit logs.

### Assumptions

- Story-level `done` rows in `_condamad/stories/story-status.md` are treated as registry evidence only, not as standalone proof of completion.
- Audit findings are considered closed only when linked to implementation, closure audit, or explicit residual-risk acceptance artifacts listed above.

## 9. Residual risks

- Real LLM provider behavior remains unproven. Impact: the repository proves builder/gateway/persistence/examples/tests, but not provider-side interpretation. Evidence: `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/02-finding-register.md` F-001. Mitigation: create a separate non-production provider smoke/evaluation story if product wants provider-level proof.
- Old `chart_json`, `natal_data`, and `llm_astrology_input_v1` references remain outside the `theme_astral` prompt contract domain. Impact: future audits must not misclassify non-theme natal/admin/test references as active theme_astral carriers. Evidence: `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1409/05-executive-summary.md` and `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1418/05-executive-summary.md`.
- Standard final-evidence files are absent for audit/architecture stories. Impact: future traceability must use audit/architecture artifacts and logs instead of one uniform `10-final-evidence.md`. Evidence: file inspection during report generation found no `generated/10-final-evidence.md` for `cs-361`, `cs-362`, `cs-363`, `cs-368`, `cs-369`.
- `_condamad/run-state.json` is untracked. Impact: unrelated worktree noise can confuse closure diffs. Evidence: `git status --short` during report generation.

## 10. Evidence gaps

- `generated/10-final-evidence.md` is Not evidenced for `cs-361`, `cs-362`, `cs-363`, `cs-368`, and `cs-369`.
- Commit range for the implementation series is Not evidenced; only current HEAD `b335aab2` and current branch `main` were observed.
- Report-time rerun of backend `ruff check .`, backend pytest, frontend checks, and app startup is NOT RUN.
- Real provider LLM invocation is EXTERNALLY REQUIRED and not evidenced.
- Exact complete command text for some summarized `cs-366` validations is partially abstracted in `generated/10-final-evidence.md`; status is evidenced, but not every command has full exit-status columns.

## 11. Recommended next actions

1. Decide whether product needs a separate non-production provider smoke/evaluation story for real LLM provider behavior, tied to `cs-369` F-001 Info.
2. If uniform CONDAMAD closure artifacts are required, backfill `generated/10-final-evidence.md` for audit/architecture stories or document that audit folders are the authoritative final evidence for non-dev stories.
3. Keep the existing theme_astral guardrail tests in review focus for future prompt work: `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py`, `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`, and provider payload tests.
4. Clean or explicitly classify `_condamad/run-state.json` before any future commit/release packaging.

## 12. Final delivery status

`Delivered`

CS-372 follow-up alignment: the `theme_astral` persisted delivery-depth contract is now expected to match the provider examples with the canonical non-commercial set `essential`, `expanded`, and `complete`; active `deep` belongs only to pre-CS-372 history and is not part of the current DB/provider contract.

The series has evidence-backed delivery across audit, architecture, backend implementation, closure audit, documentation, and examples. All story rows are `done` in `_condamad/stories/story-status.md`; `cs-364`, `cs-365`, `cs-366`, `cs-367`, `cs-370`, and `cs-371` have story final evidence with PASS validations; `cs-361`, `cs-362`, `cs-368`, and `cs-369` have audit artifacts and validation logs; `cs-363` has an architecture artifact and review handoff. Delivery remains bounded by the documented gaps: no real provider invocation, no report-time test rerun, missing uniform final-evidence files for non-dev stories, and an unrelated untracked `_condamad/run-state.json`.
