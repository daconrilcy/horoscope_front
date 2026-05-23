## CS-226 Final Evidence

### Natal Graph
- Declared `natal_chart_v1` in `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- Declared 11 inputs, 17 canonical runtime nodes and 8 projection nodes.
- Validator result: `natal_chart_v1 1 11 25 True`.
- Topological order ends with `public_natal_result`; `dignities` and `chart_signature` precede `dominance`.

### AC Traceability
- AC1, AC2, AC3, AC8, AC9, AC10, AC11: `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests\unit\domain\astrology\test_natal_calculation_graph_definition.py tests\unit\domain\astrology\test_calculation_graph_validator.py` -> `17 passed`.
- AC2: validator result stays `natal_chart_v1 1 11 25 True`.
- AC4: tests assert `houses_runtime`, `house_rulerships`, `dignities`, `chart_signature`, and dignity/dominance dependencies.
- AC5: tests assert canonical nodes do not depend on compatibility/public projections; projection scan produced no matches.
- AC6: no change to `build_natal_result`; graph definition is declarative only.
- AC7: `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests\architecture\test_api_contract_neutrality.py` -> `2 passed`.

### Commands
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app\domain\astrology\runtime\natal_calculation_graph.py tests\unit\domain\astrology\test_natal_calculation_graph_definition.py` -> `2 files left unchanged`.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` -> `All checks passed!`.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests\unit\domain\astrology\test_natal_calculation_graph_definition.py tests\unit\domain\astrology\test_calculation_graph_validator.py` -> `17 passed`.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests\architecture\test_api_contract_neutrality.py` -> `2 passed`.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests` -> `818 passed, 200 deselected`.
- `git diff --check -- backend/app/domain/astrology/runtime/natal_calculation_graph.py backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py _condamad/stories/CS-226-natal-calculation-graph-definition/evidence/validation.md _condamad/stories/CS-226-natal-calculation-graph-definition/evidence/natal-graph-dependencies.md` -> exit 0.

### Scans
- `rg -n "natal_chart_v1|build_natal_calculation_graph_definition|compatibility_projection" backend/app/domain/astrology backend/tests -g "*.py"` -> expected matches in graph module and tests.
- `rg -n "public_natal_result.*depends_on|dignity_results_projection.*depends_on" backend/app/domain/astrology/runtime -g "*.py"` -> PASS: no matches.
- `rg -n "networkx|igraph|graphlib|from app\.api|from app\.infra|sqlalchemy|fastapi" backend/app/domain/astrology/runtime/natal_calculation_graph.py` -> PASS: no matches.

### Notes
- The requested skill path `.agents/skills/condamad-review-fix-story/SKILL.md` was absent; only `.agents/skills/condamad-story-writer` exists locally.
- The CS-226 capsule has no `generated` directory; no `generated/*.md` file was read.
