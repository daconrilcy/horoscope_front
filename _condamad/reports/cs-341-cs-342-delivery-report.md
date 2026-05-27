<!-- Commentaire global: ce rapport consolide les preuves de livraison des stories CS-341 et CS-342. -->

# Delivery Report - CS-341 to CS-342

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-27 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` from `git branch --show-current` |
| Commit range | Not evidenced |
| Stories covered | `CS-341`, `CS-342` |
| Source documents | `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`; `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` |
| Story capsules | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal`; `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal` |
| Diff source | Story final evidence and current repository inspection; current `git status --short` before this report showed only untracked `_condamad/run-state.json` |
| Validation source | story-time evidence in `generated/10-final-evidence.md`, `generated/11-code-review.md`, and `evidence/validation-output.txt` for each story |
| Audits in this series | None. The user explicitly declared no audit in this series. |

## 1. Executive summary

Final delivery status: `Delivered`.

CS-341 implemented the evidence boundary change: `evidence` is no longer prompt-visible for the modern natal LLM handoff, while backend validation and audit retain evidence refs, grounding status, provenance and hashes. CS-342 then produced the closure proof and report at `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/2026-05-27-1601/validation-evidence-hors-prompt.md`.

Both story rows are `done` in `_condamad/stories/story-status.md`. Both implementation reviews are `CLEAN` in their `generated/11-code-review.md` files. No audit story is part of this series, so there are no audit findings to link to CS-341 or CS-342.

## 2. Initial context and trigger

The trigger for CS-341 is documented in `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`: after CS-339/CS-340 closed `provenance` and hash leakage, `llm_astrology_input_v1` still exposed `evidence` in prompt-visible data and tests locked an empty `evidence: {}` provider payload.

The trigger for CS-342 is documented in `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`: after CS-341, the project needed final proof that evidence stays outside the natal prompt, post-generation writing is validated by backend evidence, and audit keeps the explanation data.

