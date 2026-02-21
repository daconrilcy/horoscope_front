# Story 3.2: Persistance du contexte conversationnel

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want que le chat conserve le contexte de mes echanges,  
so that je n aie pas besoin de tout reexpliquer.

## Acceptance Criteria

1. Given une conversation active, when l utilisateur envoie de nouveaux messages, then les reponses tiennent compte du contexte precedent.
2. Le contexte est persiste de maniere tracable.

## Tasks / Subtasks

- [x] Definir la strategie de contexte pour le chat (AC: 1, 2)
  - [x] Definir la fenetre de contexte MVP (nombre de messages et limite caracteres/tokens)
  - [x] Formaliser les regles d ordre (chronologie stable) et de selection (messages user/assistant)
  - [x] Definir les metadonnees traceables de contexte (`conversation_id`, `message_ids`, taille contexte, version prompt)
- [x] Etendre la couche data conversationnelle (AC: 1, 2)
  - [x] Ajouter repository pour lire les derniers messages d une conversation dans l ordre
  - [x] Persister les metadonnees de contexte utilisees sur les messages assistant
  - [x] Garantir que la persistance reste compatible avec les modeles existants de la story 3.1
- [x] Implementer l orchestration metier de contexte (AC: 1, 2)
  - [x] Etendre `chat_guidance_service` pour construire un prompt contextuel a partir de l historique recent
  - [x] Injecter le contexte dans l appel LLM sans exposer de donnees personnelles directes
  - [x] Conserver fallback/retry de la story 3.1 avec contexte identique entre tentatives
  - [x] Lever des erreurs metier stables si le contexte est indisponible/invalide
- [x] Exposer le comportement via API v1 (AC: 1, 2)
  - [x] Conserver endpoint `POST /v1/chat/messages` avec contrat `{data, meta}` inchange
  - [x] Retourner metadonnees de contexte dans `data` (ids utilises, taille contexte, version)
  - [x] Conserver enveloppe erreur standard `{error: {code, message, details, request_id}}`
- [x] Mettre a jour UI chat minimale pour refleter la continuite (AC: 1)
  - [x] Afficher un indicateur simple de conversation active (id ou statut contextuel)
  - [x] Garder etats `loading/error/empty` explicites sans regression du flux message
  - [x] Gerer proprement la reprise sur erreur/retry en preservant la saisie utile
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires backend: selection contexte, ordre chronologique, limites fenetre, metadonnees
  - [x] Tests integration API: second message utilise bien le contexte du premier
  - [x] Tests integration API: absence contexte valide -> erreur stable
  - [x] Tests frontend: continute visuelle du fil + absence de reset intempestif
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story 3.1 a deja introduit:
  - `chat_conversations`, `chat_messages`
  - `POST /v1/chat/messages`
  - service `chat_guidance_service` + anonymisation + fallback/retry
- Cette story etend la logique sans casser le contrat externe.
- Eviter tout over-engineering: pas de memoire long terme complexe ni resume semantique avance en MVP.

### Technical Requirements

- Contexte construit a partir de messages persistés recents de la conversation active.
- Ordre deterministic: plus ancien -> plus recent pour le prompt.
- Limites explicites de taille contexte pour maitriser cout/latence.
- Tracabilite complete du contexte ayant produit la reponse assistant.
- Reutilisation des garde-fous story 3.1 (timeout, unavailable, retryable, anonymisation).

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun acces DB direct depuis router.
- Contrat API versionne `/v1` et enveloppes standard obligatoires.
- Nommage/format `snake_case` aligne avec conventions projet.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy.
- DB: PostgreSQL (SQLite local de test acceptable via config existante).
- Auth: JWT + RBAC existants.
- Frontend: React + TypeScript + client API central.

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/infra/db/repositories/chat_repository.py`
  - `backend/app/api/v1/routers/chat.py`
  - `backend/app/tests/unit/test_chat_guidance_service.py`
  - `backend/app/tests/integration/test_chat_api.py`
- Cibles frontend probables:
  - `frontend/src/pages/ChatPage.tsx`
  - `frontend/src/api/chat.ts`
  - `frontend/src/tests/ChatPage.test.tsx`

### Testing Requirements

- Unit:
  - contexte construit a partir des derniers messages
  - ordre chronologique correct
  - limite fenetre appliquee
  - metadonnees traceables persistées
- Integration:
  - envoi message 1 puis message 2 -> reponse 2 depend du contexte precedent
  - erreur stable si contexte impossible a charger
  - contrat erreur/API conforme
- Frontend:
  - continute du fil conversationnel
  - etats loading/error/empty conserves
  - retry sans perte de contexte utile

### Previous Story Intelligence

- Story 3.1 a etabli le socle technique chat: persistance, API, fallback/retry, anonymisation.
- Maintenir compatibilite totale avec les tests et contrats de 3.1.
- Ne pas reintroduire de route ou format parallele pour le chat.

### Git Intelligence Summary

- Le projet est en re-bootstrap avec historique legacy important supprime.
- Conserver des changements incrementaux et localises pour limiter le risque de regression.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.2)
- Story precedente: `_bmad-output/implementation-artifacts/3-1-chat-astrologue-avec-envoi-reception-de-messages.md`
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR20, FR21, NFR3, NFR4, NFR16, NFR20)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (boundaries, contracts API, observabilite)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (chat central, continuite, loading/error/empty, offline-readonly)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution
- Backend: `ruff check .`, `pytest -q`
- Frontend: `npm run lint`, `npm test -- --run`, `npm run build`

### Completion Notes List

- Ajout du contexte conversationnel persiste avec fenetre configurable et ordre chronologique stable.
- Ajout des metadonnees de contexte traceables dans la reponse API et dans `metadata_payload` des messages assistant.
- Conservation du retry/fallback avec contexte identique entre tentatives et erreurs stables pour contexte invalide.
- Ajout d un indicateur frontend de conversation active sans regression des etats `loading/error/empty`.
- Validation complete executee: backend `97 passed`, frontend `10 passed`, lint backend/frontend OK, build frontend OK.

### File List

- _bmad-output/implementation-artifacts/3-2-persistance-du-contexte-conversationnel.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/core/config.py
- backend/app/infra/db/repositories/chat_repository.py
- backend/app/services/chat_guidance_service.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/app/tests/integration/test_chat_api.py
- frontend/src/api/chat.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx

## Change Log

- 2026-02-18: Implementation complete de la story 3.2 (backend + frontend + tests), statut passe a `review`.
