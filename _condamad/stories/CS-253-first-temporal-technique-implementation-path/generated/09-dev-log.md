# Dev Log

- 2026-05-24: Capsule generated files were missing in the target story folder. Ran `condamad_prepare.py`, moved the generated files into the target capsule, removed the accidental helper-created duplicate capsule, and validated the target capsule.
- 2026-05-24: Implemented canonical backend-domain temporal selection contract under astrology runtime.
- 2026-05-24: Added unit and architecture tests for selection, rejected families, graph/object requirements, API neutrality and single-family guard.
- 2026-05-24: Full backend pytest initially exposed an existing doctrine-governance guard requirement for the new module; classified `temporal_technique_selection.py` in `GOVERNED_RULE_SOURCE_SURFACES`.
- 2026-05-24: Final validation passed from repository root with venv activated.
