# Story 41.11: Snapshot persisté et nettoyage de la frontière API/persistance

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a équipe backend finalisant le refactor Epic 41,
I want introduire un snapshot persisté typé et nettoyer la frontière entre persistance, réparation de contexte et exposition API,
so that la lecture des runs daily soit robuste, typée et séparée des mécanismes techniques de réparation et de continuité de service.

## Acceptance Criteria

1. La couche persistance expose un objet `PersistedPredictionSnapshot` typé au lieu d’un `dict[str, Any]` hétérogène pour les lectures complètes de run.

2. La lecture d’un run pour réutilisation technique par hash est clairement distincte de la lecture du dernier run utilisable pour fallback:
   - responsabilités séparées
   - noms explicites
   - pas de confusion dans le service applicatif

3. Les mécanismes d’auto-réparation du contexte prediction sont sortis du cas d’usage principal:
   - création de `PredictionContextRepairService` ou équivalent
   - `_auto_seed_prediction_context` et `_repair_locked_incomplete_reference_version` ne vivent plus dans le service principal daily
   - le déclenchement, l’idempotence et la journalisation de cette réparation sont explicites et observables

4. La frontière API finale est nettoyée:
   - le routeur appelle le service
   - charge le snapshot typé si nécessaire
   - appelle l’assembleur public
   - retourne le DTO

5. Des tests couvrent:
   - construction/usage du snapshot typé
   - séparation réutilisation vs fallback
   - déclenchement contrôlé de la réparation de contexte
   - observabilité minimale de la réparation de contexte

## Tasks / Subtasks

- [ ] Task 1: Introduire le snapshot typé de persistance (AC: 1)
  - [ ] Créer `backend/app/prediction/persisted_snapshot.py`
  - [ ] Modéliser le run complet, les catégories, blocs, turning points et metadata nécessaires
  - [ ] Adapter les repositories/services de lecture à renvoyer ce snapshot

- [ ] Task 2: Séparer lecture de réutilisation et lecture de fallback (AC: 2, 5)
  - [ ] Clarifier les méthodes repository/service concernées
  - [ ] Éviter les chemins ambigus autour des “last runs”
  - [ ] Mettre à jour les tests de service

- [ ] Task 3: Extraire la réparation de contexte prediction (AC: 3)
  - [ ] Créer `backend/app/services/prediction_context_repair_service.py`
  - [ ] Déplacer l’auto-seed et la réparation de référence verrouillée incomplète
  - [ ] Injecter ce composant là où le comportement est réellement requis
  - [ ] Ajouter une journalisation claire du déclenchement et du résultat de réparation

- [ ] Task 4: Finaliser la frontière API/persistance (AC: 4)
  - [ ] Vérifier que le routeur ne manipule plus de `dict` hétérogènes de run
  - [ ] Faire consommer le snapshot typé par l’assembleur public
  - [ ] Vérifier la lisibilité finale du flux daily
  - [ ] Documenter la transition entre le read model provisoire de 41.9 et le snapshot typé final

- [ ] Task 5: Valider la non-régression (AC: 5)
  - [ ] Ajouter/mettre à jour les tests unitaires et d’intégration
  - [ ] Exécuter lint et tests backend ciblés
  - [ ] Vérifier un appel `/v1/predictions/daily` nominal et un scénario de continuité de service

## Dev Notes

- Cette story finalise le nettoyage de la frontière technique après les stories 41.8 à 41.10.
- Le snapshot typé doit devenir la représentation standard lue par la projection publique.
- La réparation de contexte est utile, mais elle ne doit plus polluer le cas d’usage principal “obtenir l’horoscope du jour”.
- La séparation réutilisation vs fallback doit être lisible à la lecture du code sans devoir connaître l’historique du service.
- Cette story finalise la transition de lecture commencée en 41.9 en remplaçant le read model provisoire par le snapshot typé cible.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/prediction/persistence_service.py`
  - `backend/app/prediction/persisted_snapshot.py` (nouveau)
  - `backend/app/services/prediction_context_repair_service.py` (nouveau)
  - `backend/app/services/daily_prediction_service.py`
  - `backend/app/api/v1/routers/predictions.py`
  - `backend/app/prediction/public_projection.py`

### Technical Requirements

- Le snapshot typé doit couvrir le besoin de l’assembleur public sans repasser par des dictionnaires non typés.
- La réparation de contexte doit rester idempotente et explicitement contrôlée.
- La réparation de contexte doit être observable en production via logs structurés explicites.
- Préserver la compatibilité avec les runs persistés existants autant que possible.

### Architecture Compliance

- Cette story matérialise la frontière finale:
  - service applicatif
  - persistance typée
  - assembleur public
  - routeur HTTP mince
- Les comportements techniques transverses de réparation ne doivent plus vivre dans le cœur du cas d’usage.

### Library / Framework Requirements

- Réutiliser la stack backend existante uniquement.
- Aucun ajout de dépendance requis.

### File Structure Requirements

- Le snapshot typé vit dans `backend/app/prediction/persisted_snapshot.py`.
- Le service de réparation de contexte vit dans `backend/app/services/prediction_context_repair_service.py`.

### Testing Requirements

- Couvrir:
  - lecture snapshot typé
  - séparation réutilisation/fallback
  - réparation de contexte
  - journalisation/observabilité de la réparation de contexte
  - intégration `/v1/predictions/daily`
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 31.3 a déjà introduit des notions de seed/réparation de version de référence; cette story doit préserver ce comportement tout en le sortant du service principal. [Source: _bmad-output/implementation-artifacts/31-3-migration-d-reference-version-2-seed-lock.md]
- 35.1 a posé la persistance du run; cette story complète la lecture en snapshot typé pour la projection publique moderne. [Source: _bmad-output/implementation-artifacts/35-1-persistance-run.md]

### Git Intelligence Summary

- Les incidents récents sur `/v1/predictions/daily` ont montré que la lisibilité de la chaîne de lecture/reconstruction est devenue critique; cette story finalise la remise en ordre structurelle.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md` et des artefacts BMAD existants.

### References

- [Source: user refactor plan 2026-03-10 — Phase 5 nettoyage API et persistance]
- [Source: backend/app/prediction/persistence_service.py]
- [Source: backend/app/api/v1/routers/predictions.py]
- [Source: backend/app/services/daily_prediction_service.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir du plan de refacto Epic 41 fourni le 2026-03-10.

### Completion Notes List

- Story prête pour finaliser la frontière persistance/API daily prediction avec snapshot typé et réparation de contexte extraite.

### File List

- `_bmad-output/implementation-artifacts/41-11-snapshot-persisted-et-nettoyage-frontiere-api-persistance.md`
