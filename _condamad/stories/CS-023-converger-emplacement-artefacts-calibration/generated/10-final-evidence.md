# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-023-converger-emplacement-artefacts-calibration

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `calibration-artifact-location-audit.md` documents `canonical path: docs/calibration`. | scan PASS. | PASS | |
| AC2 | Producers use `artifact_paths.py`. | `test_calibration_artifact_locations.py` PASS. | PASS | |
| AC3 | `backend/docs/calibration/percentile_report.json` deleted. | guard and `backend/docs/calibration absent` evidence. | PASS | |
| AC4 | Split path guard added. | same guard PASS. | PASS | |
| AC5 | Existing calibration tests pass. | 18 passed for targeted calibration set. | PASS | |

## Files changed

- `backend/app/services/calibration/artifact_paths.py`
- `backend/app/scheduled_tasks/compute_calibration_percentiles.py`
- `backend/app/services/calibration/generate_review_grid.py`
- `backend/app/tests/unit/test_calibration_artifact_locations.py`
- deleted `backend/docs/calibration/percentile_report.json`

## Commands run

- `pytest -q app/tests/unit/test_calibration_artifact_locations.py app/tests/unit/test_calibration_job.py app/tests/unit/test_calibration_runtime.py app/tests/unit/test_v3_calibration.py` — PASS, 18 passed.
- `pytest -q` — PASS, 3613 passed, 12 skipped.
- CONDAMAD validate/lint — PASS.

## Remaining risks

Aucun risque restant identifie.
