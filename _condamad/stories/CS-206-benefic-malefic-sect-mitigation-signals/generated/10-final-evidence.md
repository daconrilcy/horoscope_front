# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-206-benefic-malefic-sect-mitigation-signals
- Source story: `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals/00-story.md`
- Capsule path: `_condamad/stories/CS-206-benefic-malefic-sect-mitigation-signals`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes
- Python commands: run after `.\.venv\Scripts\Activate.ps1`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for CS-206. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC16 validated. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific files and scans. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed and run. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-133 covered. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `sect-nature-runtime-audit-before.md`; runtime condition seed/reference updated. | Repository/factory tests and evidence scan. | PASS |
| AC2 | `SectNatureMitigationCondition` in `advanced_conditions/contracts.py`. | Detector contract test. | PASS |
| AC3 | Detector maps malefic + in sect to `mitigated`. | Detector golden case. | PASS |
| AC4 | Detector maps malefic + out of sect to `aggravated`. | Detector golden case. | PASS |
| AC5 | Detector maps benefic + in sect to `supported`. | Detector golden case. | PASS |
| AC6 | Detector maps benefic + out of sect to `weakened`. | Detector golden case. | PASS |
| AC7 | Detector emits `neutral` / `unknown` for non-evaluable natures. | Detector neutral, mixed, luminary and unknown tests. | PASS |
| AC8 | Detector skips missing sect condition; JSON no-time filters CS-206 facts. | Detector and `build_chart_json` no-time tests. | PASS |
| AC9 | `AdvancedConditionEngine` invokes the detector through runtime-supported condition types. | Engine emission and runtime support tests. | PASS |
| AC10 | `json_builder.py` serializes only precomputed CS-206 contracts. | JSON serialization test and calculator-import scan. | PASS |
| AC11 | `TraditionalConditionNormalizer` attaches CS-206 facts. | Normalizer and golden snapshot tests. | PASS |
| AC12 | Runtime type/weight added with neutral downstream weight. | Engine test proving neutral shared weight. | PASS |
| AC13 | Dignity scoring calculators untouched; golden score fields preserved. | Natal/golden tests and regenerated snapshot. | PASS |
| AC14 | No frontend change; generic projection remains backend-owned. | Frontend scans; npm checks not applicable. | PASS |
| AC15 | No local doctrine constants or legacy fields introduced. | RG-133 scans. | PASS |
| AC16 | Evidence references runtime source and before/after outputs. | Evidence files and JSON validation. | PASS |

## Files changed

- Domain: `advanced_conditions/contracts.py`, `sect_nature_mitigation_detector.py`, `advanced_condition_engine.py`, `traditional_condition_normalizer.py`, `advanced_conditions/__init__.py`.
- Runtime seeds/repository: `astral_advanced_condition_types.json`, `astral_advanced_condition_weights.json`, `astrology_runtime_reference_repository.py`.
- Public projection: `services/chart/json_builder.py`.
- Tests/factory: detector, engine, normalizer, chart JSON, runtime repository, existing advanced condition snapshot tests and runtime factory.
- Evidence/capsule: CS-206 generated files and evidence JSON/markdown.
- Golden evidence: CS-200 `golden-cases-after.json` updated for additive CS-206 facts.

## Files deleted

None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py`.
- Updated engine, normalizer, chart JSON and runtime reference tests.
- Updated existing advanced-condition tests to allow the additive CS-206 condition.

## Commands run

| Command | Result |
|---|---|
| `ruff format .` | PASS |
| `ruff check .` | PASS |
| `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | PASS: 72 passed |
| `pytest -q` | PASS: 2816 passed, 1 skipped, 1177 deselected |
| `python -m json.tool ...before.json`; `python -m json.tool ...after.json` | PASS |
| `condamad_story_validate.py 00-story.md` | PASS |
| `condamad_story_validate.py --explain-contracts 00-story.md` | PASS |
| `condamad_story_lint.py 00-story.md` | PASS |
| `condamad_story_lint.py --strict 00-story.md` | PASS |
| `git diff --check` | PASS; only CRLF normalization warnings |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8010` + `/openapi.json` | PASS |

## Commands skipped or blocked

- Frontend npm lint/tests: NOT_APPLICABLE, no frontend file changed.
- Commit/push: skipped, not requested.

## DRY / No Legacy evidence

- `sect_nature_mitigation` derives planet nature only from `AstrologyRuntimeReference.planet_natures`.
- No production benefic/malefic constant list was introduced.
- `backend/app/services/chart` and `frontend` do not import the detector or advanced condition engine.
- Legacy field scan is clean.
- The only `planet_code in` scan hits are pre-existing structural/dominance/runtime membership checks and are classified in `evidence/sect-nature-mitigation-validation.md`.

## Diff review

- Three read-only review layers ran after implementation.
- Findings fixed:
  - final evidence incomplete.
  - runtime parent weight made neutral to avoid unintended shared positive score.
  - no-time JSON now filters `sect_nature_mitigation` from public advanced conditions.
  - no-time JSON now also filters CS-206 profile breakdown and explanation facts.
  - RG-133 scan hits classified in evidence.
- Review/fix loop iterations: 2.
- Final self-review result: CLEAN; no remaining actionable finding identified.

## Feedback propagation

- Routing decision: `no-propagation`.
- Reason: all review findings were local CS-206 projection/evidence fixes and
  did not reveal a reusable process, AGENTS, skill, or shared guardrail gap.

## Final worktree status

- Worktree contains expected CS-206 source, tests, seed, evidence and capsule changes.
- No unrelated user changes were reverted.

## Remaining risks

- None identified after lint, full backend tests, story validation, RG-133 scans and local API start.

## Suggested reviewer focus

Review runtime ownership, neutral scoring, no-time filtering and serialize-only public projection.
