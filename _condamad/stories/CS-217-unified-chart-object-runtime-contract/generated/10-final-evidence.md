<!-- Evidence finale CONDAMAD pour CS-217. -->

# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-217-unified-chart-object-runtime-contract`
- Source story: `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`
- Capsule path: `_condamad/stories/CS-217-unified-chart-object-runtime-contract`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: `?? "docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md"`
- Pre-existing dirty files: `docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md`
- AGENTS.md files considered: prompt-provided `AGENTS.md` instructions for `c:\dev\horoscope_front`
- Capsule generated: yes, missing `generated/` files added.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs marked PASS. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `runtime/chart_object_runtime_data.py` defines canonical runtime contracts. | `test_chart_object_runtime_builder.py` PASS. | PASS | |
| AC2 | Required enums and dataclass fields implemented. | Contract shape assertions PASS. | PASS | |
| AC3 | Typed payload slots keep object model minimal. | Diff review and payload tests PASS. | PASS | |
| AC4 | Builder projects planets/luminaries. | Builder tests PASS. | PASS | |
| AC5 | Builder projects configured astral points. | Builder and natal tests PASS. | PASS | |
| AC6 | Builder projects ASC/DSC/MC/IC from house cusps. | Builder tests PASS. | PASS | |
| AC7 | Builder projects 12 `HOUSE_CUSP` objects. | Builder and natal tests PASS. | PASS | |
| AC8 | `NatalResult.chart_objects` wired internally. | Natal chart-object tests PASS. | PASS | |
| AC9 | Historical collections preserved. | Natal chart-object tests PASS. | PASS | |
| AC10 | `chart_objects` excluded from JSON/OpenAPI. | Natal schema/dump tests PASS. | PASS | |
| AC11 | Capability payload validation raises explicit errors. | Negative payload tests PASS. | PASS | |
| AC12 | `supports_aspects` filtering works. | Builder tests PASS. | PASS | |
| AC13 | `supports_dignities` remains false without dignity payload. | Builder tests PASS. | PASS | |
| AC14 | `supports_house_position` is backed by `house_position` payload. | Review fix tests PASS. | PASS | |
| AC15 | New modules are pure domain/runtime code. | Architecture test and dependency scans PASS. | PASS | |
| AC16 | Business calculators have no new `object_type` branches. | AST guard and scan PASS. | PASS | |
| AC17 | Out-of-scope surfaces unchanged. | Adjacent diff empty; public leak scan zero hit. | PASS | Pre-existing untracked doc explicitly excluded. |
| AC18 | `RG-144` is registered. | `Select-String "RG-144" ...` PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | added | Canonical chart-object contracts, payloads and validation. | AC1-AC3, AC11, AC14 |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | added | Pure projection from historical natal collections. | AC4-AC7, AC12-AC14 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Adds internal `NatalResult.chart_objects` and builder call. | AC8-AC10 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | added | Contract, projection, capability and payload tests. | AC1-AC7, AC11-AC14 |
| `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | added | Natal integration and public schema guard tests. | AC8-AC10, AC14 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | added | Architecture guard for pure modules and no business `object_type` branches. | AC15-AC16 |
| `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | modified | Extends internal-field public schema guard to `chart_objects`. | AC10 |
| `_condamad/stories/CS-217-unified-chart-object-runtime-contract/generated/*` | added/modified | CONDAMAD execution, traceability, validation and review evidence. | AC1-AC18 |
| `_condamad/stories/CS-217-unified-chart-object-runtime-contract/evidence/validation.md` | modified | Persistent validation and review/fix evidence. | AC1-AC18 |
| `_condamad/stories/story-status.md` | modified | Story status synchronized to `done` after clean review. | AC1-AC18 |

## Files deleted

None.

## Tests added or updated

