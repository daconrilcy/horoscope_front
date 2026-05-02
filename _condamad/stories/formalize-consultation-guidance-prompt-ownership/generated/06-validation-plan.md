# Validation Plan

## Environment assumptions

- Commands run on Windows PowerShell.
- Every Python command must activate `.\.venv\Scripts\Activate.ps1` first.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story structure validation | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md` | `backend/` | yes | PASS |
| Story strict lint | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md` | `backend/` | yes | PASS |
| Guidance placeholder contract | `pytest -q app/tests/unit/test_guidance_service.py` | `backend/` | yes | PASS |
| Consultation precheck no LLM | `pytest -q app/tests/unit/test_consultation_generation_service.py` | `backend/` | yes | PASS |
| Governance anti-drift | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | yes | PASS |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Documentation ownership evidence | `rg -n "guidance_contextual" docs\llm-prompt-generation-by-feature.md` | repo root | yes | documented hits |
| Consultation family drift scan | `rg -n '"consultation"\|consultation_contextual\|developer_prompt.*prompt_content\|PROMPT_FALLBACK_CONFIGS' backend\app\domain backend\app\services backend\tests` | repo root | yes | only classified guard/known catalog hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format check | `ruff format --check .` | `backend/` | yes | PASS |
| Lint | `ruff check .` | `backend/` | yes | PASS |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression suite | `pytest -q` | `backend/` | yes | PASS |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | PASS |
| Diff summary | `git diff --stat` | repo root | yes | story files only in tracked diff |
| Worktree status | `git status --short` | repo root | yes | expected modified/untracked files only |
