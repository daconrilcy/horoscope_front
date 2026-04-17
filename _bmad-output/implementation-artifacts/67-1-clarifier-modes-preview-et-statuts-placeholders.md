# Story 67.1: Clarifier les modes de preview et les statuts de placeholders

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / LLM operator,
I want que la vue detail distingue explicitement `assembly preview`, `runtime preview` et `live execution`,
so that je ne confonde plus une preview statique incomplète avec une erreur fonctionnelle.

## Acceptance Criteria

1. La vue detail affiche explicitement le mode courant parmi `assembly preview`, `runtime preview`, `live execution`.
2. En mode `assembly preview`, l'absence de placeholders runtime attendus n'est plus présentée comme une erreur d'exécution.
3. Un placeholder absent en preview statique peut être affiché avec un statut stable du type `expected_missing_in_preview`.
4. Un placeholder réellement bloquant en `runtime preview` ou en `live execution` reste distingué comme bloquant.
5. La terminologie de l'UI n'emploie plus `prompt final` pour un rendu incomplet ou best-effort.

## Tasks / Subtasks

- [x] Task 1: Recadrer la sémantique backend des placeholders (AC: 1, 2, 3, 4)
  - [x] Introduire ou adapter un statut stable pour les placeholders attendus mais absents en preview statique.
  - [x] Conserver un statut distinct pour les placeholders bloquants en runtime preview.
  - [x] Veiller à ne pas casser les payloads déjà consommés par la page admin existante.
- [x] Task 2: Recadrer les libellés frontend de la vue detail (AC: 1, 2, 5)
  - [x] Afficher un badge/marqueur visible du mode courant.
  - [x] Renommer les libellés ambigus autour de `rendered_prompt` et du "final prompt".
  - [x] Rendre les états de preview partielle compréhensibles sans lecture du JSON brut.
- [x] Task 3: Verrouiller les tests de non-régression (AC: 2, 3, 4, 5)
  - [x] Ajouter des tests backend de classification preview vs runtime.
  - [x] Ajouter des tests frontend de libellés et d'états placeholders.

## Dev Notes

### Technical Requirements

- Réutiliser l'endpoint detail canonique existant `GET /v1/admin/llm/catalog/{manifest_entry_id}/resolved`.
- Ne pas créer une logique parallèle d'analyse des placeholders côté frontend.
- La distinction preview statique / runtime doit rester pilotée par le backend.
- Respecter la politique de redaction admin existante sur les valeurs de placeholders.

### Architecture Compliance

- Le runtime nominal reste gouverné par `manifest_entry_id`, assembly résolue, execution profile résolu et placeholders du registre.
- La story doit rester une évolution de l'inspection admin, pas une exécution provider.
- Ne pas réintroduire `use_case` comme axe nominal ou vocabulaire principal.

### File Structure Requirements

- Backend: `backend/app/api/v1/routers/admin_llm.py`, éventuellement schémas associés.
- Frontend: `frontend/src/api/adminPrompts.ts`, `frontend/src/pages/admin/AdminPromptsPage.tsx`, CSS associée.
- Tests: `backend/tests/integration/test_admin_llm_catalog.py`, `frontend/src/tests/AdminPromptsPage.test.tsx`.

### Testing Requirements

- Tester explicitement:
  - preview statique avec placeholders runtime attendus,
  - runtime preview avec placeholder réellement manquant,
  - libellés UI non ambigus,
  - absence de régression sur `66-46`.

### Previous Story Intelligence

- `66.45` a déjà imposé le catalogue canonique et `manifest_entry_id` comme clé nominale.
- `66.46` a déjà introduit la vue detail resolved et l'état `blocking_missing`; cette story doit en corriger la sémantique sans casser l'inspection.

### Project Structure Notes

- Pas de style inline.
- Réutiliser les classes et tokens admin existants.
- Garder la preview déterministe et locale tant qu'aucune exécution explicite n'est demandée.

### References

- [docs/llm-prompt-generation-by-feature.md](C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [66-45-vue-catalogue-canonique-prompts-actifs.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md)
- [66-46-vue-detail-resolved-prompt-assembly.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md)
- [admin_llm.py](C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [AdminPromptsPage.tsx](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Implementation Plan

1. Backend : statut `expected_missing_in_preview`, query `inspection_mode`, `render_error_kind`, champ `inspection_mode` sur la vue résolue.
2. Corriger `assemble_developer_prompt` pour `None` sur les flags `_enabled` (assemblies détachées / snapshot).
3. Frontend : types, `getAdminResolvedAssembly` + hook, UI badge/sélecteur/libellés.
4. Tests intégration catalog + tests AdminPromptsPage, lint.

### Completion Notes List

- Story file created from BMAD backlog.
- Endpoint `GET /v1/admin/llm/catalog/{id}/resolved` : paramètre `inspection_mode` (`assembly_preview` défaut, `runtime_preview`, `live_execution`), champ `inspection_mode` dans la réponse, statut `expected_missing_in_preview` pour les requis absents en assembly, `render_error_kind` pour distinguer rendu incomplet statique vs erreur d’exécution.
- Correction `assemble_developer_prompt` : `feature_enabled` / `subfeature_enabled` / `plan_rules_enabled` à `None` traités comme activés (aligné sur l’intention par défaut), corrige l’aperçu vide pour assemblies reconstruites depuis snapshot sans booléens SQL chargés.
- UI Admin Prompts : badge mode, sélecteur de mode, libellés pipeline/résultat, libellés de statuts placeholders, message atténué si `render_error_kind === static_preview_incomplete`.
- Clarification UX ajoutée après revue : le mode `live_execution` est explicitement présenté comme une inspection qui reprend actuellement la sémantique placeholder de `runtime_preview` sans exécution provider réelle.

### File List

- `_bmad-output/implementation-artifacts/67-1-clarifier-modes-preview-et-statuts-placeholders.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/llm_orchestration/services/assembly_resolver.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

## Change Log

- 2026-04-17 : Story 67-1 — modes d’inspection, statuts placeholders, libellés UI, tests backend/frontend, correctif assembly `feature_enabled` None.
- 2026-04-17 : Correctif post-review — aide UI explicite sur `live_execution` pour éviter l’ambiguïté avec une exécution réelle.

### Review Findings

- [x] [Review][Patch] Classifier `render_error_kind` sans heuristique fragile sur sous-chaînes (`unauthorized`, `legacy`) — exploiter `PromptRenderError.details` ou un code d’erreur stable lorsque disponible [`backend/app/api/v1/routers/admin_llm.py`] — corrigé : `_classify_admin_render_error_kind` (détails `missing_variables` / `placeholder` + repli message ciblé)
- [x] [Review][Patch] Aide UX pour distinguer « Exécution live » de la prévisualisation runtime (même logique aujourd’hui) — corrigé : libellé du mode et texte d’aide précisent que `live_execution` conserve pour l’instant une sémantique d’inspection runtime sans appel provider réel
- [x] [Review][Defer] Statut `unknown` vs `expected_missing_in_preview` pour placeholders hors registre — reporté, voir `deferred-work.md`
