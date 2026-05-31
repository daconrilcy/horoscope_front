# Final Evidence — CS-403-quota-natal-transactionnel-remediation

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-403-quota-natal-transactionnel-remediation
- Source story: `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/00-story.md`
- Source brief: `_story_briefs/cs-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides.md`
- Capsule path: `_condamad/stories/CS-403-quota-natal-transactionnel-remediation`
- Source finding closure status: full-closure for the quota/remediation scope carried by this story.

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` was already modified before implementation.
- Tracker verification: `CS-403` row path and source brief matched the requested story and brief.
- Guardrails applied: `RG-002`, `RG-005`, `RG-006`, `RG-150`, `RG-152`, `RG-157`.
- Existing `generated/11-code-review.md`: editorial/pre-implementation story review only; not used as final implementation review evidence.
- Capsule repair: required generated files were missing and were repaired with `condamad_prepare.py --repair-generated-only`, then validated.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC12 all classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## Implementation summary

- Added endpoint regression tests proving rejected complete responses, provider errors and post-acceptance commit failures do not leave an unprotected quota debit path.
- Preserved canonical ownership: public router remains HTTP orchestration, entitlement gate owns quota checks/debit, generation service owns invalid-reading claim/release and public replay filtering.
- Added durable remediation policy evidence under the story capsule.
- No frontend change, no API route shape change, no new dependency, no legacy shim.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `check_access_for_complete_generation` verifies access before generation; endpoint tests cover no-consume rejected/provider paths. | Unit quota test and long entitlement suite PASS. | PASS |
| AC2 | Router calls `consume_on_acceptance` after accepted non-cached complete response. | Unit quota-on-acceptance tests and integration quota selection PASS. | PASS |
| AC3 | Debit remains before `db.commit`; commit-failure endpoint test exercises rollback path after acceptance. | Long entitlement suite and `git diff --check` PASS. | PASS |
| AC4 | Rejected/provider paths release corrective claim and do not call `consume_on_acceptance`. | Long entitlement suite PASS. | PASS |
| AC5 | Stored payload classifier rejects missing/invalid narrative, duplicate content and empty sources. | Narrative unit suite and rejected public boundary suite PASS. | PASS |
| AC6 | `consume_on_acceptance` skips `corrective_regeneration=True`. | Unit quota suite and long entitlement suite PASS. | PASS |
| AC7 | Corrective claim moves invalid row to a reserved corrective use case and release restores original use case. | Rejected public boundary suite PASS. | PASS |
| AC8 | Corrective claim update requires original `use_case`, hiding the reserved row from a second active claim. | Long entitlement suite PASS. | PASS |
| AC9 | Public replay excludes rejected and corrective-reserved rows. | Rejected public boundary suite PASS. | PASS |
| AC10 | Public router has no `check_and_consume` path. | Targeted `rg` scan PASS with no matches; `ruff check .` PASS. | PASS |
| AC11 | Runtime route and OpenAPI still register `POST /v1/natal/interpretation`. | Runtime `app.routes` / `app.openapi()` check PASS. | PASS |
| AC12 | Remediation policy and before/after evidence are persisted under story evidence. | Capsule final validation PASS after this update. | PASS |

## Files changed

- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/00-story.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/01-execution-brief.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/04-target-files.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/06-validation-plan.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/10-final-evidence.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/generated/11-code-review.md`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/quota-remediation-before.txt`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/quota-remediation-after.txt`
- `_condamad/stories/CS-403-quota-natal-transactionnel-remediation/evidence/remediation-policy.md`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added three endpoint regression tests in `test_natal_chart_long_entitlement.py`:
  rejected response no-debit, provider error no-debit, and commit failure rollback after acceptance.

## Commands run

| Command | Result | Evidence summary |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-403-quota-natal-transactionnel-remediation --root .` | PASS | Capsule generated files repaired. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-403-quota-natal-transactionnel-remediation` | PASS | Capsule structure valid. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-403-quota-natal-transactionnel-remediation --final` | PASS | Final CONDAMAD consistency gate passed. |
| `ruff format backend\app\tests\integration\test_natal_chart_long_entitlement.py` | PASS | Modified Python test formatted. |
| `ruff check --fix backend\app\tests\integration\test_natal_chart_long_entitlement.py` | PASS | Import ordering fixed. |
| `ruff check .` | PASS | Project lint green. |
| `python -B -m pytest -q backend\tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short` | PASS | 4 passed. |
| `python -B -m pytest -q backend\tests\unit\test_narrative_natal_reading_v1.py --tb=short` | PASS | 14 passed. |
| `python -B -m pytest -q --long backend\app\tests\integration\test_natal_chart_long_entitlement.py --tb=short` | PASS | 16 passed. |
| `python -B -m pytest -q --long backend\tests\integration -k "natal and (quota or interpretation or rejected)" --tb=short` | PASS | 10 passed, 233 deselected. |
| `python -B -m pytest -q --long backend\tests\integration\test_natal_interpretation_rejected_public_boundary.py --tb=short` | PASS | 8 passed. |
| `python -B -m pytest -q --long backend\app\tests\integration\test_natal_interpretation_endpoint.py --tb=short` | PASS | 8 passed. |
| `python -B -c "from app.main import app; ..."` | PASS | Runtime route and OpenAPI contain `POST /v1/natal/interpretation`. |
| `rg -n "check_and_consume" backend\app\api\v1\routers\public\natal_interpretation.py` | PASS | No matches; router has no direct check-and-consume path. |
| `git diff --check` | PASS | No whitespace errors; warning only for pre-existing `_condamad/run-state.json` line endings. |

## Commands skipped or blocked

- Full `python -B -m pytest -q --tb=short` was not run because the capsule defines targeted story validations and long integration suites; compensating evidence is the story-specific unit, integration, route/OpenAPI and lint checks above.
- A broad legacy/fallback scan produced existing references in `interpretation_service.py` and `was_fallback` fields; they are pre-existing schema/legacy conversion vocabulary outside this story's delta, not newly introduced active compatibility paths.

## DRY / No Legacy evidence

- No duplicate quota implementation added.
- No `check_and_consume` call exists in `backend/app/api/v1/routers/public/natal_interpretation.py`.
- No frontend or legacy adapter path was added.
- Corrective remediation uses existing canonical gate and generation service methods.

## Diff review

- `git diff --stat` scoped to story paths shows backend test additions plus story evidence/status files only.
- `git diff --check` PASS.

## Final worktree status

- Story-owned modifications are limited to the files listed above.
- Pre-existing dirty file remains `_condamad/run-state.json`.

## Remaining risks

- The full repository pytest suite was not run; targeted capsule validations passed.
- The commit-failure test proves rollback orchestration with a mocked commit failure, not a physical database crash.

## Suggested reviewer focus

- Review the transaction boundary around router `consume_on_acceptance` and `db.commit`, plus the corrective claim release behavior on rejected/provider paths.

## Feedback loop routing

- no-propagation: this run produced local story evidence and tests; no reusable process correction was required after final validation.
