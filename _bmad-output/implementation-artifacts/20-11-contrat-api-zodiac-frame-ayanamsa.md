# Story 20.11: Contrat API zodiac/frame/ayanamsa

Status: done

## Story

As a API consumer,
I want un contrat explicite pour `zodiac`, `frame`, `ayanamsa` et `altitude_m`,
so that je peux piloter le calcul natal sans ambiguïté et diagnostiquer les erreurs proprement.

## Acceptance Criteria

1. **Given** `zodiac=sidereal` sans ayanamsa **When** la requête est traitée **Then** l'ayanamsa effective (`lahiri` ruleset par défaut) est visible dans la réponse.
2. **Given** `frame=topocentric` sans altitude **When** la requête est traitée **Then** l'altitude effective est `0`.
3. **Given** des paramètres invalides (`zodiac`/`frame`) **When** la requête est soumise **Then** l'API retourne `422` avec code métier explicite.
4. **Given** un résultat retourné **When** on lit `result` et `metadata` **Then** les champs dupliqués de configuration de calcul sont cohérents.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-3) Durcir la validation des entrées API natal
  - [x] Enum stricte `zodiac`, `frame`
  - [x] Gestion explicite ayanamsa par défaut en sidéral
- [x] Task 2 (AC: 1, 2, 4) Exposer les paramètres effectifs
  - [x] Garantir la traçabilité des valeurs effectives dans `result` et `metadata`
- [x] Task 3 (AC: 3) Normaliser les erreurs
  - [x] Codes d'erreur stables (`invalid_*`) avec détail actionnable
- [x] Task 4 (AC: 1-4) Couverture tests API/integration
  - [x] Cas sidéral sans ayanamsa
  - [x] Cas topocentric sans altitude
  - [x] Cas paramètres invalides
  - [x] Invariant cohérence `result`/`metadata`

## Dev Notes

- Endpoint concerné: `/v1/users/me/natal-chart` et lecture `/v1/users/me/natal-chart/latest`.
- La logique centrale passe par `NatalCalculationService.calculate(...)`.
- Vérifier la non-régression de `accurate=False` et des payloads existants frontend.

### Project Structure Notes

- Backend API + services.
- Impacts: routers `users`, modèles de requête/réponse, `natal_calculation_service`, tests d'intégration.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2011--contrat-api-et-traçabilité-des-options-zodiacframe]
- [Source: backend/app/services/natal_calculation_service.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (with Adversarial Review fixes by Gemini CLI)

### Debug Log References

### Completion Notes List

- Implémentation du contrat de calcul effectif dans `NatalCalculationService.calculate(...)`:
  - validation/normalisation métier de `zodiac` (`tropical|sidereal`) et `frame` (`geocentric|topocentric`)
  - ayanamsa effectif par défaut `lahiri` quand `zodiac=sidereal` sans valeur fournie
  - altitude effective `0.0` quand `frame=topocentric` sans valeur fournie
  - **Fix (Review)**: Validation stricte de `ayanamsa` contre `SUPPORTED_AYANAMSAS` (lahiri, fagan_bradley).
  - **Fix (Review)**: Exigence du mode `accurate=True` pour toute requête `sidereal` ou `topocentric` afin d'éviter les résultats incohérents du moteur `simplified`.
  - **Fix (Review)**: Mapping des erreurs `EphemerisCalcError` et `HousesCalcError` vers `NatalCalculationError` (évite les 500 en cas de défaut d'éphémérides).
- Extension du contrat de sortie pour exposer `altitude_m` dans `result` et `metadata`.
- Ajout de tests d'intégration API couvrant:
  - sidéral sans ayanamsa (avec `accurate=True`)
  - topocentric sans altitude (avec `accurate=True`)
  - erreurs `invalid_zodiac` / `invalid_frame` / `invalid_ayanamsa`
  - erreur `accurate_mode_required`
  - invariant de cohérence entre `result` et `metadata`
- Validation locale effectuée (venv activé):
  - `pytest -q app/tests/integration/test_user_natal_chart_api.py` (35 passed)

### File List

- backend/app/services/natal_calculation_service.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/services/user_natal_chart_service.py
- backend/app/tests/integration/test_user_natal_chart_api.py
- backend/app/services/ai_engine_adapter.py
- backend/app/services/geocoding_service.py
- backend/app/tests/unit/conftest.py
- backend/app/domain/astrology/calculators/aspects.py
- backend/app/domain/astrology/ephemeris_provider.py
- backend/app/tests/integration/test_ephemeris_api.py
- backend/app/tests/integration/test_natal_chart_accurate_api.py
- backend/app/tests/unit/test_ephemeris_bootstrap.py
- backend/app/tests/unit/test_ephemeris_provider.py

## Change Log

- 2026-02-26: Implémentation du contrat API `zodiac/frame/ayanamsa/altitude_m` avec valeurs effectives exposées et erreurs métier explicites (`invalid_zodiac`, `invalid_frame`), plus couverture de tests d'intégration associée.
- 2026-02-26: Validation globale repo lancée; blocages hors périmètre détectés (lint historique + tests dépendants d'un provider LLM non configuré), puis levés dans la même session. Story promue en `review`.
- 2026-02-27: Correctif post-review - alignement comportement/contrat `frame=topocentric` sur les positions planétaires (propagation complète vers provider SwissEph).
