# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Canonical path documented. | `calibration-artifact-location-audit.md`. | `rg -n "canonical path" ...`. | PASS |
| AC2 | Producers write to canonical path. | `artifact_paths.py`, producer imports. | `pytest -q app/tests/unit/test_calibration_artifact_locations.py`. | PASS |
| AC3 | Backend docs artifact removed/migrated. | Deleted stale JSON and empty folder. | scan and guard PASS. | PASS |
| AC4 | Guard blocks split paths. | `test_calibration_artifact_locations.py`. | Same command PASS. | PASS |
| AC5 | Existing calibration tests pass. | No algorithm change. | calibration targeted tests PASS. | PASS |
