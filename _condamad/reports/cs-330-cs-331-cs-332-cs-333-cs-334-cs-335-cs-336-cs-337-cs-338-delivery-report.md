# Delivery Report - cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-27 10:51:46 +02:00 |
| Repository | `C:/dev/horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced; report-time `git rev-parse --short HEAD` returned `5448e380`, but no implementation commit range was provided. |
| Stories covered | `cs-330`, `cs-331`, `cs-332`, `cs-333`, `cs-334`, `cs-335`, `cs-336`, `cs-337`, `cs-338` |
| Source documents | `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`; `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`; `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`; `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`; `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md`; `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`; `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`; `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md`; `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md` |
| Story status source | `_condamad/stories/story-status.md`: rows `CS-330` through `CS-338` are `done`, last update `2026-05-27`. |
| Diff source | Story final evidence files `generated/10-final-evidence.md`; story code reviews `generated/11-code-review.md`; CS-338 final extinction report. |
| Validation source | story-time evidence and review evidence; report-time validation commands were not rerun. |
| Report-time worktree note | `git status --short` returned `?? _condamad/run-state.json` before this report was created; this file is repeatedly documented as pre-existing in story final evidence. |

## 1. Executive summary

The series is `Delivered` based on the available CONDAMAD evidence. All nine stories are marked `done` in `_condamad/stories/story-status.md`, each story has `generated/10-final-evidence.md`, and each reviewed story has `generated/11-code-review.md` with a `CLEAN` verdict or no actionable issue remaining.

The delivery moved natal LLM astrology input from legacy carriers toward the canonical `llm_astrology_input_v1` path: contract definition in CS-330, mapper in CS-331, runtime wiring in CS-332, hash/audit evidence in CS-333, use-case migration in CS-334, prompt boundary guards in CS-335, legacy surface removal in CS-336, legacy test/mock cleanup in CS-337, and final extinction closure in CS-338.

No audits were listed for this series by the user. The stories cite predecessor transition and architecture documents as sources, but there is no `cs-330` to `cs-338` audit story or audit directory to link as a series audit. The final CS-338 validation report is a closure report, not a separate audit story.

## 2. Initial context and trigger

The trigger was to replace `chart_json` as the proved prompt-visible natal LLM carrier with a richer, structured, auditable input. CS-330 states that `llm_astrology_input_v1` must rely on `structured_facts_v1` as factual source and `AINarrativeInputContract` as narrative signal owner, separating facts, signals, limits, evidence, shaping, provenance, and exclusions (`_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`).

The sequence then progressively wired, guarded, migrated, and closed that transition:

- CS-331 maps recent astrological richness into `llm_astrology_input_v1` without using `chart_json` as canonical source.
- CS-332 makes the contract prompt-visible in natal runtime.
- CS-333 makes prompt-influencing data auditable with `llm_input_hash` and evidence refs.
- CS-334 migrates modern natal use cases to require the modern key.
- CS-335 adds non-invention and payload boundary guards.
- CS-336 removes active legacy injection surfaces from the natal LLM path.
- CS-337 removes tests and mocks that preserved obsolete natal legacy behavior.
- CS-338 proves the extinction state with `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `cs-330` | Define internal versioned `llm_astrology_input_v1` contract. | `_condamad/stories/CS-330-llm-astrology-input-v1-contract/generated/03-acceptance-traceability.md` | No prompt rewrite, no runtime wiring, no public API/frontend/DB/provider call per brief. |
| `cs-331` | Build deterministic mapper from recent astrology surfaces to `llm_astrology_input_v1`. | `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/generated/03-acceptance-traceability.md` | No prompt rewrite, no endpoint/frontend change, no legacy deletion, no new calculations. |
| `cs-332` | Wire `llm_astrology_input_v1` into natal execution and prompt payload. | `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/generated/03-acceptance-traceability.md` | No provider policy change, no physical deletion of legacy carriers, no public API/frontend change. |
| `cs-333` | Align `projection_hash`, `llm_input_hash`, evidence refs and natal audit. | `_condamad/stories/CS-333-aligner-hash-evidence-audit-entree-llm-astrologique/generated/03-acceptance-traceability.md` | No security/admin endpoint/prompt rewrite/CI change beyond required audit input evidence. |
| `cs-334` | Migrate modern natal use cases off normal `chart_json` prompt ownership. | `_condamad/stories/CS-334-migrer-use-cases-natals-hors-chart-json-legacy/generated/03-acceptance-traceability.md` | No editorial prompt rewrite, no full legacy physical deletion, no public API/frontend change. |
| `cs-335` | Add prompt-visible/runtime-only/validation-only/audit-only guards. | `_condamad/stories/CS-335-guards-non-invention-frontieres-payload-llm/generated/03-acceptance-traceability.md` | No real LLM evaluation, no prompt rewrite, no physical legacy deletion. |
| `cs-336` | Remove active legacy natal LLM injection surfaces. | `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/generated/03-acceptance-traceability.md` | No frontend/API endpoint/provider policy change; non-LLM public chart uses of `chart_json` can remain ownerised. |
| `cs-337` | Remove legacy tests, fixtures and mocks that preserve obsolete natal LLM behavior. | `_condamad/stories/CS-337-supprimer-tests-mocks-legacy-injection-llm/generated/03-acceptance-traceability.md` | Do not remove valid non-LLM `chart_json` tests; do not mask failures with opportunistic skip/xfail. |
| `cs-338` | Prove final extinction of the legacy natal LLM injection path. | `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/generated/03-acceptance-traceability.md` | No new LLM feature, no prompt editorial rewrite, no frontend/API change, no legacy compatibility reintroduction. |

