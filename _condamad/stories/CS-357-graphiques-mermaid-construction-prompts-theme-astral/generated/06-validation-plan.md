# Validation Plan

## Targeted Checks

```powershell
python -B -c "from pathlib import Path; assert Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md').exists()"
python -B -c "from pathlib import Path; p=Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md'); assert p.read_text().count('```mermaid') >= 7"
rg -n "Comment lire les diagrammes|```mermaid|flowchart|sequenceDiagram" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "free|basic|premium|editorial|budget|sections|schema" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "Birth data|llm_astrology_input_v1|assembly|renderer|messages provider" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "facts|signals|limits|shaping|evidence|provenance" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "persona|astrologue|developer prompt|PromptAssemblyConfig|compose_persona_block" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "hard policy|non-invention|validation|repair|rejection|no provider call" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "system_core|developer prompt|payload user|provider parameters" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "prompt-visible|backend-only|projection_hash|llm_input_hash" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "provider_response|chart_json|natal_data" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "natal-prompt-construction-by-plan|CS-356" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
python -B -c "from pathlib import Path; r=Path('_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence'); assert (r/'validation.txt').exists(); assert (r/'source-coverage.md').exists(); assert (r/'docs-baseline.txt').exists(); assert (r/'docs-after.txt').exists(); assert (r/'guardrails.txt').exists()"
python -B -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend/src'], text=True); assert out.strip()==''"
```

## Early Guard Scans

```powershell
rg -n "prompt-visible|backend-only|validation-only|audit-only" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
rg -n "projection_hash|llm_input_hash|provider_response|chart_json|natal_data" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
git diff --check -- _condamad/docs/prompt-generation-cartography _condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral _condamad/stories/story-status.md
```

## Lint / Static Checks

```powershell
ruff check .
```

## Full Regression Checks

```powershell
python -B -m pytest -q --tb=short
```

## Rule For Skipped Commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
