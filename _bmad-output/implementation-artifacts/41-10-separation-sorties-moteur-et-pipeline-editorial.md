# Story 41.10: Séparation des sorties moteur et du pipeline éditorial

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a équipe backend maintenant le moteur astrologique daily,
I want séparer explicitement calcul pur, bundle éditorial et bundle persistable,
so that le moteur n’ait plus à muter implicitement ses objets de sortie et que la persistance comme l’API sachent exactement où lire chaque information.

## Acceptance Criteria

1. Le moteur distingue explicitement au moins trois niveaux de sortie:
   - `CoreEngineOutput` pour le calcul pur sans texte
   - `EditorialOutputBundle` pour les textes et résumés
   - `PersistablePredictionBundle` pour la structure prête à sauvegarder

2. `EngineOrchestrator` ne mute plus implicitement les objets cœur pour y injecter les summaries éditoriaux:
   - les blocs temporels et turning points du cœur restent des objets de calcul
   - les textes éditoriaux sont transportés séparément

3. Le pipeline éditorial est rendu explicite derrière une interface de service:
   - `PredictionEditorialService` ou équivalent
   - l’orchestrateur ne dépend plus des détails internes `EditorialTemplateEngine` + builder

4. La persistance lit ses données depuis le bundle persistable explicite:
   - plus d’accès implicite et hétérogène aux summaries selon les objets
   - catégories, blocs et turning points ont une source lisible et cohérente pour leurs textes
   - `PersistablePredictionBundle` porte explicitement la responsabilité finale des textes persistés de catégories, blocs et turning points

5. Le contrat fonctionnel externe reste stable:
   - à comportement égal, le contenu éditorial persistant et exposé reste identique ou compatible
   - la story modifie le contrat interne du moteur, pas la sémantique externe attendue par l’API

6. Les tests couvrent la nouvelle séparation:
   - tests du moteur pur sans éditorial
   - tests du service éditorial
   - tests de persistance sur lecture du bundle persistable

## Tasks / Subtasks

- [ ] Task 1: Introduire les structures de sortie explicites (AC: 1, 2)
  - [ ] Définir `CoreEngineOutput`
  - [ ] Définir `EditorialOutputBundle`
  - [ ] Définir `PersistablePredictionBundle`
  - [ ] Ajuster les types et points d’assemblage internes

- [ ] Task 2: Extraire le service éditorial (AC: 2, 3)
  - [ ] Introduire `backend/app/prediction/editorial_service.py`
  - [ ] Encapsuler `EditorialTemplateEngine` et le builder derrière une interface claire
  - [ ] Réduire la connaissance de l’orchestrateur sur les détails du pipeline éditorial

- [ ] Task 3: Refaire l’assemblage moteur -> persistance (AC: 2, 4, 5)
  - [ ] Adapter `EngineOrchestrator`
  - [ ] Adapter `PredictionPersistenceService`
  - [ ] Vérifier la cohérence des `category_summaries`, `time_block_summaries` et `turning_point_summaries`
  - [ ] Expliciter que `PersistablePredictionBundle` possède la responsabilité finale de ces textes

- [ ] Task 4: Couvrir la séparation par tests ciblés (AC: 6)
  - [ ] Ajouter des tests unitaires du cœur moteur
  - [ ] Ajouter des tests du service éditorial
  - [ ] Mettre à jour les tests de persistance/intégration impactés
  - [ ] Vérifier que le contenu éditorial persistant et exposé reste identique ou compatible à comportement égal

## Dev Notes

- Cette story doit réduire la confusion actuelle entre calcul métier et enrichissement textuel.
- Le but n’est pas de changer le contenu éditorial rendu à l’utilisateur, mais de clarifier les responsabilités et les contrats internes.
- Le bundle persistable doit être le point de jonction unique entre moteur, éditorial et persistance.
- Le cœur moteur doit pouvoir être testé sans dépendre des templates éditoriaux.
- Le propriétaire final des textes persistés est le `PersistablePredictionBundle`, pas le cœur moteur brut.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/prediction/engine_orchestrator.py`
  - `backend/app/prediction/editorial_builder.py`
  - `backend/app/prediction/editorial_template_engine.py`
  - `backend/app/prediction/editorial_service.py` (nouveau)
  - `backend/app/prediction/persistence_service.py`

### Technical Requirements

- Les nouveaux bundles doivent être explicitement typés.
- Éviter toute mutation implicite d’objets partagés entre couches.
- Préserver le contenu produit des textes et summaries à comportement égal.
- Toute évolution de contrat doit rester interne tant que l’API publique et la persistance exposée restent compatibles.

### Architecture Compliance

- Cette story met en œuvre la séparation cible entre moteur pur et enrichissement éditorial.
- La persistance doit lire une projection persistable explicite, pas dépendre d’effets de bord dans les objets moteur.
- L’API publique reste consommatrice aval, pas productrice de texte métier.

### Library / Framework Requirements

- Réutiliser la stack backend existante uniquement.
- Aucun ajout de dépendance requis.

### File Structure Requirements

- Le service éditorial dédié doit vivre dans `backend/app/prediction/editorial_service.py`.
- Les structures de sortie peuvent vivre dans un module dédié prediction si cela réduit le couplage.

### Testing Requirements

- Couvrir séparément:
  - moteur pur
  - assemblage éditorial
  - persistance
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 35.4 a introduit la couche éditoriale mais avec une intégration encore couplée au moteur; cette story complète cette séparation. [Source: _bmad-output/implementation-artifacts/35-4-couche-editoriale.md]
- 40.1 a humanisé summaries de blocs et turning points; il faut conserver ce rendu tout en supprimant la mutation implicite actuelle. [Source: _bmad-output/implementation-artifacts/40-1-summaries-humanises-time-blocks-et-turning-points.md]

### Git Intelligence Summary

- Les stabilisations successives autour de l’intraday ont accru la dépendance entre output moteur et projection textuelle; cette story vise à remettre de l’ordre sans perdre les gains éditoriaux récents.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md` et des artefacts BMAD existants.

### References

- [Source: user refactor plan 2026-03-10 — Phase 4 ordre dans le moteur et l’éditorial]
- [Source: backend/app/prediction/engine_orchestrator.py]
- [Source: backend/app/prediction/persistence_service.py]
- [Source: backend/app/prediction/editorial_builder.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir du plan de refacto Epic 41 fourni le 2026-03-10.

### Completion Notes List

- Story prête pour clarifier le pipeline interne moteur -> éditorial -> persistance.

### File List

- `_bmad-output/implementation-artifacts/41-10-separation-sorties-moteur-et-pipeline-editorial.md`
