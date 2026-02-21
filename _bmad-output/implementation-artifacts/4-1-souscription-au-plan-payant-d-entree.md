# Story 4.1: Souscription au plan payant d entree

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want souscrire au plan payant de base,  
so that je peux acceder au service astrologique selon mon abonnement.

## Acceptance Criteria

1. Given un utilisateur authentifie sans abonnement actif, when il souscrit au plan d entree, then son statut d abonnement devient actif.
2. Given un abonnement actif, when l utilisateur consulte son espace compte, then le plan actif est visible avec ses informations essentielles.
3. Given un echec de paiement, when la souscription echoue, then l abonnement reste inactif avec un motif clair et une possibilite immediate de reessayer.

## Tasks / Subtasks

- [x] Definir le modele de souscription MVP et les regles d etat (AC: 1, 2, 3)
  - [x] Ajouter/adapter les modeles DB pour plan, abonnement, et tentative de paiement (`inactive`, `pending`, `active`, `failed`)
  - [x] Ajouter les migrations Alembic associees
  - [x] Initialiser le plan d entree MVP (Basic 5 EUR/mois) via seed controle
- [x] Implementer le service backend de souscription (AC: 1, 3)
  - [x] Creer un service applicatif dedie (`create_checkout`, `confirm_payment`, `retry_payment`, `get_subscription_status`)
  - [x] Gerer idempotence et transitions d etat atomiques pour eviter doubles activations
  - [x] Retourner des erreurs metier stables (`payment_failed`, `subscription_already_active`, `invalid_plan`, etc.)
- [x] Exposer API REST v1 pour la souscription utilisateur (AC: 1, 2, 3)
  - [x] Ajouter endpoints versionnes `/v1/billing/*` avec enveloppes standards `{data, meta}` et `{error:{...}}`
  - [x] Proteger endpoints via JWT (`user`) et appliquer rate limiting global + par user/plan
  - [x] Inclure endpoint de consultation de statut abonnement pour l espace compte
- [x] Integrer le flux frontend de souscription (AC: 1, 2, 3)
  - [x] Ajouter client API billing centralise (`frontend/src/api`)
  - [x] Ajouter ecran/composant de souscription dans espace compte avec etats `loading/error/empty`
  - [x] Afficher clairement le motif d echec et un CTA `Reessayer` immediat
- [x] Ajouter observabilite et audit minimaux (AC: 1, 3)
  - [x] Journaliser tentative, succes, echec et retry de paiement avec `request_id`
  - [x] Exposer metriques minimales (taux succes/echec, latence endpoint souscription)
  - [x] Tracer les changements d etat d abonnement pour support/ops
- [x] Tester et valider la story (AC: 1, 2, 3)
  - [x] Tests unitaires backend: transitions d etat, idempotence, erreurs paiement, retry
  - [x] Tests integration API: auth 401/403, souscription succes, echec paiement, retry, consultation statut
  - [x] Tests frontend: parcours souscription, affichage plan actif, gestion echec et relance
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story source: Epic 4 Story 4.1 cible la monetisation MVP B2C avec un seul plan d entree.
- Contraintes produit: premiere valeur avant paywall, puis souscription simple et explicite.
- Cette story ne doit pas implementer l upgrade multi-niveaux (Story 4.3) ni la logique complete de quotas (Story 4.2), mais doit preparer leurs points d extension.

### Technical Requirements

- Conserver API v1 REST avec contrats d erreurs unifies et `snake_case`.
- Assurer coherences transactionnelles des etats d abonnement (pas de double activation en concurrence).
- En cas d echec paiement, ne jamais activer l abonnement et fournir un motif actionnable cote UI.
- Garder la logique metier de souscription dans `services`, pas dans routers ni composants UI.
- Prevoir idempotence sur creation de session/confirmation de paiement.

### Architecture Compliance

- Respecter `api -> services -> domain -> infra`.
- Persistance principale PostgreSQL via SQLAlchemy + migrations Alembic.
- Rate limiting global + par user/plan conforme aux contraintes architecture.
- Observabilite minimale obligatoire: logs structures + metriques + erreurs.
- RBAC MVP: role `user` pour souscription utilisateur (support/ops hors scope de cette story).

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic.
- DB: PostgreSQL (SQLite local acceptable pour tests).
- Auth: JWT access/refresh existant.
- Frontend: React + TypeScript + client API central + TanStack Query.
- Formulaires frontend: React Hook Form + Zod (si nouveau formulaire dedie).

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/api/v1/routers/` (nouveau routeur billing ou extension routeur users)
  - `backend/app/services/` (service de souscription et erreurs metier)
  - `backend/app/infra/db/models/` (plan, subscription, payment_attempt)
  - `backend/migrations/versions/` (migration Alembic)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/` (client billing)
  - `frontend/src/components/` ou `frontend/src/pages/` (ecran compte/souscription)
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - transitions d etat `inactive/pending/active/failed`
  - idempotence des operations sensibles
  - erreurs metier stables et explicites
