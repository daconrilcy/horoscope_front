# Delivery Report - cs-339-cs-340

<!-- Commentaire global: ce rapport consolide les preuves de livraison CS-339 et CS-340 sur la frontiere provenance prompt/audit du LLM natal. -->

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-05-27, report-time |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Commit range | Not evidenced; current HEAD observed as `105d46f0`, but no implementation commit range or PR reference is recorded in the consulted artifacts. |
| Stories covered | `CS-339`, `CS-340` |
| Source documents | `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`; `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`; `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/00-story.md`; `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/00-story.md` |
| Diff source | Story final evidence and review artifacts; report-time `git diff --stat` produced no summary output, while `git status --short` showed only untracked `_condamad/run-state.json` before this report. |
| Validation source | story-time evidence, story review artifacts, saved validation logs, and CS-340 validation report. Report-time application validation: NOT RUN. |
| Audits in this series | None. User instruction states: `Audits de la serie: Aucun audit dans cette serie.` |

## 1. Executive summary

Both stories are evidenced as complete. `CS-339` implemented the prompt/audit boundary correction: the natal LLM provider prompt is derived from canonical `prompt_visible` roles and no longer receives `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, or `persisted_answer` (`_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/generated/10-final-evidence.md`). `CS-340` closed the validation with a timestamped report and an implementation review cycle that found and fixed nested leakage of `grounding_status`, `validation_owner`, and `evidence_refs` before the final `CLEAN` verdict (`_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/11-code-review.md`).

Final initiative status: `Delivered`. The material gaps are absent CI/PR/commit-range provenance and no report-time rerun of backend validation, by instruction to produce only the delivery report.

## 2. Initial context and trigger

The trigger for `CS-339` was a contradiction after CS-330 through CS-338: `llm_astrology_input_v1` classified hash provenance as audit-only, but the gateway projected `provenance` into the prompt-visible payload (`_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`). The required closure was to keep prompt-visible blocks limited to `facts`, `signals`, `limits`, `evidence`, and `shaping`, while preserving audit and persistence access to hashes.

The trigger for `CS-340` was to validate the corrected boundary after `CS-339`, including tests, scans, runtime files, occurrence classification, and a report under `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/<YYYY-MM-DD-HHMM>/validation-frontiere-provenance.md` (`_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`).

No audit story or audit directory belongs to this series. Therefore no audit findings or candidates are linked here. The relevant review finding was implementation-review evidence inside `CS-340`, not an audit artifact.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| `CS-339` | Remove audit-only provenance data from the modern natal LLM prompt while preserving audit and persistence fields. | `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/generated/03-acceptance-traceability.md` | No frontend changes, no public endpoint changes, no real provider call, no storage policy change, no hash semantic recalculation; see source brief and `00-story.md`. |
| `CS-340` | Prove closure of the prompt/audit boundary after `CS-339`, including report, scans, validation and occurrence classification. | `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/03-acceptance-traceability.md` | No reimplementation except blocking fixes found by validation, no frontend changes, no real provider call, no broad historical cleanup; see source brief and `00-story.md`. |

## 4. Implementation summary

`CS-339` changed `backend/app/domain/llm/runtime/gateway.py` so `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS` is derived from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`, with prompt payload evidence saved in `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/prompt-payload-after.json`. It updated `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` and `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` to assert canonical prompt-visible blocks and absence of audit-only keys (`CS-339` final evidence).

`CS-340` produced `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`, refreshed scan artifacts, and tightened runtime/test guards after review found nested audit/validation fields still reaching provider handoff. Evidence: `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/11-code-review.md` records iteration 1 `CHANGES_REQUESTED`, the fix in `gateway.py`, updated guards, and iteration 2 `CLEAN`.

