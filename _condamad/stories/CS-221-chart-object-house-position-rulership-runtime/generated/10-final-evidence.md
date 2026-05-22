# CS-221 Final Evidence

## Story status

- Validation outcome: PASS
- Final status: done
- Ready for review: completed with clean review
- Story key: `CS-221-chart-object-house-position-rulership-runtime`
- Source story: `_condamad/stories/CS-221-chart-object-house-position-rulership-runtime/00-story.md`
- Capsule path: `_condamad/stories/CS-221-chart-object-house-position-rulership-runtime`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing generated execution files were created before implementation

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated from story. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Completed with AC1-AC18. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated target map; code evidence below is authoritative. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Completed with actual command outcomes. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Completed with classified hits. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

All AC1-AC18 are `PASS`; detailed mapping is in `generated/03-acceptance-traceability.md`.

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | modified | Add complete house payload, rulership payload/capability and validation. | AC1, AC3, AC4, AC9, AC15 |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | modified | Build enriched house-position payloads and declare rulership capability on eligible bodies. | AC1, AC2, AC9 |
| `backend/app/domain/astrology/builders/chart_object_house_runtime_enricher.py` | added | Project `HouseRulerResult` and `sign_rulerships` into `payloads.rulership`. | AC3, AC5, AC6, AC7, AC8, AC13, AC14 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Run rulership enrichment inside natal orchestration. | AC10, AC11, AC16 |
| `backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py` | added | Unit coverage for payload shape, modality, rules, flags, dispositors and non-eligible objects. | AC1-AC9 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | modified | Cover new capability/payload fields and house modality. | AC1, AC2, AC4 |
| `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | modified | Integration coverage for natal chart_objects, historical output preservation and house/rulership payloads. | AC10, AC11, AC16 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | modified | Guards against local resolver/table and object-type eligibility. | AC13, AC14, AC15 |
| `_condamad/stories/CS-221-chart-object-house-position-rulership-runtime/evidence/validation.md` | added | Persistent validation evidence. | AC17 |
| `_condamad/stories/CS-221-chart-object-house-position-rulership-runtime/generated/*.md` | added/modified | CONDAMAD capsule execution evidence. | AC17 |

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py`.
- Updated `test_chart_object_runtime_builder.py`, `test_natal_result_chart_objects.py`, `test_chart_object_runtime_architecture.py`.
- AC11 review fix: `test_build_natal_result_populates_chart_objects_without_replacing_collections` now asserts `house_rulers`, `houses`, `planet_positions`, `dignities`, `dominant_planets.planets`, and `chart_objects`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | PASS | 0 | 33 passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | PASS | 0 | 18 passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py -k replacing_collections` | repo root | PASS | 0 | AC11 targeted review fix passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | PASS | 0 | Review-fix rerun: 51 passed. |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; ruff check .; Pop-Location` | repo root | FAIL then fixed | 1 | Format ran; initial lint found import ordering only. |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check . --fix; ruff check .; Pop-Location` | repo root | PASS | 0 | 1 import-order issue fixed; all checks passed. |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; pytest -q; Pop-Location` | repo root | PASS | 0 | Final rerun: 3014 passed, 1 skipped, 1177 deselected. |
| `.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -c "from app.main import app; print(len(app.routes))"; Pop-Location` | repo root | PASS | 0 | FastAPI app imports; 221 routes. |
| CS-221 scans listed in `generated/06-validation-plan.md` | repo root | PASS | 0/1 | Zero-hit scans use exit 1 as expected; classified hits documented. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git reports CRLF normalization warnings only. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

- No second resolver/table, no shim/fallback/alias, no frontend/API/DB/public JSON change.
- `RulershipPayloadEnricher` follows existing selector/projector/enricher pattern used by dignity/dominance.
- Classified scan hits are documented in `generated/07-no-legacy-dry-guardrails.md`.

## Diff review

- `git diff --stat`: tracked story-scoped backend domain/tests and governance files; untracked story files classified through `git status --short`/`git ls-files --others --exclude-standard`.
- `git diff --check`: PASS with CRLF warnings only.
- Adjacent diff on planetary conditions, interpretation, json_builder, API, infra, migrations and frontend: empty.
- Expected untracked files: CONDAMAD generated/evidence files, `backend/app/domain/astrology/builders/chart_object_house_runtime_enricher.py`, and `backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py`.

## Final worktree status

- Expected story changes only; see final `git status --short` in chat/final response.

## Remaining risks

- Aucun risque restant identifie.

## Suggested reviewer focus

- Review the new `RulershipPayloadEnricher` contract and confirm `supports_rulership` is the desired dedicated capability.
