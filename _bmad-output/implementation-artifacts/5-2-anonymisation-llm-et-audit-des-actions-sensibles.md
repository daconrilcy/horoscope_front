# Story 5.2: Anonymisation LLM et audit des actions sensibles

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a operations user,  
I want garantir l anonymisation avant envoi LLM et auditer les actions critiques,  
so that la confidentialite et la conformite sont assurees.

## Acceptance Criteria

1. Given un appel sortant vers un LLM, when la requete est preparee, then les identifiants personnels directs sont retires ou pseudonymises avant emission.
2. Given une action sensible (privacy, auth, billing, gestion credentials), when l action est executee, then un evenement d audit structure est journalise avec `request_id`, `actor`, `action`, `target`, `status` et horodatage.
3. Given une demande de suivi support/ops, when l historique d audit est consulte, then les evenements recents sont recuperables via API securisee RBAC avec filtres minimaux (type, statut, date, user cible).

## Tasks / Subtasks

- [x] Definir le contrat d anonymisation LLM (AC: 1)
  - [x] Lister les champs sensibles a neutraliser (`email`, nom/prenom, telephone, adresse, identifiants internes explicites)
  - [x] Definir la strategie de pseudonymisation deterministe (token placeholders stables)
  - [x] Definir les regles de non-regression (aucun identifiant direct ne doit sortir vers le provider LLM)
- [x] Implementer la couche d anonymisation avant appel LLM (AC: 1)
  - [x] Ajouter un composant dedie dans `backend/app/infra/llm/anonymizer.py` (extension du composant existant)
  - [x] Integrer anonymisation dans le flux chat/guidance avant emission provider
  - [x] Ajouter tests unitaires de transformation + cas limites (texte libre, donnees partielles, contexte long)
- [x] Concevoir le schema d audit des actions sensibles (AC: 2, 3)
  - [x] Ajouter modele DB `audit_events` avec index de recherche operatoire
  - [x] Ajouter migration Alembic associee (contraintes + index)
  - [x] Definir taxonomie d actions (`privacy_export`, `privacy_delete`, `auth_login`, `billing_plan_change`, etc.)
- [x] Implementer le service d audit centralise (AC: 2)
  - [x] Ajouter `audit_service` avec API interne `record_event(...)`
  - [x] Standardiser le payload d audit (request_id, actor, target, action, status, metadata minimale)
  - [x] Integrer l emission d audit dans points critiques (privacy, auth, billing)
- [x] Exposer API de consultation audit pour support/ops (AC: 3)
  - [x] Ajouter endpoint REST v1 dedie (`/v1/audit/events`)
  - [x] Proteger via JWT + RBAC (`support`, `ops`) et interdire role `user`
  - [x] Ajouter filtres minimaux (action, status, date_from/date_to, target_user_id, pagination)
- [x] Ajouter observabilite, robustesse et garde-fous (AC: 1, 2, 3)
  - [x] Journaliser erreurs d anonymisation/audit avec `request_id` sans fuite de donnees sensibles
  - [x] Ajouter metriques minimales (`llm_anonymization_events_total`, `audit_events_total`, `audit_events_failures_total`)
  - [x] Garantir erreurs metier stables (`audit_forbidden`, `audit_validation_error`, `llm_anonymization_failed`)
- [x] Tester et valider la story (AC: 1, 2, 3)
  - [x] Unit tests backend anonymizer + audit service
  - [x] Integration tests API audit (401/403, filtres, pagination, role support/ops)
  - [x] Tests de non-fuite: verifications explicites qu un email/identifiant brut n est pas transmis au client LLM
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story source: Epic 5 Story 5.2 (FR31, FR32, FR33) complete le socle privacy commence en story 5.1.
- Cette story est critique conformite: ne pas limiter l audit a des logs applicatifs libres, utiliser un schema explicite consultable.
- Reutiliser les patterns etablis:
  - enveloppes API `{data, meta}` / `{error:{...}}`
  - `request_id` systematique
  - RBAC explicite
  - rate limiting global + user + user/plan ou global + role selon endpoint
- Cette story prepare aussi le terrain pour Epic 6 (support/ops outillage) via la couche d audit consultable.

### Technical Requirements

