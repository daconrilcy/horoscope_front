# Story 69.2: Afficher le retour LLM brut, structuré et les métadonnées d'exécution

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / release operator,
I want consulter le résultat complet d'une exécution manuelle,
so that je puisse comprendre à la fois ce qui a été envoyé et ce que le LLM a renvoyé.

## Acceptance Criteria

1. La zone `Retour LLM` affiche statut, durée, provider, modèle, paramètres résolus, prompt envoyé et réponse brute.
2. Si la sortie est parseable, l'UI affiche une vue structurée/prettifiée distincte de la réponse brute.
3. En cas d'erreur, l'UI distingue les erreurs de rendu, provider et validation.
4. La redaction admin reste appliquée aux champs sensibles de la requête et de la réponse.

## Tasks / Subtasks

- [x] Task 1: Définir le payload de réponse d'exécution admin (AC: 1, 2, 3, 4)
  - [x] Exposer les métadonnées utiles à l'opérateur.
  - [x] Prévoir réponse brute et réponse structurée.
- [x] Task 2: Construire l'affichage frontend du retour LLM (AC: 1, 2, 3)
  - [x] Organiser la zone `Retour LLM`.
  - [x] Prévoir vues succès/erreur.
- [x] Task 3: Ajouter redaction et tests (AC: 3, 4)
  - [x] Vérifier les champs masqués/tronqués.
  - [x] Vérifier la lisibilité des états d'erreur.

## Dev Notes

### Technical Requirements

- Ne pas réduire le résultat à un seul texte.
- Conserver la distinction entre:
  - prompt réellement envoyé,
  - paramètres runtime,
  - réponse brute provider,
  - réponse structurée exploitée par l'application.

### Architecture Compliance

- Réutiliser les objets et conventions runtime existants autant que possible.
- Garder l'inspection cohérente avec l'observabilité canoniquement propagée par le gateway.

### File Structure Requirements

- Backend admin LLM.
- Frontend page admin prompts.
- Tests backend/frontend ciblés.

### Testing Requirements

- Succès avec sortie structurée.
- Succès sans parsing structuré.
- Erreur provider.
- Erreur validation de sortie.
- Redaction appliquée.

### Previous Story Intelligence

- `69.1` produit l'exécution réelle.
- Cette story ne doit pas dupliquer la logique d'exécution; elle doit surtout structurer la lecture opérateur de son retour.

### Project Structure Notes

- Prévoir une présentation lisible même pour des réponses longues.

### References

- [docs/llm-prompt-generation-by-feature.md](C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [AdminPromptsPage.tsx](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Payload `AdminCatalogManualExecuteResponseData` enrichi (prompt anonymisé, paramètres runtime sanitizés, sortie structurée sanitizée, chemins d'erreur avec `failure_kind`).
- Zone « Retour LLM » : grille métadonnées, JSON params runtime, prompt, bloc structuré séparé du brut, états chargement / succès / erreur.
- Erreurs API : distinction via `failure_kind` (input_validation, gateway_config, output_validation, provider_error, render_pipeline, unexpected).
- Tests : intégration catalogue mise à jour, unit test helper redaction structurée.

### File List

- `backend/app/core/sensitive_data.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/unit/test_admin_manual_execute_response.py`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/69-2-afficher-retour-llm-brut-structure-metadonnees-execution.md`

### Change Log

- 2026-04-18 : Implémentation story 69.2 — payload exécution admin enrichi, UI Retour LLM, redaction/anonymisation, tests.
- 2026-04-18 : Correctifs post code-review — parseable cohérent, `PromptRenderError`, tests erreurs, `failure_kind` opérationnel dans les détails API.
- 2026-04-18 : Code review passe 2 — aucun nouveau patch requis ; story et sprint passés en **done**.
- 2026-04-18 : Test d’intégration succès sans `structured_output` ; `UnknownUseCaseError` → `failure_kind` `unknown_use_case` ; résidu `GatewayError` enrichi de `gateway_error_class` (sanitization admin) + libellé front.

### Review Findings

#### Code review (2026-04-18) — bmad-code-review 69-2

- [x] [Review][Patch] Incohérence `structured_output_parseable` / `structured_output` — corrigé : `parseable` aligné sur présence d’un dict sanitizé. `backend/app/api/v1/routers/admin_llm.py`.

- [x] [Review][Patch] `PromptRenderError` — handler dédié `failure_kind` `prompt_render` avant `GatewayError`. `backend/app/api/v1/routers/admin_llm.py`.

- [x] [Review][Patch] Tests d’intégration `output_validation`, `provider_error`, `prompt_render` + refactor seed/teardown + unit test non-dict. `backend/tests/integration/test_admin_llm_catalog.py`, `backend/tests/unit/test_admin_manual_execute_response.py`.

- [x] [Review][Patch] `failure_kind` ne doit pas être redigé dans les détails d’erreur admin — ajout à `OPERATIONAL_FIELDS`. `backend/app/core/sensitive_data.py`.

- [x] [Review][Defer] Libellé `failure_kind` `render_pipeline` pour `runtime_preview_incomplete` — nom proche d’une erreur de rendu template ; acceptable si documenté pour l’opérateur. — deferred, naming / doc only.

- [x] [Review][Defer] `anonymize_text` sans try/except dans le helper — aligné avec le reste du projet ; risque résiduel si configuration d’anonymisation défaillante. — deferred, pattern existant.

#### Revue complémentaire (2026-04-18, passe 2)

- Aucun nouveau finding **patch** ni **decision-needed**. Les correctifs de la passe 1 sont présents dans le diff (parseable, `PromptRenderError`, tests d’erreur, `failure_kind` dans `OPERATIONAL_FIELDS`).
- **Recommandation mineure (defer)** : un test d’intégration HTTP 200 avec mock **sans** `structured_output` renforcerait la ligne « Succès sans parsing structuré » des Dev Notes (déjà partiellement couvert par les tests unitaires du helper).
- Sous-classes `GatewayError` hors `PromptRenderError` / `OutputValidationError` (ex. erreurs catalogue) restent étiquetées `provider_error` — acceptable tant que le message distingue ; amélioration transverse possible plus tard.
