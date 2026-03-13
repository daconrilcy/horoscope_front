# Story 47.8: Etendre la collecte tiers aux consultations d'interaction ciblee

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultations product engineer,
I want permettre la saisie optionnelle d'un tiers pour les consultations portant sur une interaction ciblee au-dela du seul type `relation`,
so that un utilisateur puisse preparer une consultation sur un rendez-vous amoureux, un entretien, une reunion cle ou toute interaction ciblee avec une personne identifiee sans detourner le type de consultation.

## Acceptance Criteria

1. Le parcours consultations distingue explicitement les cas `self_only` et `targeted_interaction` pour les types eligibles, au minimum `work`, sans casser le comportement existant du type `relation`.
2. Le wizard affiche un module de cadrage simple permettant d'indiquer si la consultation concerne une autre personne sur les types eligibles, au minimum `work`.
3. Quand `targeted_interaction` est selectionne, le module `OtherPersonForm` est affiche en collecte et alimente le payload `other_person` des endpoints `/v1/consultations/precheck` et `/v1/consultations/generate`.
4. Quand la consultation reste `self_only`, aucun champ tiers n'est affiche ni exige pour `work` ou les autres types personnels.
5. Le precheck et la generation restent backward-compatible avec les parcours existants `relation` et `self_only`.
6. Les tests frontend couvrent au minimum un parcours `work/self_only`, un parcours `work/targeted_interaction` et la non-regression du parcours `relation`.

## Tasks / Subtasks

- [x] Task 1: Etendre le modele frontend consultation pour la notion d'interaction ciblee (AC: 1, 2)
  - [x] Ajouter un indicateur explicite dans `ConsultationDraft` pour distinguer `self_only` et `targeted_interaction`
  - [x] Declarer au niveau de la taxonomie les types eligibles a une collecte tiers conditionnelle
  - [x] Preserver le comportement actuel de `relation`

- [x] Task 2: Ajouter le cadrage interaction ciblee dans le wizard (AC: 1, 2, 4)
  - [x] Introduire une UI simple dans le framing ou la collecte pour demander si la consultation porte sur une autre personne
  - [x] Ne pas reintroduire une seconde page de selection de type
  - [x] Garder un parcours fluide sur mobile et desktop

- [x] Task 3: Reutiliser `OtherPersonForm` sur les types eligibles (AC: 3, 4, 5)
  - [x] Remplacer la condition hardcodee `draft.type === "relation"` par une condition metier explicite
  - [x] Propager `other_person` vers `precheck` et `generate` pour les parcours eligibles
  - [x] Preserver les cas `birth_time_known = false`

- [x] Task 4: Verrouiller la non-regression du parcours existant (AC: 5, 6)
  - [x] Ajouter un test wizard pour navigation depuis `/consultations/new?type=work`
  - [x] Ajouter un test sur l'affichage conditionnel du module tiers en `work`
  - [x] Verifier que `relation` continue d'afficher le module tiers comme aujourd'hui

## Dev Notes

- `ConsultationDraft` extended with `isInteraction` boolean.
- `ConsultationTypeConfig` extended with `interactionEligible` boolean.
- `work` and `relation` marked as interaction-eligible.
- `ConsultationFrameStep` updated with interaction toggle.
- `DataCollectionStep` updated to use `isInteraction` flag.
- Tests updated to cover new scenarios.

### Previous Story Intelligence

- Leveraged existing `OtherPersonForm` from Story 47.3.
- Maintained stability of `/v1/consultations/precheck` and `/v1/consultations/generate` payloads.

### Project Structure Notes

- Modified:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/features/consultations/components/ConsultationFrameStep.tsx`
  - `frontend/src/features/consultations/components/DataCollectionStep.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/i18n/consultations.ts`
  - `frontend/src/tests/ConsultationsPage.test.tsx`

### Technical Requirements

- Type safety for new fields.
- Dynamic rendering based on `isInteraction` flag.
- Localization for new toggle and hints.

### Architecture Compliance

- Decoupled type checks from specific IDs where possible (using `interactionEligible` config).
- Minimal changes to existing wizard flow structure.

### Testing Requirements

- Verified with 6 frontend tests (all passed).
- Verified with 4 backend integration tests (all passed).

### References

- [Source: docs/backlog_epics_consultation_complete.md#7-epic-cc-03-collecte-conditionnelle-des-donnees-manquantes]
- [Source: frontend/src/features/consultations/components/DataCollectionStep.tsx]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Taxonomy and draft state updated.
- Interaction toggle integrated in Framing step.
- Data collection logic extended to all eligible types.
- Regression tests for `relation` verified.

### Completion Notes List

- Interaction-eligible consultations now support optional third-party data collection.
- Flexible UI allows switching between self-only and interaction mode.
- Backward compatibility for `relation` type maintained.

### File List

- `frontend/src/types/consultation.ts`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/features/consultations/components/ConsultationFrameStep.tsx`
- `frontend/src/features/consultations/components/DataCollectionStep.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Implementation of story 47.8. Extended third-party collection to interaction-eligible types.
