# Story 41.14: Projection publique des micro-tendances des journées plates

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant le daily,
I want voir quelques micro-tendances lisibles lorsque la journée est globalement calme,
so that je comprenne les nuances relatives du jour sans que le produit me présente de faux moments forts ou de faux créneaux d’action.

## Acceptance Criteria

1. Le contrat `/v1/predictions/daily` s’enrichit de façon additive pour les journées plates avec:
   - `flat_day`
   - `relative_top_categories`
   - `relative_summary`
   - `micro_trends`

2. Une journée plate reste exposée comme plate:
   - `best_window = null`
   - `main_turning_point = null`
   - `decision_windows = null`
   - `turning_points = []`

3. Les micro-tendances restent strictement secondaires:
   - elles n’alimentent pas la timeline décisionnelle
   - elles ne créent pas de nouvelles fenêtres ou pivots
   - elles utilisent un wording de nuance, pas de promesse d’action forte

4. Le rendu relatif ne s’affiche que si les conditions produit sont réunies:
   - journée plate absolue
   - baseline utilisateur disponible
   - signal relatif minimum atteint

5. Le contrat reste backward-compatible:
   - ajout de champs optionnels uniquement
   - aucun champ existant cassé ou renommé

6. Des tests couvrent:
   - journée plate sans micro-tendance exploitable
   - journée plate avec micro-tendances visibles
   - journée active inchangée
   - cohérence entre `summary`, `categories`, `timeline`, `turning_points` et `decision_windows`

## Tasks / Subtasks

- [x] Task 1: Étendre le contrat public daily (AC: 1, 5)
  - [x] Définir les nouveaux champs DTO/backend
  - [x] Garder les champs optionnels et additifs
  - [x] Préserver la compatibilité des consommateurs existants

- [x] Task 2: Adapter l’assembleur public (AC: 2, 3, 4)
  - [x] Enrichir `PublicPredictionAssembler` et les policies concernées
  - [x] Calculer `flat_day`
  - [x] Injecter `micro_trends` et `relative_summary` sans toucher aux fenêtres/pivots

- [x] Task 3: Définir les règles éditoriales de micro-tendance (AC: 3, 4)
  - [x] Ajouter un wording spécifique aux journées plates
  - [x] Éviter tout vocabulaire de forte actionnabilité
  - [x] Limiter l’affichage à 3 micro-tendances maximum

- [x] Task 4: Couvrir les scénarios produit et la non-régression (AC: 6)
  - [x] Tests unitaires de projection publique
  - [x] Tests d’intégration `/v1/predictions/daily`
  - [x] Vérifier qu’une journée active reste gouvernée par le scoring absolu

## Dev Notes

- Cette story est le point de contact produit visible de la calibration relative.
- La vérité métier principale reste l’absolu: une journée plate doit demeurer plate.
- Le wording doit explicitement présenter les micro-tendances comme des nuances légères.
- Les journées non plates ne doivent pas être polluées par cette nouvelle couche.
- La logique de gating `flat_day` doit rester centralisée et non dupliquée.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/prediction/public_projection.py`
  - `backend/app/api/v1/routers/predictions.py`
  - `backend/app/services/daily_prediction_types.py`
  - `backend/app/prediction/persisted_snapshot.py` ou types équivalents si enrichissement nécessaire

### Technical Requirements

- Les nouveaux champs doivent être optionnels.
- Les micro-tendances doivent dépendre du scoring relatif déjà calculé, pas recalculer localement les statistiques.
- Le résumé relatif doit être cohérent avec `relative_top_categories`.
- Le budget de bruit intraday Epic 41.5 doit rester respecté.

### Architecture Compliance

- L’exposition publique reste gérée par l’assembleur et ses policies, pas par le routeur.
- Les micro-tendances ne doivent pas recoupler l’API publique à des détails internes du moteur intraday.
- Le contrat public doit rester orienté produit et lisible.

### Library / Framework Requirements

- Réutiliser FastAPI, Pydantic et la stack existante uniquement.
- Aucun ajout de dépendance requis.

### File Structure Requirements

- La projection des micro-tendances doit rester dans `backend/app/prediction/public_projection.py`.
- Le routeur ne doit faire qu’exposer le DTO enrichi.

### Testing Requirements

- Couvrir:
  - journée plate neutre sans micro-tendance
  - journée plate avec micro-tendances
  - journée active inchangée
  - backward compatibility du DTO
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 41.4 a recentré le contrat API sur l’aide à la décision intraday; cette story doit préserver cette lisibilité tout en ajoutant une lecture secondaire relative. [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]
- 41.9 a déplacé la logique de projection publique dans l’assembleur; l’extension relative doit donc vivre là, pas dans le routeur. [Source: _bmad-output/implementation-artifacts/41-9-assembleur-public-et-projection-api-explicite.md]

### Git Intelligence Summary

- Les corrections récentes autour des journées plates ont montré que la frontière entre signal public et bruit est sensible; cette story doit enrichir les journées calmes sans rouvrir les problèmes de faux pivots ou faux best windows.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md`, de `epics.md` et de la spec `_bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]
- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/api/v1/routers/predictions.py]
- [Source: backend/app/tests/integration/test_daily_prediction_qa.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir de la spec de calibration relative Epic 41 rédigée le 2026-03-10.
- Implémentation des DTOs enrichis dans `predictions.py`.
- Intégration de `PublicMicroTrendPolicy` et mise à jour de `PublicSummaryPolicy` dans `public_projection.py`.
- Correction de bugs de délégation (`is_non_actionable_day`) et de Pydantic validation dans les tests.

### Completion Notes List

- Story terminée : les journées plates exposent désormais des micro-tendances et un résumé relatif sans affecter les journées actives.
- Validation Pydantic et tests d'intégration API vérifiés.
- Support explicite des micro-tendances percentile-only quand le fallback variance nulle est actif.
- Résumé relatif aligné sur les micro-tendances positives et négatives sans wording systématiquement positif.
- Tests d'intégration renforcés sur journée active réelle, cohérence `summary`/`micro_trends` et DTO additive.

### File List

- `backend/app/api/v1/routers/predictions.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/tests/integration/test_daily_prediction_flat_day.py`
- `_bmad-output/implementation-artifacts/41-14-projection-publique-des-micro-tendances-des-journees-plates.md`
