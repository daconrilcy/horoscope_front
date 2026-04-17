# Story 69.2: Afficher le retour LLM brut, structuré et les métadonnées d'exécution

Status: ready-for-dev

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

- [ ] Task 1: Définir le payload de réponse d'exécution admin (AC: 1, 2, 3, 4)
  - [ ] Exposer les métadonnées utiles à l'opérateur.
  - [ ] Prévoir réponse brute et réponse structurée.
- [ ] Task 2: Construire l'affichage frontend du retour LLM (AC: 1, 2, 3)
  - [ ] Organiser la zone `Retour LLM`.
  - [ ] Prévoir vues succès/erreur.
- [ ] Task 3: Ajouter redaction et tests (AC: 3, 4)
  - [ ] Vérifier les champs masqués/tronqués.
  - [ ] Vérifier la lisibilité des états d'erreur.

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

- Story file created from BMAD backlog.

### File List

- `_bmad-output/implementation-artifacts/69-2-afficher-retour-llm-brut-structure-metadonnees-execution.md`
