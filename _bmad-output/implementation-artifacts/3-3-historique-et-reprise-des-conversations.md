# Story 3.3: Historique et reprise des conversations

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want retrouver et reprendre mes conversations passees,  
so that je continue mes echanges sans perte d information.

## Acceptance Criteria

1. Given plusieurs conversations existantes, when l utilisateur consulte son historique et rouvre un fil, then les messages precedents sont restaures.
2. La reprise se fait sur le bon contexte conversationnel.

## Tasks / Subtasks

- [x] Definir le perimetre historique MVP (AC: 1, 2)
  - [x] Definir le tri et l ordre d affichage des conversations (plus recentes en premier)
  - [x] Definir les metadonnees minimales listees (id conversation, date maj, apercu dernier message)
  - [x] Definir les regles de reprise (conversation active cible, contexte charge)
- [x] Etendre la couche data conversationnelle (AC: 1, 2)
  - [x] Ajouter repository pour lister les conversations d un utilisateur avec pagination
  - [x] Ajouter repository pour recuperer les messages d une conversation dans l ordre chronologique
  - [x] Verifier l isolation stricte par `user_id` pour eviter toute fuite de conversation
- [x] Implementer les services metier d historique/reprise (AC: 1, 2)
  - [x] Ajouter service de listing historique conversationnel
  - [x] Ajouter service d ouverture/reprise d un fil existant
  - [x] Garantir une erreur metier stable si conversation introuvable/non autorisee
- [x] Exposer les endpoints API v1 (AC: 1, 2)
  - [x] Ajouter endpoint `GET /v1/chat/conversations` (liste historique utilisateur)
  - [x] Ajouter endpoint `GET /v1/chat/conversations/{conversation_id}` (messages du fil)
  - [x] Conserver contrats `{data, meta}` et enveloppe erreur standard `{error: {code, message, details, request_id}}`
- [x] Mettre a jour UI chat pour l historique/reprise (AC: 1, 2)
  - [x] Afficher la liste des conversations passees avec etat vide explicite
  - [x] Permettre la selection d un fil et restaurer les messages dans le panneau chat
  - [x] Conserver les etats `loading/error/empty` sans regression du flux d envoi existant
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires backend: tri historique, pagination, controle d acces conversation
  - [x] Tests integration API: listing historique, ouverture fil, conversation non autorisee/inexistante
  - [x] Tests frontend: affichage historique, reprise fil, maintien de la continuite visuelle
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story 3.1 a etabli le socle d envoi/reception des messages et la gestion des erreurs techniques.
- Story 3.2 a etabli la persistance du contexte et les metadonnees de contexte.
- Cette story ajoute la navigation dans l historique et la reprise d un fil existant sans casser le contrat chat actuel.

### Technical Requirements

- Historique conversationnel restreint au proprietaire authentifie.
- Ordre de messages deterministic: plus ancien -> plus recent.
- Reprise d un fil existant sans perte du contexte precedent.
- Pagination sur la liste de conversations pour maitriser charge et latence.
- Erreurs metier stables et actionnables pour `conversation_not_found` / `conversation_forbidden`.

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun acces DB direct depuis router.
- Endpoints versionnes `/v1` avec schemas `snake_case`.
- Conserver les conventions d erreurs unifiees.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy.
- DB: PostgreSQL (SQLite local test acceptable via config).
- Auth: JWT + RBAC existants (`user`, `support`, `ops`).
- Frontend: React + TypeScript + client API central.

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/api/v1/routers/chat.py`
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/infra/db/repositories/chat_repository.py`
  - `backend/app/tests/unit/test_chat_guidance_service.py`
  - `backend/app/tests/integration/test_chat_api.py`
- Cibles frontend probables:
  - `frontend/src/api/chat.ts`
  - `frontend/src/pages/ChatPage.tsx`
  - `frontend/src/tests/ChatPage.test.tsx`

### Testing Requirements

- Unit:
  - listing conversations ordonne et pagine
  - chargement messages d un fil en ordre chronologique
  - blocage d acces a un fil appartenant a un autre utilisateur
- Integration:
  - `GET /v1/chat/conversations` renvoie l historique utilisateur
  - `GET /v1/chat/conversations/{id}` renvoie le fil et ses messages
  - erreurs stables pour conversation absente/non autorisee
- Frontend:
  - etat vide historique visible
  - selection d un fil restaure le fil de messages
  - etats `loading/error/empty` conserves

### Previous Story Intelligence

- Les stories 3.1 et 3.2 ont pose les modeles `chat_conversations` et `chat_messages` ainsi que la logique de contexte.
- Reutiliser ces assets; ne pas dupliquer une seconde logique de conversation.

### Git Intelligence Summary

- Repository en phase de re-bootstrap; limiter les deltas aux composants chat existants.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.3)
- Story precedente: `_bmad-output/implementation-artifacts/3-2-persistance-du-contexte-conversationnel.md`
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR21, NFR3, NFR4, NFR16)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (API contracts, layering, observabilite)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (continuite du chat, etats loading/error/empty)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution
- Backend: `ruff check .`, `pytest -q`
- Frontend: `npm run lint`, `npm test -- --run`, `npm run build`

### Completion Notes List

- Ajout de l historique conversationnel utilisateur avec pagination (`GET /v1/chat/conversations`).
- Ajout de la reprise d un fil conversationnel avec restauration des messages (`GET /v1/chat/conversations/{conversation_id}`).
- Ajout de garde-fous d acces (`conversation_not_found`, `conversation_forbidden`) et pagination invalide (`invalid_chat_pagination`).
- Mise a jour du frontend chat avec liste d historique, etat vide historique, et reprise de fil.
- Validation complete executee: backend `106 passed`, frontend `11 passed`, lint backend/frontend OK, build frontend OK.

### File List

- _bmad-output/implementation-artifacts/3-3-historique-et-reprise-des-conversations.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/chat.py
- backend/app/infra/db/repositories/chat_repository.py
- backend/app/services/chat_guidance_service.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/unit/test_chat_guidance_service.py
- frontend/src/api/chat.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx

## Change Log

- 2026-02-19: Implementation complete de la story 3.3 (backend + frontend + tests), statut passe a `review`.
