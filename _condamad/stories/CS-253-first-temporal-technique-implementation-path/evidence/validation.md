# Validation evidence

Commands counted:

- `.\.venv\Scripts\Activate.ps1; ruff format <modified python files>`: PASS.
- `.\.venv\Scripts\Activate.ps1; ruff check backend`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_temporal_technique_selection.py`: PASS, `7 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_temporal_family_single_path.py`: PASS, `4 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py`: PASS, `14 passed`.
- `.\.venv\Scripts\Activate.ps1; $env:PYTHONPATH='backend'; python -B -c "<risk-accepted-non-public gate assertion>"`: PASS.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_astrology_doctrine_governance_guardrails.py ...`: PASS, `26 passed`.
- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend`: PASS, `3228 passed, 1 skipped, 1182 deselected`.
- `rg -n "temporal_technique_selection|transit_chart_v1|synastry_chart_v1|solar_return_v1|lunar_return_v1|progressed_chart_v1|composite_chart_v1|profection_v1|forecasting_v1|transit_chart" backend\app\api frontend\src backend\migrations -g "*.py" -g "*.ts" -g "*.tsx"`: PASS, exit `1` means no matches.
- `rg -n "app\.domain\.prediction|app\.services\.prediction" backend\app\domain\astrology\runtime\temporal_technique_selection.py backend\app\domain\astrology\runtime\__init__.py -g "*.py"`: PASS, exit `1` means no matches.
- `.\.venv\Scripts\Activate.ps1; python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-253-first-temporal-technique-implementation-path\00-story.md`: PASS.
- `.\.venv\Scripts\Activate.ps1; python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-253-first-temporal-technique-implementation-path\00-story.md`: PASS.

Discarded validation attempt:

- `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q` from `backend/`: activation path was wrong for that working directory and one architecture guard failed before the doctrine-governance classification was added. Not counted as final evidence; rerun from repository root passed.
