# No Legacy / DRY Guardrails

## Canonical behavior

- `scripts/llm-release-readiness.ps1` owns the release readiness orchestration.
- The pytest cache path default is repo-relative: `$root/.pytest_cache_runtime`.
- `-PytestCachePath` is the only allowed explicit override.
- The script reports `llm_release_readiness_ok` only after the aggregate
  readiness JSON decision is `go`.

## Forbidden patterns

- `C:\dev\horoscope_front` in `scripts/llm-release-readiness.ps1`.
- A hard-coded absolute `.pytest_cache_runtime` path.
- A second readiness script.
- Compatibility wrapper, alias, shim, or silent fallback to the old local path.
- Changes to LLM prompts/providers to make readiness pass.
- Printing a success marker when `llm-release-readiness.json` contains
  `decision: no-go`.

## Required negative evidence

- `rg -n "C:\\dev\\horoscope_front" scripts/llm-release-readiness.ps1`
- `pytest -q app/tests/unit/test_llm_release_readiness_script.py`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/llm-release-readiness.ps1 backend/app/tests/unit/test_llm_release_readiness_script.py`

## Allowed exception

| File | Symbol | Reason | Decision |
|---|---|---|---|
| `scripts/llm-release-readiness.ps1` | `-PytestCachePath` | Surcharge explicite du cache pytest pour execution locale/CI specifique. | Permanent, sans fallback implicite. |

## Applicable regression guardrails

- `RG-016`: les tests de narration LLM ne doivent pas redevenir consommateurs nominaux de `LLMNarrator`.
- `RG-021`: les preuves release LLM ne doivent pas contourner les tests de gouvernance prompts.
- `RG-022`: les chemins de validation LLM actifs doivent rester collectes.
- `RG-015`: le nouveau test de garde script doit rester reference dans le registre
  d'ownership qualite/ops.

## Review checklist

- Le chemin par defaut est derive de `$root`.
- Les trois appels pytest reutilisent la meme variable de cache.
- Le parametre `-PytestCachePath` est optionnel et explicite.
- Aucun chemin absolu local ne reste dans le script.
- Les chemins de tests obsoletes remplaces sont documentes comme chemins actifs
  collectes, sans changement de prompts/providers.
- Un rapport readiness `no-go` fait echouer le script.
- Les changements backend release restent limites a la repetabilite des tests et
  au prechargement de relations deja serialisees par les snapshots.
- Le nouveau test script est reference dans l'ownership backend qualite/ops.
