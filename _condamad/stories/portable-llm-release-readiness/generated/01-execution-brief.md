# Execution Brief

## Story key

`portable-llm-release-readiness`

## Objective

Rendre `scripts/llm-release-readiness.ps1` portable en remplacant le cache pytest absolu par un chemin derive du repo root, avec surcharge explicite `-PytestCachePath`.

## Boundaries

- Modifier uniquement le script readiness LLM, les tests de garde lies au script et les preuves CONDAMAD de cette story.
- Conserver les artefacts de sortie release existants.
- Ne pas changer les tests LLM executes, les criteres de release, les prompts, les providers ou les contrats API.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer le baseline `rg -n "C:\\dev\\horoscope_front|pytest_cache_runtime|PytestCache" scripts/llm-release-readiness.ps1`.

## Write rules

- Aucun fallback vers `C:\dev\horoscope_front`.
- Aucun nouveau script readiness.
- Aucun changement de dependance.
- Les commandes Python doivent etre lancees apres activation `.\\.venv\\Scripts\\Activate.ps1`.

## Done conditions

- Le script ne contient plus le chemin absolu local.
- Le cache par defaut est repo-relative.
- `-PytestCachePath` permet une surcharge explicite.
- Les tests et scans demandes passent ou sont documentes avec limitation.
- `generated/10-final-evidence.md` est complete.

## Halt conditions

- Le script depend d'un job externe imposant le chemin absolu local.
- Les validations ciblees echouent sans correctif sur dans le scope.
- Une modification hors scope serait necessaire pour satisfaire les AC.
