# Validation Output

All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

| Command | Result |
|---|---|
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` | PASS - CONDAMAD domain audit validation passed. |
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` | PASS - CONDAMAD domain audit lint passed. |
| `rg -n "legacy|recent-refonte|transition|target-candidate|out-of-scope" _condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` | PASS - required class vocabulary found in audit artifacts. |
| `rg -n "NatalExecutionInput|chart_json|natal_data|astro_context|evidence_catalog" _condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` | PASS - required LLM input surfaces found in audit artifacts. |
| `python -S -B -c "... required audit files exist ..."` | PASS - story-specific and CONDAMAD standard files exist. |
| `python -S -B -c "... git status --short -- backend/app backend/tests frontend ..."` | PASS - no application, test or frontend file changes. |
| `pytest -q backend/tests/unit/domain/astrology` | PASS - 594 passed in 4.84s. |

## Not Run

- `ruff format .` was not run because this is an audit-only story and formatters are outside the read-only audit workflow.
- `ruff check .` was not run because no Python application or test file was changed; the skill artifact validator/linter and targeted astrology tests were the applicable checks.
