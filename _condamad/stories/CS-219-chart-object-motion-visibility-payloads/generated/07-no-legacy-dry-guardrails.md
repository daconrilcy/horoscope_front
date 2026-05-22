# No Legacy / DRY Guardrails

## Canonical Owners

| Responsibility | Canonical owner |
|---|---|
| Runtime payload contract | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` |
| Conditions calculation | `backend/app/domain/astrology/planetary_conditions/*` |
| Chart-object mapping | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` |
| Natal integration | `backend/app/domain/astrology/natal_calculation.py` |

## Forbidden

- Compatibility wrapper, alias, fallback or legacy import.
- Local recalculation of retrograde, station, cazimi, combustion, under beams,
  oriental/occidental relation or visibility in the builder/runtime.
- Local magic thresholds in the builder/runtime.
- Payload present when matching capability is false.
- Capability true when matching payload is absent.
- Consumer branching on `object_type` for motion/visibility.

## Required Evidence

- Targeted tests for payload builders and validator.
- Natal integration tests proving applicable objects and non-applicable objects.
- Architecture guard tests.
- RG-146 scan.
- Threshold and calculator-call scans.
