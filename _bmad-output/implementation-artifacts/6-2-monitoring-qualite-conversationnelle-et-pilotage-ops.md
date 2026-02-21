# Story 6.2: Monitoring qualite conversationnelle et pilotage ops

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a operations user,  
I want suivre les KPI qualite/usage et appliquer un rollback de configuration,  
so that je maintiens la qualite de service.

## Acceptance Criteria

1. Given une couche d observabilite active, when des derives sont detectees (hors-scope, erreurs, latence), then les indicateurs remontent dans les outils ops.
2. Given une configuration operationnelle modifiable, when une degradation qualite est observee, then une configuration peut etre revertee rapidement avec tracabilite.
3. Given un utilisateur ops authentifie, when il consulte le monitoring conversationnel, then les KPI minimaux (hors-scope, erreurs, latence, volume) sont visibles avec fenetre temporelle.
4. Given une action de rollback ops, when elle est executee, then l action est protegee RBAC et auditee (`request_id`, acteur, action, cible, statut).

## Tasks / Subtasks

- [x] Definir les KPI conversationnels et contrats d exposition (AC: 1, 3)
  - [x] Definir metriques minimales: `out_of_scope_rate`, `llm_error_rate`, `p95_latency_ms`, `messages_total`
  - [x] Definir fenetres de consultation (`1h`, `24h`, `7d`) et format de reponse API
  - [x] Definir regles de calcul robustes (division by zero, absence de donnees, bornes)
- [x] Exposer API monitoring ops (AC: 1, 3)
  - [x] Ajouter endpoint(s) REST v1 sous `/v1/ops/monitoring/*`
  - [x] Proteger via RBAC `ops` strict (pas `user`, pas `support`)
  - [x] Ajouter rate limiting global + role + user
- [x] Implementer rollback config qualite (AC: 2, 4)
  - [x] Reutiliser etendre le service persona/config existant pour rollback explicite et tracable
  - [x] Garantir idempotence raisonnable et messages d erreur metier stables
  - [x] Ajouter audit systematique des rollbacks (`success`/`failed`)
- [x] Renforcer observabilite backend (AC: 1)
  - [x] Completer emission des metriques sur parcours chat/guidance (erreurs, latence, hors-scope)
  - [x] Ajouter logs structures operationnels avec `request_id`
  - [x] Verifier compatibilite dashboard/consommation ops
- [x] Integrer panneau ops frontend (AC: 2, 3)
  - [x] Ajouter client API monitoring dans `frontend/src/api/`
  - [x] Ajouter panel ops affichant KPI + controls de rollback
  - [x] Gerer explicitement `loading/error/empty`
- [x] Tester et valider la story (AC: 1, 2, 3, 4)
  - [x] Unit tests backend: agregation KPI + regles de calcul + rollback
  - [x] Integration tests backend: RBAC, endpoints monitoring, rollback + audit
  - [x] Tests frontend: rendu KPI, erreurs, rollback actionnable
  - [x] Validation finale: `ruff check backend` + `pytest -q backend` + `npm run lint` + `npm test -- --run`

## Dev Notes

- Story source: Epic 6 Story 6.2 (FR35, FR36, FR37), dans la continuité directe de la story 6.1.
- Reutiliser les acquis en place:
  - `backend/app/api/v1/routers/ops_persona.py`
  - `backend/app/services/persona_config_service.py`
  - `backend/app/services/audit_service.py`
  - `backend/app/infra/observability/metrics.py`
- Eviter tout sur-design dashboard: MVP ops focalise sur KPI de decision + rollback fiable.

### Technical Requirements

