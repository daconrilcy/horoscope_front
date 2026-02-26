# Story 20.10: Calcul des aspects avec orbes hiérarchiques

Status: ready-for-dev

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

- [ ] Task 1 (AC: 1-3) Étendre le moteur `calculate_major_aspects`
  - [ ] Remplacer `max_orb` global par stratégie de résolution hiérarchique
  - [ ] Intégrer les règles par aspect et overrides de paires/luminaires
- [ ] Task 2 (AC: 4) Étendre le schéma de sortie des aspects
  - [ ] Ajouter `orb_used` au modèle de domaine (`AspectResult`)
  - [ ] Propager dans API/DTO de résultat natal
- [ ] Task 3 (AC: 1-4) Tests unitaires de calcul
  - [ ] Cas `default_orb`
  - [ ] Cas override luminaires
  - [ ] Cas override paire
  - [ ] Vérification stabilité tri/déterminisme

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

### Completion Notes List

### File List
