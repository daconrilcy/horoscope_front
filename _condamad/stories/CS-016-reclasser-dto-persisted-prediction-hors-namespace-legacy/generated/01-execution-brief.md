# Execution Brief — CS-016

## Primary objective

Finaliser la reclassification des DTO persisted prediction hors du namespace legacy `app.prediction`, avec owner canonique documente et garde anti-reintroduction.

## Boundaries

- Modifier uniquement les consommateurs directs des DTO persisted et les preuves CONDAMAD.
- Ne pas recreer `backend/app/prediction`.
- Ne pas ajouter de shim, alias, re-export ou fallback.
- Ne pas changer le schema SQL, les migrations Alembic ou le contrat API.

## Done when

- `persisted-dto-classification.md`, `persisted-dto-before.md` et `persisted-dto-after.md` sont remplis.
- Les repositories DB n'importent plus `app.prediction.persisted_*` ni `app.prediction.context`.
- Un guard pytest bloque la reintroduction des imports legacy depuis `app/infra/db/repositories`.
- Les tests persistence, relative scoring, API daily, guardrails et lint requis passent ou sont documentes.
