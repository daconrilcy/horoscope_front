# Final Evidence - CS-336 supprimer-surfaces-legacy-injection-llm-natale

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-336-supprimer-surfaces-legacy-injection-llm-natale`
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale`
- Story registry: `ready-to-review` on 2026-05-27

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source and status row match `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`.
- Initial worktree already contained CS-336 code/capsule changes; they were treated as in-scope existing work.
- Capsule validation before implementation: PASS.
- Applicable guardrails: RG-002 public API neutrality, RG-022 collected prompt-generation validation paths.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated AC-by-AC. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated before implementation. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated before implementation. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated before implementation. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated for review. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `NatalExecutionInput` old fields removed; adapter no longer forwards old carriers. | Runtime/architecture tests pass. | PASS | |
| AC2 | Gateway no longer rebuilds natal validation payloads from `chart_json`, `natal_data`, or `evidence_catalog`. | Targeted payload tests pass. | PASS | |
| AC3 | Canonical registry, prompt governance family and active natal seed prompts expose `llm_astrology_input_v1`, not old carriers. | Contract, seed and lint tests pass. | PASS | |
| AC4 | Transition carrier registry and preview variables deleted; AST guard blocks return. | Architecture guard passes. | PASS | |
| AC5 | Residual scan saved and classified in `evidence/removal-audit.md`. | Targeted `rg` scan captured. | PASS | |
| AC6 | Prompt-visible natal payload snapshot uses canonical key and excludes legacy material. | Boundary tests and payload snapshot pass. | PASS | |
| AC7 | No API routers changed; `app.routes` and `app.openapi()` checks pass. | OpenAPI command passes. | PASS | |
| AC8 | Evidence artifacts and traceability updated. | Capsule validation passes. | PASS | |

## Files changed

- Runtime/config: `backend/app/domain/llm/runtime/*`, `backend/app/domain/llm/configuration/assembly_resolver.py`, `backend/app/domain/llm/governance/data/prompt_governance_registry.json`.
- Natal service/seeds: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/ops/llm/bootstrap/seed_29_prompts.py`, `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py`.
- Tests/guards: `backend/tests/**`, `backend/app/tests/unit/**`.
- Evidence: `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/**`, `_condamad/stories/story-status.md`.

## Files deleted

- None.

## Tests added or updated

- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/unit/test_natal_llm_use_case_input_contract.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/integration/test_llm_runtime_suppression.py`
- `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py`
- `backend/app/tests/unit/test_*` and `backend/app/tests/integration/test_admin_llm_natal_prompts.py` touched by natal runtime, seed and lint changes.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-336-supprimer-surfaces-legacy-injection-llm-natale` | repo root | PASS |
| `ruff format <changed python files>` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py tests/architecture/test_llm_legacy_extinction.py tests/unit/test_natal_llm_use_case_input_contract.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/integration/test_llm_runtime_suppression.py app/tests/unit/test_ai_engine_adapter.py app/tests/unit/test_gateway_input_validation_payload.py --tb=short` | `backend` | PASS, 34 passed |
| `python -B -m pytest -q app/tests/unit/test_seed_29_prompt_contract.py app/tests/unit/test_seed_30_8_v3_prompt_contract.py app/tests/unit/test_prompt_lint_natal.py app/tests/integration/test_admin_llm_natal_prompts.py app/tests/unit/test_natal_interpretation_service.py app/tests/unit/test_natal_interpretation_service_v2.py app/tests/unit/legacy_services/test_natal_interpretation_service_v2_refacto.py app/tests/unit/test_ai_engine_adapter.py app/tests/unit/test_gateway_input_validation_payload.py --tb=short` | `backend` | PASS, 59 passed, 6 deselected |
| `python -B -m pytest -q tests --tb=short` | `backend` | PASS, 1208 passed, 218 deselected |
| `python -B -c "from app.main import app; assert app.routes; assert app.openapi()['paths']; assert 'chart_json' not in str(app.openapi()) and 'natal_data' not in str(app.openapi())"` | `backend` | PASS |
| `rg -n "chart_json|natal_data|evidence_catalog|legacy|fallback|transition-condition" backend/app backend/tests` | repo root | PASS with classified residual hits |
| `git diff --check` | repo root | PASS |

## Commands skipped or blocked

- No provider call: explicitly out of scope.
- No frontend validation: no frontend file changed and story excludes frontend.

## DRY / No Legacy evidence

- No shim, alias, wrapper, fallback prompt carrier, or renamed old key was introduced.
- Old natal prompt carriers were deleted from the runtime DTO, adapter handoff, gateway natal payload assembly, prompt governance family and active natal seed prompts.
- Remaining `chart_json`/`natal_data` hits are non-natal/public chart projection, tests/guards, or historical/legacy surfaces outside the modern natal LLM prompt path.

## Diff review

- `git diff --stat` reviewed for story-scoped paths.
- `git diff --check`: PASS.
- No public API router, frontend, DB migration, provider policy, or dependency file changed.

## Final worktree status

- Final `git status --short` is recorded in chat/final handoff.
- Remaining dirty files are scoped to CS-336 implementation, tests, generated evidence, and story status.

## Remaining risks

- Residual historical seed scripts outside `backend/app/ops/llm` still mention old prompt text; they are outside the required final scan and not active in the modern natal bootstrap path reviewed here.

## Suggested reviewer focus

- Verify residual old-key classification around generic gateway legacy dict compatibility and non-natal event guidance remains outside modern natal prompt ownership.

## Feedback loop routing

- No propagation needed: the failed full-suite test was fixed by converting an obsolete acceptance test into a negative guard already covered by this story.
