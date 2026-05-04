# Execution Brief - CS-012

## Story key

`CS-012-ajouter-garde-anti-croissance-app-prediction`

## Primary objective

Ajouter une garde d'architecture collectee par pytest qui bloque la croissance non classee
de `backend/app/prediction` et les imports interdits sous ce namespace.

## Boundaries

- Modifier uniquement le test de garde prediction et les artefacts CONDAMAD de CS-012.
- Ne pas modifier le code applicatif `backend/app/prediction`.
- Ne pas ajouter de dependance.
- Ne pas creer de nouveau dossier racine backend.

## Non-goals

- Pas de migration de fichiers prediction.
- Pas de refactor DB, LLM ou API.
- Pas d'exception dossier-wide.
- Pas de garde grep-only comme preuve principale.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Relever `git status --short`.
- Inspecter `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- Inspecter `backend/app/prediction`.

## Done conditions

- L'allowlist persistante existe et couvre exactement les fichiers Python actuels.
- Le test AST echoue en cas de nouveau fichier non allowliste.
- Le test AST echoue en cas d'import interdit.
- Les exceptions d'import sont documentees avec condition de sortie, ou explicitement absentes.
- Les guards LLM existants restent passants.
- Les preuves finales et le registre story-status sont synchronises.
