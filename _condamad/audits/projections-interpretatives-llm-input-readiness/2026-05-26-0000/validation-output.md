# Validation Output

Toutes les commandes Python, pytest et ruff ci-dessous ont ete lancees depuis la racine du repository apres activation de `.\.venv\Scripts\Activate.ps1`.

## Skill Validation

```text
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
CONDAMAD domain audit validation passed.
```

```text
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
CONDAMAD domain audit lint passed.
```

## Story Artifact Checks

```text
python -c "from pathlib import Path; root=Path('_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000'); required=['00-audit.md','01-contract-comparison.md','02-field-classification.md','03-llm-readiness-matrix.md','04-recommendations.md','00-audit-report.md','01-evidence-log.md','02-finding-register.md','03-story-candidates.md','04-risk-matrix.md','05-executive-summary.md']; assert root.exists(); missing=[name for name in required if not (root/name).exists()]; assert not missing, missing"
PASS
```

```text
rg -n "structured_facts_v1|beginner_summary_v1|AINarrativeInput" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
PASS: hits found.

rg -n "client_interpretation_projection_v1" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
PASS: hits found.

rg -n "readiness_flags|evidence_refs|projection_hash|llm_input_hash|prompt_version|provider|model" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
PASS: hits found.

rg -n "factuel|signal interpretatif|shaping editorial|audit|exclusion|debug" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
PASS: hits found.

rg -n "current-llm-use|recommended-target|available-not-injected|product-only|audit-only" _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
PASS: hits found.
```

## Read-Only App Guard

```text
python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests'], text=True); assert out.strip() == '', out"
PASS
```

```text
git status --short -- _condamad _story_briefs backend/app backend/tests
?? _condamad/audits/projections-interpretatives-llm-input-readiness/
?? _condamad/run-state.json
```

`backend/app` et `backend/tests` restent inchanges; `_condamad/run-state.json` etait deja non suivi avant la creation de l'audit.

## Tests And Lint

```text
pytest -q backend/tests/unit/domain/astrology
594 passed in 4.72s
```

```text
pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py
5 passed in 1.12s
```

```text
ruff format --check .
1686 files already formatted
```

```text
ruff check .
All checks passed!
```

## Source Search

```text
rg -n "structured_facts_v1|beginner_summary_v1|client_interpretation_projection_v1" .\backend\app .\backend\tests
PASS: hits confirm projection owners, endpoint service, API/tests and integration coverage.

rg -n "AINarrativeInput|readiness_flags|evidence_refs|projection_hash|llm_input_hash" .\backend\app .\backend\tests
PASS: hits confirm AI narrative contract, audit persistence, rejected answer workflow and associated tests.
```

## Targeted Review Revalidation

```text
rg -n -e "AINarrativeInputBuilder" -e "AINarrativeInputContract" -e "structured_facts_v1" -e "client_interpretation_projection_v1" -e "beginner_summary_v1" .\backend\app\services\llm_generation .\backend\app\domain\llm .\backend\tests\llm_orchestration
PASS: zero hits; command exits 1 because rg reports no match.
```

```text
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
CONDAMAD domain audit validation passed.
```

```text
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000
CONDAMAD domain audit lint passed.
```