- Monitoring expose des KPI fiables meme si volume faible ou nul (pas de crash, valeurs coherentes).
- Rollback ops doit etre rapide, trace et reversible sans intervention manuelle DB.
- Les endpoints ops restent strictement reserves au role `ops`.
- Les erreurs d API doivent rester stables (`snake_case`) avec `request_id`.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- RBAC/JWT existants comme mecanisme unique d autorisation.
- Observabilite centralisee: metriques + logs structures + audit actions sensibles.
- Frontend: client API central, etats UX explicites.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Redis.
- Frontend: React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest + Testing Library frontend.

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/api/v1/routers/ops_persona.py` (extension rollback/monitoring ops)
  - `backend/app/api/v1/routers/` (nouveau routeur monitoring si pertinent)
  - `backend/app/services/persona_config_service.py`
  - `backend/app/services/audit_service.py`
  - `backend/app/infra/observability/metrics.py`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/`
  - `frontend/src/components/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - calcul KPI sur cas limites (pas de donnees, volume partiel)
  - transitions rollback et erreurs metier
- Integration:
  - endpoints monitoring ops (401/403/429/200)
  - rollback trace par audit
- Frontend:
  - etats `loading/error/empty`
  - affichage KPI et action rollback

### Previous Story Intelligence

- Story 6.1 a deja etabli:
  - patterns RBAC `support|ops` et rate limiting compose
  - structure audit standard
  - panel support/ops React avec client API dedie
- Pour 6.2:
  - conserver ces patterns et eviter divergence de contrats API
  - privilegier extension des briques ops existantes avant creation de nouvelles couches

### Git Intelligence Summary

- Historique recent axe robustesse tests et correction rapide des findings review.
- Continuer avec deltas limites + couverture tests integration prioritaire.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 6, Story 6.2)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR35, FR36, FR37, NFR18, NFR20, NFR21)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (observabilite, rollback config, RBAC ops)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (etats UX critiques)
- Story precedente: `_bmad-output/implementation-artifacts/6-1-outillage-support-compte-incidents-demandes-privacy.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Backend: `.\.venv\Scripts\Activate.ps1; ruff format backend`
- Backend: `.\.venv\Scripts\Activate.ps1; ruff check backend`
- Backend: `.\.venv\Scripts\Activate.ps1; pytest -q backend`
- Frontend: `npm run lint`
- Frontend: `npm test -- --run`

### Completion Notes List

- Ajout du monitoring ops conversationnel (`/v1/ops/monitoring/conversation-kpis`) avec RBAC `ops`, fenetres `1h/24h/7d`, rate limiting et erreurs stables.
- Renforcement observabilite chat/guidance: compteurs/messages, erreurs LLM, latence, logs avec `request_id`.
- Rollback persona conserve et etendu avec audit verifie en integration (`request_id`, acteur, action, cible, statut).
- Ajout d un panneau frontend ops monitoring avec etats `loading/error/empty`, KPI et action de rollback persona.
- Couverture tests ajoutee backend/frontend pour KPI, RBAC, 429 et audit rollback.
- Corrections review appliquees: audit rollback rendu strict (erreur explicite `audit_unavailable`), calcul `out_of_scope_rate` aligne sur volume chat, retention bornée des evenements metriques, p95 percentile interpolation, etat empty UI clarifie, et affichage explicite `aggregation_scope`.

### File List

- `_bmad-output/implementation-artifacts/6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`
- `backend/app/main.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/api/v1/routers/ops_monitoring.py`
- `backend/app/api/v1/routers/ops_persona.py`
- `backend/app/infra/observability/metrics.py`
- `backend/app/services/ops_monitoring_service.py`
- `backend/app/services/chat_guidance_service.py`
- `backend/app/services/guidance_service.py`
- `backend/app/api/v1/routers/chat.py`
- `backend/app/api/v1/routers/guidance.py`
- `backend/app/tests/unit/test_ops_monitoring_service.py`
- `backend/app/tests/integration/test_ops_monitoring_api.py`
- `backend/app/tests/integration/test_ops_persona_api.py`
- `frontend/src/App.tsx`
- `frontend/src/api/opsMonitoring.ts`
- `frontend/src/components/OpsMonitoringPanel.tsx`
- `frontend/src/tests/OpsMonitoringPanel.test.tsx`
