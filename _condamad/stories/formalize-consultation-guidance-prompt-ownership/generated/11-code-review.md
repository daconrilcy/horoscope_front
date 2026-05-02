# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md`
- Review date: 2026-05-02
- Scope: current worktree diff after consultation ownership implementation, residual-risk migration, DB-test helper refactor, and story closure.

## Inputs reviewed

- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md`
- Generated capsule artifacts through `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `docs/llm-prompt-generation-by-feature.md`
- `backend/scripts/seed_consultation_templates.py`
- `backend/migrations/versions/20260502_0084_normalize_consultation_template_objectives.py`
- `backend/app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py`
- `backend/app/tests/helpers/db_session.py`
- `backend/app/tests/unit/test_consultation_generation_service.py`
- `backend/app/tests/unit/test_guidance_service.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- Runtime/config files named by the story for consultation and guidance ownership.

## Diff summary

- Consultation-specific prompts are documented as a `guidance_contextual` subcase.
- Consultation seed `prompt_content` values are short product objectives, not provider instructions.
- Migration `20260502_0084` normalizes existing canonical consultation template rows.
- The migration test covers an already-seeded DB with legacy prompt-like text and uses the canonical DB helper `build_sqlite_test_engine`.
- Guidance, consultation, governance, migration, and DB harness tests cover the acceptance and regression surfaces.
- `backend/horoscope.db` was restored before commit; the migration remains the source of truth for DB changes.

## Review layers

- Diff integrity: reviewed tracked and untracked story files, including migration, helper, tests, docs, capsule, and DB snapshot status.
- Acceptance audit: AC1-AC4 mapped to docs, tests, migration, and scans.
- Validation audit: reviewer reran targeted tests, DB harness guard, lint, format check, Alembic head check, scans, capsule validation, and full backend pytest.
- DRY / No Legacy audit: no new consultation family, `consultation_contextual` runtime use case, prompt fallback, wrapper, alias, or `developer_prompt` mapping found.
- Regression guardrails: `RG-004`, `RG-006`, `RG-011`, and `RG-020` are covered by executable checks or targeted scans.

## Findings

No actionable findings.

## Acceptance audit

- AC1: PASS. Documentation, seed data, and migration all classify consultation `prompt_content` as short product objective data under `guidance_contextual`.
- AC2: PASS. Guidance placeholder test verifies `situation`, `objective`, `time_horizon`, `natal_chart_summary`, and `guidance_contextual`.
- AC3: PASS. Consultation precheck refusal test verifies no `GuidanceService.request_contextual_guidance_async` call.
- AC4: PASS. Governance test rejects `consultation` family drift and `consultation_contextual`.

## Validation audit

- PASS: `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_consultation_generation_service.py app/tests/unit/test_guidance_service.py tests/llm_orchestration/test_prompt_governance_registry.py` -> 52 passed.
- PASS: `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`.
- PASS: `.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .`.
- PASS: `.\.venv\Scripts\Activate.ps1; cd backend; alembic heads` -> `20260502_0084 (head)`.
- PASS: targeted reintroduction scan over `backend\app\domain backend\app\services backend\tests`; hits are classified guard/fallback references only.
- PASS: runtime/config scan for `consultation_contextual|"consultation"` over consultation ownership files returned zero hits.
- PASS: `RG-004`/`RG-006` scans for service/domain `app.api` imports and local HTTP error handling returned zero hits.
- PASS: `git diff --check` with CRLF warnings only.
- PASS: `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` -> 3503 passed, 12 skipped.

## DRY / No Legacy audit

- No duplicate consultation prompt family or runtime use case was introduced.
- No `PROMPT_FALLBACK_CONFIGS["consultation"]` or equivalent consultation fallback was introduced.
- No `developer_prompt.*prompt_content` mapping exists in the scanned surfaces.
- The seed and migration both contain the canonical objective strings intentionally: the seed is current-state data, and the migration is a frozen historical data correction.
- The migration test no longer owns an unclassified SQLite factory; the engine creation is centralized in the canonical DB test helper.

## Commands run by reviewer

```powershell
git status --short
git diff --stat
Get-Content -Raw .agents\skills\condamad-code-review\SKILL.md
Get-Content -Raw .agents\skills\condamad-code-review\workflow.md
Get-Content -Raw .agents\skills\condamad-code-review\references\review-doctrine.md
Get-Content -Raw .agents\skills\condamad-code-review\references\finding-taxonomy.md
Get-Content -Raw .agents\skills\condamad-code-review\references\codex-modern-review-guidance.md
Get-Content -Raw .agents\skills\condamad-regression-guardrails\SKILL.md
Get-Content -Raw _condamad\stories\regression-guardrails.md
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_migration_20260502_0084_consultation_template_objectives.py app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_consultation_generation_service.py app/tests/unit/test_guidance_service.py tests/llm_orchestration/test_prompt_governance_registry.py
.\.venv\Scripts\Activate.ps1; cd backend; ruff check .
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .
.\.venv\Scripts\Activate.ps1; cd backend; alembic heads
rg -n '"consultation"|consultation_contextual|developer_prompt.*prompt_content|PROMPT_FALLBACK_CONFIGS' backend\app\domain backend\app\services backend\tests
rg -n 'consultation_contextual|"consultation"' backend/app/domain/llm/governance/data/prompt_governance_registry.json backend/app/domain/llm/configuration/canonical_use_case_registry.py backend/scripts/seed_consultation_templates.py backend/migrations/versions/20260502_0084_normalize_consultation_template_objectives.py backend/app/services/llm_generation/consultation_generation_service.py backend/app/services/llm_generation/guidance/guidance_service.py
rg -n "from app\.api|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core
rg -n "HTTPException|JSONResponse|def _error_response|api_error_response" backend/app/services/llm_generation backend/app/services/consultation backend/app/domain/llm backend/app/api/v1/routers/public/consultations.py
git diff --check
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q
```

## Residual risks

- None identified after reverting the local SQLite snapshot from commit scope.

## Verdict

CLEAN