The story registry marks both rows as `done` in `_condamad/stories/story-status.md`.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| `CS-339` | AC1 gateway projection uses canonical roles. | `CS-339` brief and `generated/03-acceptance-traceability.md` | `backend/app/domain/llm/runtime/gateway.py`: prompt blocks derive from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`. | `python -B -m pytest -q tests\architecture\test_llm_astrology_input_payload_boundaries.py tests\integration\test_llm_legacy_extinction.py --tb=short`: PASS, 5 passed, 7 deselected, in `CS-339/evidence/validation.txt`. | Delivered |
| `CS-339` | AC2 prompt keeps `facts`, `signals`, `limits`, `evidence`, `shaping`. | `CS-339` brief | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`; `prompt-payload-after.json` contains those top-level blocks. | `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_evidence.py tests\llm_orchestration\test_llm_astrology_input_boundaries.py --tb=short`: PASS, 6 passed. | Delivered |
| `CS-339` | AC3 prompt excludes `provenance`, hashes and provider/persistence fields. | `CS-339` brief | Runtime tests reject forbidden keys; `prompt-payload-after.json` has no top-level `provenance`. | Same orchestration pytest PASS; `rg` scan recorded in `CS-339/evidence/validation.txt`. | Delivered |
| `CS-339` | AC4 audit persistence still receives hash metadata. | `CS-339` brief | `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` asserts audit model fields from full payload. | `python -B -m pytest -q tests\integration\llm\test_natal_llm_astrology_input_audit.py --long --tb=short`: PASS, 2 passed. | Delivered |
| `CS-339` | AC5 hash behavior remains stable. | `CS-339` brief | Hash owner remains `llm_astrology_input_v1`; gateway only changes prompt projection. | `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py tests\unit\domain\astrology\test_llm_astrology_input_hash.py --tb=short`: PASS, 12 passed. | Delivered |
| `CS-339` | AC6 legacy natal LLM guards still pass. | `CS-339` brief | No `chart_json` / `natal_data` prompt fallback added. | Architecture/legacy pytest PASS in `CS-339/evidence/validation.txt`. | Delivered |
| `CS-339` | AC7 evidence artifacts persisted. | `CS-339` brief | `prompt-payload-before.json`, `prompt-payload-after.json`, `validation.txt`. | `python -B -c "... evidence exists ..."`: PASS in `CS-339/evidence/validation.txt`. | Delivered |
| `CS-340` | AC1 validation report exists in timestamped directory. | `CS-340` brief | `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`. | Report path Python check: PASS in `CS-340/evidence/validation-output.txt`. | Delivered |
| `CS-340` | AC2 tests no longer require `provenance.llm_input_hash` in the prompt. | `CS-340` brief | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` asserts canonical prompt-visible keys only. | Targeted pytest PASS and scan artifacts in `CS-340/evidence/`. | Delivered |
| `CS-340` | AC3 provider handoff payload excludes audit-only fields. | `CS-340` brief | `test_gateway_provider_handoff_uses_local_double_and_prompt_boundary` inspects `mock_client.execute` messages; review fix excludes nested audit/validation keys. | Targeted pytest PASS, 24 passed, 9 deselected, in `CS-340/evidence/validation-output.txt`. | Delivered |
| `CS-340` | AC4 persistent audit keeps `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status`, `evidence_refs`. | `CS-340` brief | `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`. | Targeted audit pytest included in PASS command in `CS-340/evidence/validation-output.txt`. | Delivered |
| `CS-340` | AC5 modern natal use cases avoid hash/provenance placeholders. | `CS-340` brief | Registry/prompt placeholder scan over `app tests`. | `rg -n "\{\{provenance\}\}|\{\{projection_hash\}\}|\{\{llm_input_hash\}\}" app tests`: PASS, no matches. | Delivered |
| `CS-340` | AC6 backend validation passes. | `CS-340` brief | Runtime/test/report artifacts updated. | `ruff format --check app tests`: PASS; `ruff check .`: PASS; `python -B -m pytest -q tests --tb=short`: PASS, 1211 passed, 221 deselected. | Delivered |
| `CS-340` | AC7 remaining prompt/audit terms classified. | `CS-340` brief | Validation report section `Resultats de scans`; `boundary-scan-before.txt`; `boundary-scan-after.txt`. | Report section check PASS in `CS-340/evidence/validation-output.txt`. | Delivered |
| `CS-340` | AC8 `CS-339` complete before closure execution. | `CS-340` brief | `_condamad/stories/story-status.md` row `CS-339` is `done`. | `python -B -c "...CS-339..."`: PASS in `CS-340/evidence/validation-output.txt`. | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/llm/runtime/gateway.py`: `CS-339` final evidence states prompt blocks are derived from canonical `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`; `CS-340` review states the gateway recursively removes prompt-excluded audit/validation keys before provider serialization.
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: CS-340 report names this as canonical owner for `prompt_visible` / `audit_only` roles and complete `provenance` audit block.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: CS-340 report names this as the audit persistence owner for provenance and hashes.

