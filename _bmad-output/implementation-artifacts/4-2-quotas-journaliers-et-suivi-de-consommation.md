# Story 4.2: Quotas journaliers et suivi de consommation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want voir mon quota restant et que le systeme applique mes limites,  
so that je comprends clairement mes droits d usage.

## Acceptance Criteria

1. Given un utilisateur avec plan actif, when il envoie des messages, then le quota journalier est decompte correctement a chaque message reussi.
2. Given un utilisateur ayant atteint sa limite journaliere, when il envoie un nouveau message, then l acces est bloque avec une erreur metier explicite et un message actionnable.
3. Given un utilisateur connecte, when il consulte son espace compte/chat, then le quota du jour (limite, consomme, restant, reset_at) est visible avec etats loading/error/empty.

## Tasks / Subtasks

- [x] Definir le modele de consommation journaliere (AC: 1, 2, 3)
  - [x] Ajouter le stockage du compteur quotidien par utilisateur (date de reference UTC, used_count, updated_at)
  - [x] Definir la regle de reset journalier (boundary UTC explicite) et la documenter
  - [x] Ajouter migration Alembic associee et contraintes d unicite (user_id + quota_date)
- [x] Implementer le service metier de quota (AC: 1, 2)
  - [x] Creer un service dedie (`get_quota_status`, `consume_quota_or_raise`) dans `backend/app/services/`
  - [x] Reutiliser le plan actif existant (`daily_message_limit`) sans dupliquer la logique abonnement de la story 4.1
  - [x] Gerer les erreurs metier stables (`quota_exceeded`, `no_active_subscription`, `invalid_quota_state`)
  - [x] Garantir l atomicite du decrement en cas de concurrence (transaction/locking SQL)
- [x] Integrer l enforcement quota dans le flux chat (AC: 1, 2)
  - [x] Brancher le controle quota avant traitement message dans router/service chat
  - [x] Ne decremeter le quota que sur message effectivement accepte
  - [x] Retourner 429 metier (`quota_exceeded`) avec details (`remaining`, `limit`, `reset_at`, `request_id`)
- [x] Exposer API de suivi consommation (AC: 3)
  - [x] Ajouter endpoint v1 dedie quota/consommation (`GET /v1/billing/quota` ou equivalent coherent API)
  - [x] Conserver enveloppes standards `{data, meta}` et `{error:{...}}`
  - [x] Proteger via JWT + RBAC `user` + rate limiting global + user + user/plan
- [x] Integrer affichage frontend quota (AC: 3)
  - [x] Ajouter client API quota dans `frontend/src/api/` avec gestion erreur unifiee
  - [x] Afficher limite/consomme/restant/reset dans zone compte/chat
  - [x] Ajouter blocage UI explicite quand quota atteint (message + prochain reset)
  - [x] Gerer `loading/error/empty` proprement
- [x] Ajouter observabilite et audit minimaux (AC: 1, 2, 3)
  - [x] Logger chaque tentative de consommation et chaque blocage quota avec `request_id`
  - [x] Ajouter metriques minimales (`quota_consumed_total`, `quota_exceeded_total`, latence endpoint quota)
  - [x] Tracer les erreurs de coherence quota (support/ops)
- [x] Tester et valider la story (AC: 1, 2, 3)
  - [x] Unit tests backend: reset journalier, decrement, concurrence, erreurs metier
  - [x] Integration tests API: 401/403, quota status, decrement progressif, blocage depassement
  - [x] Integration tests chat: message bloque quand quota atteint
  - [x] Frontend tests: affichage quota + etat limite atteinte + loading/error/empty
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story source: Epic 4 Story 4.2 (FR25, FR26) cible le controle d usage B2C apres activation abonnement.
- Cette story doit reutiliser les acquis de Story 4.1 (plan actif, RBAC `user`, request_id, rate limiting user/plan, conventions d erreurs).
- Ne pas implementer ici l upgrade/multi-plan (Story 4.3), uniquement enforcement quota du plan actif.

### Technical Requirements

