# Calibration Artifact Location Audit

## Decision

canonical path: `docs/calibration`

## Removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `backend/docs/calibration/percentile_report.json` | generated artifact | dead | no producer writes here; scans found no active first-party consumer | `docs/calibration/percentile_report.json` | delete | `rg -n "backend/docs/calibration\|docs/calibration\|percentile_report\|review-grid" app tests scripts ../docs` and `pytest -q app/tests/unit/test_calibration_artifact_locations.py` | none |
| `docs/calibration/percentile_report.json` | generated artifact | canonical-active | percentile job and docs | same | keep | `resolve_percentile_report_path()` guard | none |
| review grids under `docs/calibration` | generated artifact | canonical-active | review grid producer | same | keep | `_default_output_path()` guard | none |
