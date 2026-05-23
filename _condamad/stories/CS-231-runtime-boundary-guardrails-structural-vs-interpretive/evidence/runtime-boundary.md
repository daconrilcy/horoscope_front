# CS-231 Runtime Boundary Evidence

## Structural Runtime Guard

- Structural zones are enumerated in `STRUCTURAL_ROOTS`:
  `calculators`, `runtime`, `builders`, `dominance`, `fixed_stars`, `dignities`, `planetary_conditions`, `advanced_conditions`.
- Forbidden structural tokens:
  `default_valence`, `interpretive_valence`, `energy_type`, `interpretive_weight`, `meaning`, `narrative`, `prompt`, `llm`, `OpenAI`, `AIEngineAdapter`.
- The guard is AST-based and reports `path:line:owner:token`.
- Future calculators remain covered because `backend/app/domain/astrology/calculators` is scanned as a root, not as a fixed file list.

## Allowlist

The local allowlist is typed as `(relative_path, owner, field) -> (reason, decision)`.

Allowed permanent interpretive owners:

- `AspectInterpretiveProfileRuntimeData`: aspect profile fields separated from the structural definition.
- `AspectInterpretiveHintsRuntimeData`: typed hints for interpretive adapters and prompts.
- `resolve_aspect_interpretive_hints`: resolver that enriches from an existing structural runtime and profile.

Allowed temporary legacy owners:

- `AspectDefinitionRuntimeData`: transition contract that still groups legacy fields before exposing separated views.
- `AspectInterpretationRuntimeData`: legacy projection of short interpretive indices.
- `AspectReferenceData`: DB/reference payload still loaded with legacy interpretive columns.
- `_aspect_definition`: bridge from legacy payload to structural definition plus interpretive profile.
- `AspectRuntimeWeightTaxonomy`: named legacy target for interpretive weight audit.

Review fix:

- The AST guard now catches forbidden tokens embedded in identifiers, not only exact
  identifier matches.
- `PlanetConditionSignalProfileReferenceData` exposes `signal_hint` in the
  structural runtime reference; the infra mapper remains responsible for reading
  the legacy DB column named `prompt_hint`.

## Interpretive Adapter Guard

- Interpretive roots are `backend/app/domain/astrology/interpretation` and `backend/app/domain/astrology/interpretation_adapters`.
- Recalculation symbols are forbidden there:
  `calculate_major_aspects`, `calculate_interchart_aspects`, `resolve_orb`, `PlanetDominanceEngine`, `FixedStarConjunctionCalculator`, `EssentialDignityCalculator`, `AccidentalDignityCalculator`.
- The targeted scan found no matches in those roots.

## Documentation

`docs/architecture/astrology-runtime-surfaces.md` now contains:

- `Runtime boundary matrix CS-231`.
- The four layer terms: `structural runtime`, `interpretive runtime`, `public projection`, `legacy projection`.
- Allowed paths for `default_valence`, `interpretive_valence`, `energy_type` and `interpretive_weight`.

## Non-Goals Preserved

- No frontend file was changed by CS-231.
- No Alembic migration or DB model change was introduced.
- No FastAPI route, public schema or serializer was intentionally changed.
- No prompt, provider, score, orb or doctrine change was introduced by CS-231.
