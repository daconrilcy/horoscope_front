# Story 47.2: Exposer le précheck de complétude et de précision des consultations

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend architect,
I want exposer un service de pré-analyse (`precheck`) pour chaque type de consultation,
so that le frontend puisse informer l'utilisateur de la qualité attendue du résultat et proposer des alternatives ou fallbacks avant de consommer des tokens LLM.

## Acceptance Criteria

1. Un endpoint `POST /v1/consultations/precheck` est disponible et documenté via OpenAPI.
2. Le précheck retourne un niveau de précision (`high`, `medium`, `limited`, `blocked`) basé sur la présence de la date/heure de naissance utilisateur et les exigences du type de consultation.
3. Le précheck identifie explicitement les champs manquants (`missing_fields`) et suggère un mode de `fallback` si nécessaire (ex: `user_no_birth_time`).
4. Le modèle de réponse inclut une section `safeguard` (placeholder pour story 47.4) capable de signaler des thématiques refusées ou sensibles.
5. Un client frontend centralisé dans `frontend/src/api/consultations.ts` permet de consommer ce précheck via un hook `useConsultationPrecheck`.
6. La logique de précheck est testée unitairement (backend) et son intégration est vérifiée dans le wizard (frontend).

## Tasks / Subtasks

- [x] Task 1: Définir le modèle de données du précheck consultation (AC: 1, 3, 4, 6)
  - [x] Créer les schémas Pydantic consultation pour le précheck
  - [x] Définir des enums ou constantes stables pour PrecisionLevel, ConsultationStatus, FallbackMode, SafeguardIssue

- [x] Task 2: Implémenter un service backend consultation-precheck réutilisant les services existants (AC: 1, 2, 3)
  - [x] Ajouter une couche `services/consultation_precheck_service.py`
  - [x] Réutiliser `UserBirthProfileService` pour valider la complétude du profil natal

- [x] Task 3: Exposer le routeur API consultation et un client frontend centralisé (AC: 4, 5)
  - [x] Ajouter le routeur `/v1/consultations/*` dans le backend
  - [x] Créer `frontend/src/api/consultations.ts` avec le hook `useConsultationPrecheck`

- [x] Task 4: Intégrer l'affichage consultation-ready dans le parcours (AC: 5)
  - [x] Mettre à jour `ConsultationWizardPage` pour appeler le precheck au changement de type
  - [x] Gérer les états de chargement du precheck dans le wizard

- [x] Task 5: Tester le contrat et les cas limites (AC: 6)
  - [x] Ajouter des tests backend unitaire et d'intégration
  - [x] Mettre à jour les tests frontend pour supporter le nouveau flux asynchrone

## Dev Notes

- Le précheck ne doit pas être bloquant par défaut sauf absence totale de profil natal.
- Il doit être rapide (pas d'appel LLM à ce stade).
- Il prépare le terrain pour le routage LLM de la story 47.5.

### Previous Story Intelligence

- Story 47.1 a déjà stabilisé les IDs de type. Le précheck doit se baser sur ces IDs.
- L'infrastructure `fetchWithAuth` et `react-query` du projet doit être privilégiée.

### Project Structure Notes

- Nouveaux fichiers:
  - `backend/app/api/v1/schemas/consultation.py`
  - `backend/app/services/consultation_precheck_service.py`
  - `backend/app/api/v1/routers/consultations.py`
  - `frontend/src/api/consultations.ts`
- Fichiers modifiés:
  - `backend/app/main.py` (enregistrement routeur)
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/state/consultationStore.tsx`

### Technical Requirements

- Pydantic v2 respecté.
- Hook React standard avec gestion d'état `loading/error`.
- Typage TypeScript strict pour les contrats API.

### Architecture Compliance

- Service backend découplé du routeur.
- Pas de logique de calcul astrologique complexe dans le précheck (juste de la vérification de présence de données).

### Testing Requirements

- Couvrir `test_precheck_no_profile`, `test_precheck_incomplete_profile`.
- Vérifier que le wizard attend le precheck avant de permettre la génération.

### References

- [Source: docs/backlog_epics_consultation_complete.md#6-epic-cc-02-precheck-de-completude-et-precision]
- [Source: backend/app/services/user_birth_profile_service.py]
- [Source: frontend/src/api/auth.ts]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Backend service and router implemented with success.
- Integration tests (3 passed) and unit tests (3 passed).
- Frontend hook and integration in wizard with successful tests.
- Fixed some language detection issues in frontend tests.

### Completion Notes List

- Created `ConsultationPrecheckService` and corresponding schemas.
- Exposed `POST /v1/consultations/precheck` endpoint.
- Implemented `useConsultationPrecheck` hook in frontend.
- Integrated precheck call in `ConsultationWizardPage`.
- Robust test coverage for both backend and frontend.

### File List

- `backend/app/api/v1/schemas/consultation.py`
- `backend/app/services/consultation_precheck_service.py`
- `backend/app/api/v1/routers/consultations.py`
- `backend/app/tests/unit/services/test_consultation_precheck_service.py`
- `backend/app/tests/integration/test_consultations_router.py`
- `frontend/src/api/consultations.ts`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Initial implementation of story 47.2. Consultation precheck API and hook.
