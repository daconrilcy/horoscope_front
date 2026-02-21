# Story 3.5: Guidance contextuelle sur situation critique

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want demander une guidance contextuelle sur ma situation du moment,  
so that je recois des conseils personnalises pour une decision immediate.

## Acceptance Criteria

1. Given un profil utilisateur complet et un contexte saisi, when l utilisateur demande une guidance contextuelle, then la reponse prend en compte le contexte explicite fourni.
2. Les recommandations restent actionnables, prudentes et coherentes avec les garde-fous metier.

## Tasks / Subtasks

- [x] Definir le cadre guidance contextuelle MVP (AC: 1, 2)
  - [x] Definir le payload d entree (`situation`, `objective`, `time_horizon` optionnel)
  - [x] Definir le format de sortie standard (synthese, axes de lecture, actions conseillees, disclaimer)
  - [x] Definir les bornes de garde-fous (pas d injonction medicale/legale/financiere)
- [x] Etendre la couche metier backend (AC: 1, 2)
  - [x] Ajouter service de guidance contextuelle (extension de `guidance_service` ou service dedie)
  - [x] Integrer profil natal + contexte utilisateur saisi + contexte conversationnel cible
  - [x] Ajouter erreurs metier stables (`invalid_guidance_context`, `missing_birth_profile`)
- [x] Exposer API v1 guidance contextuelle (AC: 1, 2)
  - [x] Ajouter endpoint `POST /v1/guidance/contextual`
  - [x] Conserver contrat `{data, meta}` + enveloppe erreur standard
  - [x] Proteger endpoint via JWT + RBAC `user`
- [x] Integrer garde-fous IA (AC: 2)
  - [x] Prompt policy prudent + bornes explicites
  - [x] Anonymisation avant appel LLM
  - [x] Retry/fallback coherent avec stories 3.1/3.4
- [x] Mettre a jour UI minimale (AC: 1, 2)
  - [x] Ajouter formulaire de guidance contextuelle (situation + objectif)
  - [x] Afficher reponse structuree avec etats `loading/error/empty`
  - [x] Conserver continuite UX avec chat/historique sans regression
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires backend: validation contexte, profil manquant, format reponse
  - [x] Tests integration API: succes guidance contextuelle, erreurs metier stables, RBAC
  - [x] Tests frontend: saisie contexte, rendu guidance, etats critiques
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story 3.1: orchestration LLM + retry/fallback.
- Story 3.2: persistance du contexte conversationnel.
- Story 3.3: historique/reprise des conversations.
- Story 3.4: guidance periodique guardrailed.
- Cette story etend vers guidance contextuelle immediate sans casser les contrats existants.

### Technical Requirements

- Le contexte saisi par utilisateur doit etre valide et non vide.
- Reponse contextualisee basee sur profil natal + situation.
- Sortie guardrailed, prudente, actionnable, non prescriptive sur domaines sensibles.
- Erreurs metier stables et mapping HTTP coherent.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- Pas d acces DB direct depuis router.
- Endpoints versionnes `/v1`, schemas `snake_case`.
- Observabilite minimale des erreurs/latence guidance.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy.
- DB: PostgreSQL (SQLite local test acceptable).
- Auth: JWT + RBAC existants.
- Frontend: React + TypeScript + client API central.

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/api/v1/routers/guidance.py`
  - `backend/app/services/guidance_service.py`
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Cibles frontend probables:
  - `frontend/src/api/guidance.ts`
  - `frontend/src/pages/ChatPage.tsx` (ou vue dediee guidance)
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - validation payload contextuel
  - mapping erreurs metier
  - non-regression guardrails/disclaimer
- Integration:
  - `POST /v1/guidance/contextual` succes
  - `401/403/404/422/503` selon cas
  - enveloppe erreur standard
- Frontend:
  - saisie et envoi guidance contextuelle
  - rendu structure et etats critiques
  - non-regression chat/guidance periodique

### Previous Story Intelligence

- Reutiliser patterns robustes etablis en 3.4 (anti-fuite prompt, ciblage conversation, budget de contexte).
- Eviter duplication de logique entre guidance periodique et contextuelle.

### Git Intelligence Summary

- Repository en re-bootstrap; preferer deltas localises et incrementaux.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 3, Story 3.5)
- Story precedente: `_bmad-output/implementation-artifacts/3-4-guidance-quotidienne-et-hebdomadaire.md`
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR17, NFR3, NFR4, NFR16, NFR20)
- Architecture: `_bmad-output/planning-artifacts/architecture.md`
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Create-story workflow execution
- Dev-story workflow implementation:
  - `.\.venv\Scripts\Activate.ps1; ruff check .`
  - `.\.venv\Scripts\Activate.ps1; pytest -q`
  - `npm run lint`
  - `npm test -- --run`
  - `npm run build`

### Completion Notes List

- Endpoint `POST /v1/guidance/contextual` implemente avec RBAC `user`, enveloppe standard et mapping d erreurs metier stable.
- Service contextuel ajoute avec validation du contexte, integration profil natal, ciblage optionnel de conversation et garde-fous/retry.
- Frontend chat etendu avec formulaire de guidance contextuelle et rendu structure (`loading/error/empty`).
- Couverture test completee backend/frontend, sans regression sur chat et guidance periodique.

### File List

- _bmad-output/implementation-artifacts/3-5-guidance-contextuelle-sur-situation-critique.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/guidance.py
- backend/app/services/guidance_service.py
- backend/app/tests/integration/test_guidance_api.py
- backend/app/tests/unit/test_guidance_service.py
- frontend/src/api/guidance.ts
- frontend/src/pages/ChatPage.tsx
- frontend/src/tests/ChatPage.test.tsx
