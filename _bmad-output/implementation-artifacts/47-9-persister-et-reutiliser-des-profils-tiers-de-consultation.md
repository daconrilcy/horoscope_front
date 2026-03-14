# Story 47.9: Persister et reutiliser des profils tiers de consultation

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur de consultation ciblee,
I want pouvoir enregistrer et reutiliser le profil de naissance d'un tiers,
so that je n'aie pas a ressaisir ses donnees (date, heure, lieu) a chaque nouvelle consultation portant sur cette meme personne.

## Acceptance Criteria

1. L'utilisateur peut lister ses profils tiers deja enregistres lors de l'etape de collecte tiers du wizard consultations.
2. La selection d'un profil existant remplit automatiquement les champs de naissance du tiers et valide l'etape.
3. Lors de la saisie d'un nouveau tiers, une option "Enregistrer dans mes contacts" est proposee.
4. L'enregistrement exige un pseudonyme (nickname) pour identifier le contact et affiche une mise en garde sur la protection de la vie privee (ne pas utiliser de nom complet).
5. Un profil tiers enregistre porte son historique d'usage (derniere consultation, type, contexte court) sans stocker le contenu genere lui-meme (deja dans l'historique consultations).
6. Le backend expose les endpoints `GET /v1/consultations/third-parties` et `POST /v1/consultations/third-parties` pour la gestion de ces profils.
7. La generation d'une consultation peut declencher l'enregistrement automatique du tiers si l'option etait cochee (`save_third_party: true`).
8. Les tests couvrent la creation, le listing, la selection d'un existant et la mise a jour de l'usage.

## Tasks / Subtasks

- [x] Task 1: Creer les modeles de persistance des profils tiers (AC: 5, 6)
  - [x] Ajouter `ConsultationThirdPartyProfileModel` (nickname, birth_data, user_id)
  - [x] Ajouter `ConsultationThirdPartyUsageModel` pour tracer les consultations liees
  - [x] Implementer le repository associe

- [x] Task 2: Implementer les endpoints backend de gestion des tiers (AC: 6, 7)
  - [x] Ajouter les schemas Pydantic pour list/create/usage
  - [x] Implementer `ConsultationThirdPartyService`
  - [x] Exposer les routes dans le routeur consultations

- [x] Task 3: Integrer l'enregistrement opt-in dans la generation (AC: 3, 4, 7)
  - [x] Mettre a jour `ConsultationGenerateRequest` pour inclure `save_third_party` et `nickname`
  - [x] Brancher la creation du profil dans `ConsultationGenerationService` lors de la generation reussie

- [x] Task 4: Refondre l'UI de collecte tiers pour supporter le reuse (AC: 1, 2, 4)
  - [x] Ajouter une selection de contact existant dans `OtherPersonForm`
  - [x] Ajouter le toggle d'enregistrement et le champ pseudonyme
  - [x] Inclure la mise en garde privacy

- [x] Task 5: Verrouiller par les tests (AC: 8)
  - [x] Ajouter des tests d'integration backend pour les nouveaux endpoints
  - [x] Ajouter des tests frontend sur la selection d'un contact existant

## Dev Notes

- Created `ConsultationThirdPartyProfileModel` and `ConsultationThirdPartyUsageModel`.
- Exposed `GET /v1/consultations/third-parties` and `POST /v1/consultations/third-parties`.
- Updated `OtherPersonForm` with contact selection and save opt-in.
- Integrated `save_third_party` in `ConsultationGenerationService`.
- Fixed several `ImportError` in `backend/app/infra/db/models/__init__.py` related to enterprise billing, usage, and observability models that were incorrectly named or missing.

### Previous Story Intelligence

- Reused `OtherPersonData` schema and geocoding protocol.
- Leveraged `ConsultationGenerationService` updated in Story 47.5.

### Project Structure Notes

- New backend files:
  - `backend/app/infra/db/models/consultation_third_party.py`
  - `backend/app/infra/db/repositories/consultation_third_party_repository.py`
  - `backend/app/services/consultation_third_party_service.py`
  - `backend/app/tests/integration/test_consultation_third_party.py`
- Modified frontend:
  - `frontend/src/api/consultations.ts`
  - `frontend/src/features/consultations/components/OtherPersonForm.tsx`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/i18n/consultations.ts`

### Technical Requirements

- GDPR compliance: nickname recommended, explicit privacy warning.
- Usage tracking: update `updated_at` on profile when used in a new consultation.

### Architecture Compliance

- Decoupled third party management from core user profile.
- Repository pattern followed.

### Testing Requirements

- Backend integration tests: 3 passed.
- Frontend tests: 12 passed.

### References

- [Source: docs/backlog_epics_consultation_complete.md#7-epic-cc-03-collecte-conditionnelle-des-donnees-manquantes]
- [Source: backend/app/infra/db/models/consultation_third_party.py]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Backend endpoints implemented and tested.
- UI for profile reuse and saving added to wizard.
- Fixed circular and missing imports in DB models.
- All tests verified passing.

### Completion Notes List

- Persistent third-party profiles implemented.
- Users can now save and reuse birth data for partners, recruiters, etc.
- Usage history recorded for each saved profile.
- Privacy warning integrated in the UI.

### File List

- `backend/app/infra/db/models/consultation_third_party.py`
- `backend/app/infra/db/repositories/consultation_third_party_repository.py`
- `backend/app/services/consultation_third_party_service.py`
- `backend/app/api/v1/routers/consultations.py`
- `backend/app/api/v1/schemas/consultation.py`
- `backend/app/tests/integration/test_consultation_third_party.py`
- `frontend/src/api/consultations.ts`
- `frontend/src/features/consultations/components/OtherPersonForm.tsx`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Implementation of story 47.9. Third-party profile persistence and reuse.
