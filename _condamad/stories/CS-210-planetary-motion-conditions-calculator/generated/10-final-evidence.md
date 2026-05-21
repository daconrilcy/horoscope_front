# Final Evidence - CS-210

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-210-planetary-motion-conditions-calculator
- Source story: `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
- Capsule path: `_condamad/stories/CS-210-planetary-motion-conditions-calculator`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Review/fix `git status --short`: CS-210 implementation, tests, story status
  and capsule evidence were already dirty when this review cycle started.
- Pre-existing dirty files: scoped to CS-210 closure; no unrelated dirty file was
  touched.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Created |
| `generated/04-target-files.md` | yes | yes | PASS | Created |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created |
| `generated/10-final-evidence.md` | yes | yes | PASS | Created |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `planetary_motion_calculator.py` exposes `calculate_planetary_motion_condition`; package exports updated. | Targeted tests PASS. | PASS | |
| AC2 | `PlanetaryMotionProfile` added in `contracts.py`, frozen, slotted, and finite-validated. | Contract tests PASS. | PASS | |
| AC3 | `_motion_direction` maps signed speed to direct/retrograde/stationary. | Direction tests PASS. | PASS | |
| AC4 | Stationary threshold is checked before signed direction. | Positive and negative threshold tests PASS. | PASS | |
| AC5 | Zero speed returns `STATIONARY`. | Zero-speed test PASS. | PASS | |
| AC6 | Ratio uses `abs(speed) / mean_speed` when valid. | Ratio tests PASS. | PASS | |
| AC7 | Speed states use configurable profile thresholds. | Parametrized threshold tests PASS. | PASS | |
| AC8 | Finite zero/negative mean speed returns ratio `None` and `UNKNOWN`; non-finite profile values are rejected. | Invalid mean speed and finite-validation tests PASS. | PASS | Direction still remains numeric direct/retrograde for finite speeds. |
| AC9 | `DEFAULT_PLANETARY_MOTION_PROFILES` contains the ten requested profiles. | Catalogue tests PASS. | PASS | Mapping is read-only. |
| AC10 | Batch calculator raises explicit `ValueError` for missing profiles and rejects profile/planet mismatches. | Batch tests PASS. | PASS | |
| AC11 | Calculator and catalogue contain no forbidden imports or symbols. | Required `rg` scans zero-hit. | PASS | |
| AC12 | No adjacent integration was added. | Adjacent `git diff --` empty. | PASS | |
| AC13 | Backend checks pass in venv. | `ruff format .`, `ruff check .`, `pytest -q` PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/planetary_conditions/contracts.py` | modified | Add immutable `PlanetaryMotionProfile`. | AC2, AC8 |
| `backend/app/domain/astrology/planetary_conditions/__init__.py` | modified | Export profile, catalogue and calculator functions. | AC1, AC9 |
| `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py` | added | Pure movement condition calculator. | AC1, AC3-AC8, AC10, AC11 |
| `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py` | added | Read-only default profile catalogue. | AC9, AC11 |
| `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | modified | Cover `PlanetaryMotionProfile`. | AC2, AC8 |
| `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py` | added | Cover calculator behavior and catalogue. | AC1, AC3-AC10 |
| `_condamad/stories/CS-210-planetary-motion-conditions-calculator/generated/*` | added | CONDAMAD capsule evidence. | AC1-AC13 |
| `_condamad/stories/CS-210-planetary-motion-conditions-calculator/evidence/validation.md` | added | Persistent validation evidence. | AC11-AC13 |
| `_condamad/stories/story-status.md` | modified | Mark CS-210 ready-to-review during implementation and done after clean review. | AC13 |

## Files deleted

None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`.
- Updated `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | repo root | PASS | 0 | 28 passed |
| `ruff format .` | repo root | PASS | 0 | 1 file reformatted first run; 1492 unchanged on rerun |
| `ruff check . --fix` | repo root | PASS | 0 | Import order fixed |
| `ruff check .` | repo root | PASS | 0 | All checks passed |
| `pytest -q` | repo root | PASS | 0 | 2853 passed, 1 skipped, 1177 deselected |
| `$motion_paths = @(...); rg -n "from app\\.api\|from app\\.infra\|from app\\.infrastructure\|from app\\.services" $motion_paths; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit $LASTEXITCODE }` | repo root | PASS | 0 | zero forbidden hits; wrapper maps raw `rg` zero-hit exit 1 to validation success |
| `$motion_paths = @(...); rg -n "sqlalchemy\|fastapi\|pydantic\|OpenAI\|AIEngineAdapter" $motion_paths; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit $LASTEXITCODE }` | repo root | PASS | 0 | zero forbidden hits; wrapper maps raw `rg` zero-hit exit 1 to validation success |
| `$motion_paths = @(...); rg -n "\\bscore\\b\|score_delta\|accidental_score_delta\|essential_score_delta\|strength_modifier" $motion_paths; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit $LASTEXITCODE }` | repo root | PASS | 0 | zero forbidden hits; wrapper maps raw `rg` zero-hit exit 1 to validation success |
| `$motion_paths = @(...); rg -n "interpretation\|meaning\|description\|narrative\|prompt" $motion_paths; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit $LASTEXITCODE }` | repo root | PASS | 0 | zero forbidden hits; wrapper maps raw `rg` zero-hit exit 1 to validation success |
| `git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | PASS | 0 | empty diff |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story` | repo root | PASS | 0 | story validation PASS |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story` | repo root | PASS | 0 | no missing required contracts |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story` | repo root | PASS | 0 | story lint PASS |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story` | repo root | PASS | 0 | strict story lint PASS |
| `git diff --check` | repo root | PASS | 0 | no whitespace errors |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No duplicate calculator existed before implementation.
- `RG-135`, `RG-136` and `RG-137` were present and respected.
- Forbidden import, dependency, scoring and narrative scans returned zero hits.
- Adjacent surfaces diff is empty.
- No profile/planet mismatch fallback is accepted; mismatches fail explicitly.

## Diff review

- Scope is limited to `planetary_conditions`, its unit tests, and CS-210 evidence.
- No frontend, API, DB, migration, `NatalResult` or JSON projection change.
- No shim, alias, fallback, compatibility path or second owner added.

## Final worktree status

Captured before final closure: expected CS-210 changes only, including the
review evidence correction for this review/fix loop.

## Remaining risks

None identified after review fixes.

## Suggested reviewer focus

- Verify threshold inclusivity for speed states and the `STATIONARY` priority.
- Verify the default profile catalogue values and immutability.
