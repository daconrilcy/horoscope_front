# CONDAMAD Code Review

## Review target

- Story: `CS-189-brancher-etoiles-fixes-scoring-runtime`
- Verdict: CLEAN
- Review/fix iterations in this closure cycle: 2
- Subagent review layers used: no.

## Inputs reviewed

- `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `evidence/fixed-stars-runtime-before.md`
- `evidence/fixed-stars-runtime-after.md`
- `evidence/guard-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `git diff --stat`, implementation diff, tests diff and `git diff --check`.

## Diff summary

- `FixedStarData` carries magnitude, keywords, source category and source key.
- `PredictionReferenceRepository.get_fixed_stars()` loads those fields from DB-backed reference tables.
- `PredictionContextLoader` preserves the enriched immutable contract.
- `EnrichedAstroEventsBuilder` reads fixed-star orb, magnitude threshold and base weight from ruleset parameters.
- `DomainRouter` routes fixed-star events through explicit `fixed_star_category_weights`.
- `reference_seed_service` seeds fixed-star ruleset parameters and repairs locked V2 rulesets missing them.
- Unit and integration tests cover runtime contract, metadata, filtering, routing, contribution and seed repair.

## Review layers

- Diff integrity: scoped to CS-189 backend/capsule files; no unrelated frontend, dependency, migration or secret change found.
- Acceptance audit: AC1 to AC7 mapped to implementation and validation evidence.
- Validation audit: targeted backend tests, long seed integration, lint/format checks, story validation, startup import and negative scans rerun in the activated venv.
- DRY / No Legacy audit: no local fixed-star catalog, hardcoded fixed-star orb, prediction dependency from astrology, or duplicate scoring engine found.
- Edge/security/data audit: no HTTP, auth, secret, migration or external-client surface changed; DB reads remain in repository layer.

## Findings

No remaining actionable findings.

### Fixed during review/fix iteration 1

#### CR-1 Low - Review evidence claimed subagents for a cycle that did not use them

- Bucket: patch
- Location: `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/generated/11-code-review.md`
- Source layer: validation
- Evidence: the existing review artifact stated `Subagent review layers used: yes`, while this requested closure cycle was run directly in the main Codex session.
- Impact: misleading closure evidence and an inaccurate audit trail.
- Fix applied: rewrote this review artifact to reflect the actual review/fix cycle and validation evidence.

### Clean review iteration 2

Fresh review after the evidence correction found no new actionable findings.

## Acceptance audit

- AC1 PASS: enriched DTO and repository/freezer preservation are implemented and tested.
- AC2 PASS: fixed-star orb comes from `fixed_star_orb_deg`; hardcoded `dist <= 1.0` scan is clean.
- AC3 PASS: magnitude threshold behavior is explicit and tested.
- AC4 PASS: fixed-star metadata shape is explicit and public projection remains compatible.
- AC5 PASS: retained events have positive runtime weight and produce non-zero contribution through the existing calculator.
- AC6 PASS: no local fixed-star catalog or forbidden fixed-star symbols remain.
- AC7 PASS: required backend validations pass in the activated venv.

## Validation audit

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`: PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .`: PASS, 1409 files already formatted.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_prediction_reference_repository.py tests/unit/prediction/test_public_astro_daily_events.py app/tests/unit/test_domain_router.py app/tests/unit/test_contribution_calculator.py`: PASS, 70 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py`: PASS, 11 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest --long -q app/tests/integration/test_seed_31_prediction_v2.py`: PASS, 7 passed.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md`: PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; print(app.title)"`: PASS, `horoscope-backend`.
- `git diff --check`: PASS.

## DRY / No Legacy audit

- `rg -n "_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"` from `backend`: zero hit.
- `rg -n "dist.*1\.0" app/domain/prediction/enriched_astro_events_builder.py` from `backend`: zero hit.
- `rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"` from `backend`: zero hit.
- Scoring remains in `DomainRouter` and `ContributionCalculator`; no parallel fixed-star scoring engine was introduced.

## Commands run by reviewer

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff check .
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_prediction_reference_repository.py tests/unit/prediction/test_public_astro_daily_events.py app/tests/unit/test_domain_router.py app/tests/unit/test_contribution_calculator.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest --long -q app/tests/integration/test_seed_31_prediction_v2.py
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_" app/domain/prediction app/tests tests -g "*.py"
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "dist.*1\.0" app/domain/prediction/enriched_astro_events_builder.py
.\.venv\Scripts\Activate.ps1; cd backend; rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; print(app.title)"
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md
git diff --check
```

## Residual risks

Aucun risque restant identifie.

## Verdict

CLEAN
