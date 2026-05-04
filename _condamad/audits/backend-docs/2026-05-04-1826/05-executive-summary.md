# Executive Summary - backend-docs

`backend/docs` is a catch-all today, but not because every file is wrong. The folder contains valuable guarded assets alongside unclassified and likely stale material.

## Findings by Severity

| Severity | Count | Findings |
|---|---:|---|
| Critical | 0 | none |
| High | 0 | none |
| Medium | 4 | F-001, F-002, F-003, F-004 |
| Low | 0 | none |
| Info | 1 | F-005 |

## Key Conclusions

- Keep and protect the LLM cleanup registry unless a deliberate migration updates the validator and tests.
- Add an ownership/classification index before moving files; otherwise cleanup risks breaking guarded docs.
- Treat `backend/docs/calibration/percentile_report.json` as the first cleanup candidate because active code writes to `docs/calibration`, not `backend/docs/calibration`.
- Decide whether the entitlement document is canonical runtime documentation or historical story accumulation.

## Recommended Next Action

Start with `SC-001` and `SC-004` together: classify the folder and converge the calibration artifact location. Then handle entitlement parity (`SC-002`) and LLM doc governance (`SC-003`) with narrower domain stories.

## Validation Status

- Audit artifacts created under `_condamad/audits/backend-docs/2026-05-04-1826/`.
- Application code unchanged.
- CONDAMAD validation and lint passed after `.venv` activation.
