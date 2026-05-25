# Validation Plan

All Python commands must run after activating `.\.venv\Scripts\Activate.ps1` from the repository root.

## Evidence contract checks

```powershell
$env:CS262_AUDIT = '_condamad/audits/ai-traceability/2026-05-24-1734'
$env:CS262_FINAL = '_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/generated/10-final-evidence.md'
python -B -c "from pathlib import Path; import os; p=Path(os.environ['CS262_AUDIT']); assert all((p/name).exists() for name in ['00-audit-report.md','01-evidence-log.md','02-finding-register.md','03-story-candidates.md','04-risk-matrix.md','05-executive-summary.md'])"
python -B -c "from pathlib import Path; import os; assert Path(os.environ['CS262_FINAL']).exists()"
rg -n "00-audit-report.md|01-evidence-log.md|02-finding-register.md" $env:CS262_FINAL
rg -n "03-story-candidates.md|04-risk-matrix.md|05-executive-summary.md" $env:CS262_FINAL
rg -n "answer_id|prompt_version|provider|model|full_prompt|prompt_ref|prompt_payload_snapshot" $env:CS262_FINAL
rg -n "CS-288|resolved-by-CS-288|open-decision|retention|DPO" $env:CS262_FINAL
```

## Runtime evidence checks

```powershell
Set-Location backend
python -B -m pytest -q tests/unit/test_narrative_answer_audit_model.py tests/integration/test_narrative_answer_audit_repository.py tests/integration/test_narrative_answer_audit_schema.py --tb=short
ruff format --check app\infra\db\models\user_natal_interpretation.py tests\unit\test_narrative_answer_audit_model.py tests\integration\test_narrative_answer_audit_repository.py tests\integration\test_narrative_answer_audit_schema.py
ruff check .
Set-Location ..
```

## Tracker and immutability checks

```powershell
python -B -c "from pathlib import Path; text=Path('_condamad/stories/story-status.md').read_text(encoding='utf-8'); assert 'CS-262' in text and 'ready-to-review' in text"
python -B -c "from pathlib import Path; assert Path('_condamad/stories/CS-262-audit-existing-prompt-version-answer-id-storage/generated/10-final-evidence-validation.txt').exists()"
git status --short -- backend/app backend/tests frontend/src backend/migrations
```

## CONDAMAD capsule checks

```powershell
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py --final _condamad\stories\CS-292-reconcile-cs-262-ai-traceability-final-evidence
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-292-reconcile-cs-262-ai-traceability-final-evidence\00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-292-reconcile-cs-262-ai-traceability-final-evidence\00-story.md
```

## Skipped command rule

Record any skipped validation with the exact command, reason, risk and compensating evidence.
