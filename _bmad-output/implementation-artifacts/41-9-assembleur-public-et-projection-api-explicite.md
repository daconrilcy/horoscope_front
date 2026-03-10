# Story 41.9: Assembleur public et projection API explicite

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a équipe backend responsable du contrat `/v1/predictions/daily`,
I want sortir toute la logique de projection publique du routeur vers un assembleur dédié,
so that la frontière API devienne lisible, testable et distincte de la logique HTTP et du calcul moteur.

## Acceptance Criteria

1. La logique de projection publique est déplacée hors de `backend/app/api/v1/routers/predictions.py` vers un module dédié:
   - `PublicPredictionAssembler`
   - `PublicDecisionWindowPolicy`
   - `PublicTurningPointPolicy`
   - `PublicTimelinePolicy`
   - `PublicSummaryPolicy`

2. Le routeur `GET /v1/predictions/daily` devient essentiellement un point d’entrée HTTP:
   - validation des paramètres et dépendances FastAPI
   - appel du service applicatif
   - chargement du modèle de lecture nécessaire
   - appel de l’assembleur public
   - retour du DTO

3. Les fonctions de reconstruction publique actuelles sont migrées dans la nouvelle couche dédiée:
   - `_build_public_decision_windows`
   - `_build_public_turning_points`
   - `_build_public_timeline`
   - `_build_summary`
   - `_filter_major_categories`
   - `_build_turning_point_summary`
   - `_build_timeline_summary`

4. La sémantique publique actuelle est conservée:
   - la projection produit actuelle reste préservée à comportement égal
   - les catégories dominantes, fenêtres filtrées, pivots publics, timeline synthétique et résumé restent cohérents entre eux
   - l’assembleur ne fige pas un faux contrat de projection directe depuis les seuls aspects majeurs
   - le DTO public reste identique ou compatible à comportement égal

5. La story accepte explicitement une entrée de lecture provisoire tant que le snapshot typé de 41.11 n’existe pas encore:
   - l’assembleur peut consommer un read model intermédiaire non encore typé si nécessaire
   - la transition vers `PersistedPredictionSnapshot` est prévue sans double refacto de la sémantique publique
   - les responsabilités de lecture et d’assemblage restent déjà séparées

6. La nouvelle projection est testée indépendamment du routeur:
   - tests unitaires d’assembleur/policies
   - tests d’intégration API vérifiant que le contrat reste stable

## Tasks / Subtasks

- [ ] Task 1: Créer la couche `public_projection` (AC: 1)
  - [ ] Ajouter `backend/app/prediction/public_projection.py`
  - [ ] Définir les responsabilités des policies et de l’assembleur
  - [ ] Éviter un module monolithique en organisant clairement les helpers internes

- [ ] Task 2: Migrer la logique métier publique hors du routeur (AC: 1, 3, 4)
  - [ ] Déplacer les builders et filtres publics existants
  - [ ] Préserver les règles issues de 41.6 sur les aspects majeurs et pivots publics
  - [ ] Maintenir la compatibilité des tests existants

- [ ] Task 3: Réduire le routeur API à sa responsabilité HTTP (AC: 2, 5)
  - [ ] Simplifier `backend/app/api/v1/routers/predictions.py`
  - [ ] Retirer la logique de projection devenue redondante
  - [ ] Conserver les validations et dépendances FastAPI explicites
  - [ ] Introduire si besoin un read model intermédiaire acceptable avant 41.11

- [ ] Task 4: Tester la projection publique comme couche dédiée (AC: 6)
  - [ ] Ajouter des tests unitaires ciblés de l’assembleur
  - [ ] Mettre à jour les tests d’intégration `/v1/predictions/daily`
  - [ ] Vérifier l’absence de changement de contrat inattendu

## Dev Notes

- Cette story est le cœur du désenchevêtrement entre moteur, persistance et payload public.
- Le routeur ne doit plus “recalculer du produit”; il doit déléguer à un assembleur clairement identifié.
- La meilleure option retenue est bien une projection publique dédiée, et non une exposition brute de l’output moteur.
- La sémantique produit actuelle issue de 41.6 doit être conservée, mais déplacée au bon endroit.
- Tant que 41.11 n’est pas implémentée, l’assembleur peut consommer un modèle de lecture intermédiaire stable; cette story ne doit pas forcer prématurément `PersistedPredictionSnapshot`.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/api/v1/routers/predictions.py`
  - `backend/app/prediction/public_projection.py` (nouveau)
  - `backend/app/prediction/persistence_service.py`
  - `backend/app/prediction/schemas.py`

### Technical Requirements

- L’assembleur doit consommer une représentation de lecture stable, sans dépendre du routeur.
- Cette représentation peut être provisoire avant 41.11, à condition que l’interface assembleur reste séparée de la lecture de persistance.
- Les policies doivent être testables indépendamment et rester déterministes.
- Ne pas dupliquer la logique entre routeur et assembleur pendant la migration finale.

### Architecture Compliance

- Cette story matérialise l’architecture cible “moteur interne → projection persistée → assembleur API public”.
- Le routeur FastAPI ne doit plus contenir de logique métier produit significative.
- La projection publique doit vivre côté backend domain/service/prediction, pas côté frontend.

### Library / Framework Requirements

- FastAPI et Pydantic existants uniquement.
- Aucun ajout de dépendance externe nécessaire.

### File Structure Requirements

- La nouvelle couche doit vivre dans `backend/app/prediction/public_projection.py`.
- Le routeur doit rester un fichier d’API, pas un conteneur de policies.

### Testing Requirements

- Couvrir:
  - projection de `decision_windows`
  - projection de `turning_points`
  - projection de `timeline`
  - génération du `summary`
  - compatibilité entre entrée de lecture provisoire et future entrée snapshot typée
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 41.4 a introduit le recentrage API/UI autour de l’aide à la décision intraday; cette story consolide cette direction en l’isolant du routeur. [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]
- 41.6 a ajouté une projection publique plus cohérente; la logique doit maintenant quitter `predictions.py` pour éviter la dette de conception actuelle. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]

### Git Intelligence Summary

- `3448e68 feat(daily): align agenda and turning points semantics` a renforcé la logique publique dans le routeur; cette story vise explicitement à l’extraire sans perdre la sémantique produit acquise.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md` et des artefacts BMAD existants.

### References

- [Source: user refactor plan 2026-03-10 — Phase 3 projection publique dédiée]
- [Source: backend/app/api/v1/routers/predictions.py]
- [Source: backend/app/prediction/persistence_service.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir du plan de refacto Epic 41 fourni le 2026-03-10.

### Completion Notes List

- Story prête pour extraire la logique publique du routeur sans changer la sémantique du contrat daily.

### File List

- `_bmad-output/implementation-artifacts/41-9-assembleur-public-et-projection-api-explicite.md`
