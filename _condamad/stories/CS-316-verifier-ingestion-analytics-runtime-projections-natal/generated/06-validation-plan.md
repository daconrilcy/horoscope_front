# Validation Plan

## Contract Checks

- Validate `evidence/analytics-runtime-config.json` provider and closure.
- Validate `evidence/analytics-ingestion-ledger.json` contains exactly the
  seven CS-311 event names.
- Compare ledger public fields with CS-311 `event-catalog.json`.
- Check `evidence/external-validation-required.md` exists.

## Guard Scans

- Scan CS-316 evidence for forbidden sensitive field names.
- Scan frontend feature/component/api sources for direct provider calls:
  `plausible(`, `_paq.push`, and `VITE_ANALYTICS_PROVIDER`.
- Run RG-047 inline-style policy test and contextual scan.
- Run RG-071 natal interpretation/component architecture tests.
- Run `git diff --check`.

## Frontend Checks

Run from `frontend/`:

- `pnpm lint`
- `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi`
- `node .\scripts\run-vite-logged.mjs vitest vitest run`

## Capsule Checks

- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-316-verifier-ingestion-analytics-runtime-projections-natal`
