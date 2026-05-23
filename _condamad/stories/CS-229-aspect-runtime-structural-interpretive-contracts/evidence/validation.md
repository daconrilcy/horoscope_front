## CS-229 Final Evidence

### Aspect Runtime Layers
- Structural runtime, interpretive runtime, public projection and legacy projection are documented in `docs/architecture/astrology-runtime-surfaces.md`.
- Capsule preparation scripts were unavailable: `.agents/skills/condamad-dev-story/SKILL.md`, `condamad_prepare.py` and `condamad_validate.py` were not present.

### Contracts
- `AspectStructuralRuntimeData` contains only structural facts.
- `AspectInterpretiveHintsRuntimeData` contains typed sourced hints.
- `AspectStructuralDefinitionRuntimeData` and `AspectInterpretiveProfileRuntimeData` are separated through `AspectDefinitionRuntimeData.structural_definition()` and `.interpretive_profile()`.
- `resolve_aspect_interpretive_hints()` assembles typed hints from `AspectStructuralRuntimeData` and `AspectInterpretiveProfileRuntimeData`.

### Boundaries
- Structural calculators do not consume `AspectInterpretiveProfileRuntimeData`.
- `AspectStructuralModifierRuntimeData` has no `interpretive_weight`.
- The dedicated hints resolver rejects mismatched structural/profile aspect codes.
- Prediction remains outside the structural aspect runtime; CS-229 did not change prediction outputs.

### Compatibility
- No public API, DB, Alembic, frontend or prompt file was intentionally changed.
- Existing public aspect fields remain stable through legacy `AspectRuntimeData.interpretation`.
- `app.routes`, `app.openapi()` and `TestClient` are captured in `evidence/openapi-routes.md`.

### Guardrails
- AST guard blocks interpretive fields on structural contracts.
- Scans cover valence, energy_type, meaning, narrative, prompt and llm; legacy matches are documented in `evidence/aspect-runtime-boundary.md`.

### Commands
- `.\.venv\Scripts\Activate.ps1; python -B -m ruff format backend`: PASS, `1564 files left unchanged`.
- `.\.venv\Scripts\Activate.ps1; python -B -m ruff check backend`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_aspect_runtime_contracts.py backend\tests\unit\domain\astrology\test_aspect_runtime_builder.py backend\tests\unit\domain\astrology\test_aspect_modifiers.py backend\tests\unit\domain\astrology\test_aspect_strength.py backend\tests\unit\domain\astrology\test_dominant_aspects.py backend\tests\architecture\test_aspect_runtime_boundary.py backend\tests\architecture\test_chart_interpretation_input_boundary.py backend\tests\architecture\test_api_contract_neutrality.py`: PASS, `34 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_aspect_runtime_contracts.py backend\tests\unit\domain\astrology\test_aspect_modifiers.py backend\tests\architecture\test_aspect_runtime_boundary.py`: PASS, `19 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests`: PASS, `849 passed, 201 deselected`.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-229-aspect-runtime-structural-interpretive-contracts\00-story.md`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-229-aspect-runtime-structural-interpretive-contracts\00-story.md`: PASS.
- `git diff -- backend\app\api backend\alembic backend\app\infra frontend\src`: PASS, no diff output.
- `git diff --check`: PASS with line-ending warnings only.

### AC Traceability
- AC1: `docs/architecture/astrology-runtime-surfaces.md`; `test_aspect_runtime_boundary.py`.
- AC2, AC3, AC4, AC10: `test_aspect_runtime_contracts.py`.
- AC5, AC7: `test_aspect_modifiers.py`; `test_aspect_strength.py`.
- AC6, AC11, AC12: `test_aspect_runtime_boundary.py`.
- AC8: `test_dominant_aspects.py`.
- AC9: `test_chart_interpretation_input_boundary.py`.
- AC13: `test_api_contract_neutrality.py`; `evidence/openapi-routes.md`.
- AC14: no DB/Alembic diff.
- AC15: this evidence folder.
