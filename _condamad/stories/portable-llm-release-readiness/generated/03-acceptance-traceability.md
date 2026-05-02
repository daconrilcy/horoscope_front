# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le chemin local absolu est absent. | `scripts/llm-release-readiness.ps1` ne contient plus `C:\dev\horoscope_front`. | `rg -n "C:\\dev\\horoscope_front" scripts/llm-release-readiness.ps1` zero-hit. | Passed |
| AC2 | Le cache vient du repo root. | Le script calcule le cache par defaut via `$root`, expose `-PytestCachePath`, execute les tests backend depuis `backend/` et stoppe sur code natif non nul. | `pytest -q app/tests/unit/test_llm_release_readiness_script.py`. | Passed |
| AC3 | Les preuves release restent documentees. | Baseline, after-scan et note d'execution sont conserves dans la capsule. | `rg -n "readiness|pytest" _condamad/stories/portable-llm-release-readiness` retourne les preuves attendues. | Passed |
| AC4 | Les invariants LLM applicables restent gardes. | Aucun changement des prompts/providers LLM; `test_llm_release.py` isole ses versions de snapshots et `ReleaseService.build_snapshot()` precharge les relations serialisees. | Tests RG-016/RG-021/RG-022 et `pytest -q` backend passes dans l'evidence historique; le script complet echoue maintenant correctement tant que le rapport agrege est `no-go`. | Passed |
| AC5 | La story valide. | Capsule CONDAMAD complete et story source mise a jour uniquement sur status/tasks. | `condamad_story_validate.py` et `condamad_story_lint.py --strict` passent. | Passed |
| AC6 | Un rapport readiness `no-go` fait echouer le script. | `Assert-ReadinessReportGo` lit `llm-release-readiness.json` et leve une erreur si `decision != "go"`. | `pytest -q app/tests/unit/test_llm_release_readiness_script.py`. | Passed |
| AC7 | Les preconditions backend release necessaires au script sont repetables et couvertes. | `ReleaseService.build_snapshot()` precharge les relations serialisees; `test_llm_release.py` utilise des versions uniques; les registres ownership couvrent le script et le nouveau test. | `pytest -q tests/integration/test_llm_release.py` et `pytest -q app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py`. | Passed |
