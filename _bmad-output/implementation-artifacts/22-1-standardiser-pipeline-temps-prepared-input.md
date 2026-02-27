# Story 22.1: Standardiser le temps dans prepared_input

Status: done

## Story
... (rest of story) ...

### File List

- backend/app/domain/astrology/natal_preparation.py
- backend/app/tests/unit/test_natal_preparation.py
- backend/app/tests/integration/test_natal_prepare_api.py
- frontend/src/api/natalChart.ts
- _bmad-output/implementation-artifacts/22-1-standardiser-pipeline-temps-prepared-input.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-27: Implémentation story 22.1 — ajout `jd_ut` et `timezone_used` dans `BirthPreparedData`, logging conversion, compteur timezone invalide. Tests golden Paris 1973 ajoutés. (claude-sonnet-4-6)
- 2026-02-27: Code Review Fixes — amélioration de la précision de `jd_ut` (float), support des secondes fractionnaires dans le parsing, correction du fallback minuit local, et mise à jour des types frontend. (gemini-cli)
