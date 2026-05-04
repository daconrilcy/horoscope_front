# Execution Brief

- Story key: CS-023-converger-emplacement-artefacts-calibration.
- Objective: converge calibration generated artifacts to one canonical location.
- Decision: keep `docs/calibration`; delete `backend/docs/calibration/percentile_report.json`.
- Done: shared path helper, producer rewiring, guard against `backend/docs/calibration`, targeted and full tests passing.
