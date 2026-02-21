# Story 11.2: Modules tarot/runes derriere feature flags

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product owner,  
I want introduire tarot/runes de maniere controlee,  
so that nous puissions iterer sans destabiliser le coeur MVP.

## Acceptance Criteria

1. Given une strategie de feature flags en place, when un module est active pour un segment cible, then le flux est disponible sans impacter les utilisateurs non cibles.
2. Given un module active, when un rollback est necessaire, then la desactivation immediate est possible.

## Tasks / Subtasks

- [x] Concevoir les feature flags fonctionnels tarot/runes (AC: 1, 2)
  - [x] Definir les flags (`tarot_enabled`, `runes_enabled`) et leur scope (global, segment, utilisateur)
  - [x] Formaliser les regles de priorite/precedence (global vs segment vs override explicite)
  - [x] Documenter la strategie de rollback instantane (kill switch)
- [x] Etendre le backend pour l evaluation des flags (AC: 1, 2)
  - [x] Ajouter la lecture des flags dans la couche `services`/`domain` avant execution module
  - [x] Retourner des erreurs metier explicites quand module non autorise
  - [x] Garantir un comportement deterministe et auditable des decisions de gating
- [x] Integrer les modules tarot/runes derriere gating (AC: 1)
  - [x] Ajouter les points d entree applicatifs (chat et/ou endpoint dedie) sans casser les parcours MVP existants
  - [x] Injecter le contexte utilisateur/persona dans les traitements module
  - [x] Assurer la reinjection de resultat module dans le fil conversationnel si active
- [x] Mettre a jour l UX front pour les etats feature flags (AC: 1, 2)
  - [x] Afficher etats `module-locked`, `module-ready`, `in-progress`, `completed`, `error`
  - [x] Masquer/neutraliser proprement les modules desactivees
  - [x] Eviter tout appel API inutile quand flag inactif
- [x] Instrumenter observabilite et pilotage produit (AC: 1, 2)
  - [x] Ajouter metriques d exposition/activation/erreurs/latence par module et segment
  - [x] Ajouter traces d audit pour activation/desactivation des flags
  - [x] Exposer un minimum de KPI ops produit pour suivi d impact
- [x] Couvrir par tests et validations (AC: 1, 2)
  - [x] Tests unitaires backend sur evaluation des flags et chemins autorise/refuse
  - [x] Tests integration API sur activation segmentee et rollback immediate
  - [x] Tests frontend sur rendu des etats lock/ready/error et non-regression parcours MVP

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 11, Story 11.2).
- Cette story est post-MVP et doit rester strictement encapsulee derriere flags pour proteger les flux coeur (theme natal, chat principal, billing/privacy).
- Dependances prioritaires:
  - `_bmad-output/implementation-artifacts/11-1-raffinement-multi-persona-astrologue.md`
  - `_bmad-output/implementation-artifacts/3-1-chat-astrologue-avec-envoi-reception-de-messages.md`
  - `_bmad-output/implementation-artifacts/3-7-parametrage-des-bornes-de-persona-astrologue.md`
  - `_bmad-output/implementation-artifacts/6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`

### Technical Requirements

- Le gating doit etre applique avant tout appel couteux (LLM/calcul) pour minimiser risque et cout.
- Les decisions d activation doivent etre traçables et observables.
- Le rollback doit etre operationnel sans redeploiement applicatif.

### Architecture Compliance

- Respecter l architecture backend en couches `api/core/domain/services/infra`.
- Conserver le contrat API REST `/v1` et le format d erreur unifie.
- Respecter RBAC minimal existant pour operations sensibles d activation/deactivation.

### Library / Framework Requirements

- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic.
- Frontend: React + TypeScript + TanStack Query + Zustand.
- Tests: Pytest (backend), Vitest/Testing Library (frontend).

### File Structure Requirements

- Cibles backend probables:
  - `backend/app/services/` (evaluation feature flags, orchestration tarot/runes)
  - `backend/app/api/v1/routers/` (endpoints modules ou extensions chat)
  - `backend/app/domain/` (regles de gating metier)
  - `backend/app/infra/db/models/` et `backend/migrations/versions/` (si stockage flags persistant)
  - `backend/app/tests/`
- Cibles frontend probables:
  - `frontend/src/pages/` (vue modules specialises / integration chat)
  - `frontend/src/api/` (clients modules + flags)
  - `frontend/src/components/` (states lock/ready/error)
  - `frontend/src/tests/`

### Testing Requirements

- Verifier non-regression des parcours MVP quand flags inactifs.
- Verifier activation selective par segment et visibilite correcte cote UI.
- Verifier rollback instantane et comportement stable des sessions deja ouvertes.

### Previous Story Intelligence

- 11.1 a etabli un socle de personnalisation et d instrumentation persona reutilisable pour segmenter et mesurer les nouveaux modules.
- Conserver la logique de rollback/observabilite deja introduite sur les personas.

### Git Intelligence Summary

- Commits recents (2026-02-21) renforcent auth/role gating; aligner la story avec ce mecanisme au lieu d ajouter une deuxieme logique parallele.
- Favoriser un delta petit et coherent: gating central -> integration modules -> UI -> tests.

### Project Context Reference

- `AGENTS.md`: deltas minimaux, code maintenable, tests/lint obligatoires, stack imposee.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 11, Story 11.2)
- `_bmad-output/planning-artifacts/ux-design-specification.md` (sections modules specialises et states lock/ready)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/11-1-raffinement-multi-persona-astrologue.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/ux-design-specification.md`
- `_bmad-output/implementation-artifacts/11-1-raffinement-multi-persona-astrologue.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Completion Notes List

- Ajout d un socle feature flags persistent (`feature_flags`) avec segmentation par role/utilisateur et kill switch ops.
- Ajout d un router ops dedie (`/v1/ops/feature-flags`) avec RBAC ops, rate limiting et audit des updates.
- Ajout d endpoints modules chat (`/v1/chat/modules/availability`, `/v1/chat/modules/{module}/execute`) relies au quota et au gating.
- Execution modules tarot/runes implementee avec reinjection optionnelle dans conversation et attribution persona active.
- Instrumentation metriques modules ajoutee: exposition, activation, erreurs, latence.
- UI chat enrichie avec etats `module-locked`, `module-ready`, `in-progress`, `completed`, `error`.
- Tests ajoutes backend (unit + integration) et frontend (ChatPage modules).
- Correctif review: le quota est maintenant consomme uniquement apres validation de disponibilite module.
- Correctif review: `conversation_forbidden` est mappe en HTTP 403 sur l endpoint modules.
- Correctif review: precedence de segmentation clarifiee avec priorite `target_user_ids` (override explicite).
- Validations executees:
  - backend: `ruff format .`, `ruff check .`, `pytest -q app/tests/unit/test_feature_flag_service.py app/tests/integration/test_ops_feature_flags_api.py app/tests/integration/test_chat_api.py`
  - frontend: `npm run lint`, `npm run test -- src/tests/ChatPage.test.tsx`

### File List

- `_bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/infra/db/models/feature_flag.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/feature_flag_service.py`
- `backend/app/api/v1/routers/ops_feature_flags.py`
- `backend/app/api/v1/routers/chat_modules.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/api/v1/routers/auth.py`
- `backend/app/main.py`
- `backend/migrations/versions/20260221_0021_add_feature_flags_table.py`
- `backend/app/tests/unit/test_feature_flag_service.py`
- `backend/app/tests/integration/test_ops_feature_flags_api.py`
- `backend/app/tests/integration/test_chat_api.py`
- `frontend/src/api/chat.ts`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/tests/ChatPage.test.tsx`
