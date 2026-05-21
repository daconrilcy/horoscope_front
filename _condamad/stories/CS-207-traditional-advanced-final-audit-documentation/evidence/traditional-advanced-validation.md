# Traditional Advanced Validation

## Commands Run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | PASS | 0 | 100 tests passed |
| `npm --prefix frontend test -- NatalExpertPanel` | repo root | PASS | 0 | 1 file, 4 tests passed; covers display-only backend facts, sect grouping, legacy/empty/unavailable/no-time payloads, loading, error, and missing chart states |
| `npm --prefix frontend run lint` | repo root | PASS | 0 | `tsc --noEmit -p tsconfig.lint.json` and `tsc --noEmit -p tsconfig.node.json` passed |
| `npm --prefix frontend run build` | repo root | PASS | 0 | production build succeeded |
| `.\\.venv\\Scripts\\Activate.ps1; ruff format .` | repo root | PASS | 0 | 1484 files left unchanged |
| `.\\.venv\\Scripts\\Activate.ps1; ruff check .` | repo root | PASS | 0 | all checks passed |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation PASS |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md` | repo root | PASS | 0 | no missing required contracts |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md` | repo root | PASS | 0 | story lint PASS |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-207-traditional-advanced-final-audit-documentation/00-story.md` | repo root | PASS | 0 | strict story lint PASS |
| `$e = "_condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence"; Test-Path "$e/traditional-advanced-audit-report.md"; Test-Path "$e/traditional-advanced-contract-map.md"; Test-Path "$e/traditional-advanced-regression-matrix.md"; Test-Path "$e/traditional-advanced-scan-results.md"; Test-Path "$e/traditional-advanced-validation.md"; Test-Path "$e/traditional-advanced-final-status.json"` | repo root | PASS | 0 | all six checks returned `True` |
| `.\\.venv\\Scripts\\Activate.ps1; python -m json.tool _condamad/stories/CS-207-traditional-advanced-final-audit-documentation/evidence/traditional-advanced-final-status.json` | repo root | PASS | 0 | final status JSON parsed successfully |

## Commands With Expected Nonzero Search Exit

| Command | Result | Classification |
|---|---|---|
| `rg -n $doctrine backend/app frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 1 | PASS: zero hits expected |
| `rg -n $calculators backend/app/services/chart frontend backend/app/infra/db/repositories -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 1 | PASS: zero hits expected |
| `rg -n $frontendDerivation frontend -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 1 | PASS: zero hits expected |
| `rg -n $legacy backend/app backend/tests frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 0 | PASS: hits classified in scan results |

## Skipped Or Adapted Commands

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `npm --prefix frontend run typecheck` | conditional | `frontend/package.json` has no `typecheck` script. | A standalone typecheck script cannot be invoked by that name. | `npm --prefix frontend run lint` runs the configured TypeScript no-emit checks and passed; `npm --prefix frontend run build` also passed. |

## Generated Contract Check

No generated client or OpenAPI contract was modified. No route, method, status code, public field, seed, migration, or generated schema file changed.

## App-Surface Diff Check

Production application files were not modified. The diff is limited to CS-207 generated/evidence files and story status/review evidence during closure.
