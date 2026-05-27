# Dev Log

## Preflight

- Initial `git status --short`: pre-existing untracked `_condamad/run-state.json`, CS-339 brief, and CS-340 brief.
- Story registry row: `CS-339` path and source brief matched the target story.
- Capsule: required generated files were missing, then repaired with `condamad_prepare.py --repair-generated-only`.
- Capsule validation: `condamad_validate.py` PASS.

## Search evidence

- Scoped `rg` found `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS` in `gateway.py`, prior `provenance` prompt acceptance in orchestration/architecture tests, and audit hash assertions in `test_natal_llm_astrology_input_audit.py`.
- `RG-002` and `RG-022` were resolved from `_condamad/stories/regression-guardrails.md`.

## Implementation notes

- Gateway prompt projection now derives from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
- Runtime prompt tests parse the rendered payload and assert canonical prompt-visible key membership.
- Runtime and architecture guards reject audit-only prompt surfaces.
- Audit and hash behavior remain on the complete `llm_astrology_input_v1` object outside prompt rendering.
- Before/after prompt payload artifacts were saved under `evidence/`.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `ruff format app\domain\llm\runtime\gateway.py tests\llm_orchestration\test_llm_astrology_input_boundaries.py tests\architecture\test_llm_astrology_input_payload_boundaries.py` | PASS | Scoped formatting per project constraint. |
| `ruff check .` | PASS | Backend lint. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py tests\unit\domain\astrology\test_llm_astrology_input_hash.py --tb=short` | PASS | 12 passed. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_evidence.py tests\llm_orchestration\test_llm_astrology_input_boundaries.py --tb=short` | PASS | 6 passed. |
| `python -B -m pytest -q tests\architecture\test_llm_astrology_input_payload_boundaries.py tests\integration\test_llm_legacy_extinction.py --tb=short` | PASS | 5 passed, 7 deselected by default fast selection. |
| `python -B -m pytest -q tests\integration\llm\test_natal_llm_astrology_input_audit.py --long --tb=short` | PASS | 2 passed; `--long` required for `tests/integration/**`. |
| `python -B -m pytest -q tests --long --tb=short` | PASS | 1422 passed, 9 skipped. |
| `rg -n "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS\|prompt_visible\|audit_only\|projection_hash\|llm_input_hash\|provenance" app tests` | PASS | Hits are canonical contract, audit/persistence, tests, or unrelated provenance domains; no rendered prompt leak. |
| `git diff --check -- <story paths>` | PASS | Whitespace check clean; Git reported CRLF normalization warnings only. |

## Issues encountered

- A preparation attempt produced a case-insensitive capsule path collision on Windows; the tracked story files were restored before continuing.
- `backend/.tmp-pytest` remains locked after the full test run; cleanup was attempted twice and the residual is outside source/evidence changes.

## Decisions made

- No frontend delegation used because the story explicitly excludes frontend.
- No feedback-loop propagation: no reusable guardrail or skill correction is required beyond local story evidence.

## Final `git status --short`

- Modified: `_condamad/stories/story-status.md`, gateway, two backend tests.
- Added/untracked story evidence and generated capsule files for CS-339.
- Pre-existing untracked: `_condamad/run-state.json`, CS-339 brief, CS-340 brief.
