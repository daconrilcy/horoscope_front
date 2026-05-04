# Execution brief - CS-018

## Story key

`CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction`

## Primary objective

Remplacer la garde temporaire anti-croissance CS-012 par une garde finale
d'extinction: aucun fichier sous `backend/app/prediction` et aucun import actif
`app.prediction` dans le runtime ou les tests collectes.

## Boundaries

- Modifier uniquement la garde architecture prediction et les preuves CONDAMAD.
- Ne pas migrer le moteur, les DTO, les routeurs ou les contrats API.
- Ne pas ajouter de dependance.
- Ne pas recreer de namespace, shim, alias, fallback ou re-export legacy.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Lire `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- Capturer l'etat initial du worktree avec `git status --short`.

## Write rules

- Garder `backend/app/tests/unit/test_daily_prediction_guardrails.py` comme garde canonique.
- Les references `app.prediction` admises doivent rester historiques et hors runtime/tests collectes.
- Persister `guard-before.md`, `guard-after.md` et les preuves finales.

## Done conditions

- AC1 a AC5 ont une preuve de code et une preuve de validation.
- Les scans `rg` cibles sont zero-hit ou classes.
- Les tests et lint requis passent apres activation du venv.
- `_condamad/stories/story-status.md` indique `ready-to-review`.

## Halt conditions

- Un fichier runtime doit rester sous `backend/app/prediction`.
- Un test collecte doit rester consommateur nominal de `app.prediction`.
- Une validation obligatoire echoue sans correctif sur.
