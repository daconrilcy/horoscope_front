# Story 69.1: Exécuter manuellement une cible canonique depuis un sample payload

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / LLM operator,
I want déclencher explicitement une exécution LLM à partir d'une runtime preview valide,
so that je puisse vérifier le comportement réel du provider sur une cible canonique contrôlée.

## Acceptance Criteria

1. Une exécution réelle peut être déclenchée uniquement depuis une runtime preview valide.
2. Une runtime preview incomplète bloque l'action d'exécution avec un message explicite.
3. L'appel réel transporte les métadonnées runtime pertinentes (`manifest_entry_id`, provider, modèle, paramètres).
4. L'exécution suit le chemin nominal du gateway et ses garde-fous existants.

## Tasks / Subtasks

- [ ] Task 1: Définir l'endpoint ou la commande admin d'exécution manuelle (AC: 1, 2, 3, 4)
  - [ ] Choisir un endpoint explicite distinct de la preview.
  - [ ] Définir le contrat d'entrée à partir du sample payload sélectionné.
- [ ] Task 2: Brancher le déclenchement UI (AC: 1, 2)
  - [ ] Ajouter l'action `Exécuter avec le LLM`.
  - [ ] Afficher les préconditions et les blocages.
- [ ] Task 3: Verrouiller la corrélation et la sécurité (AC: 3, 4)
  - [ ] Préserver request/correlation ids et métadonnées d'observabilité.
  - [ ] Vérifier permissions admin strictes.

## Dev Notes

### Technical Requirements

- Cette story introduit un appel provider réel.
- Il ne faut pas contourner `LLMGateway` ni `ProviderRuntimeManager`.
- Le déclenchement doit être explicitement opérateur, jamais implicite au chargement de la page.

### Architecture Compliance

- Respecter les garde-fous `timeout`, `retry`, `classification d'erreurs`, `redaction`, `observability`.
- L'exécution admin doit être distinguable du trafic nominal produit.

### File Structure Requirements

- Backend admin LLM router.
- Frontend admin prompts.
- Tests backend et frontend sur succès/erreur/blocage.

### Testing Requirements

- Cas valide.
- Cas bloqué car runtime preview incomplète.
- Cas erreur provider.
- Cas accès non autorisé.

### Previous Story Intelligence

- `68.2` fournit la runtime preview sur laquelle l'exécution s'appuie.
- `66.33`, `66.37`, `66.43`, `66.44` sont des références critiques pour le comportement runtime et ops.

### Project Structure Notes

- Toute action doit être visible et explicitement confirmable côté UI.

### References

- [docs/llm-prompt-generation-by-feature.md](C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [66-33-durcissement-operationnel-appel-provider-openai.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-33-durcissement-operationnel-appel-provider-openai.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)
- [66-43-chaos-testing-provider-runtime.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-43-chaos-testing-provider-runtime.md)
- [66-44-gate-production-continue-par-snapshot.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-44-gate-production-continue-par-snapshot.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Story file created from BMAD backlog.

### File List

- `_bmad-output/implementation-artifacts/69-1-executer-manuellement-cible-canonique-depuis-sample-payload.md`
