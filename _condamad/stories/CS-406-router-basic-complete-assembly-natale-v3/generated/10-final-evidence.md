# Final Evidence — CS-406-router-basic-complete-assembly-natale-v3

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-406-router-basic-complete-assembly-natale-v3
- Source story: `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/00-story.md`
- Source brief: `_story_briefs/cs-401-router-basic-complete-vers-assembly-natale-v3.md`
- Tracker row: `CS-406` path/source checked and updated to `ready-to-review`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` was already dirty before implementation.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule generated/validated before generated-file loading because required generated files were missing.
- Applicable guardrails: `RG-149`, `RG-150`, `RG-152`, `RG-155`, `RG-156`, `RG-157`.
- Non-applicable scope: frontend, auth, billing, migrations, pricing.

## Capsule validation

- Initial capsule validation after preparation: PASS.
- Final capsule validation: PASS after this evidence update.
- Existing `generated/11-code-review.md`: classified `obsolete-pre-implementation`.

## Implementation summary

- `backend/app/domain/llm/runtime/gateway.py`: `_normalize_plan_for_assembly` now preserves `basic` only for `natal/interpretation` + `natal_interpretation`; all other Basic scopes still normalize through `normalize_plan_scope`.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`: Basic natal execution profile now has explicit dedicated defaults (`verbosity_profile=detailed`, `max_output_tokens=2400`) while Free remains the default short profile.
- `backend/tests/llm_orchestration/test_assembly_resolution.py`: added runtime tests for Basic registry plan, Free short, Premium complete, Chat Basic unchanged, Guidance Basic unchanged.
- `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`: added AST/contract tests for the Basic seed tuple and V3 contract.
- `backend/tests/integration/test_admin_llm_catalog.py`: added active snapshot catalog visibility for `natal:interpretation:basic:fr-FR`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Runtime Basic plan resolves Basic assembly. | pytest assembly resolution PASS. | PASS |
| AC2 | Seed tuple maps Basic to `natal_interpretation`. | seed unit PASS. | PASS |
| AC3 | Canonical contract for `natal_interpretation` is `AstroResponse_v3`. | seed unit PASS. | PASS |
| AC4 | Targeted Basic execution profile created/updated. | taxonomy pytest PASS. | PASS |
| AC5 | Basic defaults differ from Free defaults. | seed unit PASS. | PASS |
| AC6 | Free short assembly remains selected. | runtime pytest PASS. | PASS |
| AC7 | Premium complete assembly remains selected. | runtime pytest PASS. | PASS |
| AC8 | Chat Basic still resolves Free scope. | runtime pytest PASS. | PASS |
| AC9 | Spy proves `AssemblyRegistry` receives `plan="basic"`. | runtime pytest PASS. | PASS |
| AC10 | Basic seed tuple discoverable via AST test and targeted `rg`. | seed unit and `rg` PASS. | PASS |
| AC11 | Admin catalog exposes Basic natal active snapshot. | integration pytest with `--long` PASS. | PASS |
| AC12 | Traceability, dev log, final evidence, and evidence files persisted. | capsule validation PASS. | PASS |
| AC13 | Guidance Basic still resolves Free scope. | runtime pytest PASS. | PASS |

## Files changed

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `_condamad/stories/CS-406-router-basic-complete-assembly-natale-v3/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added seed unit coverage: `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py`.
- Updated orchestration runtime coverage in `backend/tests/llm_orchestration/test_assembly_resolution.py`.
- Updated admin catalog integration coverage in `backend/tests/integration/test_admin_llm_catalog.py`.

## Commands run

| Command | Result |
|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-406-router-basic-complete-assembly-natale-v3\00-story.md --root C:\dev\horoscope_front --story-key CS-406-router-basic-complete-assembly-natale-v3` | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-406-router-basic-complete-assembly-natale-v3` | PASS |
| `python -B -m ruff format backend\app\domain\llm\runtime\gateway.py backend\app\ops\llm\bootstrap\seed_66_20_taxonomy.py backend\tests\llm_orchestration\test_assembly_resolution.py backend\tests\unit\test_seed_66_20_taxonomy_basic_natal.py backend\tests\integration\test_admin_llm_catalog.py` | PASS |
| `python -B -m ruff check backend\app\domain\llm\runtime\gateway.py backend\app\ops\llm\bootstrap\seed_66_20_taxonomy.py backend\tests\llm_orchestration\test_assembly_resolution.py backend\tests\unit\test_seed_66_20_taxonomy_basic_natal.py backend\tests\integration\test_admin_llm_catalog.py` | PASS |
| `python -B -m pytest -q backend\tests\llm_orchestration\test_assembly_resolution.py -k "basic or natal" --tb=short` | PASS: 6 passed, 13 deselected |
| `python -B -m pytest -q backend\tests\unit\test_seed_66_20_taxonomy_basic_natal.py --tb=short` | PASS: 2 passed |
| `python -B -m pytest -q backend\tests\llm_orchestration\test_execution_profile_taxonomy.py --tb=short` | PASS: 4 passed |
| `python -B -m pytest -q --long backend\tests\integration\test_admin_llm_catalog.py -k "natal and basic" --tb=short` | PASS: 1 passed, 27 deselected |
| `python -B -m pytest -q backend\tests\unit\test_narrative_natal_reading_v1.py backend\tests\unit\domain\astrology\test_client_interpretation_support_elements.py --tb=short` | PASS: 16 passed |
| Targeted `rg` scans for Basic seed tuple, no section padding fallback, no public `check_and_consume`, and prompt cartography anti-promotion text | PASS |
| Short local startup: `python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8765`; `GET /docs` | PASS: HTTP 200; process stopped |

## Commands skipped or blocked

- Full backend pytest suite skipped: broader than the story validation plan and slower than necessary; targeted runtime, seed, catalog, and applicable guardrail tests passed.
- `pytest -q --long backend/app/tests/integration/test_natal_chart_long_entitlement.py` skipped: quota surface unchanged by this story; `check_and_consume` negative scan passed for the public natal route.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback path, duplicate active implementation, or legacy import was added.
- Existing global `normalize_plan_scope("basic") == "free"` remains unchanged for non-dedicated Basic assemblies.
- Basic preservation is contextual in the gateway and covered by Chat/Guidance non-regression tests.

## Diff review

- `git diff --stat` reviewed for backend runtime, seed, tests, and capsule paths.
- `git diff --name-only` reviewed; unrelated pre-existing dirty file `_condamad/run-state.json` left untouched.
- `git diff --check` PASS.

## Final worktree status

- Modified by this story: backend runtime/seed/tests and CS-406 capsule/status evidence.
- Pre-existing dirty file remains: `_condamad/run-state.json`.

## Remaining risks

- Basic profile values (`gpt-4o-mini`, detailed, 2400 tokens) are explicit implementation defaults; product may later choose different commercial tuning.

## Suggested reviewer focus

- Verify the contextual condition in `LLMGateway._normalize_plan_for_assembly` is narrow enough: only `natal/interpretation` + `natal_interpretation` should preserve Basic.

## Feedback loop routing

- no-propagation: no reusable process/guardrail update was identified beyond this story evidence.
