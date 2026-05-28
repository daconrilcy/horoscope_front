# Final Evidence — CS-359-migrer-event-guidance-hors-chart-json-legacy

## Story status

- Validation outcome: pass
- Ready for review: yes
- Story key: CS-359-migrer-event-guidance-hors-chart-json-legacy
- Source story: `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/00-story.md`
- Capsule path: `_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy`
- Final decision: `delete`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source and tracker row match brief `_story_briefs/cs-359-migrer-event-guidance-hors-chart-json-legacy.md`.
- Initial `git status --short`: pre-existing `?? _condamad/run-state.json`.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule generated/validated after required generated files were missing.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story source loaded. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated during preflight. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated during preflight. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated during preflight. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated during preflight. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `evidence/event-guidance-decision.md` records `delete`. | before/after scans persisted. | PASS |
| AC2 | Removed canonical `event_guidance` contract. | targeted pytest + AST guard PASS. | PASS |
| AC3 | Removed guidance seed and taxonomy event rows. | targeted pytest + after scan PASS. | PASS |
| AC4 | Removed `chart_json` and `event_description` from guidance governance. | governance pytest PASS. | PASS |
| AC5 | Removed adapter special-case, paid use-case entry, and prompt catalog entry. | AST guard PASS. | PASS |
| AC6 | Residual hits classified as chat intent, anti-return tests, or CONDAMAD evidence/docs. | `event-guidance-scan-after.txt`. | PASS |
| AC7 | Natal legacy carrier guards unchanged and passing. | astrology boundary + legacy extinction tests PASS. | PASS |
| AC8 | CS-350 doc now says `event_guidance` is deleted by CS-359. | after scan PASS. | PASS |
| AC9 | Public API route paths unchanged. | OpenAPI before/after paths equal; TestClient `/openapi.json` PASS. | PASS |
| AC10 | Decision, scans and OpenAPI snapshots persisted. | capsule validation PASS. | PASS |
| AC11 | RG-149 now says `event_guidance` is deleted by CS-359. | after scan PASS. | PASS |

## Files changed

- Backend LLM runtime/config: `canonical_use_case_registry.py`, `adapter.py`, `gateway.py`, `catalog.py`, `prompt_governance_registry.json`.
- Backend seed/bootstrap: `seed_guidance_prompts.py`, `seed_66_20_taxonomy.py`.
- Tests: `test_llm_legacy_extinction.py`, `test_prompt_governance_registry.py`, `test_natal_metrics.py`.
- Docs/guardrails: CS-350 prompt-generation cartography, `regression-guardrails.md`.
- Evidence/capsule: `generated/03-acceptance-traceability.md`, `generated/10-final-evidence.md`, `evidence/**`.

## Files deleted

- No physical file deleted. Runtime entries for `event_guidance` were removed from canonical registries/seeds/configs.

## Tests added or updated

- Added guards that `event_guidance` has no canonical contract, no guidance seed and no supported fallback surface.
- Updated prompt governance test so `event_description` is rejected for the guidance family.
- Replaced `event_guidance` as a generic non-natal metric fixture with `test_guidance`.

## Commands run

| Command | Result |
|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --story-key CS-359-migrer-event-guidance-hors-chart-json-legacy` | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-359-migrer-event-guidance-hors-chart-json-legacy` | PASS |
| `rg -n "event_guidance\|chart_json\|natal_data" backend/app backend/tests _condamad/docs/prompt-generation-cartography _condamad/stories/regression-guardrails.md ...` | PASS, persisted before/after |
| OpenAPI snapshot before/after with `app.openapi()` | PASS, public paths unchanged |
| AST/JSON guard for contract, adapter, seed, governance | PASS |
| `ruff format <changed python files>` | PASS |
| `python -B -m pytest -q --tb=short <targeted LLM/tests>` | PASS, 54 passed, 16 deselected |
| `ruff check .` | PASS |
| `python -B -m pytest -q --tb=short` | PASS, 3349 passed, 1 skipped, 1223 deselected |
| `TestClient(app).get('/openapi.json')` | PASS, 200 |
| `git diff --check -- <story paths>` | PASS |

All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Commands skipped or blocked

- No applicable validation was skipped.

## DRY / No Legacy evidence

- No shim, alias, fallback or duplicate active path was added.
- `event_guidance` is absent from canonical contracts, seed prompts, taxonomy event mapping, prompt catalog, paid use-case set and adapter routing.
- `chart_json` and `event_description` are absent from the guidance governance family.
- Residual backend hits are anti-return tests or `offer_event_guidance` chat intent, not the deleted runtime use case.

## Final worktree status

- Story files modified as expected.
- Pre-existing untracked `_condamad/run-state.json` remains unrelated.

## Diff review

- `git diff --stat -- <story paths>` reviewed: 13 application/doc/test files changed before evidence/status updates, with net deletion of dormant event guidance runtime entries.
- `git diff --name-only -- <story paths>` reviewed: changes are scoped to backend LLM runtime/config/seeds/tests, CS-350/RG-149 docs, and CS-359 evidence.
- `git diff --check -- <story paths>` PASS.

## Remaining risks

- No runtime risk identified for public API paths; OpenAPI paths are unchanged.
- Reviewer should confirm that retaining chat intent `offer_event_guidance` is acceptable as a product suggestion distinct from the deleted LLM use case.

## Feedback loop routing

- No new reusable process failure to propagate. Capsule preparation ambiguity was handled with `--story-key`; no skill update required.

## Suggested reviewer focus

- Confirm the deletion decision and the classification of residual `offer_event_guidance` as chat intent only.
