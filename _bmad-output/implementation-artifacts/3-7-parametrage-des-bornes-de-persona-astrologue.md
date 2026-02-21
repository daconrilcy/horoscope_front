# Story 3.7: Parametrage des bornes de persona astrologue

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a operations user,  
I want configurer les limites de comportement du persona astrologue,  
so that je controle le ton, le perimetre et la qualite des reponses.

## Acceptance Criteria

1. Given une interface/configuration ops disponible, when un parametre de persona est modifie, then la nouvelle configuration est appliquee au chat.
2. Un rollback est possible en cas de derive qualite.

## Tasks / Subtasks

- [x] Definir le cadre persona MVP (AC: 1, 2)
  - [x] Definir les parametres supportes (ton, niveau de prudence, perimetre hors-scope, style de reponse)
  - [x] Definir les valeurs par defaut et contraintes de validation
  - [x] Definir un schema versionne de configuration persona (id/version/status)
- [x] Etendre la couche metier backend (AC: 1, 2)
  - [x] Ajouter un service de gestion de configuration persona (`create/update/get/rollback`)
  - [x] Integrer la configuration active dans la construction de prompt chat/guidance
  - [x] Garantir fallback sur configuration par defaut si config active invalide/introuvable
- [x] Exposer API v1 de parametrage persona (AC: 1, 2)
  - [x] Ajouter endpoints ops (lecture/edition/activation/rollback) sous `/v1/ops/persona`
  - [x] Proteger endpoints via JWT + RBAC role `ops`
  - [x] Conserver enveloppes standards `{data, meta}` et `{error: {code, message, details, request_id}}`
- [x] Ajouter tracabilite et observabilite ops (AC: 2)
  - [x] Journaliser les changements de persona (qui, quoi, quand, version precedente/nouvelle)
  - [x] Journaliser les rollbacks et leur motif
  - [x] Exposer metadonnees minimales dans les logs structures pour suivi qualite
- [x] Mettre a jour UI ops minimale (AC: 1, 2)
  - [x] Ajouter formulaire de parametres persona (validation client + etats loading/error/empty)
  - [x] Ajouter action de rollback vers version precedente
  - [x] Afficher confirmation explicite de configuration active
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires backend: validation config, activation, rollback, fallback default
  - [x] Tests integration API: RBAC `ops`, succes edition, succes rollback, erreurs metier stables
  - [x] Tests frontend: edition persona, confirmation activation, rollback visible
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story 3.1: orchestration chat et structures de prompt.
- Story 3.4/3.5: guidance guardrailed et coherente.
- Story 3.6: detection hors-scope et recovery.
- Cette story introduit la gouvernance explicite du comportement astrologue, avec rollback operationnel.

### Technical Requirements

- La configuration persona doit etre validee et versionnee.
- Le chat/guidance doit utiliser uniquement la configuration active.
- Un rollback doit etre atomique et traçable.
- Les erreurs metier doivent rester stables et actionnables.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- Pas d acces DB direct depuis les routers.
- Endpoints versionnes `/v1`, schema `snake_case`.
- Observabilite minimale sur changements de config et rollbacks.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy.
- DB: PostgreSQL (SQLite local test acceptable).
- Auth: JWT + RBAC existants.
- Frontend: React + TypeScript + client API central.

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/api/v1/routers/ops_persona.py` (ou extension routeur ops)
  - `backend/app/services/` (service de configuration persona)
  - `backend/app/infra/db/models/` (modeles configuration/version persona)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Cibles frontend probables:
  - `frontend/src/api/` (client ops persona)
  - `frontend/src/pages/` (vue ops persona)
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - validation des parametres persona
  - activation de version
  - rollback vers version precedente
  - fallback config par defaut
- Integration:
  - endpoints ops persona proteges (401/403)
  - succes update/activate/rollback
  - enveloppe erreur standard
- Frontend:
  - saisie et soumission configuration
  - etats loading/error/empty
  - confirmation de rollback

### Previous Story Intelligence

- Reutiliser le pattern de robustesse et de contrats API deja etabli dans les stories 3.1 a 3.6.
- Garder des changements incrementaux localises pour limiter les regressions.

### Git Intelligence Summary

- Repository en re-bootstrap; privilegier des deltas localises et explicites.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.7)
- Story precedente: `_bmad-output/implementation-artifacts/3-6-detection-hors-scope-et-recuperation-guidee.md`
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR23, NFR16, NFR20, NFR21)
- Architecture: `_bmad-output/planning-artifacts/architecture.md`
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow implementation:
  - `.\.venv\Scripts\Activate.ps1; ruff check .`
  - `.\.venv\Scripts\Activate.ps1; pytest -q`
  - `npm run lint`
  - `npm test -- --run`
  - `npm run build`

### Completion Notes List

- Ajout d un service versionne de configuration persona avec activation et rollback.
- Ajout des endpoints ops `/v1/ops/persona/config` (GET/PUT) et `/v1/ops/persona/rollback` (POST) proteges RBAC `ops`.
- Integration de la policy persona active dans la generation de prompt chat et guidance.
- Ajout d un panneau Ops frontend pour editer la persona et declencher un rollback.
- Couverture tests backend/frontend completee sans regression.

### File List

- _bmad-output/implementation-artifacts/3-7-parametrage-des-bornes-de-persona-astrologue.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/main.py
- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/ops_persona.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/persona_config.py
- backend/app/services/persona_config_service.py
- backend/app/services/chat_guidance_service.py
- backend/app/services/guidance_service.py
- backend/app/tests/unit/test_persona_config_service.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/app/tests/unit/test_guidance_service.py
- backend/app/tests/integration/test_ops_persona_api.py
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/api/opsPersona.ts
- frontend/src/components/OpsPersonaPanel.tsx
- frontend/src/tests/OpsPersonaPanel.test.tsx
