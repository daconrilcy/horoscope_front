# Target Files

## Must Inspect Before Implementation

- `AGENTS.md`
- `_story_briefs/cs-357-ajouter-graphiques-mermaid-construction-prompts-theme-astral.md`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/00-story.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`

## Required Searches Before Editing

```powershell
rg -n "llm_astrology_input_v1|facts|signals|limits|shaping|persona|hard policy|provider" _condamad\docs\prompt-generation-cartography
rg -n "projection_hash|llm_input_hash|provider_response|chart_json|natal_data|observability" _condamad\docs\prompt-generation-cartography
rg -n "RG-042|RG-149|RG-041|RG-002" _condamad\stories\regression-guardrails.md
git status --short -- backend/app backend/tests frontend/src
```

## Modified Files

- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-baseline.txt`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/docs-after.txt`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/guardrails.txt`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/source-coverage.md`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/validation.txt`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/evidence/validation.md`
- `_condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden Or High-Risk Files

- `backend/app/**`
- `backend/tests/**`
- `frontend/src/**`
- `backend/alembic/**`
- prompt seed files, output schemas, provider integration files and runtime configuration outside documentation evidence
