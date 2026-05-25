# Final Evidence — CS-285-structured-facts-v1-builder

## Story status

- Validation outcome: PASS
- Ready for review: completed clean
- Story key: CS-285-structured-facts-v1-builder
- Source story: `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md`
- Capsule path: `_condamad/stories/CS-285-structured-facts-v1-builder`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: run; many unrelated pre-existing changes recorded outside CS-285.
- AGENTS.md considered: root `AGENTS.md` / prompt instructions.
- Story registry: `CS-285` row path and brief source matched the request.
- Capsule validation: `condamad_validate.py _condamad\stories\CS-285-structured-facts-v1-builder` PASS.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status updated to done after clean implementation review. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC8 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Current file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Builder delegates to `ChartInterpretationInputBuilder`; architecture guard persisted. | AST/unit guard PASS. | PASS | Existing owner reused. |
| AC2 | Payload emits `projection_id: structured_facts_v1`; sample JSON persisted. | Unit shape test PASS. | PASS | No public serializer added. |
| AC3 | Stable sorting and canonical hash-input JSON implemented. | Stability unit test PASS. | PASS | Identical input yields identical canonical JSON. |
| AC4 | Payload contains factual sections only. | Unit absence assertion and targeted `rg` PASS. | PASS | Forbidden text-like labels removed from `excluded_surfaces`. |
| AC5 | Missing optional runtime data has null/empty collection semantics. | Missing-data unit test PASS. | PASS | Deterministic sorted list. |
| AC6 | No route, OpenAPI, DB, migration or frontend file changed. | `app.openapi()`, `app.routes`, `TestClient('/health')` PASS. | PASS | Public surface neutral. |
| AC7 | One canonical builder owner under interpretation. | Single-owner and doctrine-governance guards PASS. | PASS | No shim/alias/fallback. |
| AC8 | Evidence files persisted under `evidence/`. | File existence and capsule validation PASS. | PASS | Sample, validation and guards present. |

## Files changed

- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `_condamad/stories/CS-285-structured-facts-v1-builder/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-285-structured-facts-v1-builder/generated/09-dev-log.md`
- `_condamad/stories/CS-285-structured-facts-v1-builder/generated/10-final-evidence.md`
- `_condamad/stories/CS-285-structured-facts-v1-builder/evidence/*`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`

## Commands run

| Command | Result | Evidence summary |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...` | PASS | Generated missing capsule files. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-285-structured-facts-v1-builder` | PASS | Capsule structure valid. |
| `ruff format app\domain\astrology\interpretation\structured_facts_v1_builder.py tests\unit\domain\astrology\test_structured_facts_v1_builder.py` | PASS | Scoped formatting. |
| `ruff check app\domain\astrology\interpretation\structured_facts_v1_builder.py tests\unit\domain\astrology\test_structured_facts_v1_builder.py` | PASS | Targeted lint. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_structured_facts_v1_builder.py --tb=short` | PASS | 7 passed. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_structured_facts_v1_builder.py tests\architecture\test_astrology_doctrine_governance_guardrails.py --tb=short` | PASS | 9 passed after doctrine-governance declaration. |
| `ruff check .` | PASS | Full backend lint. |
| `python -B -m pytest -q --tb=short` | PASS | 3322 passed, 1 skipped, 1204 deselected after review fixes. |
| `python -B -c "from app.main import app; ... app.openapi() ..."` | PASS | No `structured_facts_v1` OpenAPI exposure. |
| `python -B -c "from app.main import app; ... app.routes ..."` | PASS | No route path exposure. |
| `rg -n "prompt\|llm_output\|final_narrative\|rendered_text\|provider_response" <CS-285 files>` | PASS | No matches; exit 1 treated as expected absence. |

## Commands skipped or blocked

- Broad capsule scan over `app/domain/astrology/interpretation tests` was captured in `evidence/broad-forbidden-scan.txt`; it has historical matches in unrelated tests that define forbidden token lists. Story-owned targeted scan is clean.

## DRY / No Legacy evidence

- One canonical `StructuredFactsV1Builder` owner under `backend/app/domain/astrology/interpretation`.
- `structured_facts_v1_builder.py` is declared in doctrine-governance surfaces because it references sign profile data.
- No frontend, API router, DB, migration, generated client, shim, alias or fallback path added.
- Builder consumes the existing `ChartInterpretationInputBuilder` owner rather than raw public payloads.

## Diff review

- `git diff --check -- <CS-285 paths>` PASS.
- Scoped diff reviewed for builder, unit test and capsule evidence.

## Final worktree status

- Final `git status --short` remains dirty due to many pre-existing unrelated changes plus CS-285 additions/updates.

## Remaining risks

- Broad forbidden-term scan remains noisy because existing tests contain assertion lists with those tokens; reviewer should rely on the targeted CS-285 scan for this story.

## Suggested reviewer focus

- Confirm the exact `structured_facts_v1` payload shape is sufficient for the next persistence/audit hash consumer before that consumer is implemented.
- Review/fix iteration 1 found and fixed forbidden text-like `excluded_surfaces` labels and a missing doctrine-governance declaration.
