# Story 41.3 : Fenêtres décisionnelles et pivots filtrés

Status: backlog

## Story

En tant que product owner de la prédiction quotidienne,
je veux remplacer la timeline rigide par quelques fenêtres décisionnelles fortes et des pivots filtrés,
afin que l'utilisateur voie clairement quand agir, temporiser ou éviter une décision, sans bruit inutile.

## Acceptance Criteria

### AC1 — Le découpage intraday n'est plus une simple grille horaire fixe

- [ ] Les blocs sont créés à partir de changements de signal réels puis fusionnés tant que le signal reste équivalent
- [ ] La timeline ne produit plus par défaut une série de blocs horaires répétitifs 00:00-01:00, 01:00-02:00, etc.

### AC2 — Les pivots reposent sur le signal utile

- [ ] Les pivots sont détectés à partir du signal brut ou semi-brut pertinent, pas seulement via des notes entières arrondies
- [ ] Les changements mineurs ou purement techniques ne deviennent pas des pivots utilisateur

### AC3 — Le moteur expose des fenêtres décisionnelles métier

- [ ] Le moteur produit une structure de fenêtres avec type (`favorable`, `prudence`, `pivot`) et score/confiance
- [ ] Chaque fenêtre contient un nombre limité de catégories vraiment dominantes et de drivers principaux
- [ ] Le nombre de fenêtres quotidiennes reste raisonnable et lisible

### AC4 — Le meilleur créneau devient un indicateur d'actionnabilité

- [ ] Le “meilleur créneau” est sélectionné sur un score d'actionnabilité et de stabilité, pas uniquement sur le top 3 global

### AC5 — Contrat API prêt pour le front

- [ ] L'API daily prediction peut exposer ces nouvelles fenêtres sans casser les usages existants, ou via un champ additionnel versionné

## Tasks / Subtasks

### T1 — Redéfinir la logique de pivot

- [ ] Réviser `TurningPointDetector`
- [ ] Définir des critères de valeur produit et de filtrage

### T2 — Revoir la génération des blocs

- [ ] Remplacer le découpage horaire fixe par un découpage piloté par variation de signal
- [ ] Fusionner les blocs quasi-identiques

### T3 — Introduire les fenêtres décisionnelles

- [ ] Définir le datamodel backend
- [ ] Calculer type, force et confiance
- [ ] Préparer le mapping API

### T4 — Recalculer le “best window”

- [ ] Mettre à jour `EditorialOutputBuilder`
- [ ] Vérifier la cohérence avec les nouvelles fenêtres

### T5 — Tests

- [ ] Ajouter des tests unitaires et d'intégration sur le bruit intraday et le nombre de fenêtres produites

## Dev Notes

- Cette story est le cœur produit du chantier: elle transforme un moteur “chronologie calculée” en moteur “aide à la décision”.
- Elle dépend de 41.1 et 41.2.

### Fichiers probables à toucher

- `backend/app/prediction/turning_point_detector.py`
- `backend/app/prediction/block_generator.py`
- `backend/app/prediction/editorial_builder.py`
- `backend/app/prediction/schemas.py`
- `backend/app/api/v1/routers/predictions.py`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
