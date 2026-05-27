# Validation Plan

## Targeted report checks

```powershell
rg -n "Evidence gap|residual risk|validation|CS-343|CS-348|CS-350" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
rg -n "CS-343|CS-348|CS-350" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
rg -n "Evidence path|Source|Evidence gap" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
rg -n "Evidence gap" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
rg -n "contradiction|Gaps" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
rg -n "Validation evidence|validation" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
rg -n "residual risk|Risques residuels" .\_condamad\reports\prompt-generation-cartography\2026-05-27-0000
```

## File existence and no-application-delta checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; paths=[Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/report-prompt-generation-cartography.md'),Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/evidence-sources.md'),Path('_condamad/reports/prompt-generation-cartography/2026-05-27-0000/validation-output.md')]; missing=[str(p) for p in paths if not p.is_file()]; print('PASS' if not missing else 'FAIL '+repr(missing))"
git status --short -- backend/app backend/tests frontend/src
```

## Capsule validation

```powershell
.\.venv\Scripts\Activate.ps1
python -B .\.agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-349-report-cartographie-generation-prompt-llm
```

## Skipped commands

- `ruff check .`: skipped because CS-349 changes only Markdown evidence/report files and no Python source.
- `python -B -m pytest -q --tb=short`: skipped because no application, backend test, frontend or migration code changed; upstream story-time tests are cited in `evidence-sources.md`.
