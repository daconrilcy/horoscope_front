# No Legacy / DRY Guardrails

## Canonical Owners

- Planet nature: `AstrologyRuntimeReference.planet_natures`.
- Chart sect: existing `ChartSectResult`.
- Per-planet sect condition: existing `PlanetSectCondition`.
- Sect nature mitigation: new pure detector under `backend/app/domain/astrology/advanced_conditions`.
- Public JSON: serialize-only `backend/app/services/chart/json_builder.py`.

## Forbidden Patterns

- Local benefic/malefic planet sets or maps.
- Branches by planet name for Mars, Saturn, Jupiter or Venus.
- Recalculation from `json_builder.py` or frontend.
- Importing `SectCalculator`, `PlanetSectConditionCalculator`, `SectNatureMitigationDetector` or `AdvancedConditionEngine` in projection/frontend.
- Legacy public fields: `sect_mitigation_legacy`, `legacy_sect_mitigation`, `benefic_code`, `malefic_code`, `planet_nature_code_legacy`.
- Fallbacks, compatibility aliases, shims, duplicate active engines or TODOs.

## Required Negative Evidence

- RG-133 scans for forbidden constants, planet-name branches and recalculation imports.
- JSON builder tests proving projection consumes precomputed `TraditionalPlanetCondition` facts.
- Detector tests with injected runtime natures proving behavior is not tied to planet names.

## Exceptions

- None.

## Review Checklist

- One detector owns mitigation semantics.
- Seeds and runtime repository include one condition type/weight for downstream impact.
- Dignity score calculators are untouched.
- Frontend remains display-only and untouched unless generic display is insufficient.
