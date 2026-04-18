# Story 69.3: Sécuriser la surface d'exécution manuelle et verrouiller sa QA

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin platform owner,
I want encadrer l'exécution manuelle par des garde-fous UX, sécurité et tests,
so that la surface reste utile sans devenir une source d'erreur opératoire ou de fuite de données.

## Acceptance Criteria

1. L'exécution réelle est protégée par une confirmation explicite et un mode visuellement identifiable.
2. Les permissions admin sont vérifiées en frontend et surtout en backend.
3. Les tests couvrent preview, exécution, succès, échec et redaction.
4. L'observabilité permet de distinguer une exécution admin volontaire d'un trafic produit nominal.

## Tasks / Subtasks

- [x] Task 1: Encadrer l'action UI d'exécution (AC: 1)
  - [x] Ajouter une confirmation explicite.
  - [x] Afficher le mode courant en permanence.
- [x] Task 2: Verrouiller permissions et sécurité backend (AC: 2)
  - [x] Vérifier les guards admin.
  - [x] Refuser tout appel non autorisé même hors UI.
- [x] Task 3: Couvrir QA et observabilité (AC: 3, 4)
  - [x] Ajouter les tests backend/frontend requis.
  - [x] Ajouter ou réutiliser des marqueurs d'observabilité identifiant l'origine admin.

## Dev Notes

### Technical Requirements

- Toute exécution admin doit être explicitement identifiable en logs et événements.
- La confirmation UI ne remplace jamais le contrôle backend.

### Architecture Compliance

- Réutiliser les guards admin existants.
- S'aligner sur l'observabilité et les pratiques de release/ops déjà introduites dans l'epic 66.

### File Structure Requirements

- Backend admin router + sécurité.
- Frontend admin prompts.
- Suites de tests ciblées.

### Testing Requirements

- Test non autorisé.
- Test confirmation/action visible.
- Test marquage observabilité admin.
- Test non-régression preview/exécution.

### Previous Story Intelligence

- `69.1` et `69.2` rendent la surface d'exécution opérationnelle.
- Cette story doit en fermer les risques principaux avant mise en usage effectif.

### Project Structure Notes

- Pas de raccourci sécurité côté UI.
- Réutiliser les mécanismes admin déjà présents dans le monorepo.

### References

- [architecture.md](C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)
- [66-44-gate-production-continue-par-snapshot.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-44-gate-production-continue-par-snapshot.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Story file created from BMAD backlog.
- **Implémentation (2026-04-18)** : modal de confirmation avant POST `execute-sample`, bandeau de mode d'inspection permanent, renfort observabilité backend (logs structurés `admin_manual_llm_execute_surface`, champ `execution_surface` dans l'audit, en-tête `X-Admin-Manual-Llm-Execute` sur toutes les réponses de cette route), tests 401/403 + en-tête sur succès/échec, test Vitest sur le flux de confirmation.

### File List

- `_bmad-output/implementation-artifacts/69-3-securiser-surface-execution-manuelle-et-qa.md`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- (revue) `backend/tests/integration/test_admin_llm_catalog.py` — constante d’en-tête partagée

### Change Log

- 2026-04-18 : Garde-fous UX (confirmation + bandeau de mode), observabilité admin (logs, audit, en-tête HTTP), tests d’auth et de flux front.
- 2026-04-18 : Revue code — tests d’intégration alignés sur `ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER` (plus de littéral dupliqué).

### Review Findings

- [x] [Review][Patch] Assertions d’en-tête HTTP dupliquent le littéral `X-Admin-Manual-Llm-Execute` au lieu d’importer `ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER` depuis `app.api.v1.routers.admin_llm` — risque de dérive si le nom change. [`backend/tests/integration/test_admin_llm_catalog.py` ~1854, ~1925] — corrigé : import et assertions sur la constante.

- [x] [Review][Defer] Cas limite TanStack : si `manualExecuteMutation.isSuccess` est vrai sans `data`, le bloc « aide » sous « Retour LLM » ne s’affiche plus (condition réduite à `!isSuccess`). Acceptable si le contrat mutation garantit `data` en succès ; sinon à surveiller. [`frontend/src/pages/admin/AdminPromptsPage.tsx` ~1272]
