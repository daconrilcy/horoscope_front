# Dev Log

## Preflight

- Initial `git status --short`: `_condamad/run-state.json` dirty before implementation.
- Story tracker row verified: `CS-412` path and source brief match the user request.
- Capsule generated files were missing; repaired with `condamad_prepare.py --repair-generated-only`, then validated PASS.
- A mistaken parallel generated capsule `_condamad/stories/cs-412` was created by the first prepare command and immediately removed after path verification.

## Search evidence

- Inspected `NatalFactGraph`, `EligibilityContext`, fact graph builder and adjacent fact graph tests.
- Scoped guardrails resolved from story: `RG-144`, `RG-145`, `RG-147`, `RG-148`, `RG-151`, `RG-156`, `RG-160`, `RG-161`.

## Implementation notes

- Added canonical internal owner `backend/app/domain/astrology/interpretation/natal_salience_model.py`.
- Added targeted salience model tests and archetype corpus tests.
- Added golden archetype metadata fixture for house 10, house 4, house 7, house 12, date-only, Fire, Water, strong Moon, dominant Saturn and constrained Venus.
- Review/fix iteration 1 corrected repeated Fire/Water balance handling so repeated elemental profiles are scored as supporting material instead of excluded weak signals.
- Added explicit tests for repeated Fire/Water, dominant planet and strong constraint coverage.
- No frontend, API, DB, prompt or public projection changes.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ... --with-optional` | PASS | Capsule repaired in target folder. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | PASS | Capsule structure valid. |
| `ruff format <changed python files>` | PASS | Scoped format. |
| `ruff check <changed python files>` | PASS | Scoped lint. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py --tb=short` | PASS | 13 passed. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_basic_natal_fact_graph.py backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py --tb=short` | PASS | 18 passed. |
| scoped `rg` recalculation/public-leak/forbidden-signal scans | PASS | Exit 1 means no matches for negative scans. |

## Decisions made

- Exact aspect salience consumes an explicit runtime source marker containing `exact`; it does not calculate or compare orbs.
- Minor/technical terms are represented as split string fragments in tests/model blocklist so the required negative scans prove they do not appear as central literal signals.
- Feedback loop routing: no-propagation; no failed validation or reusable process defect remains after evidence correction.

## Final `git status --short`

- Recorded in final evidence after validation gate.
