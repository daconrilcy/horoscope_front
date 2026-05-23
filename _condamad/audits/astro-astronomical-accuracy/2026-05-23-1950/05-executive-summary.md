# Executive Summary - Astro Astronomical Accuracy

## Decision Summary

The backend has a real `swisseph` calculation path for planets, houses, sidereal Lahiri, topocentric frame and altitude handling. It also has ephemeris bootstrap validation and metadata propagation. These are strong foundations, but they do not yet prove audit-grade astronomical accuracy by themselves.

The principal gap is evidence quality, not absence of implementation. The simplified engine still exists and is callable through domain routing. Golden data exists, but the repository does not yet prove all sensitive scenarios required by CS-241: Paris normal case, DST ambiguous time, DST nonexistent time, high latitude case, Sidereal Lahiri case, topocentric case, whole sign case and Placidus edge case.

## Findings By Severity

- High: F-001 simplified and `swisseph` paths remain active; F-002 golden chart coverage is incomplete.
- Medium: F-003 ephemeris evidence is implemented but not fully guaranteed by configuration; F-004 edge options need external reference proof.
- Low: F-005 no exact astronomical accuracy guardrail exists yet.

## Recommended Next Actions

1. Prioritize CS-240 to prove or enforce `swisseph`-only production mode.
2. Prioritize CS-241 to add the required external-reference golden chart suite.
3. Then implement CS-242 to persist ephemeris version/hash/config evidence in chart traces.

## Validation Status

- Audit artifacts created under `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950/`.
- CONDAMAD validator and linter passed from repo root after venv activation during targeted audit review.
- Application code, tests, migrations, seed data and frontend files were intentionally left unchanged.
