# Story 10.1: Couverture tests frontend B2B completee

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend engineer,  
I want couvrir les clients API B2B avec des tests dedies,  
so that les regressions front B2B soient detectees tot.

## Acceptance Criteria

1. Given les modules frontend B2B existants, when les tests sont ajoutes et executes, then les chemins nominaux et erreurs sont couverts.
2. Given le perimetre B2B critique du frontend, when la campagne de tests est lancee, then la couverture obtenue est alignee avec le niveau de criticite.

## Tasks / Subtasks

- [x] Cartographier le perimetre frontend B2B critique et les risques de regression (AC: 1, 2)
  - [x] Identifier les clients API B2B utilises en production (`credentials`, `usage`, `editorial`, `billing`)
  - [x] Lister les ecrans/composants B2B relies a ces clients
  - [x] Prioriser les parcours selon impact business (lecture etat compte, consultation quotas/usage, facturation, erreurs d acces)
- [x] Completer les tests unitaires/integration des clients API B2B (AC: 1)
  - [x] Couvrir les reponses nominales (200) pour chaque client B2B critique
  - [x] Couvrir les erreurs metier/API (`401`, `403`, `404`, `409`, `429`, erreurs standardisees)
  - [x] Verifier la propagation correcte des messages d erreur et `request_id`
- [x] Completer les tests des composants/pages B2B relies aux clients (AC: 1, 2)
  - [x] Couvrir les etats `loading`, `error`, `empty`, `success` des panneaux B2B
  - [x] Verifier les interactions utilisateur principales (refresh, filtres, actions self-service si presentes)
  - [x] Verifier l affichage des details critiques (consommation, limites, facture courante/historique selon UI disponible)
- [x] Renforcer la robustesse des scenarios asynchrones et retry front (AC: 1)
  - [x] Tester les comportements TanStack Query en cas d echec/retry
  - [x] Verifier l absence de regressions sur les invalidations de cache B2B
- [x] Integrer un controle de couverture B2B dans le workflow qualite frontend (AC: 2)
  - [x] Definir un seuil minimum de couverture pour le scope B2B critique
  - [x] Ajouter la commande de verification dans le script qualite frontend existant
  - [x] Documenter la commande et l interpretation du resultat
- [x] Executer validation complete et documenter le bilan (AC: 1, 2)
  - [x] Executer `npm run lint`
  - [x] Executer `npm run test -- --run`
  - [x] Produire un court recap de couverture et des zones restantes a risque

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 10, Story 10.1).
- Positionnement: premiere story de l Epic 10, orientee excellence operationnelle front pour le scope B2B deja implemente dans Epic 7.
- Dependances directes:
  - `7-1-espace-compte-entreprise-et-gestion-des-credentials-api.md`
  - `7-3-gestion-des-limites-de-plan-et-suivi-de-consommation-b2b.md`
  - `7-4-personnalisation-editoriale-du-contenu-b2b.md`
  - `7-5-facturation-hybride-fixe-volume.md`

### Technical Requirements

- Focus prioritaire sur la non-regression des modules frontend B2B critiques exposes aux clients entreprise.
- Les tests doivent couvrir les chemins nominaux + erreurs API standardisees.
- Le niveau de couverture doit etre mesurable et explicite sur le perimetre B2B critique.

### Architecture Compliance

- Respecter la structure frontend existante (`src/api`, `src/components`, `src/tests`).
- Conserver la separation:
  - client HTTP centralise dans `frontend/src/api/client.ts`,
  - logique de recuperation server state via TanStack Query,
  - presentation dans composants/pages.
- Ne pas dupliquer les helpers de tests si des utilitaires existent deja.

### Library / Framework Requirements

- Frontend: React + TypeScript + TanStack Query + Zustand.
- Tests frontend: Vitest + Testing Library.
- Qualite: type-check TypeScript strict (commande `npm run lint`) + suite tests frontend (`npm run test -- --run`).

### File Structure Requirements

