# Story 3.4: Guidance quotidienne et hebdomadaire

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want obtenir des guidances periodiques liees a mon profil,  
so that je dispose d un accompagnement utile au bon moment.

## Acceptance Criteria

1. Given un profil utilisateur complet, when il demande une guidance journaliere ou hebdomadaire, then la reponse est adaptee a son profil et a la temporalite demandee.
2. Le format de sortie reste coherent avec les garde-fous metier.

## Tasks / Subtasks

- [x] Definir le cadre guidance MVP (AC: 1, 2)
  - [x] Definir les temporalites supportees (`daily`, `weekly`) et leurs contraintes d entree
  - [x] Definir le format de sortie standard (resume, points clefs, conseils actionnables, disclaimer)
  - [x] Definir les bornes de garde-fous (pas de medical/legal/financial absolu, ton prudent)
- [x] Etendre la couche metier backend (AC: 1, 2)
  - [x] Ajouter un service `guidance_service` (ou extension coherente) pour construire la guidance profilee
  - [x] Integrer les donnees utilisateur necessaires (profil natal + contexte conversationnel minimal utile)
  - [x] Ajouter des erreurs metier stables (`invalid_guidance_period`, `missing_birth_profile`)
- [x] Exposer API v1 guidance (AC: 1, 2)
  - [x] Ajouter endpoint `POST /v1/guidance` avec payload `{period: daily|weekly}`
  - [x] Conserver contrat `{data, meta}` et enveloppe erreur `{error: {code, message, details, request_id}}`
  - [x] Proteger endpoint par JWT + role `user`
- [x] Integrer garde-fous IA (AC: 2)
  - [x] Appliquer un prompt/cadrage metier explicite pour reponse guidance
  - [x] Conserver anonymisation avant appel LLM
  - [x] Conserver fallback/retry et message actionnable en cas d indisponibilite
- [x] Mettre a jour UI minimale guidance (AC: 1, 2)
  - [x] Ajouter action utilisateur pour demander guidance du jour/semaine
  - [x] Afficher reponse structuree avec etats `loading/error/empty`
  - [x] Assurer continuite UX avec le chat existant sans conflit de flux
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires backend: period validation, profil manquant, format reponse
  - [x] Tests integration API: succes daily/weekly, erreurs metier stables, RBAC
  - [x] Tests frontend: rendu des 2 temporalites, etats critiques, non-regression chat
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story 3.1 a introduit l orchestration LLM avec retry/fallback et anonymisation.
- Story 3.2 a introduit la persistance de contexte conversationnel.
- Story 3.3 a introduit l historique/reprise des conversations.
- Cette story ajoute une guidance periodique orientee profil sans casser les contrats existants.

### Technical Requirements

- Guidance basee sur profil utilisateur valide (donnees natales presentes).
- Temporalites strictes: `daily` et `weekly` uniquement.
- Reponse structuree et guardrailed (prudente, non prescriptive medicale/legale/financiere).
- Coherence des envelopes API et mapping erreurs stable.

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun acces DB direct dans les routers.
- API versionnee `/v1`, conventions `snake_case`.
- Observabilite minimum sur erreurs/latence guidance.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy.
- DB: PostgreSQL (SQLite local test acceptable).
- Auth: JWT + RBAC existants.
- Frontend: React + TypeScript + client API central.

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/api/v1/routers/` (nouveau routeur `guidance.py` ou extension routeur existant)
  - `backend/app/services/` (nouveau `guidance_service.py`)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Cibles frontend probables:
  - `frontend/src/api/`
  - `frontend/src/pages/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - validation periode guidance
  - rejection profil manquant
  - format de sortie stable
- Integration:
  - `POST /v1/guidance` succes `daily` et `weekly`
  - `401/403/422/503` selon cas
  - enveloppe erreur standard
- Frontend:
  - action guidance day/week
  - affichage structure + etats loading/error/empty
  - non-regression flux chat

### Previous Story Intelligence

- Reutiliser les patterns services/erreurs de `chat_guidance_service`.
- Conserver la meme philosophie de retry/fallback/anonymisation deja en place.

### Git Intelligence Summary

- Monorepo en re-bootstrap; maintenir des changements incrementaux localises.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.4)
- Stories precedentes:
  - `_bmad-output/implementation-artifacts/3-1-chat-astrologue-avec-envoi-reception-de-messages.md`
  - `_bmad-output/implementation-artifacts/3-2-persistance-du-contexte-conversationnel.md`
  - `_bmad-output/implementation-artifacts/3-3-historique-et-reprise-des-conversations.md`
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR16, NFR3, NFR4, NFR16, NFR20)
- Architecture: `_bmad-output/planning-artifacts/architecture.md`
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution
- Backend: `ruff check .`, `pytest -q`
- Frontend: `npm run lint`, `npm test -- --run`, `npm run build`

### Completion Notes List

- Ajout d un service guidance periodique (`daily`/`weekly`) base sur profil utilisateur et contexte conversationnel recent.
- Ajout endpoint `POST /v1/guidance` avec contrats standards, JWT/RBAC et mapping erreurs stable.
- Ajout garde-fous IA: prompt prudent, anonymisation avant LLM, fallback/retry avec message actionnable.
- Ajout UI guidance minimale dans le chat avec actions jour/semaine et etats `loading/error/empty`.
- Validation complete executee: backend `119 passed`, frontend `13 passed`, lint backend/frontend OK, build frontend OK.

### File List

- _bmad-output/implementation-artifacts/3-4-guidance-quotidienne-et-hebdomadaire.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/main.py
- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/guidance.py
- backend/app/services/guidance_service.py
- backend/app/tests/unit/test_guidance_service.py
- backend/app/tests/integration/test_guidance_api.py
- frontend/src/api/guidance.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx

## Change Log

- 2026-02-19: Implementation complete de la story 3.4 (backend + frontend + tests), statut passe a `review`.
