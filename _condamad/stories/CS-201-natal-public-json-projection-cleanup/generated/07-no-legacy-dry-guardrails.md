# No Legacy / DRY Guardrails

## Applicable Guardrails

- `RG-124` through `RG-128` apply to sect, condition, advanced scoring, golden cases and public JSON projection.

## Forbidden In This Story

- Calculator or engine imports in `backend/app/services/chart/json_builder.py`.
- Legacy sect aliases: `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`, `planet_sect_code`, `planet_sect_legacy`, `sect_score_legacy`, `legacy_planet_sect`.
- Fabricating missing persisted payload facts.
- New frontend, API, DB, migration or seed changes.
- Compatibility wrappers, transitional aliases, silent fallback paths and TODO-based legacy deferral.

## Required Negative Evidence

- Forbidden projection import scan.
- Legacy alias scan.
- Doctrine constant scan.
- Horizon tuple scan.
- Adjacent surface diff scan.

## Review Checklist

- `json_builder.py` serializes only facts already on `NatalResult`.
- Old persisted gaps are not backfilled with fake facts.
- Empty computed lists/maps serialize deterministically.
- No-time mode neutralizes time-dependent public fields.
