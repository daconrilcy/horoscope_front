# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-201-natal-public-json-projection-cleanup`
- Source story: `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- Capsule path: `_condamad/stories/CS-201-natal-public-json-projection-cleanup`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story exists. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created before code edits. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC14. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable validation plan. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated during implementation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/services/chart/json_builder.py` preserves CS-197 sect serialization. | Targeted projection tests passed. | PASS | |
| AC2 | `json_builder.py` preserves CS-198 per-planet `sect_condition` serialization and rejects missing contracts. | Targeted projection tests passed. | PASS | |
| AC3 | `planet_condition_profiles` is a direct map keyed by planet code; `planet_condition_signals` is a direct map of signal lists; `advanced_conditions` and `dominant_planets` use the public field names from the initial brief; empty computed maps are `{}`. | Targeted projection tests passed. | PASS | |
| AC4 | `astral_points` and `signs_runtime` are projected from `NatalResult`; no-time nested houses are neutralized. | Targeted projection tests passed. | PASS | |
| AC5 | No forbidden engine imports in `json_builder.py`. | Projection forbidden scan returned zero hits. | PASS | |
| AC6 | No public sect compatibility alias was added; exact scan hits are classified in `public-json-validation.md`. | Legacy alias scan hits classified as canonical runtime/reference fields, not public compatibility aliases. | PASS | |
| AC7 | No-time mode still neutralizes houses, rulers, angles, dominants and adapter; new nested house fields are null. | Targeted projection tests passed. | PASS | |
| AC8 | Old persisted payload gaps are not backfilled in storage. | `test_get_audit_record_preserves_old_payload_gaps_without_backfill` passed. | PASS | |
| AC9 | Chart JSON contract impact is documented as dynamically shaped. | OpenAPI import/generation command passed. | PASS | |
| AC10 | Evidence artifacts exist and mention every named public block. | Evidence path checks and pattern scan passed. | PASS | |
| AC11 | CS-200 golden cases still pass. | Golden case tests passed. | PASS | |
| AC12 | No frontend/API/DB adjacent surface changed. | Adjacent surface diff returned no files; OpenAPI command passed. | PASS | |
| AC13 | Score values are documented as unchanged. | Evidence scan found `no-change score`. | PASS | |
| AC14 | Astrology facts are documented as unchanged. | Evidence scan found `no-change astrology`. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/services/chart/json_builder.py` | modified | Add projection-only serializers for `astral_points` and `signs_runtime`; converge condition profiles/signals, advanced conditions and dominants to public brief shapes; remove TODO legacy wording without changing public field. | AC3, AC4, AC5, AC7 |
| `backend/app/tests/unit/test_chart_json_builder.py` | modified | Assert direct condition maps, signal-list maps, public advanced/dominance field names, new structural blocks, no-time neutralization and empty advanced block conventions. | AC1, AC2, AC3, AC4, AC7 |
| `backend/app/tests/unit/test_chart_result_service.py` | modified | Assert old stored payload gaps are not backfilled on audit read. | AC8 |
| `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | modified | Align golden projection summary with public dominant planet field names from CS-201. | AC11 |
| `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-before.json` | added | Baseline curated public JSON snapshot. | AC10, AC13, AC14 |
| `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-projection-audit-before.md` | added | Before audit of field mapping and neutralization. | AC5, AC10 |
| `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-after.json` | added | After curated public JSON snapshot. | AC10, AC13, AC14 |
| `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-validation.md` | added | Validation summary, contract impact and scan classification. | AC9, AC10, AC13, AC14 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json` | modified | Align persistent golden evidence with the corrected public dominant planet projection names. | AC11 |
| `_condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/*` | added/modified | CONDAMAD capsule, final evidence and clean review result. | all |
| `_condamad/stories/story-status.md` | modified | Set CS-201 to `done` after clean review. | all |

## Files deleted

None.

## Tests added or updated

| File | Tests |
|---|---|
| `backend/app/tests/unit/test_chart_json_builder.py` | Added structural block assertions, no-time nested house neutralization and empty advanced block test. |
| `backend/app/tests/unit/test_chart_result_service.py` | Added old persisted payload gap test. |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; ruff format .` | repo root | PASS | 0 | First run reformatted 2 story-scoped files; rerun after review fixes reported 1477 unchanged. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | PASS | 0 | 36 passed after initial implementation and after review fix. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` | repo root | PASS | 0 | 23 passed after initial implementation and after review fix. |
| `.\.venv\Scripts\Activate.ps1; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; ruff format --check .` | repo root | PASS | 0 | 1477 files already formatted. |
| `.\.venv\Scripts\Activate.ps1; python -c "from backend.app.main import app; app.openapi()"` | repo root | PASS | 0 | FastAPI app imported and OpenAPI generated. |
| `rg -n $projectionForbidden backend/app/services/chart/json_builder.py` | repo root | PASS | 1 | Zero forbidden projection engine hits. |
| `rg -n $legacyAliasPattern backend/app backend/tests -g "*.py"` | repo root | PASS | 0 | Hits are canonical runtime/reference `sect_code` and `chart_sect_code` fields, not public compatibility aliases. |
| `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS" backend/app -g "*.py"` | repo root | PASS | 1 | Zero doctrine constant hits. |
| `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology backend/app/services/chart -g "*.py"` | repo root | PASS | 1 | Zero horizon tuple hits. |
| `rg -n $forbidden $roots -g "*.py"` | repo root | PASS | 0 | Hits are allowed runtime-sourced `prompt_hint` fields in condition signal contracts/builder. |
| evidence path checks and `rg -n $evidencePattern $storyEvidence` | repo root | PASS | 0 | All evidence files exist and mention required public blocks. |
| `git diff --name-only -- frontend backend/app/api backend/app/infra migrations docs/db_seeder` | repo root | PASS | 0 | No adjacent surface files changed. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reports line-ending warnings only. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` | repo root | PASS | 0 | Story validation PASS. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` | repo root | PASS | 0 | No missing required contracts. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` | repo root | PASS | 0 | Story lint PASS. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md` | repo root | PASS | 0 | Strict story lint PASS. |
| `.\.venv\Scripts\Activate.ps1; python -m json.tool _condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-before.json` | repo root | PASS | 0 | Before snapshot is valid JSON. |
| `.\.venv\Scripts\Activate.ps1; python -m json.tool _condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-after.json` | repo root | PASS | 0 | After snapshot is valid JSON. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-code-review/scripts/condamad_review_validate.py .agents/skills/condamad-code-review` | repo root | PASS | 0 | Code-review skill validator passed. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

| Pattern | Classification | Action | Status |
|---|---|---|---|
| Forbidden projection engines in `json_builder.py` | zero hits | none | PASS |
| Legacy sect aliases | canonical runtime/reference hits only | exact hit-by-hit classification added to `public-json-validation.md`; no code change because these are not public compatibility aliases | PASS |
| Doctrine constants | zero hits | none | PASS |
| Horizon tuples | zero hits | none | PASS |
| Pure-domain forbidden imports | allowed `prompt_hint` contract fields only | documented as runtime-sourced signal payload fields | PASS |

## Diff review

`git diff --check` passed. Diff is scoped to chart JSON projection, tests, CS-201 evidence/capsule and story status. No frontend/API/DB/migration/seed files changed.

## Final worktree status

Final status command before closure:

```text
 M _condamad/stories/story-status.md
 M backend/app/services/chart/json_builder.py
 M backend/app/tests/unit/test_chart_json_builder.py
 M backend/app/tests/unit/test_chart_result_service.py
?? _condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/
?? _condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/
```

## Remaining risks

None identified after implementation validation and clean review.

## Suggested reviewer focus

Review that `json_builder.py` remains a projection layer and that public structural blocks are serialized from `NatalResult` without calculation. Pay particular attention to the classification of canonical `sect_code`/`chart_sect_code` scan hits.
