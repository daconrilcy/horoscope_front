# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: CS-010-corriger-resolution-evenements-astro-foundation
- Source story: `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/00-story.md`
- Capsule path: `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md` modified; `_condamad/stories/story-status.md` modified; CS-010 to CS-013 story folders untracked.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/`, `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/`, `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/`, `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/`.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status and task checkboxes updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific scope. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1 to AC4 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands and limitation rule listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-030 mapped. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/prediction/public_projection.py` calls `resolve_public_astro_events`; `backend/app/prediction/public_astro_daily_events.py` reads `core.detected_events`. | `pytest -q tests/unit/prediction/test_public_astro_foundation.py` passed; dedicated test covers `detected_events`. | PASS | `astro_foundation` is populated from canonical detected events. |
| AC2 | `PUBLIC_ASTRO_ASPECT_EVENT_TYPES` includes `aspect_exact_to_angle`, `aspect_exact_to_luminary`, `aspect_exact_to_personal`; foundation reuses it for `dominant_aspects`. | `pytest -q tests/unit/prediction/test_public_astro_foundation.py` passed; dedicated test covers all exact types. | PASS | No duplicate foundation-only taxonomy. |
| AC3 | No public payload field was added, renamed, or deleted; only existing `astro_foundation` content can be filled. | `pytest -q app/tests/unit/test_public_projection.py` passed; `pytest -q app/tests/integration/test_daily_prediction_api.py` passed. | PASS | API integration suite passed. |
| AC4 | `astro-foundation-before.md` and `astro-foundation-after.md` were added. | Artifacts exist and describe before/after behavior. | PASS | Baseline and fixed behavior persisted. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/prediction/public_astro_daily_events.py` | modified | Add shared event resolution and shared exact aspect event type set. | AC1, AC2 |
| `backend/app/prediction/public_projection.py` | modified | Reuse canonical event resolution and exact aspect set in `PublicAstroFoundationPolicy`. | AC1, AC2, AC3 |
| `backend/tests/unit/prediction/test_public_astro_foundation.py` | modified | Add tests for `detected_events` and exact aspect types. | AC1, AC2 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/00-story.md` | modified | Mark story ready for review and tasks complete. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-before.md` | added | Persist bug baseline. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-after.md` | added | Persist fixed behavior. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/01-execution-brief.md` | generated | Story execution scope. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/03-acceptance-traceability.md` | generated | AC traceability. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/04-target-files.md` | generated | Target file evidence. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/05-implementation-plan.md` | generated | Implementation plan. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/06-validation-plan.md` | generated | Validation plan. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/07-no-legacy-dry-guardrails.md` | generated | DRY and No Legacy evidence. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/09-dev-log.md` | generated | Development log. | AC4 |
| `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/10-final-evidence.md` | generated | Final evidence. | AC4 |
| `_condamad/stories/story-status.md` | modified | Set CS-010 to `ready-to-review`. | AC4 |

## Files deleted

| File | Reason |
|---|---|
| None | No deletion required. |

## Tests added or updated

- Added `test_astro_foundation_reads_detected_events_from_engine_output`.
- Added `test_astro_foundation_recognizes_all_exact_aspect_event_types`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-010-corriger-resolution-evenements-astro-foundation\00-story.md --root . --story-key CS-010-corriger-resolution-evenements-astro-foundation --with-optional` | repository root | PASS | 0 | Capsule files generated after venv activation. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-010-corriger-resolution-evenements-astro-foundation` | repository root | PASS | 0 | Capsule structure valid before implementation. |
| `pytest -q tests/unit/prediction/test_public_astro_foundation.py` | `backend` | PASS | 0 | 5 tests passed. |
| `pytest -q tests/unit/prediction/test_public_astro_daily_events.py` | `backend` | PASS | 0 | 6 tests passed. |
| `pytest -q app/tests/unit/test_public_projection.py` | `backend` | PASS | 0 | 13 tests passed. |
| `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend` | PASS | 0 | 25 tests passed. |
| `ruff check app/prediction/public_projection.py app/prediction/public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py` | `backend` | PASS | 0 | All checks passed. |
| `ruff format app/prediction/public_projection.py app/prediction/public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py` | `backend` | PASS | 0 | 2 files reformatted, 2 files unchanged. |
| `pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py app/tests/integration/test_daily_prediction_api.py` | `backend` | PASS | 0 | 43 tests passed. |
| `rg -n "aspect_exact_to_angle\|aspect_exact_to_luminary\|aspect_exact_to_personal\|detected_events" app/prediction` | `backend` | PASS | 0 | Hits show canonical event taxonomy and resolution in prediction modules. |
| `git diff --check` | `backend` | PASS | 0 | No whitespace errors; Git reported CRLF normalization warnings only. |
| `pytest -q` | `backend` | FAIL | 1 | 3585 passed, 12 skipped, 1 unrelated API SQL allowlist test failed. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-010-corriger-resolution-evenements-astro-foundation --final` | repository root | PASS | 0 | Final capsule validation passed. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app server startup | no | CS-010 is a backend projection unit/integration change; no route or server startup behavior changed. | Server startup was not independently re-proven in this turn. | API integration tests passed through the backend test harness. |

## DRY / No Legacy evidence

- No new dependency was added.
- No compatibility wrapper, re-export, or alias was introduced.
- Event source resolution is shared through `resolve_public_astro_events`.
- Exact aspect event type support is shared through `PUBLIC_ASTRO_ASPECT_EVENT_TYPES`.
- RG-030 scan was run: `rg -n "aspect_exact_to_angle|aspect_exact_to_luminary|aspect_exact_to_personal|detected_events" app/prediction`.

## Diff review

- Relevant backend changes are limited to public astro event resolution, public projection, and targeted tests.
- `_condamad/stories/regression-guardrails.md` already had pre-existing CS-010 to CS-013 changes; this implementation did not add a new guardrail row.
- `_condamad/stories/story-status.md` was updated only for the CS-010 status/date; existing CS-011 to CS-013 rows were preserved.
- Full backend regression failure is outside touched files and concerns API SQL boundary allowlist debt.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/prediction/public_astro_daily_events.py
 M backend/app/prediction/public_projection.py
 M backend/tests/unit/prediction/test_public_astro_foundation.py
?? _condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/
?? _condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/
?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/
?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/
```

## Remaining risks

- `pytest -q` full backend suite currently fails on `test_api_sql_boundary_debt_matches_exact_allowlist`, unrelated to CS-010. Reviewer should decide whether that pre-existing API architecture debt blocks merge.

## Suggested reviewer focus

- Review the shared event resolution helper to confirm the source precedence matches `events` then `detected_events`.
- Review that `astro_foundation` shape is unchanged while exact aspect population is corrected.
- Review the unrelated full-suite failure classification.
