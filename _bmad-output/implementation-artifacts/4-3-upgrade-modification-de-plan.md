# Story 4.3: Upgrade/modification de plan

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want modifier mon abonnement quand des niveaux supplementaires sont disponibles,  
so that mon offre correspond a mon usage reel.

## Acceptance Criteria

1. Given un utilisateur avec plan actif, when il demande un changement de plan vers un plan valide, then le nouveau plan est applique selon les regles de facturation definies et l etat de souscription reste coherent.
2. Given un changement de plan applique, when l utilisateur consulte son espace compte et son quota, then le plan actif et les nouvelles limites d usage sont visibles sans ambiguite.
3. Given un changement impossible (plan invalide, statut incompatible, tentative dupliquee), when la requete est soumise, then l API retourne une erreur metier stable et actionnable.

## Tasks / Subtasks

- [x] Definir les regles metier de changement de plan (AC: 1, 3)
  - [x] Formaliser strategie MVP de transition: upgrade immediat, downgrade a effet controle, sans etat incoherent
  - [x] Definir et documenter les erreurs metier stables (`invalid_target_plan`, `plan_change_not_allowed`, `duplicate_plan_change`, `no_active_subscription`)
  - [x] Clarifier l impact quota journalier du plan cible (application immediate ou au prochain reset UTC)
- [x] Etendre le modele billing pour les changements de plan (AC: 1, 3)
  - [x] Ajouter une trace de changement de plan (historique minimal et idempotence)
  - [x] Ajouter migration Alembic associee (contraintes d unicite/index pour eviter doublons)
  - [x] Conserver compatibilite avec les modeles et seeds existants (Story 4.1)
- [x] Implementer le service backend de plan change (AC: 1, 3)
  - [x] Ajouter une methode dediee dans `BillingService` (ex: `change_subscription_plan`)
  - [x] Garantir transition atomique DB (pas de double bascule en concurrence)
  - [x] Reutiliser `request_id`, observabilite et conventions erreurs deja en place
- [x] Exposer API REST v1 de changement de plan (AC: 1, 2, 3)
  - [x] Ajouter endpoint dedie dans `backend/app/api/v1/routers/billing.py` (ex: `POST /v1/billing/plan-change`)
  - [x] Conserver enveloppes `{data, meta}` et `{error:{code,message,details,request_id}}`
  - [x] Proteger via JWT + RBAC `user` + rate limiting global + user + user/plan
- [x] Integrer la modification de plan cote frontend (AC: 2, 3)
  - [x] Etendre client API billing (`frontend/src/api/billing.ts`)
  - [x] Ajouter UI de changement de plan dans l espace compte (`loading/error/empty`)
  - [x] Afficher clairement le plan courant, plan cible, impact quota et erreurs actionnables
- [x] Verifier l impact cross-feature sur quotas/chat (AC: 2)
  - [x] Verifier que `GET /v1/billing/quota` reflete correctement la limite du plan actif apres changement
  - [x] Verifier que l enforcement quota dans chat utilise bien la nouvelle limite sans ambiguite
  - [x] Eviter toute duplication de logique: reutiliser `QuotaService` existant
- [x] Ajouter observabilite et audit minimaux (AC: 1, 3)
  - [x] Logger chaque tentative/succes/echec de changement de plan avec `request_id`
  - [x] Ajouter metriques minimales (`billing_plan_change_total`, `billing_plan_change_failure_total`, latence endpoint)
  - [x] Tracer les transitions d offre pour support/ops
- [x] Tester et valider la story (AC: 1, 2, 3)
  - [x] Unit tests backend: transitions valides, idempotence, erreurs metier, concurrence
  - [x] Integration tests API: auth 401/403, plan change succes, conflits/invalides, quota coherent post-changement
  - [x] Tests frontend: parcours de changement de plan + erreurs + affichage impact quota
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story source: Epic 4 Story 4.3 (FR27, FR28) apres Story 4.1 (souscription) et Story 4.2 (quotas).
- Cette story doit s appuyer strictement sur les patterns deja implementes en billing/quota, sans introduire un deuxieme systeme de gestion d abonnement.
- Le perimetre B2B (Epic 7) est hors scope; ici on traite uniquement B2C user-facing.

### Technical Requirements

- Conserver API v1 REST et schema d erreurs unifie en `snake_case`.
- Changement de plan transactionnel et idempotent: jamais de double transition sur une meme requete logique.
- Reutiliser les conventions existantes:
  - `request_id` via `X-Request-Id` avec fallback UUID
  - RBAC explicite `user` sur endpoints billing
  - rate limiting `global + user + user/plan`
  - enveloppes d erreur `{error:{code,message,details,request_id}}`
