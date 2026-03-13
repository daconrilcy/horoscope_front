# Story 47.4: Implémenter les modes dégradés et fallbacks des consultations

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultation domain engineer,
I want rendre explicites les modes dégradés et les sorties bloquantes du parcours consultations,
so that le produit reste honnête sur son niveau de précision et utile même quand les données disponibles sont incomplètes.

## Acceptance Criteria

1. Le domaine consultation expose un `fallback_mode` stable au minimum pour `user_no_birth_time`, `other_no_birth_time`, `relation_user_only`, `timing_degraded`, `blocking_missing_data`.
2. Le backend distingue clairement `nominal`, `degraded` et `blocked` et n'autorise pas une génération qui simulerait une capacité absente.
3. Le frontend consultations affiche un message standardisé de limitation et une action claire (`continuer en mode dégradé`, `compléter les données`, `retour`) pour chaque fallback.
4. Les parcours `relation` et `timing` n'affichent jamais un wording laissant croire à une synastrie complète ou à un timing fin si les données nécessaires sont absentes.
5. Le résultat sauvegardé et l'ouverture dans le chat conservent la trace du `fallback_mode` et du `precision_level`.
6. Une matrice de safeguards consultation distingue explicitement pour les catégories sensibles au minimum `health`, `emotional_distress`, `obsessive_relation`, `pregnancy`, `death`, `legal_finance`, `third_party_manipulation` les issues `fallback`, `refusal` ou `reframing`.
7. `i18n/consultations.ts` expose un wording contractuel par `fallback_mode` et par issue sensible, sans formulation trompeuse sur le niveau de certitude.
8. Les tests couvrent au minimum un parcours nominal, un fallback sans heure utilisateur, un fallback sans heure tiers, un mode `relation_user_only`, un cas bloquant et un cas sensible menant à refus ou recadrage.

## Tasks / Subtasks

- [x] Task 1: Définir le référentiel de fallback consultation (AC: 1, 2)
  - [x] Introduire les constantes / enums consultation pour les fallbacks autorisés
  - [x] Documenter pour chaque fallback son déclencheur, sa promesse UX et sa limitation
  - [x] Prévoir la compatibilité avec les résultats persistés

- [x] Task 2: Implémenter la matrice de safeguards et la résolution backend nominal / degraded / blocked (AC: 1, 2, 4, 6)
  - [x] Formaliser la table de décision `fallback / refusal / reframing` pour les catégories sensibles consultation
  - [x] Brancher la résolution sur le précheck et les données collectées
  - [x] Refuser explicitement les cas réellement bloquants
  - [x] Éviter toute logique qui "inventerait" des données tiers ou une granularité temporelle absente

- [x] Task 3: Intégrer les messages et confirmations frontend (AC: 3, 4, 7)
  - [x] Ajouter un composant ou bandeau fallback consultation réutilisable
  - [x] Standardiser le wording FR/EN/ES dans `i18n/consultations.ts` avec une clé dédiée par `fallback_mode` et par issue sensible
  - [x] Prévoir les actions de poursuite ou de retour selon le mode

- [x] Task 4: Propager fallback et précision jusqu'au runtime frontend (AC: 5, 7)
  - [x] Étendre le modèle `ConsultationResult`
  - [x] Mettre à jour le store / history / chat prefill pour porter ces métadonnées
  - [x] Préserver la compatibilité de lecture des résultats 46.x qui ne possèdent pas encore ces champs

- [x] Task 5: Tester les cas dégradés, bloquants et sensibles (AC: 8)
  - [x] Ajouter des scénarios frontend sur les panneaux de limitation
  - [x] Ajouter des tests backend de résolution de fallback
  - [x] Ajouter un scénario de refus / recadrage sur catégorie sensible
  - [x] Vérifier qu'aucun wording trompeur n'apparaît sur relation / timing

## Dev Notes

- Implemented `ConsultationFallbackService` with safeguard matrix.
- Updated `ConsultationPrecheckService` with keyword-based safeguard detection and fallback resolution.
- Created `ConsultationFallbackBanner` component for UI feedback.
- Extended `ConsultationResult` and `consultationStore` to persist fallback/precision metadata.
- Updated i18n with contractual wording for all modes.

### Previous Story Intelligence

- Story 47.2 established the `ConsultationPrecheckData` model used here.
- Story 47.3 provided the wizard flow where the banner is integrated.

### Project Structure Notes

- New components:
  - `backend/app/services/consultation_fallback_service.py`
  - `frontend/src/features/consultations/components/ConsultationFallbackBanner.tsx`
- Modified files:
  - `backend/app/services/consultation_precheck_service.py`
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/i18n/consultations.ts`

### Technical Requirements

- Safeguard matrix: health -> refusal, legal -> reframing, etc.
- Keyword-based detection for MVP.
- Metadata persistence in local storage history.

### Architecture Compliance

- Backend is source of truth for fallback resolution.
- Frontend displays feedback based on precheck data.

### Testing Requirements

- Backend unit tests covering health refusal and legal reframing.
- Frontend tests updated to handle new flow.

### References

- [Source: docs/backlog_epics_consultation_complete.md#8-epic-cc-04-gestion-des-modes-degrades-et-parcours-de-fallback]
- [Source: backend/app/services/consultation_precheck_service.py]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Backend logic for safeguards and fallbacks implemented and tested.
- Frontend integration successful with a dedicated banner component.
- Metadata propagation to results and history verified.

### Completion Notes List

- Safeguard detection and resolution matrix implemented.
- Consultation fallback UI feedback added.
- Metadata persistence for fallback and precision.
- Comprehensive tests for sensitive categories.

### File List

- `backend/app/services/consultation_fallback_service.py`
- `backend/app/services/consultation_precheck_service.py`
- `backend/app/tests/unit/services/test_consultation_precheck_service.py`
- `frontend/src/features/consultations/components/ConsultationFallbackBanner.tsx`
- `frontend/src/features/consultations/index.ts`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/types/consultation.ts`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Initial implementation of story 47.4. Fallbacks and safeguards.
