# No Legacy / DRY Guardrails

## Canonical behavior

- `PredictionComputeRunner` reste l'unique proprietaire du timeout de calcul prediction.
- La session DB appelante appartient au flux service/persistence appelant et ne doit pas etre capturee par le worker.

## Forbidden

- Closure worker utilisant `db` appelant.
- Appel `context_loader.load(db, ...)` depuis le thread worker.
- Nouveau test important directement base sur `SessionLocal` ou `engine`.
- Fallback silencieux apres timeout.
- Commentaire affirmant que la session reste non-thread-safe apres correction.

## Required evidence

- Test unitaire qui echoue si le contexte est charge dans le worker ou si la session appelante est consommee apres timeout.
- Scan cible du runner pour la documentation `contexte precharge` / `thread-safe`.
- Scan des tests pour `SessionLocal|engine`.

## Applicable regression guardrails

- `RG-011`: les tests DB doivent utiliser les fixtures/helpers canoniques, pas des imports directs `SessionLocal`/`engine`.
- `RG-031`: le calcul threade prediction ne doit pas partager la session SQLAlchemy appelante avec un worker survivant.
