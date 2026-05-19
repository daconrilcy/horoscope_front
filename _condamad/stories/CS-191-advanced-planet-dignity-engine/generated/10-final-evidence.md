# Final Evidence CS-191

Status: done

## Summary

Implemented an advanced backend planetary dignity engine. The runtime now exposes
`AstrologyRuntimeReference.dignity_reference`; domain calculators consume only
that typed runtime and objective natal positions; `NatalResult` and the chart
JSON payload expose factual dignity scores.

## AC Validation

All AC1-AC8 are PASS; see `generated/03-acceptance-traceability.md`.

## Files Changed

See `generated/04-target-files.md`.

## Tests And Checks

- Targeted pytest: PASS, 51 passed.
- Full backend pytest: PASS, 2686 passed, 1 skipped, 1177 deselected.
- Ruff format/check: PASS.
- RG-118 forbidden import / hardcoded score / LLM scans: PASS, zero-hit.
- Story validation/lint: PASS after aligning the Batch Migration Plan column
  and wrapping long AC evidence lines.
- Backend local startup smoke: PASS, `uvicorn app.main:app` returned HTTP 200
  on `/docs` at `127.0.0.1:8019`, then the process was stopped.

## Persistent Evidence

- `evidence/natal-payload-before.json`
- `evidence/natal-payload-after.json`
- `evidence/dignity-runtime-reference.md`
- `evidence/dignity-guard-evidence.md`

## Review Findings Fixed

- Runtime dignity reference now includes the missing type and system inventories:
  `essential_types`, `accidental_types`, `term_systems`, `decan_systems`.
- Breakdown contracts now expose factual `reason` fields and the chart JSON
  serializes them.
- Essential dignity tests now cover `exaltation`, `detriment` and `fall`.
- `peregrine` is now based on absence of positive essential dignity, not absence
  of every essential match.
- Solar accidental dignities now skip self-distance for the Sun.
- Participating triplicity rulers use runtime `sect_code = all`.
- Sect calculation derives above/below horizon from runtime accidental rules.
- AC5 tests cover house modalities, direct/retrograde motion, planetary joy, solar priority and Sun self-exclusion.
- Score profiles and weights are read through `DignityReferenceRepository`.
- Story evidence contract now uses `No-shim proof` in the Batch Migration Plan
  and passes strict CONDAMAD story validation/lint.

## Remaining Risks

Aucun risque restant identifie.
