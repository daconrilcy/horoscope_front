# CONDAMAD Code Review — CS-019

## Review target

- Story: `_condamad/stories/CS-019-clarifier-frontiere-jobs-scripts-backend/00-story.md`
- Diff scope: extinction `backend/app/jobs`, nouvel owner `backend/app/scheduled_tasks`, owner `backend/app/services/calibration`, wrappers `backend/scripts`, tests et artefacts CONDAMAD.

## Findings

No remaining actionable finding.

## Acceptance audit

| AC | Review result |
|---|---|
| AC1 | PASS — classification et inventaires avant/apres presents. |
| AC2 | PASS — `app.jobs` est supprime, sans marker ni shim. |
| AC3 | PASS — percentile/runtime/profils sont sous `app.services.calibration`; ancien package supprime. |
| AC4 | PASS — outils QA/revue hors namespace planifiable; wrappers CLI presents. |
| AC5 | PASS — traitements planifiables sous `app.scheduled_tasks`; tests cibles passent. |
| AC6 | PASS — garde AST/path bloque `app.jobs` et imports non bornes. |
| AC7 | PASS — guardrails transverses cibles passent. |

## Validation audit

- `ruff format .` — PASS.
- `ruff check .` — PASS.
- Tests cibles CS-019 — PASS.
- Story validators/lint — PASS.
- No Legacy scans — PASS, zero import actif `app.jobs`.
- `git diff --check` — PASS, CRLF warnings only.

## DRY / No Legacy audit

- No shim, alias, fallback, compatibility wrapper or re-export preserves `app.jobs`.
- `backend/app/jobs` is deleted.
- `backend/app/scheduled_tasks` contains only schedulable entrypoints.

## Residual risks

- Aucun risque restant identifie.

## Verdict

CLEAN
