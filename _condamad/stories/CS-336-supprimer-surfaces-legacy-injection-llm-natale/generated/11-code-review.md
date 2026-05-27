# Implementation Review - CS-336 supprimer-surfaces-legacy-injection-llm-natale

Verdict: CLEAN

## Scope Reviewed

- Story: `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/00-story.md`.
- Source brief: `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`.
- Tracker row: `_condamad/stories/story-status.md`, story `CS-336`, status `done`.
- Implementation evidence: `generated/10-final-evidence.md`, `evidence/removal-audit.md`,
  `evidence/legacy-carrier-scan-after.txt`, `evidence/natal-llm-payload-after.json`,
  `evidence/public-api-boundary-after.json` and `evidence/validation.txt`.
- Runtime/config/test surfaces reviewed through targeted source inspection and current validation output.

## Fresh Review Result

- AC alignment: AC1 to AC8 have durable evidence and matching runtime, schema, guard, scan, OpenAPI and artifact proof.
- Brief alignment: implementation keeps `llm_astrology_input_v1` as the only modern natal prompt astrology carrier and does not
  broaden into frontend, public endpoints, providers, DB or migrations.
- Legacy extinction: `NatalExecutionInput` exposes `llm_astrology_input_v1` and no `chart_json`, `natal_data` or
  `evidence_catalog`; the natal adapter forwards only the canonical key in `extra_context`; gateway validation skips old
  carriers for natal schemas and prompt rendering prioritizes the canonical key.
- Residual old-key hits: classified as non-natal/public projection, negative guards, validation owners, historical fixtures or
  unrelated legacy/fallback domains in `removal-audit.md` and the saved scan.
- Guardrails: RG-002 and RG-022 evidence is present through OpenAPI checks, targeted pytest and bounded `rg`.

## Findings

No actionable implementation issue found after evidence/status synchronization.

## Issues Fixed During This Review Loop

- Evidence/status drift: replaced the prior drafting-oriented review artifact with an implementation review and synchronized
  `00-story.md`, `generated/10-final-evidence.md` and `story-status.md` to `done`.

## Candidate Findings Rejected

- `ExecutionContext.chart_json` and `ExecutionContext.natal_data` remain in generic runtime contracts. Rejected as in-scope
  issue because AC1 targets `NatalExecutionInput` and the natal adapter no longer hydrates those fields for modern natal LLM
  prompt generation.
- `event_guidance` still declares `chart_json`. Rejected because it is a non-natal/public event guidance owner explicitly
  outside this story's natal LLM scope and classified as such.

## Validation Evidence

- `.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff format --check .; ruff check .`
  - Result: PASS, `1700 files already formatted`, `All checks passed!`.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py
  tests/architecture/test_llm_legacy_extinction.py tests/unit/test_natal_llm_use_case_input_contract.py
  tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/integration/test_llm_runtime_suppression.py
  app/tests/unit/test_ai_engine_adapter.py app/tests/unit/test_gateway_input_validation_payload.py --tb=short`
  - Result: PASS, `34 passed, 8 deselected`.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest -q tests --tb=short`
  - Result: PASS, `1208 passed, 218 deselected`.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -c "from app.main import app; assert app.routes;
  assert app.openapi()['paths']; assert 'chart_json' not in str(app.openapi()) and 'natal_data' not in str(app.openapi())"`
  - Result: PASS.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; rg -n
  "chart_json|natal_data|evidence_catalog|legacy|fallback|transition-condition" app tests`
  - Result: PASS with residual hits saved in `evidence/legacy-carrier-scan-after.txt` and classified in
    `evidence/removal-audit.md`.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; rg -n "llm_astrology_input_v1" app tests`
  - Result: PASS; canonical key present in runtime, config, seeds and tests.
- `.\.venv\Scripts\Activate.ps1; python .agents\skills\condamad-dev-story\scripts\condamad_validate.py
  _condamad\stories\CS-336-supprimer-surfaces-legacy-injection-llm-natale`
  - Result: PASS.
- `.\.venv\Scripts\Activate.ps1; python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py
  _condamad\stories\CS-336-supprimer-surfaces-legacy-injection-llm-natale\00-story.md`
  - Result: PASS.
- `.\.venv\Scripts\Activate.ps1; python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict
  _condamad\stories\CS-336-supprimer-surfaces-legacy-injection-llm-natale\00-story.md`
  - Result: PASS.
- `git diff --check`
  - Result: PASS; PowerShell only emitted Git line-ending warnings after subsequent status/stat commands.

## Review Output

- Produced artifact: `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/generated/11-code-review.md`.
- Propagation decision: no-propagation; fixes are local evidence/status corrections only.

## Residual Risk

Aucun risque restant identifie.