### Test evidence

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`: prompt/provider-boundary tests assert canonical prompt-visible keys and reject forbidden audit/validation fields.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`: architecture guard prevents prompt role drift and forbidden audit-only prompt literals.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`: audit persistence proof for hashes, version, grounding and evidence refs.
- `backend/tests/integration/test_llm_legacy_extinction.py`: legacy `chart_json` / `natal_data` guard remains covered by story validation.

### Documentation evidence

- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`: final validation report defining prompt-visible blocks, audit-only fields, verified files, scans, commands and residual risks.
- `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/generated/10-final-evidence.md`: authoritative CS-339 final evidence.
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/generated/10-final-evidence.md`: authoritative CS-340 final evidence.

### Operational evidence

- `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/validation.txt`: story-time validation log with `ruff check .` PASS, targeted pytest PASS, full backend `--long` pytest PASS with 1422 passed and 9 skipped, and final capsule validation PASS.
- `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/validation-output.txt`: story-time validation log with review iteration 1 finding, fix, targeted pytest PASS, full pytest PASS with 1211 passed and 221 deselected, report checks PASS, strict lint PASS, capsule validation PASS, `git diff --check` PASS, and backend app import check PASS.
- `_condamad/codex-runs/cs-339-dev-story.log`, `_condamad/codex-runs/cs-339-review-fix-story.log`, `_condamad/codex-runs/cs-340-dev-story.log`, `_condamad/codex-runs/cs-340-review-fix-story.log`, `_condamad/codex-runs/cs-340-final-validation.log`: Codex run logs exist for implementation/review/final-validation phases. This report relies on capsule evidence and saved validation outputs for concrete command results.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `ruff check .` | full suite | PASS | `CS-339/evidence/validation.txt`; `CS-340/evidence/validation-output.txt` | Story-time backend lint. |
| `ruff format ...` / `ruff format --check app tests` | targeted / full suite | PASS | `CS-339/evidence/validation.txt`; `CS-340/evidence/validation-output.txt` | CS-340 intentionally skipped `ruff format .` to avoid unrelated churn; scoped format and check passed. |
| `python -B -m pytest -q tests...targeted... --tb=short` | targeted | PASS | `CS-339/evidence/validation.txt`; `CS-340/evidence/validation-output.txt` | CS-339: 12 + 6 + 5 + 2 passed across targeted groups; CS-340: 24 passed, 9 deselected. |
| `python -B -m pytest -q tests --long --tb=short` | full suite | PASS | `CS-339/evidence/validation.txt` | 1422 passed, 9 skipped. |
| `python -B -m pytest -q tests --tb=short` | full suite | PASS | `CS-340/evidence/validation-output.txt` | 1211 passed, 221 deselected. |
| `rg -n "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS|prompt_visible|audit_only|projection_hash|llm_input_hash|provenance" app tests` | targeted | PASS | `CS-339/evidence/validation.txt` | Residual hits classified as expected contract/audit/persistence/test/unrelated surfaces. |
| `rg -n "provenance|projection_hash|llm_input_hash|audit_only|prompt_visible|evidence_refs|grounding_status" app tests ..\_condamad ..\_story_briefs` | targeted | PASS | `CS-340/evidence/boundary-scan-after.txt`; validation report | Results saved and classified. |
| `rg -n "\{\{provenance\}\}|\{\{projection_hash\}\}|\{\{llm_input_hash\}\}" app tests` | targeted | PASS | `CS-340/evidence/validation-output.txt` | No prompt placeholders found. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | targeted | PASS | `CS-339/evidence/validation.txt`; `CS-340/evidence/validation-output.txt` | Capsule validation passed for both stories after fixes. |
| Local app startup | manual | NOT RUN | `CS-339/generated/10-final-evidence.md`; `CS-340/generated/10-final-evidence.md` | Both stories classify server startup as unnecessary/not run because scope was internal backend prompt/report validation. CS-340 did run backend app import check PASS. |
| Real LLM provider call | external | EXTERNALLY REQUIRED | `CS-339` and `CS-340` briefs list real provider calls out of scope. | Provider boundary is proved with local double, not real provider. |
| Report-time backend validation rerun | targeted | NOT RUN | Current user instruction constrained this phase to report-only artifact generation. | This report does not claim fresh application validation. |
| CI checks / PR checks | external | Not evidenced | No CI log or PR check artifact was provided or found in the consulted sources. | Attach CI/PR reference before release if required. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- No unsupported deviation found. CS-340 did include a runtime/test correction after review because validation found a blocking nested leakage; that is authorized by CS-340 scope, which allowed correction if validation proved CS-339 incomplete (`CS-340/00-story.md`; `CS-340/generated/11-code-review.md`).

### Known limits

- Report-time validation was not rerun. This phase only produced the delivery report, per user constraint; validation claims are sourced from story-time evidence artifacts.
- No real provider call was executed. Both source briefs exclude real LLM provider calls, and CS-340 validates provider handoff through a local double (`CS-340/generated/10-final-evidence.md`).
- CI/PR provenance and implementation commit range are not evidenced in the consulted artifacts.

### Assumptions

- The story-time saved command logs are accepted as validation evidence for this delivery report because the user requested a final report for an already completed implementation series and prohibited application code changes in this phase.

## 9. Residual risks

- Release traceability risk: no commit range, PR, or CI run is evidenced. Impact: weaker release provenance outside the local CONDAMAD evidence trail. Mitigation: attach the implementation commit range and CI URL to this report or release notes before external release.
- External-provider parity risk: the provider call was not executed against a real LLM service. Impact: provider transport/runtime differences are not tested here. Mitigation: run an environment-approved provider smoke test only if business release policy requires it; the stories explicitly scoped this out.
- Historical scan noise risk: broad terms such as `provenance`, `projection_hash`, and `evidence_refs` appear across unrelated historical reports, replay/projection domains and audit code. Impact: future reviewers may confuse legitimate audit ownership with prompt leakage. Mitigation: keep the CS-340 classified scan and validation report as the review anchor.

## 10. Evidence gaps

- Commit range: Not evidenced.
- CI status: Not evidenced.
- PR/review system link outside local generated review files: Not evidenced.
- Report-time backend lint/test rerun: NOT RUN by instruction; story-time PASS evidence exists.
- Local dev server startup during this reporting phase: NOT RUN; story evidence marks it unnecessary for internal backend scope.
- Real provider execution: EXTERNALLY REQUIRED / out of scope for both stories.
- Audits in this series: none; no audit findings or candidates exist to link.

## 11. Recommended next actions

1. Attach final commit range, PR link, and CI run evidence to close release provenance gaps.
2. Preserve `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md` as the canonical boundary validation reference for future prompt/audit reviews.
3. If release policy requires provider-level proof, run a controlled non-production provider smoke test and record it as external validation without changing the story status retroactively.

## 12. Final delivery status

`Delivered`

`CS-339` and `CS-340` are both `done` in `_condamad/stories/story-status.md`, have AC matrices with all acceptance criteria marked `PASS`, have final evidence with validation outcome `PASS`, and have generated implementation reviews with verdict `CLEAN`. The only remaining gaps are release provenance and external/report-time validation evidence, not uncovered implementation failures.
