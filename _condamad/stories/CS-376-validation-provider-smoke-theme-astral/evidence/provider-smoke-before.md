# Provider Smoke Before - CS-376

<!-- Commentaire global: cette preuve initiale capture l'absence du smoke provider avant implementation. -->

## Baseline

- `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py`: absent avant implementation.
- `backend/pyproject.toml`: aucun marker `provider_smoke` declare avant implementation.
- `RUN_THEME_ASTRAL_PROVIDER_SMOKE`: aucune logique runtime existante avant implementation.

## Commandes

- `Test-Path backend\tests\llm_orchestration\test_theme_astral_provider_smoke.py`: `False`.
- `rg -n "provider_smoke|RUN_THEME_ASTRAL_PROVIDER_SMOKE" backend\tests backend\pyproject.toml`: aucun match avant implementation.

## Invariant attendu

Le delta autorise uniquement une validation provider smoke non-production, opt-in, metadata-only et exclue des validations standard.
