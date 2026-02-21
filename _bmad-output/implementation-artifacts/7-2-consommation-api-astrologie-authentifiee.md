# Story 7.2: Consommation API astrologie authentifiee

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an enterprise client,  
I want appeler l API pour recuperer le contenu astrologique contractuel,  
so that je l integre dans mon offre (ex: page astrologie hebdo).

## Acceptance Criteria

1. Given une cle API B2B valide et active, when le client appelle les endpoints B2B astrologie, then les reponses sont authentifiees et retournees avec payload coherent.
2. Given une cle API valide, when le client appelle les endpoints B2B versionnes, then les contrats de reponse restent explicites et stables sous `/v1`.
3. Given une cle API absente/invalide/revoquee, when un appel est effectue, then une erreur standardisee est renvoyee avec `code`, `message`, `details`, `request_id`.
4. Given un appel B2B soumis aux limites d usage, when la limite est depassee, then une erreur standardisee de quota/rate limit est renvoyee.

## Tasks / Subtasks

- [x] Definir le contrat d authentification B2B par cle API (AC: 1, 3)
  - [x] Ajouter une dependance backend dediee (`require_b2b_api_key`) avec lecture header explicite
  - [x] Verifier le prefix + hash de secret et l etat actif de la credential
  - [x] Retourner des erreurs standardisees (`missing_api_key`, `invalid_api_key`, `revoked_api_key`)
- [x] Exposer endpoints B2B astrologie versionnes (AC: 1, 2)
  - [x] Ajouter routeur `/v1/b2b/astrology/*`
  - [x] Ajouter endpoint minimal de contenu contractuel (ex: `weekly-by-sign`)
  - [x] Garantir reponse structuree stable et versionnee
- [x] Integrer controle quota/rate limiting B2B (AC: 4)
  - [x] Appliquer rate limiting global + par credential/client
  - [x] Renvoyer erreurs standardisees en cas de depassement
  - [x] Ajouter metadonnees utiles (`retry_after` si disponible)
- [x] Ajouter audit et observabilite appels B2B (AC: 1, 3, 4)
  - [x] Journaliser les actions sensibles B2B avec `request_id`
  - [x] Auditer les echecs auth critiques (invalid/revoked)
  - [x] Ajouter compteurs techniques minimaux (volume appels, erreurs auth)
- [x] Integrer un client frontend de demonstration B2B (AC: 2, 3)
  - [x] Ajouter client API dans `frontend/src/api/` pour endpoint B2B
  - [x] Ajouter panneau simple de test (etat loading/error/empty)
  - [x] Afficher erreurs standardisees remontees par l API
- [x] Tester et valider la story (AC: 1, 2, 3, 4)
  - [x] Unit tests backend: validation API key + statuts (active/revoked)
  - [x] Integration tests backend: 200/401/403/429 + format erreurs
  - [x] Tests frontend: affichage data + gestion erreurs
  - [x] Validation finale: `ruff check backend` + `pytest -q backend` + `npm run lint` + `npm test -- --run`

## Dev Notes

- Story source: Epic 7 Story 7.2 (FR39), dependante directe de Story 7.1 (credentials B2B).
- Reutiliser les patterns etablis:
  - routeurs v1 avec enveloppe d erreur uniforme
  - RBAC et auth existants + request id
  - rate limiting compose et audit des actions sensibles
- Contraintes critiques:
  - aucun endpoint B2B astrologie sans verification de cle active
  - contrats stables sous `/v1`
  - erreurs auth/quota strictement standardisees

### Technical Requirements

- Authentification B2B par cle API active uniquement (secret compare via hash).
- Reponses versionnees et contractuelles pour integration client entreprise.
- Erreurs stables `snake_case` avec `request_id`.
- Rate limiting et signaux de quota sur endpoints B2B.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- Reutiliser briques Story 7.1 pour credentials (ne pas dupliquer logique).
- Maintenir separation claire entre auth utilisateur JWT et auth API key B2B.
- Observabilite centralisee (logs + audit + metriques minimales).

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Redis.
- Frontend: React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest + Testing Library frontend.

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/api/dependencies/` (auth B2B API key)
  - `backend/app/api/v1/routers/` (nouveau routeur astrology B2B)
  - `backend/app/services/` (service contenu astrology B2B)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/`
  - `frontend/src/components/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - validation des cles API (active/revoked/invalide)
  - mapping erreurs metier -> erreurs API
- Integration:
  - scenarios auth (missing/invalid/revoked/ok)
  - scenarios quota/rate limiting (429)
  - format d erreur uniforme
- Frontend:
  - etats `loading/error/empty`
  - rendu des donnees B2B et affichage erreurs

### Previous Story Intelligence

- Story 7.1 a etabli:
  - gestion credentials entreprise (generation/rotation/list)
  - audit transactionnel + RBAC `enterprise_admin`
  - modeles DB entreprise + contraintes de securite
- Pour 7.2:
  - s appuyer sur ces credentials sans recoder la securite
  - se concentrer sur consommation API contractuelle et robuste

### Git Intelligence Summary

- Les stories recentes privilegient robustesse security/audit + tests integration.
- Continuer avec deltas limites et verification AC par tests.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 7, Story 7.2)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR39, NFR17, NFR18)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (API versioning, auth, observabilite)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (etats `loading/error/empty`)
- Story precedente: `_bmad-output/implementation-artifacts/7-1-espace-compte-entreprise-et-gestion-des-credentials-api.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/epics.md`

### Completion Notes List

- Authentification API key B2B implemente en dependance dediee avec erreurs standardisees (401/403/503) et `request_id`.
- Endpoint versionne `/v1/b2b/astrology/weekly-by-sign` ajoute avec contrats explicites, reponse stable et rate limiting global/account/credential.
- Observabilite ajoutee: compteurs appels/erreurs auth + audit des echecs auth.
- Frontend ajoute: client `b2bAstrology` + panneau `B2BAstrologyPanel` avec etats loading/error/empty et affichage `request_id`.
- Tests ajoutes backend (unit + integration) et frontend (panel B2B), puis validations executees (ruff/pytest/eslint/vitest).

### File List

- `backend/app/services/enterprise_credentials_service.py`
- `backend/app/api/dependencies/b2b_auth.py`
- `backend/app/services/b2b_astrology_service.py`
- `backend/app/api/v1/routers/b2b_astrology.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/main.py`
- `backend/app/tests/unit/test_enterprise_api_key_auth_service.py`
- `backend/app/tests/integration/test_b2b_astrology_api.py`
- `frontend/src/api/b2bAstrology.ts`
- `frontend/src/components/B2BAstrologyPanel.tsx`
- `frontend/src/tests/B2BAstrologyPanel.test.tsx`
- `frontend/src/App.tsx`