Series audit statement: no audit was executed or supplied for this CS-341/CS-342 series. Prior reports `_condamad/reports/cs-339-cs-340-delivery-report.md` and `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` were source context, not audits in this series.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-341` | Remove `evidence` from the natal LLM prompt-visible payload and use backend evidence for post-generation validation. | `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/00-story.md`; `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/03-acceptance-traceability.md` | No real LLM provider call, frontend changes, public endpoint changes, hash semantic changes, or audit evidence deletion. |
| `CS-342` | Prove and document final closure of the evidence-out-of-prompt process after CS-341. | `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/00-story.md`; `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/03-acceptance-traceability.md` | No real LLM provider call, frontend changes, public endpoint changes, migration, or broad historical rewrite. |

## 4. Implementation summary

CS-341 code evidence:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: current inspection found `LLM_ASTROLOGY_INPUT_DATA_ROLES` with `validation_only` containing `evidence`, `grounding_status`, `validation_owner`, and `audit_only` containing `projection_hash`, `llm_input_hash`, `provider_response`, `persisted_answer`.
- `backend/app/domain/llm/runtime/gateway.py`: current inspection found `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS = tuple(LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"])`, and exclusion logic derived from `validation_only` and `audit_only`.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`: current inspection found backend-side checks over `llm_astrology_input_v1`, internal facts, signals and limits, with validation errors for unsupported claims and ignored critical limits.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: current inspection found audit persistence of `projection_hash`, `llm_input_hash`, `grounding_status`, and `evidence_refs` from `llm_astrology_input_v1`.

CS-342 delivery evidence:

- `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/2026-05-27-1601/validation-evidence-hors-prompt.md`: final validation report defines prompt-visible blocks, validation-only and audit-only fields, handoff proof, post-generation validation proof, scan classification and residual risks.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/boundary-scan.txt`: records forbidden placeholder scans and occurrence classification.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/prompt-boundary-after.json`: records prompt blocks as `facts`, `signals`, `limits`, `shaping` and excluded keys including `evidence`, `evidence_refs`, `grounding_status`, hashes, provenance, and validation owner.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-341` | AC1: prompt-visible roles exclude `evidence`. | CS-341 brief and `00-story.md`. | `llm_astrology_input_v1.py` role map; CS-341 final evidence AC1. | CS-341 `evidence/validation-output.txt`: role check PASS; targeted tests PASS. | `Delivered` |
| `CS-341` | AC2-AC3: provider payload has no top-level empty `evidence` contract. | CS-341 brief AC2-AC3. | `gateway.py` prompt projection from canonical roles; provider tests updated per CS-341 final evidence. | CS-341 validation output: targeted tests PASS; negative `rg` scans for `prompt_payload["evidence"] == {}` PASS. | `Delivered` |
| `CS-341` | AC4-AC5: internal contract and persistent audit keep evidence refs, grounding and hashes. | CS-341 brief AC4-AC5. | `interpretation_service.py` audit fields; CS-341 final evidence files changed. | CS-341 validation output: domain evidence tests and natal audit tests PASS. | `Delivered` |
| `CS-341` | AC6-AC8: backend validation accepts grounded writing and rejects unsupported or limit-ignoring writing. | CS-341 brief AC6-AC8. | `rejected_answer_workflow.py` backend checks; tests in `backend/tests/unit/test_rejected_narrative_answer_workflow.py`. | CS-341 review: initial weakness found and fixed; fresh review CLEAN; targeted tests PASS. | `Delivered` |
| `CS-341` | AC9-AC10: prior provenance/hash and `chart_json`/`natal_data` guards remain active. | CS-341 brief AC8-AC9 and final evidence. | Architecture and orchestration guards in `backend/tests/architecture` and `backend/tests/llm_orchestration`. | CS-341 validation output: targeted guard tests PASS; full backend tests PASS. | `Delivered` |
| `CS-341` | AC11: evidence artifacts persisted. | CS-341 `00-story.md`. | CS-341 `evidence/prompt-boundary-before.json`, `evidence/prompt-boundary-after.json`, `evidence/boundary-scan.txt`, `generated/10-final-evidence.md`. | `condamad_validate.py` PASS in CS-341 final evidence. | `Delivered` |
| `CS-342` | AC1: final validation report exists. | CS-342 brief livrable attendu. | `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/2026-05-27-1601/validation-evidence-hors-prompt.md`. | CS-342 final evidence: path check PASS; review fixed filename drift. | `Delivered` |
| `CS-342` | AC2-AC5: final proof for prompt-visible exclusion, provider user message exclusion, internal evidence retention, audit persistence. | CS-342 brief AC2-AC5. | CS-342 final report sections "Blocs visibles", "Donnees hors prompt", "Preuve de handoff provider", "Preuve d'audit persistant". | CS-342 validation output: targeted pytest PASS, 21 passed, 2 deselected. | `Delivered` |
| `CS-342` | AC6-AC9: compliant, invented, limit-contradicting and ungrounded writing validation. | CS-342 brief AC6-AC9. | CS-342 final report "Preuve de validation post-generation"; tests in `test_rejected_narrative_answer_workflow.py`. | CS-342 validation output: targeted pytest PASS, 21 passed, 2 deselected. | `Delivered` |
| `CS-342` | AC10-AC12: empty prompt evidence contracts absent and remaining occurrences classified. | CS-342 brief AC10-AC12. | CS-342 final report classification table; `evidence/boundary-scan.txt`. | Forbidden placeholder scans in CS-342 `boundary-scan.txt`: no matches in backend/app or backend/tests; review CLEAN. | `Delivered` |
| `CS-342` | AC13-AC14: backend validations pass and artifacts persist. | CS-342 `00-story.md`. | CS-342 final evidence and validation output artifacts. | CS-342 `evidence/validation-output.txt`: Ruff PASS, format check PASS, full backend tests PASS, story validation PASS. | `Delivered` |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: role ownership separates prompt-visible data from validation-only and audit-only fields.
- `backend/app/domain/llm/runtime/gateway.py`: provider prompt blocks are derived from canonical `prompt_visible` roles and validation/audit fields are excluded.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`: validates generated narrative output against backend-owned `llm_astrology_input_v1` facts, signals and limits.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: keeps `projection_hash`, `llm_input_hash`, `grounding_status`, and `evidence_refs` available for persistent audit outside the prompt.

### Test evidence

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`: provider payload boundary tests for prompt-visible role blocks and forbidden raw/legacy owners.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`: AST guard that gateway projection reuses canonical prompt-visible roles and removes nested audit/validation keys.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py`: positive grounded case and negative unsupported, ignored-limit and ungrounded cases.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`: persistent audit evidence for hashes and evidence refs.

### Documentation evidence

- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/10-final-evidence.md`: AC-by-AC implementation and validation evidence for CS-341.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/10-final-evidence.md`: AC-by-AC implementation and validation evidence for CS-342.
- `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/2026-05-27-1601/validation-evidence-hors-prompt.md`: final proof report requested by CS-342.
- `_condamad/stories/story-status.md`: CS-341 and CS-342 rows marked `done` on 2026-05-27.

### Operational evidence

- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/evidence/validation-output.txt`: story-time validation PASS for Ruff, targeted tests, full backend tests and role checks.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/evidence/validation-output.txt`: story-time validation PASS for targeted tests, full backend tests, Ruff, format check and story validation.
- `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/11-code-review.md`: review verdict CLEAN after one fixed validation weakness.
- `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/11-code-review.md`: review verdict CLEAN after report filename and artifact persistence fixes.
- `_condamad/codex-runs/cs-341-implementation-review-fix.log`, `_condamad/codex-runs/cs-342-implementation-review-fix.log`: implementation/review-fix run logs exist for the series.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | full suite | PASS | CS-341 `evidence/validation-output.txt`; CS-342 `evidence/validation-output.txt` | Story-time, venv active per evidence files. |
| `ruff format --check .` | full suite | PASS | CS-342 `evidence/validation-output.txt` | Story-time; CS-341 used targeted `ruff format` and `ruff check`. |
| `pytest -q tests --tb=short` from `backend` | full suite | PASS | CS-341 final evidence: 1215 passed, 221 deselected; CS-342 validation output: 1215 passed, 221 deselected | Story-time backend validation. |
| `pytest -q <CS-341 targeted tests> --tb=short` | targeted | PASS | CS-341 `evidence/validation-output.txt`: 33 passed, 9 deselected | Covers role, boundary, audit, legacy and rejection workflow tests. |
| `pytest -q backend\tests\llm_orchestration\... backend\tests\integration\llm\test_natal_llm_astrology_input_audit.py --tb=short` | targeted | PASS | CS-342 `evidence/validation-output.txt`: 21 passed, 2 deselected | Covers final handoff, evidence, validation and audit closure. |
| `rg` forbidden evidence placeholder scans | targeted | PASS | CS-341 `evidence/boundary-scan.txt`; CS-342 `evidence/boundary-scan.txt` | No active backend prompt placeholders or empty evidence prompt contracts found. |
| Real LLM provider call | external | SKIPPED | CS-341 and CS-342 briefs list real provider calls out of scope; final evidence records skip | Not required for delivery because both stories explicitly exclude it. |
| Frontend validation | targeted | SKIPPED | CS-341 and CS-342 final evidence | Backend-only/report-focused stories; no frontend files changed. |
| Report-time rerun of backend tests | full suite | NOT RUN | This report generation phase was constrained to report/artifact production only | Relies on story-time validation logs above. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No material scope deviation remains evidenced. CS-342 review records two proof-artifact issues found and fixed: final report filename drift and missing persistent scan/validation artifacts in `_condamad/stories/CS-342-preuve-finale-evidence-hors-prompt-redaction-llm-natal/generated/11-code-review.md`.

### Known limits

- Real provider execution is `SKIPPED`; both CS-341 and CS-342 briefs explicitly exclude adding or running a real LLM provider call.
- The backend textual validation is conservative and rule-based, not a general semantic verifier for every possible astrology claim; CS-341 final evidence records this as remaining risk.
- Historical `_condamad` and `_story_briefs` references still contain evidence vocabulary; CS-342 final report classifies them as historical evidence, not active prompt drift.

### Assumptions

- Story-time validation logs are treated as authoritative validation evidence because this delivery-report phase explicitly forbids application code changes and asks only for the delivery report.
- Current repository inspection is used only to anchor code-path claims, not to invent new validation results.

## 9. Residual risks

- Rule-based validation coverage: unsupported or ignored-limit checks are proven by tests, but free-text semantic completeness is limited. Evidence: CS-341 final evidence "Remaining risks".
- Live provider drift: no live provider call was run. Impact is limited to external integration behavior, while local handoff contract and backend validation are covered. Evidence: CS-342 final report "Risques residuels".
- Historical vocabulary drift: evidence terms remain in reports and briefs. CS-342 classifies them as historical/non-executable, but future broad scans must preserve that classification. Evidence: CS-342 `boundary-scan.txt` and final report classification table.

## 10. Evidence gaps

- Commit range is Not evidenced; no commit boundary was supplied and current `git status --short` before report creation showed only untracked `_condamad/run-state.json`.
- Report-time validation commands were NOT RUN; this phase produced only the consolidated report and relied on existing story-time logs.
- CI evidence is Not evidenced; no GitHub Actions or CI log was supplied in the requested source set.
- Live provider behavior is SKIPPED by story non-goal, so external provider runtime behavior is not evidenced.

## 11. Recommended next actions

1. Keep `_condamad/reports/evidence-hors-prompt-validation-redaction-llm-natal/2026-05-27-1601/validation-evidence-hors-prompt.md` as the operational proof for evidence-out-of-prompt closure.
2. If product acceptance later requires live provider confidence, create a separate story for a controlled provider integration smoke test; do not fold it into CS-341/CS-342 because both briefs excluded real provider calls.
3. Preserve the CS-342 occurrence classification when future scans find `evidence` vocabulary in historical reports or briefs.

## 12. Final delivery status

`Delivered`

CS-341 and CS-342 are delivered because their story capsules map every AC to implementation and validation evidence, story-time Ruff and backend pytest validations passed, reviews are `CLEAN`, the requested CS-342 final validation report exists, and `_condamad/stories/story-status.md` marks both stories `done`. The remaining gaps are non-blocking for the stated scope: no audit existed in this series, no live provider call was required, CI evidence was not supplied, and report-time validation was not rerun.