## 4. Implementation summary

### Contract and mapper

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: introduced and expanded the canonical contract/builder, hash material, evidence handling, data roles and prompt-visible block projection across CS-330, CS-331 and CS-333. Evidence: `CS-330/generated/10-final-evidence.md`, `CS-331/generated/10-final-evidence.md`, `CS-333/generated/10-final-evidence.md`.
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`: updated for mapping support in CS-331. Evidence: `CS-331/generated/10-final-evidence.md`.
- Tests added or updated: `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`, `test_llm_astrology_input_hash.py`, `test_llm_astrology_input_evidence.py`, and architecture boundary tests listed in CS-330 to CS-333 final evidence.

### Runtime, use cases and prompt payload

- `backend/app/domain/llm/runtime/contracts.py`, `adapter.py`, `gateway.py`: `NatalExecutionInput` transports the rich contract, the adapter propagates it through runtime context, and the gateway projects prompt-visible blocks while suppressing raw carriers for migrated natal requests. Evidence: `CS-332/generated/10-final-evidence.md`, `CS-335/generated/10-final-evidence.md`, `CS-336/generated/10-final-evidence.md`.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `assembly_resolver.py`, `backend/app/domain/llm/governance/data/prompt_governance_registry.json`: modern natal contracts and assemblies were migrated to `llm_astrology_input_v1`. Evidence: `CS-334/generated/10-final-evidence.md`, `CS-336/evidence/removal-audit.md`, `CS-338` final report.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: constructs and audits the modern LLM input while preserving non-prompt chart data ownership where still needed. Evidence: `CS-333/generated/10-final-evidence.md`, `CS-338` final report `References restantes et justification`.

### Legacy extinction and tests

- `backend/tests/architecture/test_llm_legacy_extinction.py`, `backend/tests/integration/test_llm_legacy_extinction.py`, `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`: guard against reintroducing `chart_json`, `natal_data`, or `evidence_catalog` into the natal LLM prompt/validation path. Evidence: CS-336 and CS-338 final evidence.
- Deleted legacy test/helper files: `backend/app/tests/unit/legacy_services/test_natal_interpretation_service_v2_refacto.py` and `backend/app/tests/unit/legacy_services/legacy_natal_interpretation_service.py`. Evidence: `CS-337/generated/10-final-evidence.md`.
- Golden and gateway tests/fixtures migrated: `backend/tests/fixtures/golden/natal_test.yaml`, `backend/tests/fixtures/golden/natal_premium_test.yaml`, `backend/tests/integration/test_llm_golden_regression.py`, `backend/tests/llm_orchestration/test_llm_execution_request.py`, `backend/tests/llm_orchestration/test_llm_gateway_compose.py`. Evidence: `CS-337/generated/10-final-evidence.md`.

### Audits in this series

No audit stories or audit directories were specified for CS-330 through CS-338. The user explicitly stated: "Aucun audit dans cette serie." The predecessor transition report and architecture documents referenced by the briefs are source inputs, not audits performed inside this implementation series.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `cs-330` | Internal contract exists; required blocks, ownership, exclusions, hash, public neutrality and evidence artifacts. | `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md` | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`; `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`; `CS-330/evidence/sample-payload.json` | `CS-330/generated/10-final-evidence.md`: targeted pytest 6 passed; backend tests 1167 passed, 215 deselected; OpenAPI/routes guards PASS; capsule validation PASS. | Delivered |
| `cs-331` | Mapper fills facts, signals, limits, evidence, shaping; disjoint ownership; no raw carriers; public API unchanged. | `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md` | `llm_astrology_input_v1.py`; `structured_facts_v1_builder.py`; `test_llm_astrology_input_boundary.py`; `CS-331/evidence/sample-payload.json` | `CS-331/generated/10-final-evidence.md`: ruff check PASS; targeted 18 passed then review-fix 11 passed; backend tests 1172 passed, 215 deselected; negative scan PASS. | Delivered |
| `cs-332` | Natal runtime transports and renders rich contract; no silent fallback to `chart_json` when rich input exists. | `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md` | Runtime contracts/adapter/gateway/config/natal service; `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py`; `CS-332/evidence/rendered-payload.json` | `CS-332/generated/10-final-evidence.md`: targeted CS-332 and adjacent tests 41 passed; backend pytest 3451 passed, 1 skipped, 1216 deselected; public guard PASS. | Delivered |
| `cs-333` | Stable `llm_input_hash`, prompt-visible invalidation, runtime-only stability, coherent evidence refs and audit payload. | `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md` | `llm_astrology_input_v1.py`; natal interpretation service audit update; hash/evidence/audit tests; `CS-333/evidence/hash-cases.json`; `audit-payload.json` | `CS-333/generated/10-final-evidence.md`: hash tests 3 passed; evidence tests 2 passed; long audit integration 2 passed; architecture 3 passed; backend tests 1189 passed, 217 deselected; negative hash scan PASS. | Delivered |
| `cs-334` | Modern natal use cases require `llm_astrology_input_v1`; old placeholders/schemas no longer normal owner; remaining compatibility classified. | `_story_briefs/cs-334-migrer-use-cases-natals-hors-chart-json-legacy.md` | `canonical_use_case_registry.py`; `assembly_resolver.py`; `gateway.py`; renderer and assembly tests; before/after OpenAPI and use-case snapshots | `CS-334/generated/10-final-evidence.md`: use-case contract 5 passed; prompt renderer 6 passed; assembly 15 passed; long runtime suppression 8 passed; combined 29 passed; backend tests 1195 passed, 218 deselected; local `/docs` startup PASS. | Delivered |
| `cs-335` | Prompt boundary guards prove rich blocks present, limits visible, raw runtime surfaces excluded, no external provider dependency. | `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md` | `backend/app/domain/llm/runtime/gateway.py`; `test_llm_astrology_input_boundaries.py`; `test_llm_astrology_input_payload_boundaries.py`; payload before/after snapshots | `CS-335/generated/10-final-evidence.md`: ruff check and format check PASS; boundary tests 4 passed; contract tests 9 passed; architecture payload guard 3 passed; backend tests 1202 passed, 218 deselected; scan PASS. | Delivered |
| `cs-336` | Active natal LLM legacy injection surfaces removed; no prompt fallback from old carriers; residual hits classified. | `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md` | Runtime/config/gateway/natal service/seeds/tests; `CS-336/evidence/removal-audit.md`; `legacy-carrier-scan-after.txt`; `natal-llm-payload-after.json` | `CS-336/generated/10-final-evidence.md`: targeted extinction/config/runtime tests 34 passed; seed/admin tests 59 passed, 6 deselected; backend tests 1208 passed, 218 deselected; OpenAPI guard PASS; rg classified residual hits PASS. | Delivered |
| `cs-337` | Obsolete legacy tests/mocks deleted or migrated; modern tests use `llm_astrology_input_v1`; negative guards remain. | `_story_briefs/cs-337-supprimer-tests-et-mocks-legacy-injection-llm.md` | Deleted legacy files; updated golden fixtures, gateway/golden tests; `CS-337/evidence/test-cleanup-audit.md` | `CS-337/generated/10-final-evidence.md`: targeted LLM/architecture/golden run 41 passed, 8 deselected; backend tests 1208 passed, 218 deselected; legacy-services/admin run 5 passed, 6 deselected; OpenAPI checks PASS; scans classified. | Delivered |
| `cs-338` | Final closure report proves a single natal LLM input path and classifies remaining legacy references. | `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md` | `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`; `backend/tests/integration/test_llm_legacy_extinction.py`; scan artifacts | `CS-338/generated/10-final-evidence.md`: long extinction test 7 passed; gateway validation 2 passed; long runtime suppression 8 passed; long backend suite 1420 passed, 9 skipped; rg classifications PASS; review CLEAN. | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: proves canonical contract, mapper, hash material and data role behavior for CS-330, CS-331 and CS-333.
- `backend/app/domain/llm/runtime/contracts.py`: proves `NatalExecutionInput` transport ownership and documents residual generic runtime fields classified later in CS-338.
- `backend/app/domain/llm/runtime/adapter.py` and `backend/app/domain/llm/runtime/gateway.py`: prove runtime propagation, prompt-visible projection, and old-carrier suppression for natal requests.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`: proves modern natal schemas require `llm_astrology_input_v1`; CS-338 final report cites `list_modern_natal_use_case_contracts()`.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: proves natal service builds modern input and persists coherent audit data; CS-338 classifies remaining chart construction as non-prompt ownerised behavior.

### Test evidence

- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`: contract shape, mapper ownership, raw-carrier exclusions, disjoint blocks and hash material coverage.
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` and `test_llm_astrology_input_evidence.py`: hash stability/invalidation and evidence-ref validation.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`: audit payload includes `projection_hash`, `llm_input_hash`, version, grounding status and refs.
- `backend/tests/architecture/test_llm_astrology_input_boundary.py`, `test_llm_astrology_input_runtime_boundary.py`, `test_llm_astrology_input_audit_boundary.py`, `test_llm_astrology_input_payload_boundaries.py`, `test_llm_legacy_extinction.py`: boundary, public surface, role and legacy extinction guards.
- `backend/tests/integration/test_llm_legacy_extinction.py`: final CS-338 guards proving modern natal contract exposure, user payload suppression of legacy carriers, and validation payload suppression of declared legacy carriers.

