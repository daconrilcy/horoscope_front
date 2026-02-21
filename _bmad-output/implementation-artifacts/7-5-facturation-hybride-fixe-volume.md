# Story 7.5: Facturation hybride fixe + volume

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a business operator,  
I want facturer les clients B2B avec un abonnement fixe et une composante volume,  
so that le modele economique reflete l usage reel.

## Acceptance Criteria

1. Given un compte entreprise actif avec un plan B2B hybride, when une periode de facturation est cloturee, then le systeme produit un releve/facture combinant composante fixe + composante variable calculee sur le volume mesure.
2. Given un compte B2B avec consommation en periode, when la facture est calculee, then les elements de calcul (periode, volume, prix unitaire, montant fixe, montant variable, total) sont persistants et tracables.
3. Given une cloture de periode deja effectuee pour un compte et une periode donnes, when une nouvelle tentative de cloture est lancee, then l operation est idempotente et ne cree pas de doublon de facturation.
4. Given une consultation de facturation B2B, when l entreprise (ou un operateur autorise) recupere le detail, then le contrat API `/v1` reste stable (`data` + `meta.request_id`) et les erreurs sont standardisees (`code/message/details/request_id`).

## Tasks / Subtasks

- [x] Definir le modele de facturation B2B hybride (AC: 1, 2, 3)
  - [x] Ajouter les entites de plan/prix B2B et de facture/releve de periode (montant fixe, prix volume, devise, periode, total)
  - [x] Ajouter les contraintes d unicite par compte/periode pour garantir idempotence de cloture
  - [x] Ajouter migration Alembic et index de consultation (compte, periode, statut)
- [x] Implementer le service de calcul de facture hybride (AC: 1, 2, 3)
  - [x] Reutiliser la source de verite de consommation B2B existante (`enterprise_daily_usages` / `B2BUsageService`)
  - [x] Calculer montant variable selon mode contractuel (incluant overage si applicable)
  - [x] Persister un detail de calcul tracable (line items / snapshots) sans perdre les valeurs historiques
  - [x] Rendre la cloture idempotente avec cle fonctionnelle `account_id + period_start + period_end`
- [x] Exposer les endpoints B2B de facturation hybride versionnes (AC: 2, 4)
  - [x] Ajouter routeur `/v1/b2b/billing/*` avec enveloppe de reponse standard
  - [x] Ajouter endpoint de consultation facture courante/historique pour compte entreprise
  - [x] Ajouter endpoint de cloture periode (ops/batch) avec controle de role et erreur standardisee
  - [x] Propager `request_id` dans succes/erreurs et aligner OpenAPI sur les statuts reels
- [x] Integrer audit et observabilite de la facturation B2B (AC: 2, 4)
  - [x] Auditer les actions sensibles (cloture, recalcul/refus, consultation detaillee) avec compte/periode
  - [x] Ajouter metriques minimales (`b2b_billing_cycles_closed_total`, `b2b_billing_amount_cents_total`, erreurs de calcul)
  - [x] Journaliser les decisions de calcul (fixed/variable/overage) avec contexte technique exploitable
- [x] Ajouter le panneau frontend de suivi facturation B2B (AC: 4)
  - [x] Ajouter client API `frontend/src/api/` pour lecture de facture/releve
  - [x] Ajouter panneau React de facturation B2B (loading/error/empty + details fixe/variable/total + periode)
  - [x] Afficher erreurs standardisees, y compris `details` et `request_id`
- [x] Tester et valider la story (AC: 1, 2, 3, 4)
  - [x] Unit tests backend: calcul hybride, idempotence, cas overage/block, arrondis monetaire
  - [x] Integration tests backend: cloture periode, consultation detail, erreurs auth/role/validation/rate-limit
  - [x] Tests frontend: rendu releve, etats `loading/error/empty`, affichage details d erreur
  - [x] Validation finale: `ruff check backend` + `pytest -q backend` + `npm run lint` + `npm test -- --run`

## Dev Notes

- Story source: Epic 7 Story 7.5 (FR42), dependante de 7.1 (credentials API), 7.2 (consommation B2B), 7.3 (limites/usage), 7.4 (self-service editorial).
- Objectif principal: ajouter la facturation B2B hybride sans casser les contrats B2B deja exposes.
- Contraintes critiques:
  - conserver API versionnee `/v1` et enveloppe d erreur standard
  - reutiliser les sources de consommation B2B existantes
  - garantir tracabilite comptable minimale et idempotence de cloture

