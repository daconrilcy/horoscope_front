# Validation Plan - CS-290

All Python commands were run after `. .\.venv\Scripts\Activate.ps1`.

## Commands Run

- `cd backend; ruff format app\services\llm_generation\natal\rejected_answer_workflow.py app\services\llm_generation\natal\interpretation_service.py app\infra\db\repositories\llm\narrative_answer_audit_repository.py tests\unit\test_rejected_narrative_answer_workflow.py tests\unit\test_rejected_narrative_answer_logging.py tests\integration\test_rejected_narrative_answer_audit.py tests\integration\test_rejected_narrative_answer_response.py tests\architecture\test_rejected_narrative_answer_boundary.py`
- `cd backend; ruff check app\services\llm_generation\natal\rejected_answer_workflow.py --fix`
- `cd backend; ruff check .`
- `cd backend; python -B -m pytest -q tests\unit\test_rejected_narrative_answer_workflow.py tests\unit\test_rejected_narrative_answer_logging.py tests\integration\test_rejected_narrative_answer_audit.py tests\integration\test_rejected_narrative_answer_response.py tests\architecture\test_rejected_narrative_answer_boundary.py --tb=short`
- `cd backend; python -B -m pytest -q --tb=short`
- `cd backend; python -B -c "from app.main import app; assert 'rejected_narrative_answer' not in str(app.openapi())"`
- `cd backend; python -B -c "from app.main import app; assert all('rejected-narrative' not in getattr(r, 'path', '') for r in app.routes)"`
- `rg -n "RAW_AI_ANSWER_MUST_STAY_INTERNAL|RAW_REJECTED_INTERNAL_ONLY|RAW_SECRET_ANSWER" backend\app\services\llm_generation\natal backend\app\api frontend\src`
- `rg -n "retry_queue|retry_worker|manual_publish|manual publish" backend\app\services\llm_generation\natal`
- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-290-rejected-narrative-answer-workflow`

## Skipped

- No frontend validation: story explicitly excludes frontend changes.