- Le quota ne doit jamais devenir negatif ou incoherent lors d un changement de plan.
- La logique metier reste en `services` (pas dans router/frontend).

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Persistance PostgreSQL via SQLAlchemy + migration Alembic.
- Observabilite minimale obligatoire: logs structures + metriques + erreurs.
- Contrats OpenAPI maintenus pour nouveaux endpoints/reponses.
- Frontend React + client API central + etats `loading/error/empty`.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic.
- DB: PostgreSQL cible (SQLite local acceptable en test).
- Auth: JWT access/refresh existant + RBAC minimal (`user`).
- Frontend: React + TypeScript + TanStack Query + API client centralise.
- Tests: Pytest (backend) et Vitest + Testing Library (frontend).

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/services/billing_service.py`
  - `backend/app/api/v1/routers/billing.py`
  - `backend/app/infra/db/models/billing.py`
  - `backend/migrations/versions/`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/billing.ts`
  - `frontend/src/components/BillingPanel.tsx` ou page compte associee
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - transition plan active -> nouveau plan valide
  - blocage changement invalide/incoherent
  - idempotence et robustesse concurrence
- Integration:
  - endpoint plan change protege JWT + RBAC
  - changement plan reussi + statut abonnement coherent
  - quota/status reflant le nouveau plan
  - erreurs metier stables et actionnables
- Frontend:
  - affichage plan courant/cible
  - confirmation changement de plan
  - etats `loading/error/empty`
  - message clair sur impact quota

### Previous Story Intelligence

- Story 4.1 a etabli:
  - modele billing (`billing_plans`, `user_subscriptions`, `payment_attempts`)
  - service `BillingService`
  - endpoints `/v1/billing/*` avec RBAC/rate limit/request_id
- Story 4.2 a etabli:
  - compteur quota journalier (`user_daily_quota_usages`)
  - service `QuotaService` et endpoint `/v1/billing/quota`
  - enforcement quota dans chat avec erreurs metier stables
- Pour 4.3, ne pas dupliquer ces briques: les etendre proprement.

### Git Intelligence Summary

- Historique recent axe robustesse/tests autour billing/quota. Conserver une approche deltas localises + couverture tests forte.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 4, Story 4.3)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR27, FR28, NFR3, NFR12, NFR19)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (Core Architectural Decisions, API & Communication Patterns, Pattern Examples)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (MVP vs Post-MVP Scope Clarification, Journey 1, loading/error/empty)
- Stories precedentes:
  - `_bmad-output/implementation-artifacts/4-1-souscription-au-plan-payant-d-entree.md`
  - `_bmad-output/implementation-artifacts/4-2-quotas-journaliers-et-suivi-de-consommation.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `create-story` workflow execution with epics/architecture/prd/ux analysis and sprint status sync.
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/app/tests/unit/test_billing_service.py backend/app/tests/integration/test_billing_api.py`
- `npm test -- --run src/tests/BillingPanel.test.tsx` (frontend)
- `.\\.venv\\Scripts\\Activate.ps1; ruff check backend`
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend`
- `npm run lint` (frontend)
- `npm test -- --run` (frontend)
- `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/app/tests/unit/test_billing_service.py backend/app/tests/integration/test_billing_api.py backend/app/tests/integration/test_chat_api.py`

### Completion Notes List

- Ajout de la gestion de changement de plan B2C dans `BillingService` avec idempotence, erreurs metier stables et transition atomique.
- Ajout du modele/historique `subscription_plan_changes` + migration Alembic dediee.
- Exposition de `POST /v1/billing/plan-change` avec JWT, RBAC `user`, rate limiting global/user/user-plan et enveloppes API standard.
- Ajout de l observabilite du flux plan change (logs request_id + compteurs succes/echec + latence).
- Integration frontend du changement de plan (Basic/Premium), affichage explicite du plan actif et de la limite quotidienne cible.
- Verification de l impact quota apres changement de plan via tests integration (`/v1/billing/quota` reflète la nouvelle limite).
- Tests backend/frontend ajoutes et suite complete validee.
- Corrections code-review appliquees: concurrence/idempotence robustes sur `plan-change`, `429` documente et teste, refresh quota apres changement de plan cote UI, couverture chat post-plan-change ajoutee.

### File List

- _bmad-output/implementation-artifacts/4-3-upgrade-modification-de-plan.md
- backend/app/api/v1/routers/billing.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/billing.py
- backend/app/services/billing_service.py
- backend/app/tests/integration/test_billing_api.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/unit/test_billing_service.py
- backend/migrations/env.py
- backend/migrations/versions/20260219_0008_add_subscription_plan_changes.py
- frontend/src/api/billing.ts
- frontend/src/components/BillingPanel.tsx
- frontend/src/tests/BillingPanel.test.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-19: Story 4.3 implementation complete (plan change service/API/UI, migration, observabilite, tests).
- 2026-02-19: Corrections code-review completees (concurrence/idempotence plan-change, OpenAPI 429, coherence quota UI, test chat post-plan-change).

