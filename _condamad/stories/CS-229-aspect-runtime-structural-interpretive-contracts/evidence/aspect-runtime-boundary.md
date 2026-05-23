# CS-229 Aspect Runtime Boundary Evidence

## Structural Contracts

- `AspectStructuralRuntimeData`: `aspect`, `participants`, `orb`, `metadata`, `strength`, `phase`, `modifiers`.
- `AspectStructuralDefinitionRuntimeData`: `code`, `name`, `angle`, `family`, `default_orb_deg`, `is_enabled`, `is_major`, `is_minor`, `system_code`, `legacy_orb_fields`.
- `AspectStructuralModifierRuntimeData`: `modifier_type`, `source`, `intensity`, `reason`, `applies_to`.

These contracts do not declare `default_valence`, `interpretive_valence`, `energy_type`, `interpretive_weight`, `meaning`, `narrative`, `prompt` or `llm`.

## Interpretive Contracts

- `AspectInterpretiveProfileRuntimeData` holds aspect valence/profile fields.
- `AspectInterpretiveHintsRuntimeData` holds typed sourced hints and optional `interpretive_weight`.
- `resolve_aspect_interpretive_hints()` is the bounded adapter from structural runtime plus profile to sourced hints.

## Scan Notes

Command:

```powershell
rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight|meaning|narrative|prompt|llm" backend\app\domain\astrology\runtime -g "*.py" -g "!__pycache__"
```

Result classification:

- Expected transition matches: `AspectInterpretationRuntimeData`, `AspectDefinitionRuntimeData`, `AspectCalculationResult`, `runtime_reference.AspectReferenceData`, `natal_calculation_nodes` legacy mapping.
- Expected target matches: `AspectInterpretiveHintsRuntimeData`, `AspectInterpretiveProfileRuntimeData`, `AspectRuntimeWeightTaxonomy.interpretive_hints`.
- Expected resolver matches: `resolve_aspect_interpretive_hints()` copies typed profile fields into `AspectInterpretiveHintsRuntimeData` and requires matching aspect codes.
- Existing unrelated runtime reference match: `PlanetConditionSignalProfileReferenceData.prompt_hint`; not part of aspect structural runtime.
- Guarded no-match target: `AspectStructuralRuntimeData`, `AspectStructuralDefinitionRuntimeData`, `AspectStructuralModifierRuntimeData`.

## No Forbidden Surface Deltas

Command:

```powershell
git diff -- backend\app\api backend\alembic backend\app\infra frontend\src
```

Result: no diff output.
