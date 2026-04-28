# Execution Brief

## Story key

`reduce-api-sql-boundary-debt-public-email`

## Primary objective

Extraire la persistance du désabonnement public email hors du routeur `backend/app/api/v1/routers/public/email.py`, sans modifier la route runtime `GET /api/email/unsubscribe`.

## Boundaries

- Modifier uniquement le flux `unsubscribe` et les preuves liées.
- Utiliser `backend/app/services/email/**` comme propriétaire applicatif de la persistance.
- Préserver le contrat HTTP observable: route, paramètre `token`, statuts, messages et en-têtes no-store.
- Supprimer de `router-sql-allowlist.md` uniquement les lignes devenues stale pour `app/api/v1/routers/public/email.py`.
- Ne pas modifier le frontend, les migrations, les modèles SQLAlchemy ou `route_exceptions.py`.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer les snapshots OpenAPI et SQL avant changement.

## Write rules

- Aucun wrapper, alias, fallback, re-export ou second endpoint.
- Aucun nouvel import `app.api` depuis les services.
- Aucun SQL/session direct dans `backend/app/api/v1/routers/public/email.py`.
- Pas de nouvelle dépendance.

## Done conditions

- Tous les AC ont evidence code et validation.
- Les tests d’intégration unsubscribe et les guards d’architecture API passent.
- `ruff format .`, `ruff check .` et les scans ciblés passent.
- Les preuves `openapi-*`, `router-sql-public-email-*` et `allowlist-diff.md` sont persistées.

## Halt conditions

- Le comportement public doit changer pour terminer l’extraction.
- Une dette SQL doit rester dans `public/email.py`.
- Les validations ciblées échouent sans correction sûre dans le scope.
