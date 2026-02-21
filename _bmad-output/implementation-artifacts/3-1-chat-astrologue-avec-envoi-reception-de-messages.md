# Story 3.1: Chat astrologue avec envoi/reception de messages

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want echanger par messages avec un astrologue virtuel,  
so that je peux poser mes questions au fil de mes besoins.

## Acceptance Criteria

1. Given un utilisateur authentifie avec acces au chat, when il envoie un message, then le systeme retourne une reponse astrologique.
2. Les erreurs techniques sont gerees avec un feedback clair.
3. Si le fournisseur LLM ne repond pas dans le delai attendu, un fallback/retry controle est applique puis un message actionnable est affiche.

## Tasks / Subtasks

- [x] Definir le socle metier du chat astrologue (AC: 1, 2, 3)
  - [x] Introduire les modeles conversation/message en base (conversation active + messages ordonnes)
  - [x] Definir les schemas Pydantic d entree/sortie (`message` utilisateur, `message` assistant, metadonnees de tentative/fallback)
  - [x] Maintenir le contrat d erreur standard `{error: {code, message, details, request_id}}`
- [x] Implementer le service d orchestration de reponse chat (AC: 1, 2, 3)
  - [x] Ajouter un service dedie `chat_guidance_service` (ou equivalent) dans `backend/app/services`
  - [x] Integrer un client LLM via `infra/llm/client.py` avec timeout explicite et retry borne
  - [x] Implementer fallback metier quand timeout/indisponibilite (message actionnable, `retryable=true`)
  - [x] Garantir anonymisation des donnees personnelles avant appel LLM
- [x] Exposer API v1 pour envoi/reception (AC: 1, 2, 3)
  - [x] Ajouter endpoint `POST /v1/chat/messages` (JWT requis, role `user`)
  - [x] Retourner payload unifie `{data, meta}` avec message assistant et metadonnees de traitement
  - [x] Mapper les erreurs techniques (`llm_timeout`, `llm_unavailable`, `invalid_chat_input`) vers statuts coherents (`422`/`503`)
- [x] Implementer l experience frontend minimale du chat (AC: 1, 2, 3)
  - [x] Ajouter client API central dans `frontend/src/api`
  - [x] Creer vue/composants chat de base (fil, composer, etat generation)
  - [x] Gerer etats `loading/error/empty` et message explicite en cas de fallback/retry
  - [x] Respecter accessibilite de base (focus, libelles, feedback lisible)
- [x] Tester et valider (AC: 1, 2, 3)
  - [x] Tests unitaires backend sur orchestration chat (succes, timeout, indisponibilite, fallback)
  - [x] Tests integration API (`401`, succes `200`, `503` timeout/unavailable)
  - [x] Tests frontend sur etats critiques (envoi, attente, erreur, retry visible)
  - [x] Validation finale: `ruff check .` + `pytest -q` (backend) et tests frontend existants

## Dev Notes

- Cette story couvre l echange message unique user -> assistant avec gestion d erreurs robuste.
- La persistance du contexte conversationnel multi-tours sera etendue en story 3.2; ne pas deriver sur la logique complete de memoire long terme ici.
- Reutiliser les patterns de `UserNatalChartService` pour timeout/retryable et enveloppe d erreur stable.

### Technical Requirements

- API REST versionnee `/v1` + JWT deja en place.
- Retry controle et borne (pas de boucle infinie), avec timeout explicite.
- Fallback lisible cote utilisateur en cas d indisponibilite LLM.
- Donnees LLM anonymisees avant emission (pas d identifiants personnels directs).
- Journalisation structuree des echecs LLM (latence, code erreur, retry, fallback).

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun acces DB direct depuis router.
- Le client LLM doit etre encapsule en `infra/llm/*`.
- Les contrats API restent en `snake_case` et format `{data/meta}` ou `{error}`.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, PostgreSQL.
- AuthN/AuthZ: JWT + RBAC existants (`user`, `support`, `ops`).
- Frontend: React + TypeScript, client HTTP centralise existant.
- State frontend: TanStack Query + Zustand (selon architecture cible).

### File Structure Requirements

- Cibles backend:
  - `backend/app/api/v1/routers/chat.py` (ou extension routeur existant coherent)
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/infra/llm/client.py`
  - `backend/app/infra/llm/anonymizer.py`
  - `backend/app/infra/db/models/` (conversation/message)
  - `backend/app/infra/db/repositories/` (acces conversation/message)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Cibles frontend:
  - `frontend/src/api/`
  - `frontend/src/pages/`
  - `frontend/src/components/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit backend:
  - succes message -> reponse assistant
  - timeout LLM -> fallback + erreur stable retryable
  - indisponibilite LLM -> fallback + erreur stable
  - input invalide -> `invalid_chat_input`
- Integration backend:
  - sans token -> `401`
  - role valide + envoi message -> `200`
  - timeout/unavailable -> `503` et details actionnables
- Frontend:
  - envoi message
  - etat generation visible
  - erreur + action de reprise visible
  - etats `loading/error/empty`

### Previous Story Intelligence

- Les stories 2.x ont etabli:
  - enveloppe d erreur standard
  - mapping timeout/unavailable -> `503` avec `retryable`
  - patterns de services metier minces et testables
- Reutiliser ces conventions pour eviter les divergences de contrat.

### Git Intelligence Summary

- Le repository montre un historique riche frontend precedent; la base actuelle est un re-bootstrap plus cible.
- Prioriser un delta incremental coherent avec la structure actuelle (`backend/app/*`, `frontend/src/*`) sans reintroduire une architecture legacy supprimee.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.1)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR19, NFR4, NFR16, NFR18, NFR20)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (API v1, JWT/RBAC, logs structures, Redis/PostgreSQL, separations de couches)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (chat central, etats loading/error/empty/offline, feedback clair)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution
- Backend: `ruff check backend`, `pytest -q`
- Frontend: `npm run lint`, `npm test`

### Completion Notes List

- Ajout du socle chat backend avec persistance conversation/messages, anonymisation et client LLM encapsule.
- Ajout de l endpoint `POST /v1/chat/messages` avec JWT, contrat API standard, et mapping erreurs `422/503`.
- Ajout de retry borne + erreurs actionnables (`retryable`, `fallback_message`) pour timeout/unavailable.
- Ajout d une UI chat minimale React (envoi message, fil, loading/error/empty, retry visible).
- Validation complete executee: backend `90 passed`, frontend `9 passed`, lint backend/frontend OK, build frontend OK.

### File List

- _bmad-output/implementation-artifacts/3-1-chat-astrologue-avec-envoi-reception-de-messages.md
- backend/app/core/config.py
- backend/app/main.py
- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/chat.py
- backend/app/services/chat_guidance_service.py
- backend/app/infra/llm/__init__.py
- backend/app/infra/llm/anonymizer.py
- backend/app/infra/llm/client.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/chat_conversation.py
- backend/app/infra/db/models/chat_message.py
- backend/app/infra/db/repositories/__init__.py
- backend/app/infra/db/repositories/chat_repository.py
- backend/app/tests/unit/test_chat_guidance_service.py
- backend/app/tests/integration/test_chat_api.py
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/api/chat.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx

## Change Log

- 2026-02-18: Implementation complete de la story 3.1 (backend + frontend + tests), statut passe a `review`.
