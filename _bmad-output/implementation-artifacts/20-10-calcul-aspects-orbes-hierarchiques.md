# Story 20.10: Calcul des aspects avec orbes hiérarchiques

Status: done

## Story

As a astrologie-engine maintainer,
I want appliquer une résolution hiérarchique des orbes par aspect/paires,
so that les aspects calculés reflètent la règle métier configurée par ruleset.

## Acceptance Criteria

1. **Given** un aspect avec `default_orb_deg=6` **When** `|delta-angle|=5.5` **Then** l'aspect est retenu avec `orb_used=6`.
2. **Given** un override luminaire (`orb_luminaries=8`) **When** Soleil-Lune a `orb=7` **Then** l'aspect est retenu avec `orb_used=8`.
3. **Given** un override paire (`sun-mercury=9`) **When** `orb=8.5` **Then** l'aspect est retenu avec `orb_used=9`.
4. **Given** un résultat d'aspect **When** il est sérialisé **Then** `orb` et `orb_used` sont exposés.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-3) Étendre le moteur `calculate_major_aspects`
  - [x] Remplacer `max_orb` global par stratégie de résolution hiérarchique
  - [x] Intégrer les règles par aspect et overrides de paires/luminaires
- [x] Task 2 (AC: 4) Étendre le schéma de sortie des aspects
  - [x] Ajouter `orb_used` au modèle de domaine (`AspectResult`)
  - [x] Propager dans API/DTO de résultat natal
- [x] Task 3 (AC: 1-4) Tests unitaires de calcul
  - [x] Cas `default_orb`
  - [x] Cas override luminaires
  - [x] Cas override paire
  - [x] Vérification stabilité tri/déterminisme

## Dev Notes

- Point de calcul actuel: `backend/app/domain/astrology/calculators/aspects.py`.
- Conserver le comportement déterministe (tri stable) pour ne pas casser les tests de cohérence.
- Garder un fallback sûr si une règle d'orbe est absente: utiliser `default_orb_deg` de l'aspect.

### Project Structure Notes

- Backend uniquement.
- Impacts: `domain/astrology/calculators`, `domain/astrology/natal_calculation.py`, tests unitaires aspects/natal.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2010--calcul-des-aspects-avec-résolution-dorbe-hiérarchique]
- [Source: backend/app/domain/astrology/calculators/aspects.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_aspects_calculator.py` (RED: 4 fails attendus)
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_aspects_calculator.py app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_natal_interpretation_service.py app/tests/integration/test_natal_interpretation_endpoint.py app/tests/integration/test_natal_calculate_api.py` (GREEN: 61 passed)
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/domain/astrology/calculators/aspects.py app/domain/astrology/natal_calculation.py app/tests/unit/test_aspects_calculator.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/domain/astrology/calculators/aspects.py app/domain/astrology/natal_calculation.py app/tests/unit/test_aspects_calculator.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` (25 échecs hors périmètre story: provider OpenAI non configuré + logs geocoding)

### Completion Notes List
- Implémentation de la résolution hiérarchique d’orbe dans `calculate_major_aspects` avec priorité `pair > luminaries > default`.
- Optimisation de la boucle de calcul par pré-normalisation des positions et clés de paires.
- Centralisation de `LUMINARIES` dans `app/core/constants.py` et utilisation de `DEFAULT_FALLBACK_ORB`.
- Ajout de `orb_used` dans chaque aspect calculé, en conservant le tri déterministe existant.
- Compatibilité préservée avec le format historique des définitions d’aspects.
- Extension du modèle de domaine `AspectResult` avec champ `orb_used`.
- Ajout de tests unitaires dédiés couvrant les cas AC: défaut, override luminaires, override paire et sérialisation `orb_used`.

### File List
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/tests/unit/test_aspects_calculator.py`

### Change Log
- 2026-02-26: Implémentation story 20.10 (résolution hiérarchique des orbes + champ `orb_used` + tests unitaires dédiés).
- 2026-02-27: Correctif post-review - branchement end-to-end confirmé avec chargement des règles hiérarchiques persistées depuis les données de référence (via `astro_characteristics` côté repository).