### Documentation evidence

- `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`: final closure report required by CS-338; classifies remaining references and residual risks.
- `_condamad/stories/CS-330-.../generated/10-final-evidence.md` through `_condamad/stories/CS-338-.../generated/10-final-evidence.md`: story-level completion evidence.
- `_condamad/stories/CS-330-.../generated/11-code-review.md` through `_condamad/stories/CS-338-.../generated/11-code-review.md`: implementation review evidence, with final verdict `CLEAN` or no actionable issue remaining.

### Operational evidence

- `_condamad/codex-runs/cs-330-dev-story.log` through `_condamad/codex-runs/cs-338-review-fix-story.log`: run logs exist for story writing, dev, validation and review/fix phases.
- `_condamad/codex-runs/cs-330-to-cs-338-delivery-report-delivery-report.log`: delivery-report run log exists for the consolidated report generation phase.
- `_condamad/stories/story-status.md`: rows `CS-330` to `CS-338` are `done`.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | full suite | PASS | CS-331, CS-332, CS-333, CS-334, CS-335, CS-336, CS-337, CS-338 final evidence/reviews | Story-time backend lint evidence. |
| `ruff format <changed python files>` / scoped format | targeted | PASS | CS-330 to CS-338 final evidence | Story-time scoped formatting evidence. |
| `ruff format --check .` | full suite | PASS | CS-335 final evidence: 1697 files already formatted; CS-336 review: 1700 files already formatted; CS-333 review PASS | Story-time check-only formatting evidence where run. |
| `python -B -m pytest -q tests --tb=short` | full suite | PASS | CS-330: 1167 passed, 215 deselected; CS-331: 1172 passed, 215 deselected; CS-333: 1189 passed, 217 deselected; CS-334: 1195 passed, 218 deselected; CS-335: 1202 passed, 218 deselected; CS-336/CS-337: 1208 passed, 218 deselected | Story-time fast backend suite evidence; counts differ as tests accumulated. |
| `python -B -m pytest -q --long tests --tb=short` | full suite | PASS | CS-338 final evidence: 1420 passed, 9 skipped | Long backend final closure validation. |
| CS-330 to CS-338 targeted unit/integration/architecture tests | targeted | PASS | Each story `generated/10-final-evidence.md` | Proves story-specific ACs. |
| OpenAPI/routes/TestClient guards | targeted | PASS | CS-330, CS-331, CS-332, CS-334, CS-336, CS-337 evidence | Public API neutrality for internal LLM input changes. |
| `rg` legacy and boundary scans | targeted | PASS | CS-332 transition scan; CS-334 prompt key scan; CS-335 payload scan; CS-336 legacy carrier scan; CS-337 test legacy scan; CS-338 legacy scan | Residual hits are classified where scans return hits. |
| Frontend checks | external | SKIPPED | CS-332, CS-333, CS-336, CS-337, CS-338 final evidence | Skipped because frontend was explicitly out of scope and untouched. |
| External provider / real LLM call | external | SKIPPED | CS-337 final evidence; CS-330 and CS-335 briefs exclude real LLM calls | Tests use local doubles; no provider call required. |
| Report-time test rerun | targeted | NOT RUN | This delivery report | No new runtime validation was requested; report relies on existing story evidence. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No in-series audit exists to link. The user explicitly stated "Aucun audit dans cette serie"; this report therefore links only predecessor source documents and CS-338 closure evidence, not audit findings.
- CS-332 intentionally kept transition carriers bounded rather than deleting them; this matches its non-goal "Retirer physiquement `chart_json` / `natal_data`" and is later closed by CS-336/CS-338.
- CS-334 notes that before/after use-case snapshot was semantically unchanged because the registry had already been migrated in the dirty worktree; evidence is in `CS-334/generated/10-final-evidence.md`.

