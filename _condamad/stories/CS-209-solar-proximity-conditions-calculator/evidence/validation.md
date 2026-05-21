# Validation Evidence - CS-209

## Baseline

- `Test-Path backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`: `False` before implementation.
- `RG-135`: present for pure `contracts.py`.
- `RG-136`: present for pure `solar_proximity_calculator.py`.

## Commands run

| Command | Result | Evidence |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | First run: `18 passed in 0.40s`; after review fix: `19 passed in 0.37s` |
| `ruff format .` | PASS | `1 file reformatted, 1488 files left unchanged` |
| `ruff format --check .` | PASS | Fresh review run: `1489 files already formatted` |
| `ruff check .` | PASS | `All checks passed!` |
| `pytest -q` | PASS | First run: `2834 passed, 1 skipped, 1177 deselected in 238.71s`; after review fix: `2835 passed, 1 skipped, 1177 deselected in 207.54s`; fresh review run: `2835 passed, 1 skipped, 1177 deselected in 265.18s` |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | PASS | `CONDAMAD story validation: PASS` |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | PASS | No missing required contracts |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | PASS | `CONDAMAD story lint: PASS` |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md` | PASS | `CONDAMAD story lint: PASS` |
| Backend local startup `python -m uvicorn app.main:app --host 127.0.0.1 --port 8020` then `GET /openapi.json` | PASS | Initial evidence: HTTP 200, OpenAPI response bytes `541195`; fresh review run: HTTP 200, OpenAPI response bytes `541782`; server stopped after check |
| Backend startup command with identical stdout/stderr redirection | BLOCKED then corrected | PowerShell rejected `Start-Process` because `RedirectStandardOutput` and `RedirectStandardError` used the same file; rerun with separate logs passed. |

## Scans

| Scan | Result |
|---|---|
| Calculator forbidden imports `from app.api|from app.infra|from app.infrastructure|from app.services` | PASS, zero hit |
| Calculator forbidden dependencies `sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter` | PASS, zero hit |
| Calculator forbidden scoring `\bscore\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier` | PASS, zero hit |
| Calculator forbidden text/LLM surface `interpretation|meaning|description|narrative|prompt` | PASS, zero hit |
| Contract forbidden imports/dependencies | PASS, zero hit |
| Contract forbidden calculators/free annotations | PASS, zero hit |
| Public symbol placement | PASS, hits limited to `planetary_conditions` package and its unit tests |
| Adjacent diff on forbidden surfaces | PASS, empty diff |

## Review fix validation

- Accepted finding: implicit `planet_key` alias through `strip().lower()`.
- Fix: preserve the exact `planet_key` supplied by the caller and treat only exact `planet_key == "sun"` as the inactive Sun case.
- Added guard: `test_planet_key_is_not_normalized_as_alias`.
- Result: targeted tests, Ruff, full pytest and scans PASS after the fix.
- Startup check: backend OpenAPI served successfully on `127.0.0.1:8020`.

## Commands skipped

None.