- Integration:
  - endpoints billing proteges JWT
  - activation abonnement apres succes
  - echec paiement sans activation + retry possible
  - consultation du plan actif dans espace compte
- Frontend:
  - etats `loading/error/empty`
  - message d echec paiement comprehensible
  - action de relance immediate

### Previous Story Intelligence

- Reutiliser les patterns etablis sur Epic 3: contrats API stables, RBAC strict, logs structures et validations metier explicites.
- Eviter tout contournement des conventions de couches et des enveloppes d erreur deja en place.

### Git Intelligence Summary

- Commits recents axes sur robustesse test et flux billing historiques; privilegier des deltas localises, test-first, sans regression.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.1)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR24, FR12, FR28, NFR3, NFR5, NFR12)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (Core Architectural Decisions, API & Communication Patterns, Data Architecture)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (MVP vs Post-MVP Scope Clarification, Journey 1)
- Story precedente: `_bmad-output/implementation-artifacts/3-7-parametrage-des-bornes-de-persona-astrologue.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `.\\.venv\\Scripts\\Activate.ps1; ruff check backend --fix`
- `.\\.venv\\Scripts\\Activate.ps1; ruff check backend`
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend`
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/app/tests/integration/test_billing_api.py backend/app/tests/unit/test_billing_service.py backend/app/tests/unit/test_rate_limit.py`
- `npm run lint` (frontend)
- `npm test -- --run` (frontend)

### Completion Notes List

- Tables billing ajoutees (plans, subscriptions, payment_attempts) avec migration Alembic dediee.
- Service de souscription MVP implemente avec idempotence, gestion d etats et erreurs metier stables.
- API REST v1 `/v1/billing/*` ajoutee avec JWT, rate limiting et endpoint de statut.
- Renforcement RBAC: endpoints billing limites strictement au role `user`.
- Rate limiting complete: global + user + user/plan.
- Propagation de `request_id` via `X-Request-Id` (fallback UUID), reponses API et logs billing.
- `retry_after` calcule dynamiquement dans le controleur de limite de debit.
- Flux frontend de souscription integre avec affichage des erreurs et retry immediat.
- Observabilite minimale ajoutee: logs structurés applicatifs + metriques en memoire.
- Tests backend et frontend ajoutes/mis a jour (incluant cas 403/429 + retry_after), lint/tests valides.
- Story marquee `done`.

### File List

- _bmad-output/implementation-artifacts/4-1-souscription-au-plan-payant-d-entree.md
- backend/app/api/v1/routers/billing.py
- backend/app/api/v1/routers/__init__.py
- backend/app/core/rate_limit.py
- backend/app/core/request_id.py
- backend/app/infra/db/models/billing.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/observability/metrics.py
- backend/app/main.py
- backend/app/services/billing_service.py
- backend/app/tests/integration/test_billing_api.py
- backend/app/tests/unit/test_billing_service.py
- backend/app/tests/unit/test_rate_limit.py
- backend/migrations/env.py
- backend/migrations/versions/20260219_0006_add_billing_tables.py
- frontend/src/App.tsx
- frontend/src/api/billing.ts
- frontend/src/components/BillingPanel.tsx
- frontend/src/tests/BillingPanel.test.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Senior Developer Review (AI)

### Reviewer

GPT-5 Codex

### Date

2026-02-19

### Outcome

Approved after fixes

### Findings Addressed

- [HIGH] RBAC billing non strict -> corrige avec controle explicite role `user` sur tous les endpoints billing.
- [HIGH] Rate limiting incomplet (pas de dimension plan) -> corrige avec cle `billing:user_plan:{user_id}:{plan_code}:{operation}`.
- [HIGH] `request_id` non trace (`n/a`) -> corrige avec resolution depuis header `X-Request-Id` ou UUID genere, injecte dans reponses et logs billing.
- [MEDIUM] `retry_after` hardcode -> corrige avec calcul dynamique selon la fenetre restante.
- [MEDIUM] Couverture tests insuffisante (403/429) -> corrige avec tests integration dedies.
- [MEDIUM] Couverture tests rate-limit detail -> corrige avec test unitaire sur `retry_after`.

## Change Log

- 2026-02-19: Dev implementation complete for Story 4.1 (billing MVP).
- 2026-02-19: Code review issues fixed (RBAC, request_id, rate-limit user/plan, retry_after dynamique, tests complements).