### Known limits

- Report-time validation was not rerun. All PASS statements come from story-time final evidence or review artifacts.
- Frontend checks were skipped where documented because the stories were backend-only and no frontend files were touched.
- External LLM/provider execution was skipped by scope; the boundary evidence uses local doubles and gateway/runtime tests.
- CS-338 leaves generic runtime fields `ExecutionContext.chart_json` and `ExecutionContext.natal_data` for shared/non-natal runtime compatibility; the final report classifies them as outside active natal prompt ownership and guarded by negative tests.

### Assumptions

- Delivery status follows the skill workflow status model and treats explicit story-scope skips as non-blocking when the relevant repository validation passed.
- The canonical implementation evidence is the story capsule final evidence rather than current `git diff`, because this report is post-implementation and the requested phase must not modify application code.

## 9. Residual risks

- Generic runtime fields remain: `ExecutionContext.chart_json` and `ExecutionContext.natal_data` are still present for shared runtime compatibility. Impact: future code could accidentally rewire them into natal prompt/validation. Evidence: CS-338 final report `References restantes et justification`; mitigation: keep `backend/tests/integration/test_llm_legacy_extinction.py` guards active.
- Historical documentation scans remain noisy in `_condamad` and `_story_briefs`. Impact: reviewers can confuse archive text with active runtime behavior. Evidence: CS-338 final report residual risks; mitigation: rely on classified scan tables and avoid treating historical briefs as current executable support.
- CS-337 leaves residual admin sample-payload/catalog tests using `chart_json`, classified as public admin contract owners. Impact: future cleanup may need a separate owner decision if admin public contracts change. Evidence: `CS-337/generated/10-final-evidence.md` remaining risks and `evidence/test-cleanup-audit.md`.
- CS-336 notes residual historical seed scripts outside `backend/app/ops/llm` still mention old prompt text, outside the required active scan. Impact: possible documentary or operator confusion if those scripts are mistaken for active bootstrap. Evidence: `CS-336/generated/10-final-evidence.md` remaining risks.
- CS-335 before snapshot is reconstructed from pre-change source inspection/current contract shape because a pre-existing evidence file did not exist before implementation. Impact: before/after comparison is weaker than a captured pre-implementation artifact. Evidence: `CS-335/generated/10-final-evidence.md`.

