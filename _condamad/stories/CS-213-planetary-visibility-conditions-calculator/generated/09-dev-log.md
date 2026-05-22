# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- AGENTS.md considered: `AGENTS.md`
- Regression guardrails considered: `RG-135`, `RG-136`, `RG-138`, `RG-139`, `RG-140`
- Capsule generated: yes, with `condamad_prepare.py`; the helper reports the lower-case path on Windows but files are in the canonical CS-213 directory.

## Search evidence

- Existing visibility contracts found in `contracts.py`.
- No existing calculator or targeted test file before implementation.
- Existing pure calculator patterns inspected: solar proximity, solar phase relation, moon phase.

## Implementation notes

- Added `PlanetVisibilityThresholds` and `PlanetVisibilityKey.CONJUNCT_SOLAR`.
- Created `planetary_visibility_calculator.py` with strict priority:
  `sun > conjunct solar > combust > under beams > emerging > visible`.
- Batch function iterates over proximity keys and requires matching phase relation keys.
- Updated package exports and tests.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --with-optional` | PASS | Generated missing capsule files. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` from `backend/` | FAIL | Activation path was wrong from `backend/`; no tests ran. Re-run from repo root passed. |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | 26 passed. |
| `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` | PASS | 1497 files unchanged; 2913 passed, 1 skipped, 1177 deselected. |
| Story validation/lint command block | PASS | validate, explain-contracts, lint and strict lint all passed. |
| Required `rg` scans and adjacent diff checks | PASS | Forbidden scans zero-hit; public symbols limited to allowed package/tests; adjacent symbols zero-hit; adjacent diff empty. |
| `git diff --check` | PASS | No whitespace errors; Git emitted line-ending warnings only. |
| Review-fix targeted tests | PASS | 26 passed after `sun_visible` fix. |
| Review-fix backend quality block | PASS | 1497 files unchanged; lint passed; 2913 passed, 1 skipped, 1177 deselected. |

## Issues encountered

- The capsule generator lower-cased the printed target path on Windows. Because the filesystem is case-insensitive, it wrote the intended files under the canonical story directory.
- One targeted test command was first launched from `backend/` with a root-relative venv path and failed before tests ran. It was re-run correctly from repository root.
- Independent review found a Sun reason mismatch. Fixed by returning `sun_visible`.
- Independent review found evidence ambiguity around untracked files. Fixed by recording explicit `git status --short --untracked-files=all` evidence; no commit or staging was requested.

## Feedback loop decision

- `no-propagation`: both issues were local execution mistakes already corrected and did not require a reusable guardrail or skill update.
