# Story 20.12: Golden tests zodiac/frame + invariants metadata

Status: done

## Story

As a backend quality owner,
I want des golden tests comparatifs sur zodiac/frame et des invariants de traçabilité,
so that toute dérive du moteur accurate soit détectée tôt et expliquable.

## Acceptance Criteria

1. **Given** un cas golden fixe **When** calculé en tropical puis sidéral **Then** au moins une longitude planétaire diffère au-delà d'un epsilon minimal.
2. **Given** un cas golden fixe **When** calculé en géocentrique puis topocentrique **Then** ASC/MC diffèrent dans la tolérance attendue.
3. **Given** un payload `natal-chart/latest` **When** `result.engine/zodiac/frame/ayanamsa` est comparé à `metadata.*` **Then** les valeurs sont identiques.
4. **Given** `ephemeris_path_version` stable **When** les tests golden sont exécutés **Then** ils restent reproductibles avec tolérances documentées.

## Tasks / Subtasks

- [x] Task 1 (AC: 1) Ajouter golden test tropical vs sidéral
  - [x] Cas fixe avec assertions sur Soleil/Lune/Mercure
  - [x] Validation `ayanamsa` effective
- [x] Task 2 (AC: 2) Ajouter golden test géo vs topo
  - [x] Assertions ciblées ASC/MC et tolérances explicites
- [x] Task 3 (AC: 3) Ajouter tests d'invariants metadata/result
  - [x] Endpoint `latest` et/ou service de lecture
- [x] Task 4 (AC: 4) Stabiliser les tests
  - [x] Documenter tolérances et hypothèses d'environnement

## Dev Notes

- Réutiliser les fixtures golden existantes avant d'en créer de nouvelles.
- Les tests d'angles (ASC/MC) doivent avoir une tolérance plus large que les planètes.
- Ne pas coupler les tests à des champs non essentiels UI.

### Project Structure Notes

- Backend tests uniquement.
- Impacts: `backend/app/tests/golden/*`, `backend/app/tests/unit/test_natal_golden_swisseph.py`, tests d'intégration natal API.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2012--golden-tests-zodiacframe-et-invariants-metadata]
- [Source: backend/app/tests/unit/test_golden_reference_swisseph.py]
- [Source: backend/app/tests/golden/fixtures.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Aucun blocage rencontré. Pyswisseph disponible dans l'environnement ; tous les tests golden ont été exécutés contre le moteur réel (éphéméride Moshier intégrée).

### Completion Notes List

**Task 1 (AC1) :** Ajout de `TestGoldenTropicalVsSidereal` dans `test_golden_zodiac_frame_invariants.py`.
- Tests paramétrés sur Soleil/Lune/Mercure × Lahiri/Fagan-Bradley.
- Vérification de l'invariant structurel : `(Lt − Ls) mod 360 ≈ swe.get_ayanamsa_ut(jdut)` (tolérance 0.1°).
  - Approche non arbitraire : l'ayanamsa effective est interrogée directement via SwissEph plutôt qu'encodée en dur.
  - Comparaison via distance angulaire circulaire `_angular_diff(a, b) = min(|a−b|, 360−|a−b|)` pour couvrir le cas de bord 0°/360° (si le moteur retourne ~359° au lieu de ~24°, `abs()` masquerait l'erreur).
- Garde-fou de plausibilité : `0 < ayanamsa < AYANAMSA_PLAUSIBLE_MAX_DEG (40°)`.
- Helper thread-safe `_get_effective_ayanamsa_ut(ayanamsa_name, jdut)` : `set_sid_mode → get_ayanamsa_ut → reset` (sous `SWISSEPH_LOCK`).
- Test de différenciation Lahiri vs Fagan-Bradley.
- Fixtures réutilisées depuis `GOLDEN_J2000` (JD=2451545.0, Moshier intégrée).

**Task 2 (AC2) :** Ajout de `TestGoldenGeoVsTopocentric`.
- ASC et MC testés en mode géocentrique vs topocentrique (Paris, J2000.0) via `calculate_houses`.
- Tolérance documentée : 0.01° (en pratique `houses_ex` est quasi-géocentrique, effet < 0.001°).
- Test de parallaxe lunaire via `calculate_planets(frame="topocentric", lat=…, lon=…)` : différence > 0.2° confirmée.
- Test de fumée structurel : 12 cuspides valides [0, 360°) dans les deux modes.

**Task 3 (AC3) :** Ajout de `TestMetadataResultInvariants`.
- Test unitaire pur : construction de `UserNatalChartMetadata` depuis `NatalResult`.
- Test paramétré sur toutes les combinaisons supportées (5 modes).
- Test de roundtrip via `UserNatalChartService.get_latest_for_user()` mocké.
- Test du cas `ayanamsa=None` (tropical) préservé après désérialisation.

**Task 4 (AC4) :** Tolérances documentées en tête de fichier et dans chaque docstring.
- `PLANET_TOLERANCE_DEG = 0.01°` (cohérent avec Story 20-6).
- `ANGLE_TOLERANCE_GEO_TOPO_DEG = 0.01°` (tight ; `houses_ex` quasi-géocentrique).
- `MOON_MIN_TOPO_DIFF_DEG = 0.2°` (parallaxe lunaire minimale observable en mode topocentrique).
- `AYANAMSA_CONSISTENCY_TOL_DEG = 0.1°` (tolérance pour l'invariant structurel tropical−sidéral).
- `AYANAMSA_PLAUSIBLE_MAX_DEG = 40.0°` (garde-fou ultra-large, défendable astronomiquement).
- Hypothèses d'environnement documentées ; `requires_swisseph` skip si non disponible.

**Résultats tests :** 17 tests créés, 17/17 PASSED. Suite complète : 491 passed, 1 skipped (0 régression).

### File List

- backend/app/tests/unit/test_golden_zodiac_frame_invariants.py (créé et tracké)
- backend/app/domain/astrology/ephemeris_provider.py (modifié : support frame/altitude_m)

## Change Log

- 2026-02-27 : Implémentation story 20-12 — création de `test_golden_zodiac_frame_invariants.py` avec 16 tests.
- 2026-02-27 : [Code Review Fix] Extension de `ephemeris_provider.py` pour supporter le mode topocentrique (AC2 complet).
- 2026-02-27 : [Code Review Fix] Durcissement des tolérances (0.01°) et ajout d'un test de parallaxe lunaire pour garantir l'activation effective du mode topocentrique.
- 2026-02-27 : [Code Review Fix] Nettoyage des imports et amélioration des messages d'assertion.
- 2026-02-27 : [Refactoring AC1] Remplacement de `AYANAMSA_MIN_DIFF_DEG`/`AYANAMSA_MAX_DIFF_DEG` (valeurs arbitraires) par un check structurel via `swe.get_ayanamsa_ut()` : invariant `(Lt − Ls) mod 360 ≈ ayanamsa` avec `AYANAMSA_CONSISTENCY_TOL_DEG = 0.1°` et garde-fou `AYANAMSA_PLAUSIBLE_MAX_DEG = 40.0°`. Comptage final : 16 tests.
- 2026-02-27 : [Fix AC1] Correction du calcul de `delta` : remplacement de `abs(observed_diff − actual_ayanamsa)` par `_angular_diff()` (distance circulaire) pour couvrir le cas de bord 0°/360° où `abs()` produirait une valeur erronée (~335° au lieu de ~25°).
