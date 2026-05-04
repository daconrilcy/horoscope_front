# Execution Brief

## Story key

`CS-011-supprimer-partage-session-db-calcul-threade-prediction`

## Objectif

Supprimer le partage de session SQLAlchemy appelante dans le calcul prediction execute avec timeout.

## Bornes

- Modifier uniquement le runner de calcul prediction, les tests cibles et les preuves CONDAMAD.
- Conserver l'erreur controlee de timeout existante.
- Ne pas ajouter de dependance, queue externe, pool applicatif ou fallback silencieux.

## Preflight

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Relever `git status --short`.
- Inspecter `compute_runner.py`, `context_loader.py`, `service.py` et les tests daily prediction.

## Regles d'ecriture

- Le worker ne doit pas fermer sur `db`.
- Le contexte prediction doit etre charge avant la soumission au thread, ou le worker doit utiliser une session dediee explicite.
- Les commentaires et docstrings applicatifs ajoutes ou modifies sont en francais.

## Done

- AC1 a AC4 prouves par tests, scans et preuves avant/apres.
- `generated/10-final-evidence.md` et `story-status.md` synchronises en `ready-to-review`.

## Halt

- Stopper si la correction exige de supprimer le timeout par thread ou d'introduire une nouvelle dependance.
