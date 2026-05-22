# Final Evidence - CS-216

## Story status

- Validation outcome: PASS
- Story registry status: done
- Ready for review: yes
- Story key: `CS-216-advanced-planetary-conditions-interpretation-profiles`
- Source story: `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md`
- Capsule path: `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: completed missing generated files in existing capsule

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present |
| `generated/01-execution-brief.md` | yes | yes | PASS | Added |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Added |
| `generated/04-target-files.md` | yes | yes | PASS | Added |
| `generated/06-validation-plan.md` | yes | yes | PASS | Added |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Added |
| `generated/10-final-evidence.md` | yes | yes | PASS | Added |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `contracts.py` immutable enums/dataclass | Profile runtime tests | PASS | |
| AC2 | static catalog with required keys, including planet, tradition and planet+tradition entries | Profile runtime tests | PASS | |
| AC3 | `resolve_advanced_condition_profiles` | Profile runtime tests | PASS | |
| AC4 | priority lookup in runtime, including exact planet+tradition | Profile runtime tests | PASS | |
| AC5 | generic static resolution | Profile runtime tests | PASS | |
| AC6 | deterministic tuple of multiple profiles | Profile runtime tests | PASS | |
| AC7 | missing condition tolerance | Profile runtime tests | PASS | |
| AC8 | unsupported profile key skip | Profile runtime tests | PASS | |
| AC9 | combust keywords in catalog | Profile runtime tests | PASS | |
| AC10 | retrograde keywords in catalog | Profile runtime tests | PASS | |
| AC11 | moon-only full/new moon profiles | Profile runtime tests | PASS | |
| AC12 | excluded `NatalResult.interpretation_profiles_by_planet` populated | NatalResult integration tests | PASS | |
| AC13 | no scoring terms in new package | forbidden scan zero hits | PASS | |
| AC14 | no external forbidden surface terms | forbidden scan zero hits | PASS | |
| AC15 | bounded fragments, no final-user markers | tests and scan | PASS | |
| AC16 | no condition recalculation and no adjacent forbidden diff | duplication scan and adjacent diff | PASS | |
| AC17 | `RG-143` present | registry scan | PASS | |
| AC18 | validation complete under venv | validation table below | PASS | first full pytest attempt timed out, rerun passed |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py` | added | immutable profile contracts | AC1 |
| `backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py` | added | static symbolic catalog | AC2, AC9, AC10, AC11 |
| `backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py` | added | pure resolver | AC3-AC8, AC11, AC16 |
| `backend/app/domain/astrology/interpretation/advanced_conditions/__init__.py` | added | explicit exports | AC1-AC3 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | internal profile field and population | AC12 |
| `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` | added | contract/catalog/runtime tests, including optional notes validation, brief keyword coverage and new moon runtime resolution | AC1-AC11, AC15 |
| `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | modified | internal field integration tests | AC12 |
| `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/evidence/validation.md` | added | validation evidence | AC17, AC18 |
| `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/*` | added/modified | capsule evidence | AC18 |
| `_condamad/stories/story-status.md` | modified | status sync | AC18 |
| `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | modified | status sync only | AC18 |

## Files deleted

None.

## Tests added or updated

| File | Purpose |
|---|---|
| `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` | covers contracts, catalog keys, keywords, priority, multiple profiles, missing facts, unsupported keys, moon phases and fragment bounds |
| `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | covers internal field exclusion and population |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | repo root | PASS | 0 | 12 passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | repo root | PASS | 0 | 13 passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | repo root | PASS | 0 | 25 passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py` | repo root | PASS | 0 | 8 passed after review fix |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | repo root | PASS | 0 | 26 passed after review fixes |
| `.\\.venv\\Scripts\\Activate.ps1; ruff format backend` | repo root | PASS | 0 | formatted 1 file |
| `.\\.venv\\Scripts\\Activate.ps1; ruff format backend --check` | repo root | PASS | 0 | 1510 files already formatted |
| `.\\.venv\\Scripts\\Activate.ps1; ruff check backend` | repo root | PASS | 0 | all checks passed |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q` | repo root | PASS | 0 | 2941 passed, 1 skipped, 1177 deselected after timeout retry |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q` | repo root | PASS | 0 | final rerun after review fixes: 2942 passed, 1 skipped, 1177 deselected |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | repo root | PASS | 0 | story validation passed |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | repo root | PASS | 0 | no missing required contracts |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | repo root | PASS | 0 | story lint passed |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md` | repo root | PASS | 0 | strict lint passed |
| `.\\.venv\\Scripts\\Activate.ps1; Set-Location backend; python -B -c "from app.main import app; print(type(app).__name__)"` | repo root | PASS | 0 | FastAPI import smoke passed |

## Commands skipped or blocked

None currently.

## DRY / No Legacy evidence

| Evidence | Result |
|---|---|
| scoring scan in new package | PASS, zero hits |
| forbidden external surface scan in new package | PASS, zero hits |
| final-user text marker scan in new package | PASS, zero hits |
| condition recalculation scan in new package | PASS, zero hits |
| adjacent forbidden diff review | PASS, empty diff |
| `RG-143` registry scan | PASS |

## Diff review

Scope matches CS-216: new interpretation package, natal internal field, tests and evidence only. No frontend, API, DB, migration, JSON builder, dignity or planetary-condition owner changes.

## Final worktree status

Expected story changes only. Exact final `git status --short` output after review fixes:

```text
 M _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md
 M _condamad/stories/story-status.md
 M backend/app/domain/astrology/natal_calculation.py
 M backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/evidence/
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/01-execution-brief.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/03-acceptance-traceability.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/04-target-files.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/05-implementation-plan.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/06-validation-plan.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/07-no-legacy-dry-guardrails.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/09-dev-log.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/10-final-evidence.md
?? _condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/generated/11-code-review.md
?? backend/app/domain/astrology/interpretation/advanced_conditions/
?? backend/tests/unit/domain/astrology/interpretation/
```

## Remaining risks

No implementation risk identified after review.

## Review outcome

- Independent review subagents used: yes, three read-only reviewers.
- Review/fix iterations: 2.
- Fresh independent re-review after fixes: CLEAN.
- Accepted findings:
  - story checklist evidence inconsistency, fixed in `00-story.md`;
  - missing persisted final worktree status, fixed in this evidence file;
  - natal integration test accepted empty profile tuples, fixed with a non-empty assertion;
  - optional `notes` fragments were not validated by the public profile contract, fixed in `contracts.py` with regression tests;
  - moon phase runtime coverage did not explicitly assert `new_moon` for the Moon, fixed in profile runtime tests.
  - catalogue keywords drifted from the initial brief examples for `cazimi`, `stationary`, `emerging`, `full_moon` and `new_moon`; aligned the symbolic fragments and added keyword assertions.
- Rejected findings: none.
- Fresh main-session review verdict: CLEAN.
- Feedback-loop routing: no-propagation, local evidence/test correction only.

## Suggested reviewer focus

- Verify the new profile layer remains pre-narrative and pure.
- Verify no public JSON/API/frontend/scoring surface changed.
