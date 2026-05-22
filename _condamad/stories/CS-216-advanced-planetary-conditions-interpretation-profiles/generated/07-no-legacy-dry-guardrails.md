# No Legacy / DRY Guardrails - CS-216

## Canonical Owners

- Facts: `backend/app/domain/astrology/planetary_conditions`.
- Scoring: `backend/app/domain/astrology/dignities`.
- Symbolic pre-narrative profiles: `backend/app/domain/astrology/interpretation/advanced_conditions`.
- Natal internal injection: `backend/app/domain/astrology/natal_calculation.py`.

## Forbidden Patterns

- Compatibility wrappers, aliases, shims, fallback-generated profiles, public schema projection, prompt/LLM usage, scoring, DB/API/frontend dependencies.
- Recalculation of solar proximity, motion, solar phase, visibility or moon phase facts inside `interpretation/advanced_conditions`.
- New dependencies.

## Required Negative Evidence

- Scans for scoring terms must have zero hits in the new package.
- Scans for prompt/LLM/API/DB/frontend terms must have zero hits in the new package.
- Scans for final-user text markers must have zero hits in the new package.
- Scans for calculator duplication terms must have zero hits in the new package.
- Adjacent diff review must show no changes to forbidden areas.

## Exception Register

No exceptions are authorized for CS-216. Any required exception blocks implementation.
