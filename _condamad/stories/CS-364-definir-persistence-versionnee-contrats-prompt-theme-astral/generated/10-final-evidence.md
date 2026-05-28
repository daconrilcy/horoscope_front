# Final Evidence — CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: `_condamad/run-state.json` untracked
- Pre-existing dirty files: `_condamad/run-state.json`
- AGENTS.md files considered: root `AGENTS.md` from prompt/context
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | validated | |
| `generated/01-execution-brief.md` | yes | yes | validated | |
| `generated/03-acceptance-traceability.md` | yes | yes | validated | |
| `generated/04-target-files.md` | yes | yes | validated | |
| `generated/06-validation-plan.md` | yes | yes | validated | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | validated | |
| `generated/10-final-evidence.md` | yes | yes | validated | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Stable identifiers persisted through canonical domain constants, use case, prompt, schema, seed, and manifest. | Targeted persistence tests PASS. | PASS | |
| AC2 | Active resolver reads one published assembly family by depth. | Active-read test PASS. | PASS | |
| AC3 | Prompt template lives in `llm_prompt_versions` through seed. | Targeted tests and owner scans PASS. | PASS | |
| AC4 | Delivery profile uses non-commercial depths and omits plan labels from prompt/read model. | Negative assertions PASS; scan hits only assertions. | PASS | |
| AC5 | Persona-backed `astrologer_voice` is style-only. | Persistence and readback tests PASS. | PASS | |
| AC6 | Seed updates canonical rows and avoids duplicate active prompt/profile/assembly rows. | Idempotency test PASS. | PASS | |
| AC7 | Unsupported depth or incompatible schema raises explicit `ValueError`. | Invalid-combination test PASS. | PASS | |
| AC8 | Existing LLM ORM tables match the required persistence surface. | Migration metadata test PASS. | PASS | No migration added. |
| AC9 | No parallel contract table/model/registry introduced. | Negative `rg` scan PASS no matches. | PASS | |
| AC10 | Baseline, manifest, traceability, dev log, and final evidence persisted. | Capsule validation PASS. | PASS | |

## Files changed

- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/app/main.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_migration.py`
- `backend/tests/unit/test_canonical_llm_bootstrap.py`
- `_condamad/stories/CS-364-definir-persistence-versionnee-contrats-prompt-theme-astral/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`.
- Added `backend/tests/integration/test_theme_astral_prompt_contract_migration.py`.
- Updated `backend/tests/unit/test_canonical_llm_bootstrap.py`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `ruff format <modified python files>` | `backend` | PASS | 0 | Scoped Python formatting. |
| `ruff check <modified python/tests>` | `backend` | PASS | 0 | Targeted lint before tests. |
| `python -B -m pytest -q tests\integration\test_theme_astral_prompt_contract_persistence.py tests\integration\test_theme_astral_prompt_contract_migration.py tests\unit\test_canonical_llm_bootstrap.py --tb=short` | `backend` | PASS | 0 | 6 passed, 5 deselected. |
| `python -B -m pytest -q tests\llm_orchestration\test_prompt_governance_registry.py tests\integration\test_theme_astral_prompt_contract_persistence.py tests\integration\test_theme_astral_prompt_contract_migration.py --tb=short` | `backend` | PASS | 0 | 31 passed, 5 deselected. |
| `ruff check .` | `backend` | PASS | 0 | Full backend lint. |
| `python -B -m pytest -q tests --tb=short` | `backend` | PASS | 0 | 1217 passed, 227 deselected. |
| `python -B -c "from app.main import app; print(app.title)"` | `backend` | PASS | 0 | App imports and exposes `horoscope-backend`. |
| `rg -n "theme_astral_prompt_contracts|llm_theme_astral_contracts|class .*ThemeAstral.*Model|__tablename__\s*=\s*['\"]theme_astral" backend\app backend\tests -g "*.py"` | repo root | PASS | 1 | No matches; no parallel registry/table/model. |
| `condamad_validate.py <capsule>` | repo root | PASS | 0 | Capsule structure valid. |

## Commands skipped or blocked

- none

## DRY / No Legacy evidence

- Reused existing LLM registry tables and canonical governance registry.
- No new backend root folder, provider call, gateway change, frontend change, compatibility shim, alias, or fallback.
- No migration added because existing ORM metadata covers the required contract family.
- Plan-name scan: `free/basic/premium` hits only negative test assertions in the CS-364 test file.

## Diff review

- `git diff --stat`: scoped diff reviewed.
- `git diff --check`: PASS.

## Final worktree status

- Modified: backend LLM configuration/bootstrap/governance, targeted tests, story evidence/status.
- Pre-existing untracked: `_condamad/run-state.json`.

## Remaining risks

- none

## Suggested reviewer focus

- Verify the `theme_astral` governance family and delivery depth names (`essential`, `deep`) match the intended product vocabulary before downstream CS-365/CS-366 consume them.
