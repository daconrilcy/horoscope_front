# Story 20.12: Golden tests zodiac/frame + invariants metadata

Status: ready-for-dev

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

- [ ] Task 1 (AC: 1) Ajouter golden test tropical vs sidéral
  - [ ] Cas fixe avec assertions sur Soleil/Lune/Mercure
  - [ ] Validation `ayanamsa` effective
- [ ] Task 2 (AC: 2) Ajouter golden test géo vs topo
  - [ ] Assertions ciblées ASC/MC et tolérances explicites
- [ ] Task 3 (AC: 3) Ajouter tests d'invariants metadata/result
  - [ ] Endpoint `latest` et/ou service de lecture
- [ ] Task 4 (AC: 4) Stabiliser les tests
  - [ ] Documenter tolérances et hypothèses d'environnement

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

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