- Cibles probables:
  - `frontend/src/api/*.ts` (clients B2B)
  - `frontend/src/components/*B2B*.tsx`
  - `frontend/src/tests/*.test.tsx`
  - `frontend/package.json` (scripts coverage si necessaire)
  - `frontend/README.md` ou doc equivalente pour commandes qualite

### Testing Requirements

- Verifier au minimum:
  - couverture des appels API B2B critiques en succes et echec,
  - couverture des etats UI critiques B2B (`loading/error/empty/success`),
  - validation des messages d erreurs standardises et `request_id`,
  - execution verte lint + tests frontend.

### Previous Story Intelligence

- Epic 7 a etabli les modules fonctionnels B2B; cette story consolide leur fiabilite cote frontend.
- Les revues recentes ont insiste sur la couverture des cas erreurs et la stabilite des contrats API.

### Git Intelligence Summary

- Traiter en petits deltas incrementaux par bloc fonctionnel (API client puis composants puis quality gate).
- Eviter les refactors larges hors objectif de test coverage.

### Project Context Reference

- `AGENTS.md`: React obligatoire, tests/lint obligatoires, minimiser le delta, verifier localement.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 10, Story 10.1)
- `_bmad-output/planning-artifacts/architecture.md` (patterns frontend, erreurs API, quality workflow)
- `_bmad-output/implementation-artifacts/7-1-espace-compte-entreprise-et-gestion-des-credentials-api.md`
- `_bmad-output/implementation-artifacts/7-3-gestion-des-limites-de-plan-et-suivi-de-consommation-b2b.md`
- `_bmad-output/implementation-artifacts/7-4-personnalisation-editoriale-du-contenu-b2b.md`
- `_bmad-output/implementation-artifacts/7-5-facturation-hybride-fixe-volume.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Completion Notes List

- Ajout d une couverture API B2B dediee pour `b2bAstrology`, `b2bUsage`, `b2bEditorial`, `b2bBilling` et `enterpriseCredentials`.
- Tests ajoutes pour chemins nominaux + erreurs standardisees (`401/403/422/429/500`) avec verification `request_id` quand disponible.
- Durcissement client `enterpriseCredentials` pour conserver `request_id` dans `EnterpriseCredentialsApiError`.
- Ajout d un script de controle perimetre B2B `npm run test:b2b` executant explicitement les tests API + panneaux critiques.
- Durcissement suite review: passage a une config dediee `vitest.b2b.config.ts` avec inclusion par patterns (moins fragile que liste manuelle).
- Ajout d une gate couverture B2B `npm run test:b2b:coverage` avec seuils explicites (statements/functions/lines/branches) sur perimetre API + UI B2B.
- Ajout d un controle securite runtime `npm run audit:prod` (audit npm avec `--omit=dev`) pour verifier l absence de vulnerabilites de dependances en production.
- Verification completee: `npm audit --omit=dev` retourne 0 vulnerability.
- Verification completee: `npm audit` (incluant devDependencies) retourne 0 vulnerability apres nettoyage lockfile/dependances.
- Documentation frontend mise a jour avec les commandes qualite projet.
- Validation executee: `npm run lint`, `npm run test -- --run`, `npm run test:b2b`, `npm run test:b2b:coverage`, `npm run audit:prod` (OK).

### File List

- `_bmad-output/implementation-artifacts/10-1-couverture-tests-frontend-b2b-completee.md`
- `frontend/src/api/enterpriseCredentials.ts`
- `frontend/src/tests/b2bAstrologyApi.test.ts`
- `frontend/src/tests/b2bUsageApi.test.ts`
- `frontend/src/tests/b2bEditorialApi.test.ts`
- `frontend/src/tests/b2bBillingApi.test.ts`
- `frontend/src/tests/enterpriseCredentialsApi.test.ts`
- `frontend/package.json`
- `frontend/vitest.b2b.config.ts`
- `frontend/tsconfig.lint.json`
- `frontend/README.md`