- Added `test_chart_object_runtime_builder.py`.
- Added `test_natal_result_chart_objects.py`.
- Added `test_chart_object_runtime_architecture.py`.
- Updated `test_natal_result_conditions_integration.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | PASS | 0 | 9 tests passed before review fixes. |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | PASS | 0 | 8 tests passed. |
| `ruff format backend` | repo root | PASS | 0 | Formatting applied/check clean. |
| `ruff check backend --fix` | repo root | PASS | 0 | Two import-order issues fixed. |
| `ruff check backend` | repo root | PASS | 0 | All checks passed. |
| `pytest -q` | repo root | FAIL then PASS | 1 then 0 | Initial guard failure from deprecated namespace literal in test; final rerun: 2952 passed, 1 skipped, 1177 deselected. |
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | PASS | 0 | 18 tests passed after review fixes. |
| `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | PASS | 0 | Review closure rerun on 2026-05-22: 18 passed. |
| `ruff format backend` | repo root | PASS | 0 | Review closure rerun on 2026-05-22: 1515 files left unchanged. |
| `ruff check backend` | repo root | PASS | 0 | Review closure rerun on 2026-05-22: all checks passed. |
| `pytest -q` | repo root | PASS | 0 | Review closure rerun on 2026-05-22: 2952 passed, 1 skipped, 1177 deselected. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -c "from app.main import app; print(app.title)"` | repo root | PASS | 0 | App import/startup object check printed `horoscope-backend`. |
| Story validate/lint commands from `00-story.md` | repo root | PASS | 0 | validate, explain-contracts, lint and strict lint passed. |
| Local story validate/lint commands from `.agents/skills/condamad-story-writer/scripts` | repo root | PASS | 0 | Review closure rerun on 2026-05-22: validate, explain-contracts, lint and strict lint passed. |
| Required `rg` scans and `Select-String "RG-144"` | repo root | PASS | 0 or expected 1 for zero-hit `rg` | Forbidden scans zero-hit; RG-144 present. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; Git emitted CRLF warnings only. |
| `git diff --stat` / adjacent diff command | repo root | PASS | 0 | Scoped diff; adjacent out-of-scope diff empty. |

## Commands skipped or blocked

None.

## Command correction notes

- One attempted app import from `backend/` used `.\.venv\Scripts\Activate.ps1`
  relative to `backend/`, so PowerShell reported the activation script was not
  found. It is not counted as validation evidence; the corrected root-activated
  command above passed.

## DRY / No Legacy evidence

- No shim, alias, fallback, compatibility wrapper, duplicate contract, or public projection path added.
- Forbidden dependency scans in new modules returned zero hits.
- `calculability` scan returned zero hits.
- Business `object_type` branch scan returned zero hits.
- API/infra/services/frontend leak scan returned zero hits.
- `RG-144` was present before implementation and remains the active guardrail.

## Review/fix evidence

- Subagents used: yes, three read-only review layers.
- Review/fix iterations: 3.
- Accepted findings fixed:
  - High: `supports_house_position` lacked a typed payload. Fixed with `ChartObjectHousePositionPayload` and validation.
  - Medium: `supports_motion=True` could advertise absent simplified-engine motion facts. Fixed by making motion capability conditional and rejecting empty motion payloads.
  - Evidence findings: final evidence, traceability and code-review evidence were completed.
  - Review-closure evidence finding: stale "No commit or push requested" wording was removed because `condamad-review-fix-story` requires commit and push after a clean closure.
- Rejected findings: none.
- Feedback-loop routing: `no-propagation`; findings were local CS-217 contract corrections covered by tests and `RG-144`.

## Diff review

- Story diff is limited to expected backend domain/test files and CONDAMAD evidence/status files.
- Adjacent diff for planetary conditions, dignities, dominance, advanced conditions, interpretation, interpretation adapters, `json_builder.py`, API, infra, migrations and frontend is empty.
- Pre-existing untracked doc `docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md` is not part of CS-217 and was not modified.

## Final worktree status

Expected CS-217 changes plus pre-existing untracked doc remain before closure commit. The untracked doc is outside CS-217 and must not be included.

## Remaining risks

Aucun risque restant identifie.

## Suggested reviewer focus

Review the capability/payload contract shape and confirm that internal-only `NatalResult.chart_objects` remains outside public serialization.