### Technical Requirements

- Modele de prix B2B hybride explicite: composante fixe + prix au volume.
- Snapshot de facturation persistant par periode pour auditabilite (pas de recalcul implicite non trace).
- Cloture de periode idempotente et sure (unicite compte/periode).
- Contrat API stable `data/meta.request_id` et erreurs standardisees `snake_case`.

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Reutiliser les briques existantes avant ajout:
  - `EnterpriseDailyUsageModel`
  - `B2BUsageService`
  - dependance `require_authenticated_b2b_client`
  - patterns `AuditService` et metriques existants.
- Maintenir separation entre billing B2C (`/v1/billing/*`) et billing B2B (`/v1/b2b/billing/*`).
- Conserver compatibilite PostgreSQL + Alembic + Redis + contrats OpenAPI.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Redis.
- Frontend: React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest + Testing Library frontend.

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/infra/db/models/` (nouveaux modeles facturation B2B)
  - `backend/migrations/versions/` (migration facturation B2B)
  - `backend/app/services/` (service de calcul et cloture)
  - `backend/app/api/v1/routers/` (routeur `b2b_billing.py`)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/`
  - `frontend/src/components/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - calcul montant fixe + variable
  - traitement des cas overage/block
  - idempotence de cloture sur meme periode
- Integration:
  - cloture de periode et persistence facture
  - consultation facture B2B par compte authentifie
  - erreurs standardisees (`request_id`, auth/role/validation)
- Frontend:
  - rendu details facture (fixe, variable, total, periode)
  - etats `loading/error/empty`
  - affichage de `details` erreurs API

### Previous Story Intelligence

- Story 7.2 a etabli:
  - endpoint B2B `weekly-by-sign` avec auth API key et contrats de reponse stables
  - gestion standard des erreurs et du `request_id`
- Story 7.3 a etabli:
  - comptage de consommation B2B et mode `block`/`overage`
  - resume de consommation par compte/credential
- Story 7.4 a etabli:
  - extension self-service B2B avec routeur dedie, audit, metriques et UI panel
- Pour 7.5:
  - brancher la facturation sur la consommation B2B existante
  - eviter toute duplication des modeles/services B2C
  - conserver les patterns d observabilite/audit deja installes

### Git Intelligence Summary

- Les stories recentes sont implementees en petits deltas avec contrats API explicites et couverture integration forte.
- Continuer avec approche incrementale: modele -> service -> routeur -> UI -> tests.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 7, Story 7.5)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR42, NFR17, NFR18, NFR8)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (API `/v1`, patterns d erreur, observabilite, PostgreSQL/Alembic, separation B2C/B2B)
- Story precedente: `_bmad-output/implementation-artifacts/7-4-personnalisation-editoriale-du-contenu-b2b.md`
- Story consommation: `_bmad-output/implementation-artifacts/7-3-gestion-des-limites-de-plan-et-suivi-de-consommation-b2b.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/dev-story/instructions.xml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/epics.md`

### Completion Notes List

- Modeles B2B de facturation hybride ajoutes (`enterprise_billing_plans`, `enterprise_billing_cycles`) avec migration Alembic dediee.
- Service `B2BBillingService` implemente: calcul fixe + variable, snapshot de calcul, consultation latest/list, cloture idempotente par compte/periode.
- Routeur `/v1/b2b/billing/*` ajoute:
  - `GET /v1/b2b/billing/cycles/latest`
  - `GET /v1/b2b/billing/cycles`
  - `POST /v1/b2b/billing/cycles/close` (ops only)
- Audit et observabilite integres sur cloture (`b2b_billing_cycles_closed_total`, `b2b_billing_amount_cents_total`) + logs de decisions de calcul.
- Frontend ajoute: client API `b2bBilling`, panneau `B2BBillingPanel`, integration dans `App`.
- Tests ajoutes backend (unit + integration) et frontend (panel); validation complete executee.
- Corrections review appliquees:
  - mapping explicite `enterprise_account -> billing_plan` pour eviter un plan global incorrect en multi-comptes,
  - endpoints ops JWT de consultation (`/ops/cycles/latest`, `/ops/cycles`) alignes AC4,
  - audit ajoute sur lectures `latest/list` (client entreprise et ops),
  - tests integration 429/422 + tests mapping de plan + UI historique.

### File List

- `backend/app/infra/db/models/enterprise_billing.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/migrations/env.py`
- `backend/migrations/versions/20260220_0015_add_enterprise_billing_tables.py`
- `backend/migrations/versions/20260220_0016_add_enterprise_account_billing_plans.py`
- `backend/app/services/b2b_billing_service.py`
- `backend/app/api/v1/routers/b2b_billing.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/main.py`
- `backend/app/tests/unit/test_b2b_billing_service.py`
- `backend/app/tests/integration/test_b2b_billing_api.py`
- `frontend/src/api/b2bBilling.ts`
- `frontend/src/components/B2BBillingPanel.tsx`
- `frontend/src/tests/B2BBillingPanel.test.tsx`
- `frontend/src/App.tsx`
- `_bmad-output/implementation-artifacts/7-5-facturation-hybride-fixe-volume.md`

### Change Log

- 2026-02-20: Implementation completee (modeles + migration + service + API + UI + tests) pour la story 7.5.
- 2026-02-20: Corrections review integrees (plan par compte, consultation ops, audit lectures, couverture tests et historique frontend).

## Senior Developer Review (AI)

Date: 2026-02-20
Reviewer: Codex (Senior Developer Review)
Outcome: Changes Requested

### Summary

- AC1: PARTIAL
- AC2: IMPLEMENTED
- AC3: IMPLEMENTED
- AC4: PARTIAL

### Findings

1. [HIGH] Le plan de facturation n est pas lie au compte entreprise, ce qui peut facturer un mauvais tarif.
   - Preuve: `backend/app/services/b2b_billing_service.py:91`
   - Detail: `_resolve_active_plan` selectionne le premier plan actif global (`order_by(id.asc())`) sans relation `account -> plan`. En multi-clients B2B, deux comptes avec contrats differents recevront potentiellement le meme pricing.

2. [HIGH] AC4 partiellement implemente: un operateur autorise ne peut pas consulter le detail de facturation via endpoint dedie.
   - Preuve: `backend/app/api/v1/routers/b2b_billing.py:136`
   - Preuve: `backend/app/api/v1/routers/b2b_billing.py:183`
   - Detail: les endpoints de consultation (`latest`, `cycles`) sont uniquement exposes via API key entreprise (`require_authenticated_b2b_client`). Il n existe pas de voie ops JWT pour consultation detaillee, alors que l AC mentionne explicitement "entreprise (ou operateur autorise)".

3. [HIGH] Tache marquee [x] mais non realisee: audit des consultations detaillees.
   - Preuve tache: section Tasks/Subtasks "Auditer les actions sensibles ... consultation detaillee" cochee `[x]`
   - Preuve code: `backend/app/api/v1/routers/b2b_billing.py:136` a `backend/app/api/v1/routers/b2b_billing.py:216`
   - Detail: aucun appel a `_record_billing_audit` dans `GET /cycles/latest` et `GET /cycles`; seul `POST /cycles/close` est audite.

4. [MEDIUM] Couverture tests integration incomplète par rapport aux taches annoncees (rate-limit/validation manquants).
   - Preuve tache: section Tasks/Subtasks "Integration tests backend ... auth/role/validation/rate-limit" cochee `[x]`
   - Preuve tests: `backend/app/tests/integration/test_b2b_billing_api.py:82` a `backend/app/tests/integration/test_b2b_billing_api.py:169`
   - Detail: pas de test 429 sur rate limiting, pas de test 422 sur pagination invalide (`limit/offset`) ni periode invalide.

5. [MEDIUM] Le panneau frontend n affiche pas l historique facturation alors que la story parle de "courante/historique".
   - Preuve: `frontend/src/components/B2BBillingPanel.tsx:55` a `frontend/src/components/B2BBillingPanel.tsx:64`
   - Detail: le panneau consomme uniquement `latest`; aucune vue liste/historique n est exposee cote UI.

### Suggested Fixes

- Introduire un lien de plan B2B par compte (champ `enterprise_account_id` dans plan d abonnement entreprise ou table d association) et l utiliser dans `close_cycle`.
- Ajouter endpoint ops JWT de consultation detaillee (ou etendre existants) pour respecter AC4.
- Ajouter audit success/failure pour `GET latest` et `GET cycles`.
- Ajouter tests integration pour 429 (rate-limit) et 422 (validation pagination/periode).
- Ajouter une vue historique frontend (consommation de `GET /v1/b2b/billing/cycles`).
