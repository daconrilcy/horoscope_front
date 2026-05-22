# No Legacy / DRY Guardrails

## Applicable regression guardrails

- `RG-135` - contracts remain pure dataclasses/enums without API/DB/services dependencies or free `Any`.
- `RG-136` - solar proximity remains owned by `solar_proximity_calculator.py`.
- `RG-138` - solar phase relation remains owned by `solar_phase_relation_calculator.py`.
- `RG-139` - moon phase remains owned by `moon_phase_calculator.py`.
- `RG-140` - planetary visibility remains a pure composition calculator over upstream facts.

## Forbidden for CS-213

- Recalculate solar distance or oriental/occidental relation.
- Add scoring, strength, interpretation, narration, prompt, LLM, API, DB, Pydantic or frontend surfaces.
- Produce real observational or heliacal astronomy.
- Integrate into `NatalResult`, `json_builder.py`, services, routes, infra, migrations or frontend.
- Add compatibility aliases, shims, fallbacks, broad allowlists or duplicate active owners.

## Evidence required

- Targeted unit tests for the calculator and contracts.
- Negative `rg` scans on the new calculator for forbidden dependencies and symbols.
- Positive `rg` scan proving public symbols are limited to the package and tests.
- Negative `rg` scan and empty `git diff` for adjacent surfaces.
