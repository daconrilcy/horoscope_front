# Validation Plan

## Targeted backend checks

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend\tests\integration\test_theme_natal_bigbang_replay.py backend\tests\integration\test_theme_natal_concurrency.py backend\tests\integration\test_theme_natal_entitlement_freshness.py backend\tests\integration\test_theme_natal_public_reads.py backend\tests\llm_orchestration\test_llm_legacy_extinction.py backend\tests\unit\test_natal_chart_long_quota_on_acceptance.py
ruff check backend
python -B -m pytest -q backend\tests\integration\test_theme_natal_bigbang_replay.py backend\tests\integration\test_theme_natal_concurrency.py backend\tests\integration\test_theme_natal_entitlement_freshness.py backend\tests\integration\test_theme_natal_public_reads.py backend\tests\llm_orchestration\test_llm_legacy_extinction.py backend\tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short
python -B -m pytest -q backend\tests\integration backend\tests\llm_orchestration -k "theme_natal or basic_full_reading or concurrency or entitlement" --tb=short
python -B -m pytest -q backend\tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short
```

## Frontend checks

```powershell
pnpm --dir frontend test -- natalInterpretation NatalChartPage natalPublicDomGuard
pnpm --dir frontend lint
```

## Runtime API proof

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from backend.app.main import app; assert app.routes"
python -B -c "from backend.app.main import app; assert app.openapi().get('paths')"
```

## Scan checks

```powershell
rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation" backend/app backend/tests frontend/src
rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh" frontend/src backend/app
rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|EXIGENCE PREMIUM|AstroResponse_v3" backend/app backend/tests
rg -n "ThemeNatalReadingProductContract|LLMGenerationContract|basic_full_reading|generation_contract_hash" backend/app backend/tests frontend/src _condamad/stories/regression-guardrails.md
```

## Artifact checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; base=Path(r'_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence'); required=['replay-free-basic-generate-full.md','concurrency-proof.md','entitlement-freshness-proof.md','public-get-list-accepted-only.md','legacy-scan-results.md','openapi-before.json','openapi-after.json','validation-output.txt']; missing=[name for name in required if not (base/name).exists()]; assert not missing, missing"
```

## Rule for skipped commands

No required validation command was skipped in the implementation run.
