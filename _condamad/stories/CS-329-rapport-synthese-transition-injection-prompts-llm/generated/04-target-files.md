# Target Files

<!-- Commentaire global: ce fichier liste les artefacts inspectes et modifies pour l'implementation report-only de CS-329. -->

## Must inspect before implementation

- `AGENTS.md`
- `_story_briefs/cs-329-rapport-synthese-transition-injection-prompts-llm.md`
- `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/00-story.md`
- `_condamad/stories/story-status.md`
- `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/**`
- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/**`
- `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/**`
- `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/**`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/**`

## Required searches before editing

```powershell
rg -n "CS-324|CS-325|CS-326|CS-327|CS-328" _condamad
rg -n "legacy|recent-refonte|contrat cible|chart_json|structured_facts_v1" _condamad
git status --short -- _condamad _story_briefs backend/app backend/tests frontend/src backend/migrations
```

## Modified files

- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/evidence-sources.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/validation-output.md`
- `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/generated/04-target-files.md`
- `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/generated/06-validation-plan.md`
- `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/generated/10-final-evidence.md`
- `_condamad/stories/CS-329-rapport-synthese-transition-injection-prompts-llm/generated/11-code-review.md`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `backend/app/**`
- `backend/tests/**`
- `frontend/src/**`
- `backend/migrations/**`
- prompt files, providers, public endpoints and database models
