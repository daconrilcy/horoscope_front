# Validation Evidence

Story: CS-247 graph-manifest-node-io-schema-contract

## Commands

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md --root C:\dev\horoscope_front; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract` | repo root | FAIL then repaired | Helper generated a derived-key capsule; generated files were copied to target and the target capsule was validated separately. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract` | repo root | PASS | Capsule structure valid. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app\domain\astrology\runtime\calculation_graph_manifest.py app\domain\astrology\runtime\calculation_graph_manifest_validator.py app\domain\astrology\runtime\natal_calculation_graph.py tests\unit\domain\astrology\test_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | Scoped format on changed Python files. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_definition.py tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | 26 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests` | repo root | PASS | 894 passed, 201 deselected. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert 'CalculationGraphManifest' not in str(app.openapi())"` | repo root | PASS | Manifest absent from OpenAPI output. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert not any('graph-manifest' in getattr(r, 'path', '') for r in app.routes)"` | repo root | PASS | No manifest route exposed. |
| `rg -n "GraphManifest\|NodeIOSchema\|calculation_graph_manifest" backend\app\domain\astrology\runtime backend\tests\unit\domain\astrology -g "*.py"` | repo root | PASS | Matches restricted to runtime domain and unit tests. |
| `rg -n "GraphManifest\|NodeIOSchema\|graph-manifest\|node-io-schema\|calculation_graph_manifest" backend\app\api frontend -g "*.py" -g "*.ts" -g "*.tsx"` | repo root | PASS | Exit 1 means no matches, expected for negative scan. |
| `git diff --check` | repo root | PASS | No whitespace errors; Git reported CRLF warnings for pre-existing modified files. |

## Status alignment

The tracker row was already `done` with last update `2026-05-23`; `00-story.md` still said `ready-to-review`.
The story status was aligned to `done`.

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md` | repo root | PASS | Story contract valid after status alignment. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md` | repo root | PASS | Strict story lint valid after status alignment. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract` | repo root | PASS | Capsule valid after status alignment. |

## Review-fix iteration 1

Implementation review found one actionable issue: optional node dependencies were exposed in the manifest but were not
validated or compared. The fix added optional dependency validation and deterministic comparison deltas, then reran the
relevant checks.

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app\domain\astrology\runtime\calculation_graph_manifest.py app\domain\astrology\runtime\calculation_graph_manifest_validator.py tests\unit\domain\astrology\test_calculation_graph_manifest.py` | repo root | PASS | 3 files left unchanged. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | 21 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests` | repo root | PASS | 896 passed, 201 deselected. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert 'CalculationGraphManifest' not in str(app.openapi())"` | repo root | PASS | Manifest absent from OpenAPI output. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert not any('graph-manifest' in getattr(r, 'path', '') for r in app.routes)"` | repo root | PASS | No manifest route exposed. |
| `rg -n "GraphManifest\|NodeIOSchema\|graph-manifest\|node-io-schema\|calculation_graph_manifest" backend\app\api frontend -g "*.py" -g "*.ts" -g "*.tsx"` | repo root | PASS | Exit 1 means no matches, expected for negative scan. |
| `git diff --check` | repo root | PASS | No whitespace errors; Git reported CRLF warnings for pre-existing modified files. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md` | repo root | PASS | Story contract still valid. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md` | repo root | PASS | Strict story lint still valid. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract` | repo root | PASS | Capsule validation still valid. |

## Brief-alignment review-fix iteration 2

Implementation review found one additional actionable issue: descriptor requiredness was exposed in the manifest but was
not compared. The fix added deterministic requiredness deltas and targeted unit coverage, then reran the relevant checks.

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app\domain\astrology\runtime\calculation_graph_manifest.py tests\unit\domain\astrology\test_calculation_graph_manifest.py` | repo root | PASS | 2 files left unchanged. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | 22 passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | All checks passed. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests` | repo root | PASS | 897 passed, 201 deselected. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md` | repo root | PASS | Story contract still valid. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-247-graph-manifest-node-io-schema-contract\00-story.md` | repo root | PASS | Strict story lint still valid. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract` | repo root | PASS | Capsule validation still valid. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert 'CalculationGraphManifest' not in str(app.openapi())"` | repo root | PASS | Manifest absent from OpenAPI output. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; assert not any('graph-manifest' in getattr(r, 'path', '') for r in app.routes)"` | repo root | PASS | No manifest route exposed. |
| `rg -n "GraphManifest\|NodeIOSchema\|graph-manifest\|node-io-schema\|calculation_graph_manifest" backend\app\api frontend -g "*.py" -g "*.ts" -g "*.tsx"` | repo root | PASS | Exit 1 means no matches, expected for negative scan. |
| `git diff --check` | repo root | PASS | No whitespace errors; Git reported CRLF warnings for pre-existing modified files. |

## Skipped or adjusted

- `rg ... backend\alembic ...` was adjusted because `backend/alembic` is absent in this repository.
- No frontend checks were run because the story explicitly forbids frontend changes and no frontend file was modified.
- A persistent local server was not started; `TestClient` and OpenAPI smoke tests loaded the FastAPI app in-process. Manual run remains `.\.venv\Scripts\Activate.ps1; cd backend; uvicorn app.main:app --reload`.
