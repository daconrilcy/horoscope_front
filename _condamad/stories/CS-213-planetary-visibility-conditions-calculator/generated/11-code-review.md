# CONDAMAD Code Review

## Review target

- Story: `CS-213-planetary-visibility-conditions-calculator`
- Capsule: `_condamad/stories/CS-213-planetary-visibility-conditions-calculator`
- Verdict: CLEAN
- Review/fix iterations: 3
- Subagents used: no. The current post-closure review/fix pass was performed directly in the main session.

## Inputs reviewed

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md` (`RG-135` to `RG-140`)
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
- Generated capsule files `03`, `06`, `07`, `10`
- Git commit `e7dfa1ee` and `git status --short --untracked-files=all`
- Changed backend files and tests
- Validation outputs recorded in `evidence/validation.md`

## Diff summary

- Added pure calculator: `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
- Added tests: `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`
- Updated contracts and exports for `PlanetVisibilityThresholds`, `PlanetVisibilityKey.CONJUNCT_SOLAR`, and calculator functions.
- Updated story evidence and status files.
- No adjacent API, infra, DB, migration, JSON builder, natal integration or frontend changes.

## Review layers

| Layer | Result | Notes |
|---|---|---|
| Story Conformance Review | Findings fixed | Sun reason contract and final evidence wording from the previous pass. |
| Technical Risk Review | Findings fixed | Explicit untracked-file evidence and Sun reason contract from the previous pass. |
| Source Finding Closure Review | Findings fixed | Sun reason and governance status from the previous pass. |
| Main CONDAMAD review | CLEAN after evidence correction | No remaining actionable code findings. |
| Post-closure implementation review | CLEAN | No new issue found in code, tests, capsule evidence, guardrails or validation. |

## Findings

### CR-001 High - Sun reason did not match explicit mapping

- Bucket: patch
- Location: `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py:28`
- Source layer: acceptance
- Evidence: story mapping requires `planet_key == "sun"` to return `reason="sun_visible"`.
- Impact: AC mapping was only partially satisfied and the original test asserted the wrong reason.
- Fix: `_resolve_visibility_reason(..., planet_key=planet_key)` now returns `sun_visible` for the Sun; targeted test updated.
- Status: fixed.

### CR-002 Medium - Governance status mismatch

- Bucket: patch
- Location: `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md:3`
- Source layer: source closure
- Evidence: story status remained `ready-to-dev` while registry/evidence had advanced.
- Impact: lifecycle evidence was inconsistent.
- Fix: story header and registry synchronized.
- Status: fixed.

### CR-003 Low - Final evidence used plain diff-stat wording for untracked files

- Bucket: patch
- Location: `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/generated/10-final-evidence.md`
- Source layer: validation
- Evidence: `git diff --stat` omits untracked files while the new calculator/test/evidence files are untracked because no commit/staging was requested.
- Impact: reviewer could miss files that are part of the implementation.
- Fix: final evidence now lists `git status --short --untracked-files=all` explicitly and scopes `git diff --stat` to tracked changes.
- Status: fixed.

### CR-004 Low - Review artifact claimed unavailable delegation and wrong closure mode

- Bucket: patch
- Location: `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/generated/11-code-review.md`
- Source layer: validation
- Evidence: the persisted review said subagents were used and that the story could close without commit or push.
- Impact: closure evidence did not match the current execution contract.
- Fix: review evidence now records direct main-session review, current review/fix iteration count, and closure requiring the final commit/push gate.
- Status: fixed.

### Post-Closure Review Result

- Bucket: dismiss
- Location: `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
- Source layer: acceptance / validation / no-legacy / edge
- Evidence: fresh review on 2026-05-22 found no new actionable issue after inspecting commit `e7dfa1ee`, rerunning targeted tests, forbidden scans, adjacent diff, backend lint/tests, capsule validation and local app import.
- Impact: none.
- Suggested fix: none.
- Status: clean.

## Acceptance audit

- AC1-AC4: PASS. Contracts, enum, exports and calculator exist in canonical package.
- AC5-AC15: PASS. Targeted tests cover Sun, conjunction/cazimi, combust, under beams, emerging, visible, custom thresholds, batch behavior and placeholder exclusion.
- AC16-AC20: PASS. Required scans are zero-hit for forbidden dependencies, scoring, interpretation/text generation, observation/integration, and adjacent surfaces.
- AC21: PASS. Format, lint and backend tests passed in the activated venv.

## Validation audit

Commands passed after review fixes:

- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` - 26 passed.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` - 1497 files unchanged; lint passed; 2913 passed, 1 skipped, 1177 deselected.
- Story validation/lint block - PASS.
- Required scans - PASS.
- `git diff --check` - PASS with line-ending warnings only.
- Current review rerun: `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` - 26 passed.
- Current review rerun: forbidden dependency, scoring, text generation, observation/integration and adjacent public-symbol scans - zero hits for forbidden surfaces.
- Current review rerun: `git diff --check` - PASS with line-ending warnings only.
- Final closure quality block: `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format .; ruff check .; pytest -q` - 1497 files unchanged; lint passed; 2913 passed, 1 skipped, 1177 deselected.
- Final closure story/capsule validation - PASS.
- Final local app import - printed `horoscope-backend`.
- Post-closure targeted tests: `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` - 26 passed.
- Post-closure forbidden scans and adjacent diff - zero hits for forbidden surfaces; adjacent diff empty.
- Post-closure quality block: `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .; pytest -q` - 1497 files already formatted; lint passed; 2913 passed, 1 skipped, 1177 deselected.
- Post-closure capsule validation - PASS.
- Post-closure local app import - printed `horoscope-backend`.

## DRY / No Legacy audit

- No compatibility shim, alias, fallback or duplicate owner introduced.
- Calculator imports only `collections.abc.Mapping` and same-package contracts.
- Batch missing relation fails explicitly with `KeyError`; no `UNKNOWN` fallback.
- Public symbols are limited to `planetary_conditions` and unit tests.

## Commands run by reviewer

- `git status --short --untracked-files=all`
- `git diff --stat`
- `git diff --check`
- Required `rg` scans from the validation plan
- Targeted tests and full backend quality block after fixes
- Post-closure targeted tests, forbidden scans, adjacent diff, full backend quality block, capsule validation and local app import

## Residual risks

- None identified.

## Verdict

CLEAN. Story can be closed as `done` after final validation, scoped commit and non-destructive push.
