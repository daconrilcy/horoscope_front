# Story 68.2: Rendre la runtime preview avec un sample payload sélectionné

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / prompt reviewer,
I want sélectionner un sample payload et obtenir un vrai rendu runtime du prompt,
so that je voie exactement ce qui serait envoyé au provider sans exécuter encore le LLM.

## Acceptance Criteria

1. L'admin peut sélectionner un sample payload compatible depuis la vue detail.
2. La page bascule en mode `runtime preview` et affiche le prompt rendu avec les placeholders résolus.
3. Si le sample payload est incomplet, les placeholders restants sont exposés comme bloquants pour la runtime preview.
4. Aucune exécution provider n'est déclenchée pour cette preview.

## Tasks / Subtasks

- [x] Task 1: Etendre le backend resolved pour accepter un sample payload ou sa référence (AC: 1, 2, 3, 4)
  - [x] Définir si la runtime preview réutilise le même endpoint `resolved` avec paramètres ou un endpoint dédié.
  - [x] Injecter les sample payloads dans le rendu sans casser la preview statique.
- [x] Task 2: Brancher la sélection frontend et le rendu runtime (AC: 1, 2, 3)
  - [x] Ajouter le sélecteur de sample payload.
  - [x] Afficher clairement le mode `runtime preview`.
  - [x] Rendre visibles les placeholders encore manquants.
- [x] Task 3: Tester l'absence d'appel provider (AC: 4)
  - [x] Vérifier côté backend qu'aucun runtime manager provider n'est invoqué.
  - [x] Vérifier côté frontend les états complet/incomplet.

## Dev Notes

### Technical Requirements

- La runtime preview doit rester un rendu local déterministe.
- Il est acceptable que le backend dérive un objet "render variables" enrichi à partir du sample payload.
- Le champ `chart_json` doit pouvoir être injecté sans régression sur les autres placeholders existants.

### Architecture Compliance

- Réutiliser `PromptRenderer`, `ContextQualityInjector`, `LengthBudgetInjector` et la résolution assembly existante.
- Ne pas créer un moteur ad hoc de rendu admin.

### File Structure Requirements

- Backend: `backend/app/api/v1/routers/admin_llm.py`
- Frontend: `frontend/src/api/adminPrompts.ts`, `frontend/src/pages/admin/AdminPromptsPage.tsx`
- Tests backend/frontend ciblés sur le chemin runtime preview.

### Testing Requirements

- Runtime preview complète.
- Runtime preview incomplète.
- Séparation claire avec preview statique.
- Vérification explicite "no provider call".

### Previous Story Intelligence

- `68.1` définit le modèle de sample payload.
- `67.1` à `67.3` ont préparé le vocabulaire et les emplacements UI pour cette preview.

### Project Structure Notes

- Réutiliser les surfaces admin existantes plutôt qu'un nouvel écran séparé.

### References

- [66-46-vue-detail-resolved-prompt-assembly.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md)
- [admin_llm.py](C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [PromptRenderer](C:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`
- Validation backend: `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/integration/test_admin_llm_catalog.py`
- Validation frontend: `cd frontend; npm run test -- src/tests/AdminPromptsPage.test.tsx`

### Completion Notes List

- Story file created from BMAD backlog.
- Le endpoint `GET /v1/admin/llm/catalog/{manifest_entry_id}/resolved` accepte maintenant `sample_payload_id` et enrichit les render variables sans exécuter le provider.
- La runtime preview valide la compatibilité `feature/locale` du sample payload et renvoie des erreurs explicites en cas de mismatch.
- Les placeholders résolus via sample payload sont marqués `resolution_source="sample_payload"` pour inspection opérable.
- Le frontend expose un sélecteur de sample payload en mode `runtime preview`, charge la liste par `feature/locale`, et propage la sélection au backend.
- Les tests backend/frontend couvrent le chemin runtime preview avec sample payload et garantissent l'absence d'appel provider.
- Correctifs post-review: isolation stricte `assembly_preview` vs `runtime_preview` côté frontend et garde-fou backend refusant `sample_payload_id` hors runtime preview.
- Harmonisation des codes d'erreur runtime preview (`sample_payload_not_found`, `sample_payload_target_mismatch`, `sample_payload_runtime_preview_only`) via enum partagé `AdminLlmErrorCode`.

### File List

- `_bmad-output/implementation-artifacts/68-2-rendre-runtime-preview-avec-sample-payload.md`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/api/v1/routers/admin_llm_error_codes.py`
- `backend/app/api/v1/routers/admin_llm_assembly.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

### Change Log

- 2026-04-17: Runtime preview enrichie par sample payload sélectionné (backend+frontend) avec tests de non-exécution provider.
- 2026-04-17: Correctifs post-review 68.2 (anti-course mode preview, enforcement backend runtime-only, centralisation des codes d'erreur admin LLM).
