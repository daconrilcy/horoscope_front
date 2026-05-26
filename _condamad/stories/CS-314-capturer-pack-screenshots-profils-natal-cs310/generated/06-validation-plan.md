# Validation Plan - CS-314

## Screenshot and ledger checks

- Run the evidence capture script and require seven PNG screenshots.
- Validate `screenshot-ledger.json` covers five profiles and required desktop/mobile pairs.
- Validate `anomaly-ledger.json` is empty or every anomaly links to a follow-up brief.
- Scan ledger and notes for sensitive raw payload markers.

## Frontend checks

- From `frontend`, run `pnpm lint`.
- From `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`.
- From `frontend`, run `pnpm test -- inline-style design-system theme-tokens legacy-style`.

## Backend checks

- Activate `.venv`.
- From `backend`, run `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short`.

## Capsule checks

- Run `git diff --check`.
- Activate `.venv`.
- Run `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-314-capturer-pack-screenshots-profils-natal-cs310`.
