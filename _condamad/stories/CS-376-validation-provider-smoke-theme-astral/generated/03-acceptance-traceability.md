# Acceptance Traceability - CS-376

<!-- Commentaire global: cette trace relie chaque critere d'acceptation CS-376 au code et aux validations locales. -->

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The smoke is disabled by default. | `test_missing_provider_smoke_opt_in_keeps_runtime_disabled` verifies `RUN_THEME_ASTRAL_PROVIDER_SMOKE` absent disables execution. | `python -B -m pytest -q tests\llm_orchestration\test_theme_astral_provider_smoke.py --tb=short`: `3 passed, 1 skipped`. | PASS |
| AC2 | Missing opt-in causes a clean skip. | `test_theme_astral_provider_smoke_validates_response_contract` calls `_skip_without_provider_smoke_prerequisites`. | `python -B -m pytest -q tests\llm_orchestration\test_theme_astral_provider_smoke.py -m provider_smoke --tb=short`: `1 skipped, 3 deselected`. | PASS |
| AC3 | Provider opt-in performs one call. | `RecordingProviderClient` proves `_call_theme_astral_provider_once` emits one call with timeout and response schema. | `test_opt_in_provider_path_performs_one_contractual_call`: included in targeted pytest, one recorded call. | PASS |
| AC4 | The response contract is validated. | `_schema_errors` uses canonical `THEME_ASTRAL_RESPONSE_SCHEMA`; no duplicated schema. | Targeted pytest validates compliant document; provider smoke path validates real provider output when opt-in is active. | PASS |
| AC5 | Secrets are not logged. | `_safe_metadata` excludes raw output/messages and changed smoke evidence has no credential/header markers. | `rg -n "OPENAI_API_KEY|api_key|Authorization" backend\tests\llm_orchestration\test_theme_astral_provider_smoke.py _condamad\stories\CS-376-validation-provider-smoke-theme-astral\evidence`: `PASS: no secret marker matches`. | PASS |
| AC6 | The marker is registered. | `backend/pyproject.toml` declares `provider_smoke`. | `rg -n "provider_smoke|RUN_THEME_ASTRAL_PROVIDER_SMOKE|OPENAI_API_KEY" tests pyproject.toml`: marker and env gate found. | PASS |
| AC7 | Standard tests exclude the smoke. | Provider smoke test is marked with `@pytest.mark.provider_smoke`; standard command excludes it. | `python -B -m pytest -q tests --tb=short -m "not provider_smoke"`: `1239 passed, 235 deselected`. | PASS |
| AC8 | Smoke proof is persisted. | `evidence/provider-smoke-before.md` and `evidence/provider-smoke-after.md` document before/after metadata-only proof. | Repository-root artifact check after venv activation: `provider-smoke-after.md` exists. | PASS |