- Conserver API v1 REST et schema d erreurs unifie en `snake_case`.
- Regle de quota: compteur journalier en UTC, deterministic, testable.
- Blocage strict au depassement: aucune consommation negative, aucun bypass.
- Enforcement cote backend obligatoire (le frontend ne doit jamais etre source de verite).
- Pas de duplication de logique abonnement: reutiliser `billing_service` existant pour retrouver le plan actif.

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Persistance PostgreSQL via SQLAlchemy + migration Alembic.
- Rate limiting a conserver (global + user + user/plan) sur les endpoints exposes.
- RBAC MVP: role `user` obligatoire pour endpoints quota utilisateur.
- Observabilite minimale: logs structures, metriques, erreurs.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic.
- DB: PostgreSQL cible (SQLite acceptable pour tests locaux).
- Auth: JWT access/refresh existant + controle role explicite.
- Frontend: React + TypeScript + TanStack Query + client API central.
- Tests: Pytest (backend) et Vitest + Testing Library (frontend).

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/services/` (nouveau service quota)
  - `backend/app/api/v1/routers/` (extension billing/chat)
  - `backend/app/infra/db/models/` (modele consommation quota)
  - `backend/migrations/versions/` (migration quota)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/` (quota client)
  - `frontend/src/components/` ou `frontend/src/pages/` (badge/panel quota)
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - decrement quota nominal
  - blocage quand remaining = 0
  - reset journalier UTC
  - robustesse en concurrence
- Integration:
  - protection JWT + RBAC user
  - endpoint quota status
  - chat bloque quand quota atteint
  - payload erreur quota stable et actionnable
- Frontend:
  - affichage limite/consomme/restant/reset
  - etat quota atteint visible
  - etats `loading/error/empty`

### Previous Story Intelligence

- Story 4.1 a etabli les patterns obligatoires a reutiliser:
  - `request_id` via header `X-Request-Id` avec fallback UUID
  - RBAC explicite `user` sur billing
  - rate limiting `global + user + user/plan`
  - format erreur stable `{error:{code,message,details,request_id}}`
- Reuse attendu des points d extension deja en place:
  - `backend/app/services/billing_service.py`
  - `backend/app/api/v1/routers/billing.py`
  - `backend/app/core/rate_limit.py`
  - `backend/app/core/request_id.py`

### Git Intelligence Summary

- Commits recents tres axes tests et robustesse flux billing: conserver une approche test-first avec deltas localises.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.2)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR25, FR26, FR28, NFR3, NFR12, NFR19)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (Core Architectural Decisions, API & Communication Patterns, Pattern Examples)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (MVP Scope Clarification, Journey 1, states loading/error/empty)
- Story precedente: `_bmad-output/implementation-artifacts/4-1-souscription-au-plan-payant-d-entree.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `create-story` workflow execution with epics/architecture/prd/ux analysis and sprint status sync.
- `.\\.venv\\Scripts\\Activate.ps1; ruff check backend`
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/app/tests/unit/test_quota_service.py backend/app/tests/integration/test_billing_api.py backend/app/tests/integration/test_chat_api.py`
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend`
- `npm run lint` (frontend)
- `npm test -- --run` (frontend)

### Completion Notes List

- Ajout du modele de consommation journaliere (`user_daily_quota_usages`) avec migration Alembic dediee.
- Implementation du service quota (`get_quota_status`, `consume_quota_or_raise`) avec reset UTC, atomicite et erreurs metier stables.
- Integration du quota dans le flux chat avec blocage explicite `quota_exceeded` en 429 et `request_id`.
- Ajout endpoint `GET /v1/billing/quota` protege JWT + RBAC `user` + rate limit global/user/user-plan.
- Integration frontend du suivi quota dans le chat (limite/consomme/restant/reset + etats + message limite atteinte).
- Observabilite ajoutee: logs quota avec `request_id`, compteurs `quota_consumed_total`, `quota_exceeded_total`, erreurs d etat quota.
- Tests backend/frontend ajoutes ou etendus, suite complete validee.
- Corrections post code-review appliquees: blocage UI strict quand quota atteint, gestion concurrence a la creation du compteur journalier, propagation `request_id` sur endpoints chat list/history, documentation `429` sur POST chat message, tests d integration quota/chat renforces.
- Story marquee `done`.

### File List

- _bmad-output/implementation-artifacts/4-2-quotas-journaliers-et-suivi-de-consommation.md
- backend/app/api/v1/routers/billing.py
- backend/app/api/v1/routers/chat.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/billing.py
- backend/app/services/quota_service.py
- backend/app/tests/integration/test_billing_api.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/unit/test_quota_service.py
- backend/migrations/env.py
- backend/migrations/versions/20260219_0007_add_user_daily_quota_usages.py
- frontend/src/api/billing.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-19: Story 4.2 implementation complete (quota model/service/API, enforcement chat, UI quota, tests).
- 2026-02-19: Corrections code-review completees (high/medium): blocage quota UI, robustesse concurrence quota, OpenAPI 429, propagation request_id, couverture tests integration et frontend.
