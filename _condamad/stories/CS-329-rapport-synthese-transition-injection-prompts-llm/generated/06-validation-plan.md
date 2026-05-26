# Validation Plan

<!-- Commentaire global: ce fichier liste les validations deterministes retenues pour le rapport CS-329. -->

## Report path checks

```powershell
.\.venv\Scripts\Activate.ps1
python -c "from pathlib import Path; root=Path('_condamad/reports/calculs-interpretations-vers-prompts-llm'); assert root.exists(); print('report root: OK')"
Set-Location _condamad\reports\calculs-interpretations-vers-prompts-llm
python -c "from pathlib import Path; assert Path('2026-05-26-0000/rapport-transition-injection-prompts-llm.md').exists(); print('report file: OK')"
python -c "from pathlib import Path; r=Path('2026-05-26-0000'); assert (r/'evidence-sources.md').exists() and (r/'validation-output.md').exists(); print('evidence files: OK')"
```

## Contract and content scans

```powershell
rg -n "CS-324|CS-325|CS-326|CS-327|CS-328" _condamad\reports\calculs-interpretations-vers-prompts-llm
rg -n "legacy|recent-refonte|contrat cible|chart_json|structured_facts_v1" _condamad\reports\calculs-interpretations-vers-prompts-llm
rg -n "AINarrativeInput|NatalExecutionInput|ExecutionContext|Stories de refactor recommandees" _condamad\reports\calculs-interpretations-vers-prompts-llm
rg -n "Executive summary|Etat actuel de l'injection LLM|Annexes de preuves" _condamad\reports\calculs-interpretations-vers-prompts-llm\2026-05-26-0000\rapport-transition-injection-prompts-llm.md
```

## No application change guard

```powershell
git status --short -- backend/app backend/tests frontend/src backend/migrations
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## CONDAMAD story validation

```powershell
.\.venv\Scripts\Activate.ps1
python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-329-rapport-synthese-transition-injection-prompts-llm\00-story.md
python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-329-rapport-synthese-transition-injection-prompts-llm\00-story.md
git diff --check -- _condamad\reports\calculs-interpretations-vers-prompts-llm _condamad\stories\CS-329-rapport-synthese-transition-injection-prompts-llm _condamad\stories\story-status.md
```

## Rule for skipped commands

Application test suites are not required for this report-only story because no application, test, frontend or migration file is
modified. The no-app-change guard is the relevant executable invariant.
