<!-- Preuve finale CONDAMAD pour CS-205. -->

# Final Evidence

## Story status

- Validation outcome: PASS
- Final status: done
- Ready for review: yes
- Story key: CS-205-sect-aware-triplicity-golden-cases
- Source story: `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md`
- Capsule path: `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created for CS-205. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC11 represented. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-132 and forbidden patterns listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `evidence/triplicity-runtime-audit-before.md` documents runtime field, load path, roles and participant support. | Evidence content check with `rg -n "triplicity|day|night|participating|runtime|no score change|no public payload change" ...`. | PASS | Runtime field is `AstrologyRuntimeReference.dignity_reference.triplicity_rulers`. |
| AC2 | `test_day_chart_uses_day_triplicity_ruler` and G1 snapshot. | Dedicated pytest PASS. | PASS | Day ruler read from runtime assignment. |
| AC3 | `test_night_chart_uses_night_triplicity_ruler` and G2 snapshot. | Dedicated pytest PASS. | PASS | Night ruler read from runtime assignment. |
| AC4 | `test_same_element_can_select_different_triplicity_ruler_by_sect` and G3 snapshot. | Dedicated pytest PASS + snapshot JSON valid. | PASS | Fire triplicity selects different rulers in day/night seed-backed runtime. |
| AC5 | `test_participating_triplicity_ruler_behavior`, audit and validation note. | Dedicated pytest PASS. | PASS | Participant `sect_code == "all"` is supported and applied. |
| AC6 | `test_non_ruler_does_not_receive_triplicity` and G5 snapshot. | Dedicated pytest PASS. | PASS | Day chart Mars receives peregrine, not triplicity. |
| AC7 | `test_planet_dignity_scoring_service_selects_triplicity_by_chart_sect`. | Scoring service pytest PASS. | PASS | Service consumes `ChartSectResult.chart_sect`. |
| AC8 | No production files changed. | Anti-constant, local doctrine and forbidden import scans zero-hit. | PASS | No broad allowlist. |
| AC9 | Production scoring unchanged. | Traditional golden cases PASS. | PASS | Snapshot confirms current score values. |
| AC10 | `triplicity-runtime-audit-before.md`, before/after JSON and validation markdown added. | `python -m json.tool` PASS for both JSON files; evidence `rg` PASS. | PASS | |
| AC11 | No public JSON code changed. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` PASS; forbidden path diff empty. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | added | Dedicated CS-205 G1-G6 golden tests and snapshot payload. | AC1-AC10 |
| `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | modified | Adds scoring-service proof that chart sect selects triplicity ruler. | AC7 |
| `backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py` | added | Maps canonical triplicity seed rows into runtime reference contracts for CS-205. | AC1-AC8 |
| `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-runtime-audit-before.md` | added | Runtime audit before implementation. | AC1, AC5, AC10 |
| `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json` | added | Baseline absence marker for dedicated CS-205 suite. | AC10 |
| `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json` | added | Curated G1-G6 snapshot. | AC2-AC6, AC10 |
| `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-validation.md` | added | Validation, participant and no-change evidence. | AC5, AC8-AC11 |
| `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/generated/*` | added | CONDAMAD capsule and final evidence. | AC1-AC11 |

## Files deleted

None.

## Tests added or updated

- `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | repo root | PASS | 0 | 8 tests passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | repo root | PASS | 0 | 13 tests passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py` | repo root | PASS | 0 | 57 tests passed. |
| `ruff format .` | repo root | PASS | 0 | 1 file reformatted, 1480 unchanged. |
| `ruff check .` | repo root | FAIL | 1 | Initial review-fix run found import ordering in the new CS-205 test. |
| `ruff check backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py --fix` | repo root | PASS | 0 | Import ordering fixed. |
| `ruff check .` | repo root | PASS | 0 | Final lint: all checks passed. |
| `rg -n "TRIPLICITY_RULERS\|DAY_TRIPLICITY_RULERS\|NIGHT_TRIPLICITY_RULERS\|PARTICIPATING_TRIPLICITY_RULERS\|FIRE_TRIPLICITY\|EARTH_TRIPLICITY\|AIR_TRIPLICITY\|WATER_TRIPLICITY" backend/app -g "*.py"` | repo root | PASS | 1 | Zero hits. |
| `rg -n "if .*chart_sect.*day\|if .*chart_sect.*night\|planet_code\\s+in\|element\\s*==\\s*['\\\"]fire\|element\\s*==\\s*['\\\"]earth\|element\\s*==\\s*['\\\"]air\|element\\s*==\\s*['\\\"]water" backend/app/domain/astrology/dignities -g "*.py"` | repo root | PASS | 1 | Zero hits. |
| `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|OpenAI\|AIEngineAdapter\|prompt" backend/app/domain/astrology/dignities -g "*.py"` | repo root | PASS | 1 | Zero hits. |
| `python -m json.tool _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-before.json` | repo root | PASS | 0 | Valid JSON. |
| `python -m json.tool _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/triplicity-golden-after.json` | repo root | PASS | 0 | Valid JSON. |
| `rg -n "triplicity\|day\|night\|participating\|runtime\|no score change\|no public payload change" _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence` | repo root | PASS | 0 | Expected evidence hits. |
| `git diff -- backend/app/api backend/app/infra backend/app/domain/prediction backend/migrations docs/db_seeder frontend` | repo root | PASS | 0 | Empty diff. |
| `git diff --check` | repo root | PASS | 0 | No whitespace or conflict-marker errors. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` | repo root | PASS | 0 | Story validation PASS. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` | repo root | PASS | 0 | No missing required contracts. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` | repo root | PASS | 0 | Story lint PASS. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` | repo root | PASS | 0 | Strict story lint PASS. |
| `python .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/CS-205-sect-aware-triplicity-golden-cases` | repo root | PASS | 0 | CONDAMAD capsule validation PASS. |
| `python -c "from app.main import app; print(app.title)"` | repo root | PASS | 0 | Backend app imports and exposes `horoscope-backend`. |
| `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py` | repo root | PASS | 0 | Fresh review validation: 57 tests passed after venv activation. |
| `ruff format --check .` | repo root | PASS | 0 | Fresh review validation: 1482 files already formatted after venv activation. |
| `ruff check .` | repo root | PASS | 0 | Fresh review validation: all checks passed after venv activation. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` | repo root | PASS | 0 | Fresh review validation: story validation PASS after venv activation. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md` | repo root | PASS | 0 | Fresh review validation: strict story lint PASS after venv activation. |
| `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/CS-205-sect-aware-triplicity-golden-cases` | repo root | PASS | 0 | Fresh review validation: capsule validation PASS after venv activation. |
| `python -c "from app.main import app; print(app.title)"` | repo root, then `backend` after venv activation | PASS | 0 | Fresh smoke test: backend app imports and exposes `horoscope-backend`. |

## Commands skipped or blocked

None.

## Command corrections

- A backend import smoke command was first attempted from `backend/` with the
  repository-root relative activation path, so venv activation failed. The
  command was rerun from the repository root with activation first, then
  `Set-Location backend`, and passed.

## DRY / No Legacy evidence

- Production anti-constant scan: zero hits.
- Pure dignity local doctrine scan: zero hits.
- Pure dignity forbidden import scan: zero hits.
- Forbidden path diff for API, infra, prediction, migrations, seeds and
  frontend: empty.
- Runtime expectations are read from seed-backed `triplicity_rulers`, not from
  a local element-to-ruler table.

## Diff review

- `git diff --check`: PASS.
- `git diff --stat`: only CS-205 evidence/generated files and targeted backend
  tests changed.
- No production code, seeds, migrations, frontend or public JSON diff.

## Final worktree status

`git status --short` after final validation:

```text
 M _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/00-story.md
 M _condamad/stories/story-status.md
 M backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
?? _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/
?? _condamad/stories/CS-205-sect-aware-triplicity-golden-cases/generated/
?? backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py
?? backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py
```

## Remaining risks

No remaining implementation risk identified after review fix.

## Feedback-loop routing

- no-propagation: the fresh review did not reveal reusable learning requiring a
  guardrail, AGENTS.md, evidence, test, or skill update beyond the local
  closure evidence refresh.

## Review findings

| Finding | Decision | Fix evidence | Status |
|---|---|---|---|
| Initial CS-205 tests used synthetic CS-200 `sect_aware_triplicity_reference` instead of seed-backed runtime assignments. | Accepted | Added `triplicity_seed_cases.py`, updated CS-205 tests and snapshots to map canonical seed rows (`sun` day, `jupiter` night, `saturn` participating for fire). | Resolved |
| Source story status differed from registry. | Accepted | Updated `00-story.md` status to `ready-to-review`; closure will set registry to `done`. | Resolved |

## Suggested reviewer focus

Review that tests consume runtime triplicity assignments instead of recreating a
local day/night/element doctrine table.