- Aucune donnee personnelle directe ne doit quitter le backend vers le provider LLM.
- Les evenements d audit doivent etre persistants, requetables et correles via `request_id`.
- Les champs `details/metadata` d audit doivent rester minimaux et non sensibles (pas de payload brut utilisateur).
- API audit versionnee v1, erreurs en `snake_case`, pagination obligatoire sur endpoints liste.
- Les permissions lecture audit doivent etre limitees aux roles autorises (`support`, `ops`).

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Persistance PostgreSQL via SQLAlchemy + migration Alembic.
- Anonymisation placee dans la couche `infra/llm` avant appel provider.
- Observabilite obligatoire: logs structures + metriques d anonymisation/audit.
- Conserver coherence avec conventions definies dans `architecture.md` (naming, format API, error model).

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic.
- DB: PostgreSQL cible (SQLite local acceptable pour tests).
- Auth/RBAC: JWT access/refresh existant avec roles `user`, `support`, `ops`.
- Frontend (si ecran audit ajoute): React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest frontend si impact UI.

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/infra/llm/anonymizer.py` (nouveau ou extension)
  - `backend/app/services/audit_service.py` (nouveau)
  - `backend/app/infra/db/models/` (modele audit events)
  - `backend/migrations/versions/` (migration audit)
  - `backend/app/api/v1/routers/` (routeur audit)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (si consultation audit exposee):
  - `frontend/src/api/`
  - `frontend/src/components/` ou `frontend/src/pages/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - anonymisation deterministic/pseudonymisation des identifiants
  - audit event serialization et validation champs obligatoires
  - codes erreurs stables sur cas invalides
- Integration:
  - routes audit protegees RBAC support/ops
  - filtres/pagination sur consultation audit
  - preuve non-fuite identifiants directs vers LLM
- Non-regression:
  - maintenir comportements privacy 5.1
  - verifier que les endpoints existants conservent leurs contrats de reponse

### Previous Story Intelligence

- Story 5.1 a deja mis en place:
  - workflows privacy export/suppression avec traçabilite de statut
  - patterns API d erreurs stables et `request_id`
  - rate limiting global/user/user-plan
  - panel UI privacy avec confirmation/empty states
- Pour 5.2:
  - reutiliser ces patterns sans casser les contrats existants
  - ajouter couche audit transversale plutot que dupliquer des logs par routeur

### Git Intelligence Summary

- Le code recent montre une approche par services dedies + tests integration renforces.
- Conserver des deltas localises sur:
  - `infra/llm` pour anonymisation
  - `services` pour orchestration audit
  - `api/v1/routers` pour exposition controlee support/ops

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.2)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR31, FR32, FR33, NFR5, NFR6, NFR8, NFR19)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (Authentication & Security, API Patterns, Project Structure & Boundaries)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (Journey 4 RGPD, etats `loading/error/empty`, confiance/confidentialite)
- Story precedente: `_bmad-output/implementation-artifacts/5-1-export-et-suppression-des-donnees-personnelles.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `.\.venv\Scripts\Activate.ps1; ruff check backend`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend`
- `npm run lint` (dans `frontend/`)
- `npm test -- --run` (dans `frontend/`)

### Completion Notes List

- Ajout du modele `AuditEventModel` et migration Alembic `audit_events` avec index de consultation.
- Ajout du `AuditService` (record/list + filtres + pagination + validations metier).
- Ajout du routeur `GET /v1/audit/events` protege RBAC support/ops avec rate limiting dedie.
- Integration audit sur routes sensibles: auth (`register/login/refresh`), billing (`checkout/retry/plan-change`) et privacy (`export/delete`).
- Renforcement anonymisation LLM avec pseudonymisation deterministe et couverture de champs sensibles (email/phone/name/address/id/uuid).
- Durcissement flux chat: erreur metier stable `llm_anonymization_failed` en cas d echec de sanitization.
- Ajout de metriques et logs structures pour anonymisation et audit.
- Ajout tests unitaires/integration dedies (anonymizer, audit service, audit API) + ajustements non-regression chat.
- Validation complete executee avec succes: Ruff backend, Pytest backend (213 tests), ESLint frontend, Vitest frontend.

### File List

- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/audit.py
- backend/app/api/v1/routers/auth.py
- backend/app/api/v1/routers/billing.py
- backend/app/api/v1/routers/privacy.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/audit_event.py
- backend/app/infra/llm/anonymizer.py
- backend/app/main.py
- backend/app/services/audit_service.py
- backend/app/services/chat_guidance_service.py
- backend/app/tests/integration/test_audit_api.py
- backend/app/tests/unit/test_anonymizer.py
- backend/app/tests/unit/test_audit_service.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/migrations/env.py
- backend/migrations/versions/20260219_0010_add_audit_events.py
- _bmad-output/implementation-artifacts/5-2-anonymisation-llm-et-audit-des-actions-sensibles.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
