<!-- Review finale CONDAMAD pour CS-204. -->

# CS-204 Code Review

Verdict: CLEAN
Date: 2026-05-20

## Scope Reviewed

- Backend domain contracts and normalizer for explicit hayz/rejoicing.
- Hayz calculator facts emitted through `AdvancedPlanetaryCondition`.
- Natal result attachment and JSON public projection.
- Frontend expert panel display and manual API types.
- Sect-aware triplicity day/night golden cases.
- Story documentation, status and regression guardrail `RG-131`.

## Findings

No open findings.

## Fresh Review Loop

Date: 2026-05-20

Verdict: CLEAN.

Review inputs:

- `00-story.md`, acceptance traceability, validation plan, No Legacy guardrails,
  final evidence and persistent evidence files.
- Current worktree diff for backend domain contracts, hayz facts, natal
  orchestration, public JSON projection, frontend API types, expert panel,
  tests, golden snapshots, story status and `RG-131`.
- Scoped guardrail scans for doctrine constants, forbidden calculator imports,
  frontend derivation, `calculation_facts` public leakage and forbidden path
  diffs.

Commands rerun by reviewer:

- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`:
  PASS, 44 passed.
- `npm --prefix frontend run test -- NatalExpertPanel`: PASS, 4 passed.
- `git diff --check`: PASS, only CRLF normalization warnings.
- `.\.venv\Scripts\Activate.ps1; ruff format --check .; ruff check .; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/00-story.md`:
  PASS.
- `npm --prefix frontend run lint; npm --prefix frontend run build`: PASS.
- Frontend startup on `http://127.0.0.1:5199`: PASS, HTTP `200`; process
  stopped after verification.
- Backend startup on `http://127.0.0.1:8011/docs`: PASS, HTTP `200`; process
  stopped after verification.

Fresh findings: none. No additional code fix was required in this final loop.

## Review/Fix Iteration 1

Date: 2026-05-20

Finding fixed:

- Severity: medium.
- Category: contract completeness.
- Evidence:
  `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py`
  returned `rejoicing_house: None` for non-rejoicing planets even when runtime
  `planetary_joy` rules exposed the planet's joy house, and
  `backend/app/services/chart/json_builder.py` still projected
  `traditional_conditions` in no-time mode.
- Correction:
  `TraditionalConditionNormalizer.normalize` now requires `runtime_reference`
  and sources the joy house from runtime accidental dignity rules. JSON
  projection now emits `traditional_conditions: null` for no-time payloads.
- Guard:
  `test_traditional_condition_normalizer_exposes_runtime_joy_house_without_match`
  and `test_build_chart_json_no_time` cover the regression.

Additional findings fixed:

- Public contract scope: removed `calculation_facts` from serialized
  `advanced_conditions` and from frontend API/test fixtures. The facts remain
  domain-internal and feed `traditional_conditions` only.
- Hayz false-case completeness: `TraditionalConditionNormalizer` now reuses
  `HayzCalculator.non_sect_hayz_factors` for evaluable non-hayz planets, so
  `in_sect` but non-hayz cases expose component booleans and evidence.
- Runtime rule completeness: `HayzCalculator` now evaluates all applicable hayz
  runtime rules and returns the first fully matching candidate instead of
  stopping on the first failed candidate.
- Frontend null contract: `traditional_conditions` is typed as
  `TraditionalConditionsPayload | null`, and `NatalExpertPanel` tests cover the
  null/no-time block.

## Feedback Loop

- Accepted reusable learning: a story that creates a dedicated additive public
  contract must not opportunistically extend an existing public block to carry
  internal evidence.
- Propagation: `RG-131`, `generated/06-validation-plan.md` and
  `generated/07-no-legacy-dry-guardrails.md` now include a zero-hit guard for
  public `advanced_conditions.calculation_facts` leakage.
- Validation: final scans returned zero hits for `calculation_facts` in
  `frontend/src` and `backend/app/services/chart/json_builder.py`.

## Redaction Review Loop

Date: 2026-05-20

Reviewed artifacts:

- `00-story.md`
- `generated/10-final-evidence.md`
- `evidence/hayz-rejoicing-validation.md`

Findings fixed:

- AC evidence referenced standalone test files that are not part of the final
  CS-204 implementation; the AC table and validation plan now point to the
  actual normalizer, JSON builder, hayz calculator, essential dignity and
  golden-case tests.
- The done story still had implementation tasks unchecked; tasks and subtasks
  are now marked complete.
- The contract shape described stale fields on `HayzCondition` and
  `RejoicingCondition`; it now matches the implemented dataclasses and public
  `traditional_conditions.planets` JSON shape.
- Golden-case wording suggested G7/G8/G9 were extended for all final coverage;
  the story now separates G7/G8/G9 traditional-condition coverage from the
  G13/G14 triplicity guard.
- Frontend validation commands were ambiguous from the monorepo root; evidence
  now uses `npm --prefix frontend ...`.

Final redaction verdict: CLEAN.

## Checks

- Projection recalculation risk: clean after moving normalization to
  `TraditionalConditionNormalizer`; `json_builder.py` serializes
  `NatalResult.traditional_conditions`.
- Frontend doctrine risk: clean; React renders explicit payload fields and does
  not define sect/hayz/rejoicing/triplicity constants.
- Triplicity regression risk: clean; G13/G14 cover day and night rulers for the
  same fire element.
- Story documentation risk: clean; the CS-204 capsule, `story-status.md` and
  `RG-131` are aligned with the implementation.
- Redaction drift risk: clean after the review loop above.

## Validation Evidence

See `generated/10-final-evidence.md` and
`evidence/hayz-rejoicing-validation.md`.
