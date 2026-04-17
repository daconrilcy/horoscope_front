# Story 68.3: Permettre la gestion admin des sample payloads depuis la surface de contrôle

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin platform operator,
I want créer, modifier, dupliquer et supprimer des sample payloads depuis l'interface admin,
so that la preview runtime soit maintenable sans passage par la base ou des fixtures cachées.

## Acceptance Criteria

1. L'admin peut créer un sample payload depuis l'UI avec validation guidée.
2. L'admin peut modifier et dupliquer un sample payload existant.
3. L'admin peut désactiver ou supprimer un sample payload obsolète.
4. La sélection des samples reste simple et ciblée par feature/locale.

## Tasks / Subtasks

- [ ] Task 1: Exposer le CRUD admin des sample payloads (AC: 1, 2, 3)
  - [ ] Créer les endpoints et schémas nécessaires.
  - [ ] Encadrer permissions et validation.
- [ ] Task 2: Intégrer les écrans/formulaires admin (AC: 1, 2, 3, 4)
  - [ ] Ajouter la liste, le détail, la duplication et la suppression.
  - [ ] Rendre la navigation compatible avec la zone `Données d'exemple`.
- [ ] Task 3: Tester UX et auditabilité (AC: 3, 4)
  - [ ] Vérifier les listes filtrées.
  - [ ] Vérifier le comportement des samples par défaut ou recommandés.

## Dev Notes

### Technical Requirements

- Garder un formulaire guidé et borné.
- Éviter un éditeur JSON totalement libre sans garde-fous minimaux.
- La duplication doit être préférée à l'écrasement direct des payloads de référence.

### Architecture Compliance

- Rester dans le domaine admin existant.
- Ne pas créer une surface indépendante qui contourne le catalogue canonique et la vue detail.

### File Structure Requirements

- Backend admin LLM.
- Frontend admin prompts.
- Tests backend + frontend.

### Testing Requirements

- CRUD happy path.
- Validation refus des payloads invalides.
- Filtrage feature/locale.
- Non-régression sur la runtime preview.

### Previous Story Intelligence

- `68.1` et `68.2` posent déjà le contrat et la consommation des sample payloads.
- Cette story ajoute la maintenabilité opérateur autour de ces objets.

### Project Structure Notes

- Respecter les patterns de formulaires React existants du repo.

### References

- [epics-admin-llm-preview-execution.md](C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics-admin-llm-preview-execution.md)
- [AdminPromptsPage.tsx](C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Story file created from BMAD backlog.

### File List

- `_bmad-output/implementation-artifacts/68-3-gerer-sample-payloads-depuis-surface-admin.md`
