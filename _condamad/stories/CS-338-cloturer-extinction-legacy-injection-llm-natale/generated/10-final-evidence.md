# Final Evidence - CS-338-cloturer-extinction-legacy-injection-llm-natale

<!-- Commentaire global: cette preuve finale synthetise l'implementation et la validation de CS-338. -->

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-338-cloturer-extinction-legacy-injection-llm-natale
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale`
- Story registry target status: `ready-to-review`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/00-story.md`
- Initial `git status --short`: `?? _condamad/run-state.json`
- Pre-existing dirty files: `_condamad/run-state.json`
- AGENTS.md considered: root `AGENTS.md`
- Capsule generated/repaired: yes, missing generated files repaired only
- Story-status mapping checked: row `CS-338` points to the target story path and source brief.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story unchanged |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by helper |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC evidence |
| `generated/04-target-files.md` | yes | yes | PASS | Repaired by helper |
| `generated/06-validation-plan.md` | yes | yes | PASS | Repaired by helper |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Repaired by helper |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Final report created under `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/` | Capsule validation PASS; report path exists | PASS | |
| AC2 | Report proves `llm_astrology_input_v1` as unique natal LLM input | `pytest -q --long tests\integration\test_llm_legacy_extinction.py --tb=short` PASS | PASS | |
| AC3 | Remaining legacy terms classified in report | `legacy-scan-before.txt`, `legacy-scan-after.txt` | PASS | Textual historical matches accepted as classified |
| AC4 | Backend tests run without obsolete natal LLM mocks | `pytest -q --long tests --tb=short` PASS | PASS | 1420 passed, 9 skipped |
| AC5 | Modern guards cover `llm_astrology_input_v1` | New guards in `test_llm_legacy_extinction.py` | PASS | Schema, user payload, validation payload |
| AC6 | Documentation no longer presents old carriers as active | Report classifies `_condamad` and `_story_briefs` occurrences | PASS | Historical docs kept as archive |
| AC7 | Reintroduction guard blocks old carriers | Negative guards reject prompt/validation reinjection | PASS | |
| AC8 | External ambiguity blocks closure | No `decision-utilisateur-requise`; ownerised non-natal/generic surfaces documented | PASS | |

## Files changed

- `backend/tests/integration/test_llm_legacy_extinction.py`
- `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`
- `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/generated/**`
- `_condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- `_condamad/stories/cs-338/**` temporary erroneous capsule created by the first helper attempt, removed after path verification.

## Tests added or updated

- Added three guards to `backend/tests/integration/test_llm_legacy_extinction.py`:
  - modern natal contracts only expose `llm_astrology_input_v1`;
  - natal user payload ignores `chart_json`, `natal_data`, and `evidence_catalog` when modern input exists;
  - natal validation payload ignores declared legacy carriers.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale --root . --with-optional` | repo root | PASS | 0 | Capsule repaired |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale` | repo root | PASS | 0 | Capsule structure valid |
| `ruff format tests\integration\test_llm_legacy_extinction.py` | `backend` | PASS | 0 | Scoped Python formatting |
| `ruff check .` | `backend` | PASS | 0 | All checks passed |
| `python -B -m pytest -q --long tests\integration\test_llm_legacy_extinction.py --tb=short` | `backend` | PASS | 0 | 7 passed |
| `python -B -m pytest -q app\tests\unit\test_gateway_input_validation_payload.py --tb=short` | `backend` | PASS | 0 | 2 passed |
| `python -B -m pytest -q --long tests\integration\test_llm_runtime_suppression.py --tb=short` | `backend` | PASS | 0 | 8 passed |
| `python -B -m pytest -q --long tests --tb=short` | `backend` | PASS | 0 | 1420 passed, 9 skipped |
| `rg -n "chart_json\|natal_data\|evidence_catalog\|legacy\|fallback\|transition-condition" backend\app backend\tests _condamad _story_briefs` | repo root | PASS | 0 | Occurrences classified in report |
| `rg -n "llm_astrology_input_v1" backend\app backend\tests _condamad _story_briefs` | repo root | PASS | 0 | Modern input path present |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale` | repo root | PASS | 0 | Final capsule validation |
| `git diff --check -- backend\tests\integration\test_llm_legacy_extinction.py _condamad\reports\extinction-legacy-injection-llm-natale _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale _condamad\stories\story-status.md` | repo root | PASS | 0 | No whitespace errors; Git warned LF will become CRLF for the Python test file |

## Commands skipped or blocked

- `pytest` integration commands without `--long` were not used as final evidence because `backend/conftest.py` deselects `tests/integration/**` unless `--long` is provided.
- No frontend validation launched: frontend explicitly out of scope and untouched.

## DRY / No Legacy evidence

- No shim, alias, fallback, wrapper, re-export, dependency, migration, API route, or frontend path added.
- The new tests are negative guards, not compatibility tests.
- Remaining legacy terms are ownerised in the final report as non-natal, validation-only, generic runtime, guard-negative, or archive-documentaire.
- RG-002 respected: no backend API router edits.
- RG-022 respected: validation commands target collected pytest paths and use `--long` for integration collection.
- Registry gap retained: no exact reusable guardrail exists for natal LLM legacy carrier extinction; story says not to update guardrail registry.

## Diff review

- `git diff --stat -- backend\tests\integration\test_llm_legacy_extinction.py _condamad\reports\extinction-legacy-injection-llm-natale _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale _condamad\stories\story-status.md`: reviewed.
- `git diff --name-only -- ...`: reviewed.
- `git diff --check`: PASS.

## Final worktree status

- `M _condamad/stories/story-status.md`
- `M backend/tests/integration/test_llm_legacy_extinction.py`
- `?? _condamad/reports/extinction-legacy-injection-llm-natale/`
- `?? _condamad/run-state.json` (pre-existing)
- `?? _condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/evidence/`
- `?? _condamad/stories/CS-338-cloturer-extinction-legacy-injection-llm-natale/generated/*.md`

## Remaining risks

- `_condamad` and `_story_briefs` scans remain textually noisy because they include historical audit material; all such references are classified as archive-documentaire unless executable runtime evidence says otherwise.
- Generic runtime fields `ExecutionContext.chart_json` and `ExecutionContext.natal_data` remain for non-natal/shared runtime compatibility; natal prompt and validation guards now block their active use.

## Suggested reviewer focus

- Review the classification boundary for generic runtime fields and confirm the new negative guards cover the intended natal LLM path.

## Feedback loop routing

- No reusable process update propagated: the story already records the registry gap and explicitly forbids updating `_condamad/stories/regression-guardrails.md` during this implementation.