## 10. Evidence gaps

- No implementation commit range is evidenced for the series.
- No CI run URL or external CI result is evidenced for the series; validation is local story-time evidence.
- No report-time backend test rerun was performed for this delivery report.
- No in-series audit artifacts exist; the user states there were no audits in this series.
- Full frontend validation is not evidenced and is intentionally skipped/out of scope for this backend-only series.
- Real provider/LLM runtime execution is not evidenced and was explicitly out of scope or skipped with local doubles.

## 11. Recommended next actions

1. Keep `backend/tests/integration/test_llm_legacy_extinction.py` in the long regression path, because it is the final guard against reintroducing `chart_json`, `natal_data`, or `evidence_catalog` into natal LLM prompt/validation payloads.
2. If product or architecture wants to eliminate all textual ambiguity, open a separate documentation cleanup for historical `_condamad` / `_story_briefs` references; do not mix it with runtime extinction evidence.
3. If admin public payloads should also stop using `chart_json`, create a separate ownerised story; CS-337 explicitly classifies those residual tests as outside this natal LLM cleanup.
4. On release, run the same backend long suite evidenced in CS-338: `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --long tests --tb=short`.

## 12. Final delivery status

`Delivered`

All nine stories have story-status `done`, AC traceability rows at `PASS`, final evidence, and clean review evidence. The final closure report for CS-338 proves `llm_astrology_input_v1` is the only active natal LLM astrology input path while classifying remaining legacy terms as negative guards, non-natal/shared runtime owners, validation-only surfaces, admin public contract owners, or historical documentation. Material gaps are limited to non-blocking delivery evidence gaps: no report-time rerun, no CI URL, no implementation commit range, skipped frontend/provider checks by scope, and classified residual generic runtime fields.
