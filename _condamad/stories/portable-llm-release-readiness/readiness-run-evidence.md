# Readiness Run Evidence

## Scope

La story modifie la resolution du cache pytest dans
`scripts/llm-release-readiness.ps1` et corrige les conditions necessaires pour
que le script release soit repetable localement: execution pytest depuis
`backend/`, propagation des codes de sortie natifs, chemins de tests actifs et
isolation des versions de snapshots release.

## PowerShell script validation

| Check | Result | Evidence |
|---|---|---|
| Parse PowerShell | PASS | `PSParser.Tokenize` sur `scripts/llm-release-readiness.ps1` retourne zero erreur. |
| Cache path contract | PASS | `pytest -q app/tests/unit/test_llm_release_readiness_script.py` verifie `-PytestCachePath`, `$root/.pytest_cache_runtime`, les trois options `cache_dir`, le cwd backend, l'arret sur code natif non nul et le rejet d'un rapport readiness `no-go`. |
| Forbidden local path | PASS | `rg -n "C:\\dev\\horoscope_front" scripts/llm-release-readiness.ps1` retourne zero hit. |

## Full script execution

| Command | Result | Evidence |
|---|---|---|
| `scripts\llm-release-readiness.ps1 -SkipStartupSmoke` avant garde `no-go` | HISTORICAL_PASS | Doc conformity, release lifecycle, golden/sensitive data, chaos, residual report, candidate snapshot and aggregate report completed, but la revue a identifie que le rapport pouvait rester `no-go`. |
| `scripts\llm-release-readiness.ps1` avant garde `no-go` | HISTORICAL_PASS | Same checks plus `startup_smoke_ok`; ce resultat n'est plus considere suffisant sans decision agregee `go`. |
| `scripts\llm-release-readiness.ps1 -SkipStartupSmoke` avec rapport agrege `no-go` | EXPECTED_FAIL | Les checks amont passent, puis l'etape `Readiness decision` echoue avec les blockers qualification, golden et smoke manquants; aucun `llm_release_readiness_ok` n'est affiche. |

Le premier run utilisateur avait revele que les echecs pytest etaient suivis de
faux `OK`. Le script echoue maintenant immediatement si une commande native
retourne un code non nul.

## Review fix evidence

La revue CONDAMAD a aussi releve que `build_llm_release_readiness_report.py`
retourne un code 0 meme lorsque l'artefact contient `decision: no-go`. Le script
lit maintenant `llm-release-readiness.json` apres generation et echoue avant
`llm_release_readiness_ok` si la decision agregee n'est pas `go`.

Les chemins `test_story_66_36_golden_regression.py` et
`test_story_66_43_provider_runtime_chaos.py` etaient des chemins obsoletes non
collectes; ils sont documentes comme remplaces par les chemins actifs
`test_llm_golden_regression.py` et `test_llm_provider_runtime_chaos.py`.

Le diff inclut aussi deux preconditions backend directement necessaires pour
que les tests release appeles par le script soient repetables: versions de
snapshots uniques dans `test_llm_release.py` et prechargement des relations deja
serialisees dans `ReleaseService.build_snapshot()`. Le nouveau test de garde du
script est enregistre dans l'ownership qualite/ops (`RG-015`).
