# CONDAMAD Code Review

## Review target

- Story: `CS-010-corriger-resolution-evenements-astro-foundation`
- Source: `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/00-story.md`
- Status reviewed: `ready-to-review`
- Applicable guardrail: `RG-030`

## Inputs reviewed

- Story contract and ACs.
- Capsule evidence: acceptance traceability, validation plan, No Legacy / DRY guardrails, final evidence.
- Diff for:
  - `backend/app/prediction/public_projection.py`
  - `backend/app/prediction/public_astro_daily_events.py`
  - `backend/tests/unit/prediction/test_public_astro_foundation.py`
  - `_condamad/stories/regression-guardrails.md`
  - `_condamad/stories/story-status.md`
- Persisted before/after artifacts:
  - `astro-foundation-before.md`
  - `astro-foundation-after.md`

## Diff summary

- `PublicAstroFoundationPolicy` now resolves events via `resolve_public_astro_events`.
- Public astro aspect event types are shared through `PUBLIC_ASTRO_ASPECT_EVENT_TYPES`.
- `PublicAstroDailyEventsPolicy` reuses the same resolver and aspect type set.
- Unit tests were added for `core.detected_events` and the three `aspect_exact_*` event types.
- CS-010 evidence artifacts were added.

## Review layers

- Diff integrity: no unexpected application files, dependency files, generated cache, secrets, or frontend changes found for CS-010.
- Acceptance audit: AC1 to AC4 are covered by code and targeted tests.
- Validation audit: reviewer reran required targeted checks after venv activation.
- DRY / No Legacy audit: no new compatibility wrapper, re-export, alias, public schema replacement, or non-canonical event source was introduced.
- Security/data audit: no auth, secrets, persistence, SQL, or external-client surface touched.

## Findings

No actionable CS-010 findings.

## Acceptance audit

| AC | Review result |
|---|---|
| AC1 | PASS. `backend/app/prediction/public_projection.py` calls `resolve_public_astro_events`, which resolves `core.events` then `core.detected_events`. `test_astro_foundation_reads_detected_events_from_engine_output` proves population from `detected_events`. |
| AC2 | PASS. `PUBLIC_ASTRO_ASPECT_EVENT_TYPES` includes `aspect_exact_to_angle`, `aspect_exact_to_luminary`, and `aspect_exact_to_personal`; `PublicAstroFoundationPolicy` uses it for `dominant_aspects`. |
| AC3 | PASS. No public field was added, removed, or renamed in the touched projection code; public projection and API integration tests pass. |
| AC4 | PASS. `astro-foundation-before.md` and `astro-foundation-after.md` exist and document the allowed before/after difference. |

## Validation audit

Reviewer commands run:

| Command | Working directory | Result |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/prediction/public_projection.py app/prediction/public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py` | repository root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py app/tests/integration/test_daily_prediction_api.py` | repository root | PASS, 43 tests |
| `cd backend; rg -n "aspect_exact_to_angle|aspect_exact_to_luminary|aspect_exact_to_personal|detected_events" app/prediction` | repository root | PASS, RG-030 hits reviewed |
| `git diff --check` | repository root | PASS, CRLF warnings only |
| `git diff --stat` | repository root | PASS, changed tracked files match reviewed scope |

Implementation evidence also reports a full `pytest -q` backend run failing on `test_api_sql_boundary_debt_matches_exact_allowlist`. That failure is outside the CS-010 touched files and was not reproduced as a CS-010 regression in this review, but it prevents a full clean-suite claim.

## DRY / No Legacy audit

- `PublicAstroFoundationPolicy` does not define a second foundation-only aspect taxonomy.
- No new public field replaces `astro_foundation`.
- No source outside `events`, `detected_events`, evidence metadata, or the already-existing persisted snapshot `v3_metrics.detected_events` path was added.
- `RG-030` scan evidence is present and was rerun.

## Residual risks

- Full backend suite status remains limited by the unrelated API SQL allowlist failure recorded in `generated/10-final-evidence.md`.
- Local app server startup was not rerun by the reviewer; CS-010 is covered by projection unit tests and API integration tests.

## Verdict

`ACCEPTABLE_WITH_LIMITATIONS`

Required CS-010 validation is complete and passing. The remaining limitation is the unrelated full-suite failure already recorded by the implementation evidence.
