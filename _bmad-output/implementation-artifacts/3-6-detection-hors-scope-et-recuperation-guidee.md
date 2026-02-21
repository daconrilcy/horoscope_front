# Story 3.6: Detection hors-scope et recuperation guidee

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want que le systeme gere les reponses hors-scope avec reformulation,  
so that l experience reste pertinente et fiable.

## Acceptance Criteria

1. Given une reponse detectee comme hors-scope/incoherente, when le mecanisme de controle qualite s active, then une strategie de recovery (retry/reformulation/fallback) est appliquee.
2. L evenement est journalise pour suivi ops.

## Tasks / Subtasks

- [x] Definir le cadre hors-scope MVP (AC: 1, 2)
  - [x] Definir les signaux de detection hors-scope (`off_scope_score`, mots-clefs de rupture, incoherence format)
  - [x] Definir les strategies de recovery minimales (`reformulate`, `retry_once`, `safe_fallback`)
  - [x] Definir le contrat metier stable d erreur/metadata (`off_scope_detected`, `recovery_strategy`, `recovery_applied`)
- [x] Etendre la couche metier backend (AC: 1, 2)
  - [x] Ajouter un evaluateur hors-scope dans le flux chat/guidance (`chat_guidance_service` + `guidance_service`)
  - [x] Integrer une reformulation guidee avant fallback final
  - [x] Garantir un fallback actionnable si la recuperation echoue
- [x] Exposer les metadonnees API de recovery (AC: 1, 2)
  - [x] Enrichir les reponses `POST /v1/chat/messages` (et guidance si applicable) avec metadonnees recovery non cassantes
  - [x] Conserver enveloppes API standard `{data, meta}` et `{error: {code, message, details, request_id}}`
  - [x] Maintenir JWT + RBAC role `user`
- [x] Ajouter observabilite et tracabilite ops (AC: 2)
  - [x] Journaliser les evenements hors-scope en logs structures (code, strategie, latence, retry)
  - [x] Ajouter compteurs/metriques minimales (`off_scope_count`, `recovery_success_rate`)
  - [x] Garantir absence d identifiants personnels directs dans ces traces
- [x] Mettre a jour UX chat minimale (AC: 1)
  - [x] Afficher un message clair quand une recuperation est appliquee
  - [x] Proposer une action de continuation naturelle (reformulation suggeree)
  - [x] Preserver les etats `loading/error/empty` sans regression de fluidite
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires backend: detection hors-scope, choix strategie recovery, fallback final
  - [x] Tests integration API: scenario hors-scope -> recovery appliquee, erreurs stables, RBAC
  - [x] Tests frontend: rendu du feedback recovery, non-regression parcours chat
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story 3.1: orchestration chat + retry/fallback + anonymisation.
- Story 3.2: persistance du contexte conversationnel.
- Story 3.3: historique et reprise.
- Story 3.4: guidance periodique guardrailed.
- Story 3.5: guidance contextuelle guardrailed.
- Cette story ajoute la resilience qualite (hors-scope -> recovery) sans casser les contrats existants.

### Technical Requirements

- Detection hors-scope explicite et testable, sans heuristiques opaques non tracables.
- Strategie de recovery bornee (pas de boucle infinie), priorisant reformulation puis fallback.
- Traces exploitables ops avec anonymisation et champs stables pour monitoring qualite.
- Compatibilite retro des contrats API frontend existants.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- Pas d acces DB direct depuis router.
- Endpoints versionnes `/v1`, schemas `snake_case`.
- Observabilite minimale obligatoire (logs structures + metriques erreurs/latence).

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy.
- DB: PostgreSQL (SQLite local test acceptable).
- Auth: JWT + RBAC existants.
- Frontend: React + TypeScript + client API central.

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/services/guidance_service.py`
  - `backend/app/api/v1/routers/chat.py`
  - `backend/app/api/v1/routers/guidance.py`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Cibles frontend probables:
  - `frontend/src/api/chat.ts`
  - `frontend/src/api/guidance.ts`
  - `frontend/src/pages/ChatPage.tsx`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - detection hors-scope positive/negative
  - mapping strategie (`reformulate`, `retry_once`, `safe_fallback`)
  - non-regression guardrails/disclaimers
- Integration:
  - hors-scope declenche recovery dans `POST /v1/chat/messages`
  - enveloppes erreurs et metadata stables
  - `401/403/422/503` selon cas
- Frontend:
  - feedback clair de recuperation
  - action de continuation visible
  - non-regression flux chat/guidance

### Previous Story Intelligence

- Reutiliser le pattern de robustesse deja etabli: retries bornes, fallback actionnable, anti-fuite prompt.
- Garder un delta minimal sur `ChatPage` pour eviter regressions UX.

### Git Intelligence Summary

- Repository en re-bootstrap; privilegier des changements incrementaux et localises.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.6)
- Stories precedentes:
  - `_bmad-output/implementation-artifacts/3-1-chat-astrologue-avec-envoi-reception-de-messages.md`
  - `_bmad-output/implementation-artifacts/3-2-persistance-du-contexte-conversationnel.md`
  - `_bmad-output/implementation-artifacts/3-3-historique-et-reprise-des-conversations.md`
  - `_bmad-output/implementation-artifacts/3-4-guidance-quotidienne-et-hebdomadaire.md`
  - `_bmad-output/implementation-artifacts/3-5-guidance-contextuelle-sur-situation-critique.md`
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR22, NFR16, NFR18, NFR20, NFR21)
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

- Detection hors-scope integree au flux chat avec strategies bornees: `reformulate`, `retry_once`, `safe_fallback`.
- Reponses `POST /v1/chat/messages` enrichies avec metadonnees `recovery` non cassantes.
- Journalisation structuree minimale ajoutee pour la detection/recovery hors-scope.
- UI chat mise a jour avec feedback explicite quand une recuperation est appliquee.
- Couverture tests completee backend/frontend sans regression.

### File List

- _bmad-output/implementation-artifacts/3-6-detection-hors-scope-et-recuperation-guidee.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/services/chat_guidance_service.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/app/tests/integration/test_chat_api.py
- frontend/src/api/chat.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx
