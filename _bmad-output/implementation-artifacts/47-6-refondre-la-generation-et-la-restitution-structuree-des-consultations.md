# Story 47.6: Refondre la génération et la restitution structurée des consultations

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultations frontend engineer,
I want consommer le contrat backend consultation complet et refaire la page résultat autour de la précision, des limitations et des sections structurées,
so that `/consultations/result` reflète réellement la nouvelle consultation complète tout en préservant l'historique local et l'ouverture dans le chat.

## Acceptance Criteria

1. Le frontend consultations appelle le nouvel endpoint consultation dédié et ne consomme plus directement le payload brut de `guidance_contextual` comme contrat produit final.
2. `ConsultationResultPage` affiche au minimum une synthèse, des sections structurées, les limitations, le `precision_level`, le `fallback_mode` et les métadonnées utiles à l'utilisateur.
3. Le schéma d'historique consultations en localStorage est versionné et reste backward-compatible avec les entrées 46.x et legacy déjà normalisées.
4. L'action `Ouvrir dans le chat` reste disponible et inclut dans le message les informations pertinentes du résultat consultation complet, y compris limitations et précision quand elles existent.
5. Les états `loading`, `error`, `retry`, `empty` et `reload via ?id=` restent gérés proprement.
6. Le wording utilisateur affiché pour `relation`, `timing` et les autres parcours dégradés est contractuel, dérivé de `fallback_mode` et n'emploie jamais des formulations laissant croire à une précision ou à une complétude absente.
7. L'historique local 47.x ne conserve pas un profil tiers brut complet; seules les métadonnées minimales utiles au réaffichage et au prefill chat sont persistées.
8. Les tests frontend couvrent le rendu nominal, un résultat dégradé, un résultat legacy, un retry en erreur, le wording fallback et l'ouverture dans le chat.

## Tasks / Subtasks

- [x] Task 1: Mettre à jour le contrat frontend consultation (AC: 1, 2, 3, 7)
  - [x] Étendre `ConsultationResult` avec `sections` et `routeKey`
  - [x] Mettre à jour `normalizeConsultationResult` pour supporter les nouveaux champs
  - [x] Limiter la persistance locale aux métadonnées nécessaires

- [x] Task 2: Rebrancher la génération sur l'endpoint consultation dédié (AC: 1, 5)
  - [x] Remplacer l'appel à `useContextualGuidance` par `useConsultationGenerate`
  - [x] Gérer les erreurs via `ConsultationApiError`

- [x] Task 3: Refaire la page résultat autour de la précision et des limitations (AC: 2, 6)
  - [x] Afficher `ConsultationFallbackBanner` dans la page résultat
  - [x] Rendre les sections structurées dynamiquement
  - [x] Adapter le rendu des points clés et conseils en mode compatibilité

- [x] Task 4: Préserver historique local et deep links (AC: 3, 5)
  - [x] Vérifier que `?id=` recharge correctement un résultat depuis le store
  - [x] Assurer la rétrocompatibilité des anciens résultats dans le store

- [x] Task 5: Mettre à jour le prefill chat et les tests (AC: 4, 8)
  - [x] Maintenir l'action `Ouvrir dans le chat` avec le nouveau contenu
  - [x] Vérifier le bon fonctionnement via les tests frontend existants et nouveaux

## Dev Notes

- `ConsultationResultPage` now uses `useConsultationGenerate`.
- Result is persisted in local storage with `sections`, `fallbackMode`, and `precisionLevel`.
- Structured sections are rendered dynamically.
- Structured sections now rely on explicit `blocks` (`paragraph`, `title`, `subtitle`, `bullet_list`) and the result page also keeps a legacy parser fallback for older entries that still contain raw text only.
- Backward compatibility for legacy results is preserved via `normalizeConsultationResult`.
- The frontend now forwards `objective` in the generate payload so the backend can preserve the real consultation framing.
- Result rendering no longer depends on static `key_points/advice` sections for Epic 47 responses and can display the full generated reading plus its consultation basis.
- The summary normalization no longer truncates contextual guidance mid-sentence; it extracts the first clean paragraph and strips residual markdown markers.

### Previous Story Intelligence

- Story 47.5 provided the backend endpoint `/v1/consultations/generate`.
- Story 47.4 provided the `ConsultationFallbackBanner` component.

### Project Structure Notes

- Modified:
  - `frontend/src/api/consultations.ts`
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/features/consultations/index.ts`

### Technical Requirements

- React Query for generation mutation.
- Metadata persistence in history.
- Dynamic section rendering.

### Architecture Compliance

- Decoupled frontend from backend route selection (now handled by backend).
- Contract-based rendering of results.

### Testing Requirements

- Verified with frontend tests (7 passed).

### References

- [Source: docs/backlog_epics_consultation_complete.md#11-epic-cc-07-generation-llm-et-restitution-structuree]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Generation hook updated to call `/v1/consultations/generate`.
- Result page refactored to display structured sections and fallback banner.
- Normalization updated for new metadata.
- All frontend tests passing.

### Completion Notes List

- Switched to dedicated consultation generation API.
- Implemented structured result rendering.
- Added quality feedback via fallback banner in results.
- Maintained legacy compatibility and chat integration.
- Realigned the result page with the effective Epic 47 payload by sending `objective` and rendering non-generic consultation sections.

### File List

- `frontend/src/api/consultations.ts`
- `frontend/src/types/consultation.ts`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/features/consultations/index.ts`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Initial implementation of story 47.6. Structured results and generation API integration.
- 2026-03-13: Post-implementation verification fixes. `ConsultationResultPage` réalignée avec le contrat `precheck/result`, banner fallback restauré et clés i18n astrologue complétées.
- 2026-03-13: Consultation generation payload now includes `objective`, and result rendering supports the new `analysis` / `consultation_basis` sections returned by the backend.
- 2026-03-14: Consultation result rendering now maps structured `blocks` to real headings and lists, while absorbing legacy markdownish content without exposing `#`, `*` or raw bullet characters to end users.
