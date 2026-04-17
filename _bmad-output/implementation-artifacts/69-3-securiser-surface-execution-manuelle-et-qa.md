# Story 69.3: Sécuriser la surface d'exécution manuelle et verrouiller sa QA

Status: ready-for-dev

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

- [ ] Task 1: Encadrer l'action UI d'exécution (AC: 1)
  - [ ] Ajouter une confirmation explicite.
  - [ ] Afficher le mode courant en permanence.
- [ ] Task 2: Verrouiller permissions et sécurité backend (AC: 2)
  - [ ] Vérifier les guards admin.
  - [ ] Refuser tout appel non autorisé même hors UI.
- [ ] Task 3: Couvrir QA et observabilité (AC: 3, 4)
  - [ ] Ajouter les tests backend/frontend requis.
  - [ ] Ajouter ou réutiliser des marqueurs d'observabilité identifiant l'origine admin.

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

### File List

- `_bmad-output/implementation-artifacts/69-3-securiser-surface-execution-manuelle-et-qa.md`
