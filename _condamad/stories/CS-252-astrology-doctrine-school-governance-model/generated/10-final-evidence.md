# Final Evidence — CS-252-astrology-doctrine-school-governance-model

## Story status

- Validation outcome: PASS
- Final status: done
- Story key: `CS-252-astrology-doctrine-school-governance-model`
- Source story: `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/00-story.md`
- Capsule path: `_condamad/stories/CS-252-astrology-doctrine-school-governance-model`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`
- Initial `git status --short`: dirty worktree with pre-existing CS-246..CS-251 story artifacts and backend runtime/test changes.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes; generated files were copied from the script-created derived slug into the target CS-252 capsule.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status set to `done`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story key aligned. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1..AC10 all PASS. |
| `generated/04-target-files.md` | yes | yes | PASS | Scope recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executed checks recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No legacy stance recorded. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `MANDATORY_RULE_FAMILIES` and governance declarations cover all CS-240 families. | Unit governance tests and `governance-after.json`. | PASS | |
| AC2 | `RuleSourceOwnerStatus` and entry owner fields. | Unit governance tests and status scan. | PASS | |
| AC3 | `CS_241_F003_WEIGHTING_FAMILIES` entries have owner/blocker. | Unit governance tests. | PASS | |
| AC4 | Source owner and doctrine fields are separate. | Unit governance tests. | PASS | |
| AC5 | Owner and doctrine transition validators. | Unit governance tests. | PASS | |
| AC6 | `needs-user-decision` entries keep blockers. | Unit governance tests and JSON snapshot. | PASS | |
| AC7 | AST architecture guard plus governed surfaces registry. | Architecture guard tests. | PASS | |
| AC8 | CS-253 future-technique notes. | Unit test and targeted `rg`. | PASS | |
| AC9 | API neutrality test, route and OpenAPI assertions. | `TestClient`, `app.routes`, `app.openapi()`. | PASS | |
| AC10 | Evidence files persisted. | Evidence path checks and capsule validation. | PASS | |

## Files changed

- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`
- `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None in target scope.
- Removed the script-created derived CS-252 capsule after copying generated files into the target CS-252 capsule.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`.
- Added `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`.
- Updated `backend/tests/architecture/test_api_contract_neutrality.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...` | repo root | PASS | 0 | Generated capsule files under derived slug. |
| `condamad_validate.py <CS-252 capsule>` | repo root | PASS | 0 | Target capsule valid after generated file copy. |
| `ruff format <modified python files>` | repo root | PASS | 0 | Modified Python files formatted. |
| `pytest <CS-252 targeted tests>` | repo root | PASS | 0 | 24 passed. |
| `ruff check backend` | repo root | PASS | 0 | All checks passed. |
| `python -B -m pytest -q backend\tests` | repo root | PASS | 0 | 945 passed, 201 deselected. |
| `app.openapi()` and `app.routes` assertions | repo root | PASS | 0 | Doctrine governance not exposed publicly. |
| Targeted `rg` scans | repo root | PASS | 0 | Statuses and CS-253 citation found; public exposure absent. |

## Commands skipped or blocked

- `rg ... backend\alembic ...` was adjusted because `backend\alembic` does not exist; scan ran on existing API/frontend/db-seeder paths.
- Frontend validations were not run because the story forbids frontend changes and no frontend file changed.

## DRY / No Legacy evidence

- One canonical implementation: `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`.
- Unknown rule family resolver raises explicit error; no fallback.
- Duplicate and unknown declarations fail deterministic validation.
- No compatibility route, shim, alias, re-export legacy path, public serializer, DB schema, migration, seed, frontend file, or narration change was added.

## Diff review

- `git diff --stat`: reviewed after implementation.
- `git diff --check`: no whitespace errors for story-touched files.

## Final worktree status

- Worktree remains dirty due to this story plus pre-existing unrelated CS-246..CS-251 and backend changes.

## Remaining risks

- The governance guard is intentionally strict: future existing-domain files with rule markers must be classified in `GOVERNED_RULE_SOURCE_SURFACES`.

## Suggested reviewer focus

- Review the family classifications and blockers in `ASTROLOGY_DOCTRINE_GOVERNANCE_DECLARATIONS`, especially mixed ownership for CS-240 F-001/F-002/F-003/F-004.

## Feedback loop routing

- No reusable skill or AGENTS.md update required; validation failure was local to newly introduced guard coverage and was resolved by classifying existing surfaces.
